import sched
import time
from datetime import datetime, timezone
from queue import Queue
from threading import Event, Thread
from uuid import uuid4

import requests

from .. import transport
from ..exceptions import ClientTransportException
from ..logging import logger
from ..oauth import OAuthClient, PassthroughOAuthClient
from ..uftp import PayloadMessage, PayloadMessageResponse, SignedMessage


class ShapeshifterClient:
    """
    Basis for all Shapeshifter client.
    """

    sender_role: str
    recipient_role: str
    protocol_version = "3.0.0"
    num_outgoing_workers = 10
    num_delivery_attempts = 10
    request_timeout = 30
    exponential_retry_factor = 1
    exponential_retry_base = 2

    def __init__(
        self,
        sender_domain: str,
        signing_key: str,
        recipient_domain: str,
        recipient_endpoint: str = None,
        recipient_signing_key: str = None,
        oauth_client: OAuthClient = None,
    ):
        """
        Shapeshifter client class that allows you to initiate messages to a different party.
        :param str sender_domain: your sender domain
        :param str signing_key:   your private signing key
        :param str recipient_domain:   the domain of the recipient
        :param str recipient_endpoint: the full http endpoint URL of the recipient. If omitted,
                                       will look up the endpoint using DNS.
        :param str recipient_signing_key:    the public signing key of the recipient. If omitted, will
                                              look up the signing key using DNS.
        :param OAuthClient oauth_client: Optional OAuth client instance for using oauth to authenticate outgoing messages.
        """
        if recipient_domain is None and recipient_endpoint is None:
            raise ValueError(
                "One of recipient_domain or recipient_endpoint must be provided."
            )

        self.sender_domain = sender_domain
        self.signing_key = signing_key
        self.recipient_domain = recipient_domain
        self.recipient_endpoint = recipient_endpoint
        self.recipient_signing_key = recipient_signing_key

        # The outgoing queue and scheduler are used when queueing
        # messages for delivery later. This allows the Shapeshifter
        # UFTP client to handle message retries on an exponential
        # time schedule, and delivers the result in the provided
        # callback function.
        self.outgoing_queue = Queue()
        self.outgoing_workers = None
        self.scheduler = sched.scheduler(time.monotonic, time.sleep)
        self.scheduler_event = Event()
        self.scheduler_thread = None

        if oauth_client:
            self.oauth_client = oauth_client
        else:
            self.oauth_client = PassthroughOAuthClient()

    def _send_message(self, message: PayloadMessage) -> PayloadMessageResponse:
        """
        Perform an operation. This will take the message object, pack
        it up into a SignedMessage, sign and seal it, and send it to
        the recipient. It returns an unsealed PayloadMessageResponse
        that contains the functional status of the request. The
        actual response always arrives asynchronously on your service
        (which runs separately).
        """
        if not isinstance(message, PayloadMessage):
            raise TypeError(
                f"'message' must be a (subclass of) PayloadMessage, you provided: {type(message)}"
            )

        # Fill the PayloadMessage's fields that are common to all
        # messages. We don't require the developer to fill these out
        # every time they create any message, in order to reduce the
        # duplicated code that would result in, and all of these
        # properties can be calculated in the framework anyway.
        message.version = self.protocol_version
        message.sender_domain = self.sender_domain
        message.sender_role = self.sender_role
        message.recipient_domain = self.recipient_domain
        message.time_stamp = (
            message.time_stamp or datetime.now(timezone.utc).isoformat()
        )
        message.message_id = message.message_id or str(uuid4())
        message.conversation_id = message.conversation_id or str(uuid4())

        logger.info(f"The PayloadMessage is: {message}")

        # Seal the message using our own private signing key
        sealed_message = transport.seal_message(message, self.signing_key)

        # Pack up the message into a SignedMessage
        signed_message = SignedMessage(
            sender_domain=self.sender_domain,
            sender_role=self.sender_role,
            body=sealed_message,
        )

        # Serialize the message into an XML blob
        serialized_message = transport.to_xml(signed_message)

        logger.debug(f"Sending message to {self.recipient_endpoint}:")
        logger.debug(serialized_message)

        # Send the request to the relevant endpoint
        with self.oauth_client.ensure_authenticated():
            response = requests.post(
                self.recipient_endpoint,
                data=serialized_message,
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    **self.oauth_client.auth_header
                },
                timeout=self.request_timeout,
            )
        if response.status_code != 200:
            error_msg = (
                f"Request to {self.recipient_endpoint} was not succesful: "
                f"HTTP {response.status_code}: {response.text}"
            )
            logger.error(error_msg)
            raise ClientTransportException(error_msg, response=response)

        # If the response was empty, don't attempt to parse it
        if len(response.content) == 0:
            return None

        # Instantiate a SignedMessage object from the response bytes.
        sealed_response = transport.parser.from_bytes(response.content)

        # Use the static key that was provided when the client was
        # initialized, or retrieve the key using DNS. The DNS
        # implementation caches the DNS lookups so they are not that
        # expensive after the first time.
        if not (recipient_signing_key := self.recipient_signing_key):
            recipient_signing_key = transport.get_key(
                self.recipient_domain, self.recipient_role
            )

        # Unseal the response using the other party's public signing
        # key and return the response message within it
        return transport.unseal_message(
            message=sealed_response.body, public_key=recipient_signing_key
        )

    # ------------------------------------------------------------ #
    #     Methods related to queueing and scheduling outgoing      #
    #                          messages.                           #
    # ------------------------------------------------------------ #

    def _queue_message(self, message, callback, attempt=1):
        self.outgoing_queue.put((message, callback, attempt))
        self._run_outgoing_workers()

    def _outgoing_worker(self):
        while True:
            message, callback, attempt = self.outgoing_queue.get()
            try:
                response = self._send_message(message)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if attempt <= self.num_delivery_attempts:
                    # Reschedule with exponential backoff
                    delay_time = (
                        self.exponential_retry_factor
                        * self.exponential_retry_base**attempt
                    )
                    logger.warning(
                        f"Outgoing message {message.__class__.__name__} to "
                        f"{message.recipient_domain} could not be delivered "
                        f"due to a {exc.__class__.__name__}, will try again in {delay_time:.0f} seconds."
                    )
                    self.scheduler.enter(
                        delay=delay_time,
                        priority=1,
                        action=self._queue_message,
                        argument=((message, callback, attempt + 1)),
                    )
                    self._run_scheduler()
                else:
                    logger.error(
                        f"Could not deliver {message.__class__.__name__} "
                        f"to {self.recipient_role} at {self.recipient_domain}, "
                        f"even after {self.num_delivery_attempts} attempts."
                    )
            else:
                try:
                    callback(response)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logger.error(
                        "There was an exception during the callback "
                        f"for a {message.__class__.__name__} message: "
                        f"{err.__class__.__name__}: {err}"
                    )
            finally:
                self.outgoing_queue.task_done()

    def _run_scheduler(self):
        """
        Make sure the scheduler thread is running and awake.
        """
        if not self.scheduler_thread:
            self.scheduler_thread = Thread(target=self._scheduler_thread, daemon=True)
            self.scheduler_thread.start()
        self.scheduler_event.set()

    def _scheduler_thread(self):
        """
        Intended to run the python scheduler in a background thread.
        You can wake it up anytime by setting the scheduler event.
        """
        while True:
            self.scheduler_event.wait()
            self.scheduler_event.clear()
            self.scheduler.run()

    def _run_outgoing_workers(self):
        """
        Start up the outgoing queue workers.
        """
        if not self.outgoing_workers:
            self.outgoing_workers = [
                Thread(target=self._outgoing_worker, daemon=True)
                for _ in range(self.num_outgoing_workers)
            ]
            for thread in self.outgoing_workers:
                thread.start()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

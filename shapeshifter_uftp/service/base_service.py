from datetime import datetime, timezone
from queue import Queue
from uuid import uuid4
from time import sleep
from threading import Thread
import re

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi_xml import XmlAppResponse, NonJsonRoute
import uvicorn

from ..client import client_map
from ..uftp import (
    SignedMessage,
    PayloadMessage,
    PayloadMessageResponse,
    AcceptedRejected,
)
from ..exceptions import (
    FunctionalException,
    TransportException,
    InvalidSenderException,
    InvalidMessageException,
)
from ..logging import logger
from .. import transport


class ShapeshifterService():
    """
    Basis for all Shapeshifter Services. Defines the web service, the
    message ingestion, the post-processing queue mechanics, and
    threading and context options.
    """

    protocol_version = "3.0.0"
    sender_domain = None
    sender_role = None
    acceptable_messages = []

    num_inbound_threads = 10
    num_outbound_threads = 10

    def __init__(
        self,
        sender_domain,
        signing_key,
        key_lookup_function=None,
        endpoint_lookup_function=None,
        host: str = "0.0.0.0",
        port: int = 8080,
        path="/shapeshifter/api/v3/message",
    ):
        """
        :param sender_domain: our sender domain (FQDN) that the recipient uses to look us up.
        :param signing_key: the private singing key that we use to sign outgoing messages.
        :param key_lookup_function: A callable that takes a (sender_domain, sender_role)
                                  pair and returns a verify_key (str or bytes).
                                  Omit parameter to use DNS for key lookup.
        :param key_lookup_function: A callable that takes a (sender_domain, sender_role)
                                  pair and returns a full endpoint URL (str).
                                  Omit parameter to use DNS for endpoint lookup.
        :param host: the host to bind the server to (usually 127.0.0.1 or 0.0.0.0)
        :param port: the port to bind the server to (default: 8080)
        :param path: the URL path that the server listens on (default: /shapeshifter/api/v3/message)
        """

        # Set the sender domain, which is used
        # to identify us to the other party.
        self.sender_domain = sender_domain

        # The signing key is used to sign outgoing messages. The
        # corresponding public key should be published via DNS or
        # given to the recipient out-of-band.
        self.signing_key = signing_key

        # The key lookup method is used to look up keys for the other
        # party. If omitted, use DNS lookups using well-known DNS names.
        self.key_lookup_function = key_lookup_function or transport.get_key

        # The endpoint lookup method is used to look up the endpoint
        # that we send all messages to. If omitted, use DNS lookups
        # using well-known DNS names.
        self.endpoint_lookup_function = endpoint_lookup_function or transport.get_endpoint

        # The FastAPI web app takes care of routing messages to the
        # (one) endpoint, and by virtue of FastAPI-XML convert the
        # python-friendly objects into XML and vice versa.
        self.app = FastAPI(default_response_class=XmlAppResponse)
        self.app.router.route_class = NonJsonRoute
        self.app.router.add_api_route(
            path,
            endpoint=self._receive_message,
            response_model=SignedMessage,
            methods=["POST"],
            status_code=200,
        )

        # The web server hosts the FastAPI application and takes care
        # of the HTTP transport.
        config = uvicorn.Config(app=self.app, host=host, port=port)
        self.server = uvicorn.Server(config)
        self.server_thread = None

        # Create an incoming queue for post-processing messages. This
        # queue is filled by the pre_process methods of the
        # subclasses, and is consumed by the post_process method
        self.inbound_queue = Queue()

    def run(self):
        """
        Start the web server that hosts the FastAPI application. Other
        participants can now send messages to us.
        """
        # Start the inbound workers as separate, daemonized threads
        for _ in range(self.num_inbound_threads):
            thread = Thread(target=self._inbound_worker, daemon=True)
            thread.start()

        # Start the service and start accepting incoming requests.
        self.server.run()

    def run_in_thread(self):
        """
        Run the service in a background thread.
        """
        self.server_thread = Thread(target=self.run)
        self.server_thread.start()
        while not self.server.started:
            sleep(0.1)

    def stop(self):
        """
        Stop the service if it was running in a separate thread.
        """
        self.server.should_exit = True
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()
        self.server_thread = None


    # ------------------------------------------------------------ #
    #   Message handling and processing methods, internal to the   #
    #              Shapeshifter UFTP implementation.               #
    # ------------------------------------------------------------ #

    def _receive_message(self, message: SignedMessage) -> SignedMessage:
        """
        The default entrypoint for the route. This will unpack the
        message and validate the signature. It will thes pass the
        PayloadMessago to the pre processing function for a
        response.
        """
        logger.info(f"Got a request: {message}")
        # Get the public key that is used to decrypt the message
        signing_key = self.key_lookup_function(
            message.sender_domain, message.sender_role.value
        )

        logger.debug(f"The signing key is {signing_key}")

        # Unseal the message, returning an error if required
        try:
            unsealed_message = transport.unseal_message(message.body, signing_key)

            # Verify that the sender_domain inside the message is the
            # same as the sender_domain of the SignedMessage
            # envelope
            if unsealed_message.sender_domain != message.sender_domain:
                logger.warning(
                    "Received a message with mismatching sender_domain in the "
                    f"SignedMessage envelope ({message.sender_domain}) and the "
                    f"inner PayloadMessage ({unsealed_message.sender_domain})"
                )
                raise InvalidSenderException()

            if type(unsealed_message) not in self.acceptable_messages:
                logger.warning(
                    f"Received a misdirected message of type {unsealed_message.__class__.__name__} "
                    f"from {unsealed_message.sender_domain}.")
                raise InvalidMessageException(unsealed_message)

        except TransportException as err:
            logger.warning(f"The original transport error is {err.__class__.__name__}: {err}")
            raise HTTPException(err.http_status_code) from err

        except FunctionalException as err:
            response = PayloadMessageResponse(
                reference_message_id = unsealed_message.message_id,
                result = AcceptedRejected.REJECTED,
                rejection_reason = err.rejection_reason
            )

        else:
            # If the initial checks passed, process the message in the
            # user-defined pipeline.
            response = self._pre_process_message(unsealed_message)
            if response.result == AcceptedRejected.ACCEPTED:
                self.inbound_queue.put(unsealed_message)

        # Add the default parameters to the PayloadMessageResponse.
        response.version = self.protocol_version
        response.sender_domain = self.sender_domain
        response.recipient_domain = message.sender_domain
        response.time_stamp = response.time_stamp or datetime.now(timezone.utc).isoformat()
        response.message_id = response.message_id or str(uuid4())
        response.conversation_id = unsealed_message.conversation_id
        response.reference_message_id = unsealed_message.message_id

        # Pack up the sealed message blob inside a SignedMessage
        # envelope. We attach our sender domain and role so that the
        # other side can look up the relevent keys for opening the
        # message.
        sealed_message = transport.seal_message(response, self.signing_key)
        return SignedMessage(
            sender_domain = self.sender_domain,
            sender_role = self.sender_role,
            body = sealed_message,
        )

    def _pre_process_message(self, message: PayloadMessage) -> PayloadMessageResponse:
        """
        Find the relevant pre-processing method to handle the HTTP
        request for the given message, and return its result.
        """
        pre_process_method_name = f"pre_process_{snake_case(message.__class__.__name__)}"
        pre_process_method = getattr(self, pre_process_method_name)
        return pre_process_method(message)

    def _process_message(self, message: PayloadMessage):
        """
        Find the relevant post-processing method to handle the message
        outside of the request context, and run it.
        """
        process_method_name = f"process_{snake_case(message.__class__.__name__)}"
        process_method = getattr(self, process_method_name)
        process_method(message)

    def _inbound_worker(self):
        """
        Worker that reads from the inbound queue and calls the
        handling function to post-process the message.
        """
        while True:
            message = self.inbound_queue.get()
            try:
                self._process_message(message)
            except Exception as err:
                logger.error(
                    f"An error occurred during the post-processing of a {message.__class__.__name__} message."
                    f"{err.__class__.__name__}: {err}"
                )
            finally:
                self.inbound_queue.task_done()

    def _get_client(self, recipient_domain, recipient_role):
        """
        Method to get a relevant client to communicate to the
        indicated participant.
        """
        client_cls = client_map[(self.sender_role, recipient_role)]
        recipient_endpoint = self.endpoint_lookup_function(recipient_domain, recipient_role)
        recipient_signing_key = self.key_lookup_function(recipient_domain, recipient_role)
        return client_cls(
            sender_domain = self.sender_domain,
            signing_key = self.signing_key,
            recipient_domain = recipient_domain,
            recipient_endpoint = recipient_endpoint,
            recipient_signing_key = recipient_signing_key
        )

    def __enter__(self):
        """
        Context-manager method that allows an instance of this class to be
        used in a temporary context.

        Starts the uvicorn server in a separate thread and waits for it
        to be started. Useful in testing scenarios.

        Usage:

        with MyShapeshifterServiceSubClass(...) as server:
            # your test code here, server exists cleanly when leaving
            # the 'with' block.
        """
        self.run_in_thread()
        return self

    def __exit__(self, *args, **kwargs):
        """
        Tell uvicorn we should exit and wait for the thread to finish.
        """
        self.stop()


def snake_case(text):
    """
    Convert text from CamelCase to snake_case.
    """
    return re.sub(r"(.)([A-Z][a-z])", r"\1_\2", text).lower()

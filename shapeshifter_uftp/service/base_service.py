import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Thread
from time import sleep
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Response
from fastapi.exceptions import HTTPException
from fastapi_xml import XmlAppResponse, XmlRoute

from .. import transport
from ..client import client_map
from ..exceptions import (
    FunctionalException,
    InvalidMessageException,
    InvalidSenderException,
    TransportException,
)
from ..logging import logger
from ..uftp import (
    AcceptedRejected,
    PayloadMessage,
    PayloadMessageResponse,
    SignedMessage,
    request_response_map,
)


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
        oauth_lookup_function=None,
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
        :param oauth_lookup_function: A callable that takes a (sender_domain, sender_role)
                                      pair and returns in instance of shapeshifter_uftp.OAuthClient
                                      if OAuth authentication is required.
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

        # The OAuth lookup function is used to get the OAuth instance
        # used to authenticate outgoing requests.
        self.oauth_lookup_function = oauth_lookup_function

        # The FastAPI web app takes care of routing messages to the
        # (one) endpoint, and by virtue of FastAPI-XML convert the
        # python-friendly objects into XML and vice versa.
        self.app = FastAPI(default_response_class=XmlAppResponse)
        self.app.router.route_class = XmlRoute
        self.app.router.add_api_route(
            path,
            endpoint=self._receive_message,
            response_model=None,
            methods=["POST"],
            status_code=200,
        )

        # The web server hosts the FastAPI application and takes care
        # of the HTTP transport.
        config = uvicorn.Config(app=self.app, host=host, port=port)
        self.server = uvicorn.Server(config)
        self.server_thread = None

        # Create an inbound executor worker
        self.inbound_executor = ThreadPoolExecutor(max_workers=self.num_inbound_threads)
        self.outbound_executor = ThreadPoolExecutor(max_workers=self.num_outbound_threads)


    def run(self):
        """
        Start the web server that hosts the FastAPI application. Other
        participants can now send messages to us.
        """
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

    def _receive_message(self, message: SignedMessage) -> None:
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
            self.outbound_executor.submit(self._reject_message, message, unsealed_message, err.rejection_reason)

        else:
            # If the initial checks passed, process the message in the
            # user-defined pipeline.
            self.inbound_executor.submit(self._process_message, unsealed_message)

        return Response(status_code=200)

    def _process_message(self, message: PayloadMessage):
        """
        Find the relevant post-processing method to handle the message
        outside of the request context, and run it.
        """
        process_method_name = f"process_{snake_case(message.__class__.__name__)}"
        process_method = getattr(self, process_method_name)
        try:
            process_method(message)
        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.error(
                f"An error occurred during the post-processing of a {message.__class__.__name__} message."
                f"{err.__class__.__name__}: {err}"
            )

    def _get_client(self, recipient_domain, recipient_role):
        """
        Method to get a relevant client to communicate to the
        indicated participant.
        """
        client_cls = client_map[(self.sender_role, recipient_role)]
        recipient_endpoint = self.endpoint_lookup_function(recipient_domain, recipient_role)
        recipient_signing_key = self.key_lookup_function(recipient_domain, recipient_role)
        oauth_client = self.oauth_lookup_function(recipient_domain, recipient_role) if self.oauth_lookup_function else None
        return client_cls(
            sender_domain = self.sender_domain,
            signing_key = self.signing_key,
            recipient_domain = recipient_domain,
            recipient_endpoint = recipient_endpoint,
            recipient_signing_key = recipient_signing_key,
            oauth_client = oauth_client,
        )

    def _reject_message(self, message, unsealed_message, reason):
        """
        Send a rejection to the sending party.
        """
        if type(unsealed_message) not in request_response_map:
            return

        client = self._get_client(message.sender_domain, message.sender_role)
        response_type = request_response_map[type(unsealed_message)]
        response_id_field = snake_case(type(unsealed_message).__name__) + "_message_id"
        message_contents = {
            "recipient_domain": message.sender_domain,
            "conversation_id": unsealed_message.conversation_id,
            "result": AcceptedRejected.REJECTED,
            "rejection_reason": reason,
            response_id_field: unsealed_message.message_id
        }
        response_message = response_type(**message_contents)
        client._send_message(response_message)


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

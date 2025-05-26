Shapeshifter library for Python
===============================

This is a Python implementation of the ShapeShifter UFTP protocol.

Installation
------------

.. code-block:: python3

    pip install shapeshifter-uftp

Running tests
------------

.. code-block:: bash

    $ pip install .
    $ pip install .[dev]
    $ pytest .


Getting Started
---------------

Shapehifter always requires the use of a Client and a Service, because all responses are asynchronous.

You choose the server class based on your role in the Shapeshifter conversation. If you are an Aggregator (also known as a CSP), you can use this setup:

.. code-block:: python3

    from datetime import datetime, timedelta, timezone

    from shapeshifter_uftp import ShapeshifterAgrService
    from shapeshifter_uftp.uftp import (FlexOffer, FlexOfferOption,
                                        FlexOfferOptionISP, FlexRequest,
                                        FlexRequestResponse, FlexOrder, FlexOrderResponse,
                                        AcceptedRejected)
    from xsdata.models.datatype import XmlDate


    class DemoAggregator(ShapeshifterAgrService):
        """
        Aggregator service that implements callbacks for
        each of the messages that can be received.
        """

        def process_agr_portfolio_query_response(self, message):
            print(f"Received a message: {message}")

        def process_agr_portfolio_update_response(self, message):
            print(f"Received a message: {message}")

        def process_d_prognosis_response(self, message):
            print(f"Received a message: {message}")

        def process_flex_request(self, message: FlexRequest):
            print(f"Received a message: {message}")

            # Example of how to send a new message after
            # processing an incoming message.
            dso_client = self.dso_client(message.sender_domain)

            # Send the FlexRequestResponse
            dso_client.send_flex_request_response(
                FlexRequestResponse(
                    flex_request_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                    result=AcceptedRejected.ACCEPTED
                )
            )

            # Send the FlexOffer
            dso_client.send_flex_offer(
                FlexOffer(
                    flex_request_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                    isp_duration="PT15M",
                    period=XmlDate(2023, 1, 1),
                    congestion_point="ean.123456789012",
                    expiration_date_time=datetime.now(timezone.utc).isoformat(),
                    offer_options=[
                        FlexOfferOption(
                            isps=[FlexOfferOptionISP(power=1, start=1, duration=1)],
                            option_reference="MyOption",
                            price=2.30,
                            min_activation_factor=0.5,
                        )
                    ],
                )
            )

        def process_flex_offer_response(self, message: FlexOffer):
            print(f"Received a message: {message}")

        def process_flex_offer_revocation_response(self, message):
            print(f"Received a message: {message}")

        def process_flex_order(self, message: FlexOrder):
            print(f"Received a message: {message}")

            dso_client = self.dso_client(message.sender_domain)
            dso_client.send_flex_order_response(
                FlexOrderResponse(
                    flex_order_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                    result=AcceptedRejected.ACCEPTED
                )
            )

        def process_flex_reservation_update(self, message):
            print(f"Received a message: {message}")

        def process_flex_settlement(self, message):
            print(f"Received a message: {message}")

        def process_metering_response(self, message):
            print(f"Received a message: {message}")


    def key_lookup(sender_domain, sender_role):
        """
        Lookup function for public keys, so that incoming
        messages can be verified.
        """
        known_senders = {
            ("dso.demo", "DSO"): "NsTbq/iABU6tbsjriBg/Z5dSfQstulD0GpMI2fLDWec=",
            ("cro.demo", "CRO"): "ySUYU87usErRFKGJafwvVDLGhnBVJCCNYfQvmwv8ObM=",
        }
        return known_senders.get((sender_domain, sender_role))


    def endpoint_lookup(sender_domain, sender_role):
        """
        Lookup function for endpoints, so that the service
        knowns where to send responses to.
        """
        known_senders = {
            ("dso.demo", "DSO"): "http://localhost:8081/shapeshifter/api/v3/message",
            ("cro.demo", "CRO"): "http://localhost:8082/shapeshifter/api/v3/message",
        }
        return known_senders.get((sender_domain, sender_role))

    aggregator = DemoAggregator(
        sender_domain="aggregator.demo",
        signing_key="mz5XYCNKxpx48K+9oipUhsjBZed3L7rTVKLsWmG1HOqRLIeuGpIa1KAt6AlbVGqJvewd8v1J0uVUTqpGt7F8tw==",
        key_lookup_function=key_lookup,
        endpoint_lookup_function=endpoint_lookup,
        port=8080,
    )

    # Start the Aggregator Service
    aggregator.run_in_thread()

    # Create a client object to talk to a DSO
    dso_client = aggregator.dso_client("dso.demo")

    # Create a Flex Offer Message
    flex_offer_message = FlexOffer(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        expiration_date_time=datetime.now(timezone.utc).isoformat(),
        flex_request_message_id=str(uuid4())
        offer_options=[
            FlexOfferOption(
                isps=[FlexOfferOptionISP(power=1, start=1, duration=1)],
                option_reference="MyOption",
                price=2.30,
                min_activation_factor=0.5,
            )
        ],
    )

    # As a demo, press enter to send another FlexOffer message to the DSO.
    while True:
        try:
            input("Press return to send a FlexOffer message to the DSO")
            response = dso_client.send_flex_offer(flex_offer_message)
            print(f"Response was: {response}")
        except:
            aggregator.stop()
            break

Using OAuth in outgoing requests
--------------------------------

To use OAuth in outgoing requests, you can use the provided OAuthClient class. To use it in a bare Shapeshifter client:

.. code-block:: python3

    from shapeshifter_uftp import ShapeshifterAgrDsoClient, OAuthClient

    oauth_client = OAuthClient(
        url="https://oauth.provider.url",
        client_id="my-client-id",
        client_secret="my-client-secret"
    )

    client = ShapeshifterAgrDsoClient(
        sender_domain="my.aggregator.domain",
        signing_key="abcdef",
        recipient_domain="some.dso",
        recipient_endpoint="https://some.dso.endpoint/shapeshifter/api/v3/message",
        recipient_signing_key="123456",
        oauth_client=oauth_client,
    )

    # If you use any of the sending methods, the oauth client will
    # make sure you're authenticated.
    client.send_flex_request_response(...)


Similarly, if you have a Service instance that dynamically needs to retrieve the OAuth information for each different recipient server, you can provide an ``oauth_lookup_function`` that takes a ``(sender_domain, sender_role)`` and returns an instance of OAuthClient:


Overview
--------

This library implements the full UFTP protocol that you can use for Shapeshifter communications. It implements all three roles: Distribution System Operator (**DSO**), Aggregator (**AGR**) and Common Reference Operator (**CRO**) in both directions (client and service).

Features of this package:

- Building, parsing and validation of the XML messages
- Signing and verifying of the XML messages using signatures
- DNS for service discovery and key retrieval
- Convenient clients for each role-pair
- Convenient services for each role
- JSON-serializable dataclasses for easy transport to other systems
- Fully internal queing system for full-duplex communication with minimal user code required
- Compatible with the 3.0.0 version of the Shapeshifter protocol.

Version History
---------------

+-------------+-------------------+----------------------------------+
| Version     | Release Date      | Release Notes                    |
+=============+===================+==================================+
| 2.0.0       | 2025-05-21        | Support for OAuth 2 on outgoing  |
|             |                   | messages, updated dependencies   |
+-------------+-------------------+----------------------------------+
| 1.2.0       | 2024-04-04        | Upgrade to latest FastAPI and    |
|             |                   | Pydantic.                        |
+-------------+-------------------+----------------------------------+
| 1.1.2       | 2024-03-12        | Pinned dependencies after a      |
|             |                   | breaking update to fastapi-xml   |
|             |                   | was released.                    |
+-------------+-------------------+----------------------------------+
| 1.1.0       | 2023-08-30        | Use the published 3.0.0 spec     |
|             |                   | for the XSD validation and       |
|             |                   | objects.                         |
+-------------+-------------------+----------------------------------+
| 1.0.1       | 2023-08-23        | Fixes the following two issues:  |
|             |                   |                                  |
|             |                   | - Outgoing signed messages would |
|             |                   |   be twice-encoded into base64   |
|             |                   | - Support for empty response     |
|             |                   |   messages                       |
+-------------+-------------------+----------------------------------+
| 1.0.0       | 2023-07-20        | Initial release version          |
+-------------+-------------------+----------------------------------+

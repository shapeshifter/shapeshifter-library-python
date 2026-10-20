Shapeshifter library for Python
===============================

This is a Python implementation of the ShapeShifter UFTP protocol.

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
- Compatible with version 3.0.0 and 3.1.0 of the Shapeshifter protocol.


Installation
------------

.. code-block:: python3

    pip install shapeshifter-uftp

Running tests
-------------

If you want to develop shapeshifter-uftp, you can fork or clone this repository and run the tests:

.. code-block:: bash

    $ pip install .
    $ pip install .[dev]
    $ pytest .


Running the Shapeshifter Service
================================

The shapeshifter protocol requires you to run a server that can receive HTTP POST requests. You have the following options.

- If you already have a **FastAPI** application and you'd like to run the Shapeshifter service inside that application, see `Running in FastAPI <#running-in-fastapi>`_.

- If you already have a **Flask** application and you'd like to run the Shapeshifter service inside that, see `Running in Flask <#running-in-flask>`_.

- If you don't have an existing application, or you want to run the Shapeshifter interface stand alone (perhaps inside its own Docker container), see `Running stand-alone <#running-stand-alone>`_. Since the service is implemented as a standard WSGI service, you can choose several web servers like nginx, apache2 or gunicorn, which all support WSGI interfaces.


.. _running-in-fastapi:

Running in FastAPI
------------------

To run the module in FastAPI, you can use the ``.app`` property on your instance of the Shapeshifter service, like so:

.. code-block:: python3

    from fastapi import FastAPI
    from shapeshifter_uftp.service import ShapeshifterAgrService


    class MyShapeshifterService(ShapeshifterAgrService):
        # Your implementation of the service goes here, see next section
        ...


    # Create an instance of the Shapeshifter Service
    shapeshifter_service = MyShapeshifterService(..., path="/api/v3/message")

    # Your existing FastAPI application
    app = FastAPI()

    # Mount the Shapeshifte service inside your existing FastAPI application
    app.mount("/shapeshifter", shapeshifter_service.app)

    ...

Note that the full path will be the mount point (``/shapeshifter``) plus the ``path`` defined in the MyShapeshifterService consructor (in this case, ``/api/v3/message``).


.. _running-in-flask:

Running in Flask
----------------

To run the module as part of an existing Flask application, wrap your existing application in a ``DispatcherMiddleware`` like so:

.. code-block:: python3

    from flask import Flask, DispatcherMiddleware

    from shapeshifter_uftp.service import ShapeshifterAgrService


    class MyShapeshifterService(ShapeshifterAgrService):
        # Your implementation of the service goes here, see next section
        ...

    my_app = Flask(__name__)

    shapeshifter_service = MyShapeshifterService(..., path="/api/v3/message")

    app = DispatcherMiddleware(
        my_app,
        {"/shapeshifter": shapeshifter_service}
    )

Note that the full path will be the mount point (``/shapeshifter``) plus the ``path`` defined in the MyShapeshifterService consructor (in this case, ``/api/v3/message``).


.. _running-stand-alone:

Running stand-alone
-------------------

To run the module completely stand-alone, you can use one of these following options.

Standard library wsgiref.simple_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a build-in function, and you can simply use:

.. code-block:: python3

    from shapeshifter_uftp.service import ShapeshifterAgrService


    class MyShapeshifterService(ShapeshifterAgrService):
        # Your implementation of the service goes here, see next section
        ...

    service = MyShapeshifterService(...)
    service.run()


You can customize the host, port and path from their defaults of ``'0.0.0.0'`` and ``8080`` and ``/shapeshifter/api/v3/message``. It is recommended that you leave the ``path`` to the default value, as that is the convention for Shapeshifter servers.


Using apache httpd
~~~~~~~~~~~~~~~~~~

You should use ``mod_wsgi``. For a python module like this, stored in the directory ``/app/main.py`` (as would be conventional in, say , a Docker image):

.. code-block:: python3

    # /app/main.py

    from shapeshifter_uftp.service import ShapeshifterAgrService

    class MyShapeshifterService(ShapeshifterAgrService):
        # Your implementation of the service goes here, see next section
        ...

    # Create an instance of your Shapeshifter service.
    # This instance itself is also a WSGI-compatible callable.
    service = MyShapeshifterService(..., path="/api/v3/message")

You would point the apache2 webserver to it like so:

.. code-block:: apacheconf

    <VirtualHost *:80>

        ServerName www.example.com

        WSGIPythonHome /app/.venv/bin/python
        WSGIScriptAlias /shapeshifter /app/main.py
        WSGICallableObject service

        <Directory /app>
            Require all granted
        </Directory>

    </VirtualHost>

The directive ``WSGIPythonHome`` sets the location of the python interpreter to use. In this example, a uv-like ``venv`` is assumed.

The directive ``WSGIScriptAlias`` takes two arguments:

- The mount path (``/shapeshifter``)
- The location of the python module containing the wsgi callable (``/app/main.py``)

The directive ``WSGICallableObject`` takes one argument:

- The name of the callable object. In the case of Shapeshifter-UFTP, this is the name you gave to your instance of your service subclass.

You may need to enable ``mod_wsgi`` using ``a2enmod wsgi`` or other methods.

If you are running apache exposed to the internet directly (and not in a Docker image behind some other infrastructure), you should use HTTPS on port 443, using the ``SSLEngine`` directives.


Using gunicorn
~~~~~~~~~~~~~~

A simple Python webserver that uses WSGI:


.. code-block:: python3

    # main.py
    from shapeshifter_uftp.service import ShapeshifterAgrService

    class MyShapeshifterService(ShapeshifterAgrService):
        # Your implementation of the service goes here, see next section
        ...

    # Create an instance of your Shapeshifter service.
    # This instance itself is also a WSGI-compatible callable.
    service = MyShapeshifterService(...)

Then run it like so:

.. code-block:: shell

    gunicorn main:service



Implementing your Shapeshifter Service
======================================

Shapehifter always requires the use of a Client and a Service, because all responses are asynchronous.

You choose the server class based on your role in the Shapeshifter conversation, and subclass the abstract implementation of the appropriate service. You then add implementations for each of the messages that you can receive, in order to post-process them according to you own business logic.

This is an overview of the roles, the base class, and the methods you must implement:


+------+------------------------+----------------------------------------------------------------------------------------------+
| Role | Base class             | Methods to implement                                                                         |
+======+========================+==============================================================================================+
| AGR  | ShapeshifterAgrService | * ``process_d_prognosis_response(self, message: DPrognosisResponse)``                        |
|      |                        | * ``process_flex_request(self, message: FlexRequest)``                                       |
|      |                        | * ``process_flex_offer_response(self, message: FlexOfferResponse)``                          |
|      |                        | * ``process_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse)``     |
|      |                        | * ``process_flex_order(self, message: FlexOrder)``                                           |
|      |                        | * ``process_flex_reservation_update(self, message: FlexReservationUpdate)``                  |
|      |                        | * ``process_flex_settlement(self, message: FlexSettlement)``                                 |
|      |                        | * ``process_metering_response(self, message: MeteringResponse)``                             |
|      |                        | * ``process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse)``         |
|      |                        | * ``process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse)``       |
+------+------------------------+----------------------------------------------------------------------------------------------+
| DSO  | ShapeshifterDsoService | * ``process_d_prognosis(self, message: DPrognosis)``                                         |
|      |                        | * ``process_flex_request_response(self, message: FlexRequestResponse)``                      |
|      |                        | * ``process_flex_offer(self, message: FlexOffer)``                                           |
|      |                        | * ``process_flex_order_response(self, message: FlexOrderResponse)``                          |
|      |                        | * ``process_flex_offer_revocation(self, message: FlexOfferRevocation)``                      |
|      |                        | * ``process_flex_reservation_update_response(self, message: FlexReservationUpdateResponse)`` |
|      |                        | * ``process_flex_settlement_response(self, message: FlexSettlementResponse)``                |
|      |                        | * ``process_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse)``         |
|      |                        | * ``process_dso_portfolio_update_response(self, message: DsoPortfolioUpdateResponse)``       |
|      |                        | * ``process_metering(self, message: Metering)``                                              |
+------+------------------------+----------------------------------------------------------------------------------------------+
| CRO  | ShapshifterCroService  | * ``process_agr_portfolio_query(self, message: AgrPortfolioQuery)``                          |
|      |                        | * ``process_agr_portfolio_update(self, message: AgrPortfolioUpdate)``                        |
|      |                        | * ``process_dso_portfolio_query(self, message: DsoPortfolioQuery)``                          |
|      |                        | * ``process_dso_portfolio_update(self, message: DsoPortfolioQuery)``                         |
+------+------------------------+----------------------------------------------------------------------------------------------+


If you are an Aggregator (also known as a CSP), you can use this setup:

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


Similarly, if you have a Service instance that dynamically needs to retrieve the OAuth information for each different recipient server, you can provide an ``oauth_lookup_function`` that takes a ``(sender_domain, sender_role)`` and returns an instance of OAuthClient.

Examples
========


Self-contained Aggregator service and client
--------------------------------------------

.. code-block:: python3

    from datetime import datetime, timedelta, timezone

    from shapeshifter_uftp import ShapeshifterAgrService
    from shapeshifter_uftp.uftp import (FlexOffer, FlexOfferOption,
                                        FlexOfferOptionISP)
    from xsdata.models.datatype import XmlDate


    class DemoAggregator(ShapeshifterAgrService):
        def process_agr_portfolio_query_response(self, message):
            print(f"Received a message: {message}")

        def process_agr_portfolio_update_response(self, message):
            print(f"Received a message: {message}")

        def process_d_prognosis_response(self, message):
            print(f"Received a message: {message}")

        def process_flex_offer_response(self, message):
            print(f"Received a message: {message}")

        def process_flex_offer_revocation_response(self, message):
            print(f"Received a message: {message}")

        def process_flex_order(self, message):
            print(f"Received a message: {message}")

        def process_flex_request(self, message):
            print(f"Received a message: {message}")

            # Example of how to send a new message after
            # processing an incoming message.
            dso_client = self.dso_client(message.sender_domain)
            dso_client.send_flex_offer(
                FlexOffer(
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

        def process_flex_reservation_update(self, message):
            print(f"Received a message: {message}")

        def process_flex_settlement(self, message):
            print(f"Received a message: {message}")

        def process_metering_response(self, message):
            print(f"Received a message: {message}")


    def key_lookup(sender_domain, sender_role):
        known_senders = {
            ("dso.demo", "DSO"): "NsTbq/iABU6tbsjriBg/Z5dSfQstulD0GpMI2fLDWec=",
            ("cro.demo", "CRO"): "ySUYU87usErRFKGJafwvVDLGhnBVJCCNYfQvmwv8ObM=",
        }
        return known_senders.get((sender_domain, sender_role))


    def endpoint_lookup(sender_domain, sender_role):
        known_senders = {
            ("dso.demo", "DSO"): "http://localhost:8081/shapeshifter/api/v3/message",
            ("cro.demo", "CRO"): "http://localhost:8082/shapeshifter/api/v3/message",
        }
        return known_senders.get((sender_domain, sender_role))

    if __name__ == "__main__":
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


Pre-processing messages
-----------------------

By default, Shapeshifter-UFTP will do basic message and schema validations on incoming messages, and send an ``ACCEPTED`` response back to the requesting participant as the initial HTTP response. Your ``process_*`` handler is then called separately so that you can do longer-running processing in the background and optionally send a new message to the participant.

If you want to override the initial response, you can implement a `pre_process_*` method for the specific messages you want to pre-process. This method should then return a PayloadMessageRseponse object that contains thet status. If your method returns a PayloadMessageResponse with status REJECTED, the normal `process_*` method will not be called for that message.

Example:

.. code-block:: python3

    class MyAggregatorService(ShapeshifterAggregatorService):

        ...

        def pre_process_flex_reservation_update(self, message: FlexReservationUpdate):
            return PayloadMessageResponse(
                result=REJECTED,
                rejection_reason="Flex Reservation Updates are not supported"
            )

        ...


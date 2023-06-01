Examples
========


Self-contained Aggregator service and client
--------------------------------------------

.. code-block:: python3

    from shapeshifter_uftp import *

    class MyAggregatorService(ShapeshifterAgrService):
        # Subclass of ShapeshifterAgrService that implements
        # all the processing methods for messages we might receive.

        def process_d_prognosis_response(self, message: DPrognosisResponse):
            if message.result == ACCEPTED:
                print("The DSO accepted our D-Prognosis")
            else:
                print(f"The DSO did not accept our D-Prognosis with reason: {message.rejection_reason}.")

        def process_flex_request(self, message: FlexRequest):
            # ...do something to determine how much flex we might offer

            flex_offer = FlexOffer(

            )
            with self.dso_client(message.sender_domain) as client:
                response = client.send_flex_offer(flex_offer)
                if response.result == ACCEPTED:
                    print("The DSO accepted our Flex Offer and may send a FlexOrder in the future.")
                else:
                    print(f"The DSO did not accept our Flex Offer with reasen: {message.rejection_reason}")

        def process_flex_offer_response(self, message: FlexOfferResponse):
            with self.dso_client(message.sender_domain) as client:
               client.send_message()

        def process_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse):
            if message.result == ACCEPTED:
                print("The DSO accepted our Flex Offer Revocation")
            else:
                print(f"The DSO did not accept our Flex Offer Revocation with reason: {message.rejection_reason}")

        def process_flex_order(self, message: FlexOrder):

            flex_order_response = FlexOrderResponse(

            )
            with self.dso_client(message.sender_domain) as client:
                client.send_message()

        def process_flex_reservation_update(self, message: FlexReservationUpdate):
            with self.dso_client(message.sender_domain) as client:
                client.send_message()

        def process_flex_settlement(self, message: FlexSettlement):
            with self.dso_client(message.sender_domain) as client:
                client.send_message()

        def process_metering_response(self, message: MeteringResponse):
            with self.dso_client(message.sender_domain) as client:
                client.send_message()

        def process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse):


        def process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse):


    def key_lookup_function():
        pass

    def endpoint_lookup_function():
        pass

    service = MyAggregatorService(
        sender_domain="myaggregator.nl",
        signing_key="",
        key_lookup_function=key_lookup_function,
        endpoint_lookup_function=endpoint_lookup_function,
    )

    service.run()


Pre-processing messages
-----------------------

By default, Shapeshifter-UFTP will do basic message and schema validations on incoming messages, and send an ``ACCEPTED`` response back to the requesting participant as the initial HTTP response. Your ``process_*`` handler is then called separately so that you can do longer-running processing in the background and optionally send a new message to the participant.

If you want to override the initial response, you can implement a `pre_process_*` method for the specific messages you want to pre-process. This method should then return a PayloadMessageRseponse object that contains thet status. If your method returns a PayloadMessageResponse with status REJECTED, the normal `process_*` method will not be called for that message.

Example:

.. code-block:: python3

    class MyAggregatorService(ShapeshifterAggregatorService):

        ...

        def pre_process_flex_reservation_update(self, message: FlexReservationUpdate):
            return PayloadMessageResponse(result=REJECTED, rejection_reason="Flex Reservation Updates are not supported")

        ...


Separate Aggregator Service and Client with external message processing
-----------------------------------------------------------------------

If you have an external system and want to do all Shapeshifter Processing in there, you can use Shapeshifter-UFTP to do all the message parsing, conversion, signing and verification and use JSON representations in your backend system.

Here's an example where all incoming messages are passed to an internal HTTP endpoint

.. code-block:: python3

    from shapeshifter_uftp import *

    class PassthroughAggregatorService(ShapeshifterAgrService):
        def process_d_prognosis_response(self, message: DPrognosisResponse):
            if message.result == ACCEPTED:
                print("The DSO accepted our D-Prognosis")
            else:
                print("The DSO did not accept our D-Prognosis "
                      f"with reason: {message.rejection_reason}.")

        def process_flex_request(self, message: FlexRequest):
            # ...do something to determine how much flex we might offer

            flex_offer = FlexOffer(

            )
            with self.dso_client(message.sender_domain) as client:
                response = client.send_flex_offer(flex_offer)
                if response.result == ACCEPTED:
                    print("The DSO accepted our Flex Offer "
                          "and may send a FlexOrder in the future.")
                else:
                    print("The DSO did not accept our Flex Offer "
                          f"with reason: {message.rejection_reason}")

        def process_flex_offer_response(self, message: FlexOfferResponse):
            with self.dso_client(message.sender_domain) as client:
               client.send_message()

        def process_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse):
            if message.result == ACCEPTED:
                print("The DSO accepted our Flex Offer Revocation")
            else:
                print("The DSO did not accept our Flex Offer Revocation "
                      f"with reason: {message.rejection_reason}")


A separate process might fill the client role

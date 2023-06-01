"""
Integrated example of the Shapeshifter Aggregator service and client.
This example show how you can use the asynchronous communications in
a single application without the use of queues and other external
synchronisation mechanisms.

A more decoupled and possibly production-reade example is available
separately.
"""
from time import sleep

from shapeshifter_uftp import (
    ShapeshifterAgrService,
    ShapeshifterAgrDsoClient,
    ShapeshifterAgrDsoClient,
    ACCEPTED,
    REJECTED
)

from threading import Thread

class AggregatorDemo(ShapeshifterAgrService):
    """
    A fully-functional demonstration application of an Aggregator
    """

    def pre_process_flex_request(self, message: FlexRequest) -> PayloadMessageResponse:
        """
        When a DSO sends us a Flex Request, we accept the message.
        """
        return PayloadMessageResponse(result=ACCEPTED)

    def process_flex_request(self, message: FlexRequest) -> FlexOffer:

        return FlexOffer()

    def process_flex_offer_response(self, message: PayloadMessageResponse):
        pass

    def pre_process_flex_order(self, message: FlexOrder) -> PayloadMessageResponse:
        pass

    def process_flex_order(self, message: FlexOrder):
        pass

    def pre_process_flex_reservation_update(self, message: FlexReservationUpdate) -> PayloadMessageResponse:
        pass

    def process_flex_reservation_update(self, message: FlexReservationUpdate):
        pass

    def pre_process_flex_settlement(self, message: FlexSettlement) -> PayloadMessageResponse:
        pass

    def process_flex_settlement(self, message: FlexSettlementResponse);
        pass

    def pre_process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse) -> PayloadMessageResponse:
        pass

    def process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse):
        pass

    def pre_process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse) -> PayloadMessageResponse:
        pass

    def process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse) -> AgrPortfolioUpdate:
        pass


if __name__ == "__main__":
    demo = AggregatorDemo()
    demo.run_in_thread()
    response = demo.send_message(AgrPortfolioUpdate)

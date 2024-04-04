from abc import ABC, abstractmethod

from ..client import ShapeshifterDsoAgrClient, ShapeshifterDsoCroClient
from ..uftp import (
    AcceptedRejected,
    DPrognosis,
    DsoPortfolioQueryResponse,
    DsoPortfolioUpdateResponse,
    FlexOffer,
    FlexOfferRevocation,
    FlexOrderResponse,
    FlexRequestResponse,
    FlexReservationUpdateResponse,
    FlexSettlementResponse,
    Metering,
    PayloadMessageResponse,
)
from .base_service import ShapeshifterService


class ShapeshifterDsoService(ShapeshifterService, ABC):
    """
    Service that represents the Distribution System Operator in the UFTP communication.

    It can receive requests from the Aggregator.

    You should subclass this class and implement your own message handling methods.
    """

    sender_role = "DSO"
    acceptable_messages = [
        DPrognosis,
        DsoPortfolioQueryResponse,
        DsoPortfolioUpdateResponse,
        FlexOffer,
        FlexOfferRevocation,
        FlexOrderResponse,
        FlexRequestResponse,
        FlexReservationUpdateResponse,
        FlexSettlementResponse,
        Metering,
    ]


    # ------------------------------------------------------------ #
    #      Methods related to processing D Prognosis messages      #
    # ------------------------------------------------------------ #

    def pre_process_d_prognosis(self, message: DPrognosis) -> PayloadMessageResponse:
        """
        D-Prognosis messages are used to communicate D-prognoses between AGRs
        and DSOs. D-Prognosis messages always contain data for all ISPs for the
        period they apply to, even if a prognosis is sent after the start of
        the period, when one or more ISPs are already in the operate or
        settlement phase. Receiving implementations should ignore the
        information supplied for those ISPs.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_d_prognosis(self, message: DPrognosis):
        """
        This method is called after the pre_process_d_prognosis method
        is completed. It gives you the chance to perform longer-running
        operations outside of the request context.
        """


    # ------------------------------------------------------------ #
    #     Methods related to processing Flex Request Response      #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_flex_request_response(self, message: FlexRequestResponse) -> PayloadMessageResponse:
        """
        FlexOffer messages are used by AGRs to make DSOs an offer for provision
        of flexibility. A FlexOffer message contains a list of ISPs and, for
        each ISP, the change in consumption or production offered and the price
        for the total amount of flexibility offered. FlexOffer messages can be
        sent once a FlexRequest message has been received but can also be sent
        unsolicited. Note that multiple FlexOffer messages may be sent based on
        a single FlexRequest, e.g. to increase the chance that the DSO will
        order at least part of its available flexibility. The AGR must make
        sure that it can actually provide the flexibility offered across all of
        its FlexOffers.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_request_response(self, message: FlexRequestResponse):
        """
        This method is called after the pre_process_flex_offer method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #      Methods related to processing Flex Offer messages       #
    # ------------------------------------------------------------ #


    def pre_process_flex_offer(self, message: FlexOffer) -> PayloadMessageResponse:
        """
        FlexOffer messages are used by AGRs to make DSOs an offer for provision
        of flexibility. A FlexOffer message contains a list of ISPs and, for
        each ISP, the change in consumption or production offered and the price
        for the total amount of flexibility offered. FlexOffer messages can be
        sent once a FlexRequest message has been received but can also be sent
        unsolicited. Note that multiple FlexOffer messages may be sent based on
        a single FlexRequest, e.g. to increase the chance that the DSO will
        order at least part of its available flexibility. The AGR must make
        sure that it can actually provide the flexibility offered across all of
        its FlexOffers.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_offer(self, message: FlexOffer):
        """
        This method is called after the pre_process_flex_offer method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #  Methods related to processing Flex Order Response messages  #
    # ------------------------------------------------------------ #

    def pre_process_flex_order_response(self, message: FlexOrderResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a FlexOrder message, the receiving
        implementation must reply with a FlexOrderResponse, indicating whether
        the update was handled successfully.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_order_response(self, message: FlexOrderResponse):
        """
        This method is called after the pre_process_flex_order_response method
        is completed. It gives you the chance to perform longer-running
        operations outside of the request context.
        """


    # ------------------------------------------------------------ #
    #     Methods related to processing Flex Offer Revocation      #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_flex_offer_revocation(self, message: FlexOfferRevocation) -> PayloadMessageResponse:
        """
        The FlexOfferRevocation message is used by the AGR to revoke a FlexOffer
        previously sent to a DSO. It voids the FlexOffer, even if its validity
        time has not yet expired. Revocation is not allowed for FlexOffers that
        already have associated accepted FlexOrders.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_offer_revocation(self, message: FlexOfferRevocation):
        """
        This method runs separately from the pre_process_flex_offer_revocation
        function. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #    Methods related to processing Flex Reservation Update     #
    #                      Response messages                       #
    # ------------------------------------------------------------ #

    def pre_process_flex_reservation_update_response(self, message: FlexReservationUpdateResponse) -> PayloadMessageResponse:
        """
        The FlexOfferRevocation message is used by the AGR to revoke a FlexOffer
        previously sent to a DSO. It voids the FlexOffer, even if its validity
        time has not yet expired. Revocation is not allowed for FlexOffers that
        already have associated accepted FlexOrders.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_reservation_update_response(self, message: FlexReservationUpdateResponse):
        """
        This method runs separately from the pre_process_flex_offer_revocation
        function. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #    Methods related to processing Flex Settlement Response    #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_flex_settlement_response(self, message: FlexSettlementResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a FlexSettlement message, the AGR must
        reply with a FlexSettlementResponse, indicating whether the initial
        message was handled successfully. When a FlexSettlement message is
        rejected, the DSO should consider all FlexOrderSettlement elements of
        that message related to potential dispute.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_settlement_response(self, message: FlexSettlementResponse):
        """
        This method runs separately from the
        pre_process_flex_settlement_response function. It gives you the chance
        to perform longer-running operations outside of the request context.
        """


    # ------------------------------------------------------------ #
    #  Methods related to processing DSO Portfolio Query Response  #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a DSOPortfolioQuery message, the receiving
        implementation must reply with a DSOPortfolioQueryResponse, indicating
        whether the query executed successfully, and if it did, including the
        query results. Most queries will return zero or more congestion points
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse):
        """
        This method runs after the pre_process_dso_portfolio_query_response has
        finised.
        """


    # ------------------------------------------------------------ #
    #      Methods related to processing DSO Portfolio Update      #
    #                      Response messages                       #
    # ------------------------------------------------------------ #

    def pre_process_dso_portfolio_update_response(self, message: DsoPortfolioUpdateResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a DSOPortfolioUpdate message, the
        receiving implementation must reply with a DSOPortfolioUpdateResponse,
        indicating whether the update was handled successfully.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_dso_portfolio_update_response(self, message: DsoPortfolioUpdateResponse):
        """
        This method runs after the pre_process_portfolio_update_response method
        has finished.
        """


    # ------------------------------------------------------------ #
    #       Methods related to processing Metering messages        #
    # ------------------------------------------------------------ #

    def pre_process_metering(self, message: Metering) -> PayloadMessageResponse:
        """
        The Metering message is an optional message. The DSO will specify
        whether metering messages are required for a given program. If metering
        messages are used then the AGR must send metering messages, with one
        message sent per connection point per day. The metering messages must
        all be sent before the settlement can be performed. It is recommend to
        send the metering messages daily, once the metering data has been
        collected for the day.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_metering(self, message: Metering):
        """
        This method runs after the pre_process_metering method has finished.
        """


    # ------------------------------------------------------------ #
    #  Convenience methods for getting a client to the designated  #
    #                         participant.                         #
    # ------------------------------------------------------------ #

    def agr_client(self, recipient_domain) -> ShapeshifterDsoAgrClient:
        """
        Retrieve a client object for sending messages to the AGR.
        """
        return self._get_client(recipient_domain, 'AGR')

    def cro_client(self, recipient_domain) -> ShapeshifterDsoCroClient:
        """
        Retrieve a client object for sending messages to the CRO.
        """
        return self._get_client(recipient_domain, 'CRO')

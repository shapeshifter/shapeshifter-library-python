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


# pylint: disable=too-many-public-methods
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

    @abstractmethod
    def process_d_prognosis(self, message: DPrognosis):
        """
        D-Prognosis messages are used to communicate D-prognoses between AGRs
        and DSOs. D-Prognosis messages always contain data for all ISPs for the
        period they apply to, even if a prognosis is sent after the start of
        the period, when one or more ISPs are already in the operate or
        settlement phase. Receiving implementations should ignore the
        information supplied for those ISPs.
        """

    @abstractmethod
    def process_flex_request_response(self, message: FlexRequestResponse):
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

    @abstractmethod
    def process_flex_offer(self, message: FlexOffer):
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

    @abstractmethod
    def process_flex_order_response(self, message: FlexOrderResponse):
        """
        Upon receiving and processing a FlexOrder message, the receiving
        implementation must reply with a FlexOrderResponse, indicating whether
        the update was handled successfully.
        """

    @abstractmethod
    def process_flex_offer_revocation(self, message: FlexOfferRevocation):
        """
        The FlexOfferRevocation message is used by the AGR to revoke a FlexOffer
        previously sent to a DSO. It voids the FlexOffer, even if its validity
        time has not yet expired. Revocation is not allowed for FlexOffers that
        already have associated accepted FlexOrders.
        """

    @abstractmethod
    def process_flex_reservation_update_response(
        self, message: FlexReservationUpdateResponse
    ):
        """
        The FlexOfferRevocation message is used by the AGR to revoke a FlexOffer
        previously sent to a DSO. It voids the FlexOffer, even if its validity
        time has not yet expired. Revocation is not allowed for FlexOffers that
        already have associated accepted FlexOrders.
        """

    @abstractmethod
    def process_flex_settlement_response(self, message: FlexSettlementResponse):
        """
        Upon receiving and processing a FlexSettlement message, the AGR must
        reply with a FlexSettlementResponse, indicating whether the initial
        message was handled successfully. When a FlexSettlement message is
        rejected, the DSO should consider all FlexOrderSettlement elements of
        that message related to potential dispute.
        """

    @abstractmethod
    def process_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse):
        """
        Upon receiving and processing a DSOPortfolioQuery message, the receiving
        implementation must reply with a DSOPortfolioQueryResponse, indicating
        whether the query executed successfully, and if it did, including the
        query results. Most queries will return zero or more congestion points
        """

    @abstractmethod
    def process_dso_portfolio_update_response(
        self, message: DsoPortfolioUpdateResponse
    ):
        """
        Upon receiving and processing a DSOPortfolioUpdate message, the
        receiving implementation must reply with a DSOPortfolioUpdateResponse,
        indicating whether the update was handled successfully.
        """

    @abstractmethod
    def process_metering(self, message: Metering):
        """
        The Metering message is an optional message. The DSO will specify
        whether metering messages are required for a given program. If metering
        messages are used then the AGR must send metering messages, with one
        message sent per connection point per day. The metering messages must
        all be sent before the settlement can be performed. It is recommend to
        send the metering messages daily, once the metering data has been
        collected for the day.
        """

    # ------------------------------------------------------------ #
    #  Convenience methods for getting a client to the designated  #
    #                         participant.                         #
    # ------------------------------------------------------------ #

    def agr_client(self, recipient_domain) -> ShapeshifterDsoAgrClient:
        """
        Retrieve a client object for sending messages to the AGR.
        """
        return self._get_client(recipient_domain, "AGR")

    def cro_client(self, recipient_domain) -> ShapeshifterDsoCroClient:
        """
        Retrieve a client object for sending messages to the CRO.
        """
        return self._get_client(recipient_domain, "CRO")

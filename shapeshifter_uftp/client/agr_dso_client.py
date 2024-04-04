from ..uftp import (
    DPrognosis,
    FlexOffer,
    FlexOfferRevocation,
    FlexOrderResponse,
    FlexRequestResponse,
    FlexReservationUpdateResponse,
    FlexSettlementResponse,
    Metering,
    PayloadMessageResponse,
)
from .base_client import ShapeshifterClient


class ShapeshifterAgrDsoClient(ShapeshifterClient):
    """
    Client that allows the Aggregator to connect to the DSO.
    """

    sender_role = "AGR"
    recipient_role = "DSO"

    def send_d_prognosis(self, message: DPrognosis) -> PayloadMessageResponse:
        """
        D-Prognosis messages are used to communicate D-prognoses between AGRs
        and DSOs. D-Prognosis messages always contain data for all ISPs for the
        period they apply to, even if a prognosis is sent after the start of
        the period, when one or more ISPs are already in the operate or
        settlement phase. Receiving implementations should ignore the
        information supplied for those ISPs.
        """
        return self._send_message(message)

    def send_flex_request_response(self, message: FlexRequestResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a FlexRequest message, the receiving
        implementation must reply with a FlexRequestResponse, indicating
        whether the flexibility request was processed successfully.
        """
        return self._send_message(message)

    def send_flex_offer(self, message: FlexOffer) -> PayloadMessageResponse:
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
        return self._send_message(message)

    def send_flex_offer_revocation(self, message: FlexOfferRevocation) -> PayloadMessageResponse:
        """
        The FlexOfferRevocation message is used by the AGR to revoke a FlexOffer
        previously sent to a DSO. It voids the FlexOffer, even if its validity
        time has not yet expired. Revocation is not allowed for FlexOffers that
        already have associated accepted FlexOrders.
        """
        return self._send_message(message)

    def send_flex_order_response(self, message: FlexOrderResponse) -> PayloadMessageResponse:
        """
        Confirm the flex order.
        """
        return self._send_message(message)

    def send_flex_settlement_response(self, message: FlexSettlementResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a FlexSettlement message, the AGR must
        reply with a FlexSettlementResponse, indicating whether the initial
        message was handled successfully. When a FlexSettlement message is
        rejected, the DSO should consider all FlexOrderSettlement elements of
        that message related to potential dispute.
        """
        return self._send_message(message)

    def send_flex_reservation_update_response(self, message: FlexReservationUpdateResponse) -> PayloadMessageResponse:
        """
        Confirm the flex reservation update.
        """
        return self._send_message(message)

    def send_metering(self, message: Metering) -> PayloadMessageResponse:
        """
        Send metering data to the DSO.
        """
        return self._send_message(message)

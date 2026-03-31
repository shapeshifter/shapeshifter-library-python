from ..uftp import (
    DPrognosisResponse,
    FlexOfferResponse,
    FlexOfferRevocationResponse,
    FlexOrder,
    FlexRequest,
    FlexReservationUpdate,
    FlexSettlement,
    MeteringResponse,
    UsefRole,
)
from .base_client import ShapeshifterClient


class ShapeshifterDsoAgrClient(ShapeshifterClient):
    """
    Client that allows the DSO to connect to the Aggregator.
    """

    sender_role = UsefRole.DSO
    recipient_role = UsefRole.AGR

    def send_d_prognosis_response(self, message: DPrognosisResponse) -> None:
        """
        Confirm reception of the D-prognosis.
        """
        self._send_message(message)

    def send_flex_request(self, message: FlexRequest) -> None:
        """
        FlexRequest messages are used by DSOs to request flexibility from AGRs.
        In addition to one or more ISP elements with Disposition=Requested,
        indicating the actual need to reduce consumption or production, the
        message should also include the remaining ISPs for the current period
        where Disposition=Available.
        """
        self._send_message(message)

    def send_flex_offer_response(self, message: FlexOfferResponse) -> None:
        """
        Confirm reception of a flex offer.
        """
        self._send_message(message)

    def send_flex_order(self, message: FlexOrder) -> None:
        """
        FlexOrder messages are used by DSOs to purchase flexibility from an AGR
        based on a previous FlexOffer. A FlexOrder message contains a list of
        ISPs, with, for each ISP, the change in consumption or production to be
        realized by the AGR, and the accepted price to be paid by the DSO for
        this amount of flexibility. This ISP list should be copied from the
        FlexOffer message without modification: AGR implementations will
        (and must) reject FlexOrder messages where the ISP list is not exactly
        the same as offered.
        """
        self._send_message(message)

    def send_flex_reservation_update(self, message: FlexReservationUpdate) -> None:
        """
        For bilateral contracts, FlexReservationUpdate messages are used by DSOs
        to signal to an AGR which part of the contracted volume is still
        reserved and which part is not needed and may be used for other
        purposes. For each ISP, a power value is given which indicates how much
        power is still reserved. Zero power means that no power is reserved for
        that ISP and the sign of the power indicates the direction.
        """
        self._send_message(message)

    def send_flex_settlement(self, message: FlexSettlement) -> None:
        """
        The FlexSettlement message is sent by DSOs on a regular basis
        (typically monthly) to AGRs, in order to initiate settlement.
        It includes a list of all FlexOrders placed by the
        originating party during the settlement period.
        """
        self._send_message(message)

    def send_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse) -> None:
        """
        Upon receiving and processing a FlexOfferRevocation message, the
        receiving implementation must reply with a FlexOfferRevocationResponse,
        indicating whether the revocation was handled successfully.
        """
        self._send_message(message)

    def send_metering_response(self, message: MeteringResponse) -> None:
        """
        Confirm reception of metering data.
        """
        self._send_message(message)

from abc import ABC, abstractmethod
from .base_service import ShapeshifterService
from ..client import ShapeshifterAgrCroClient, ShapeshifterAgrDsoClient
from ..uftp import (
    AgrPortfolioQueryResponse,
    AgrPortfolioUpdateResponse,
    DPrognosisResponse,
    FlexOfferResponse,
    FlexOfferRevocationResponse,
    FlexOrder,
    FlexRequest,
    FlexReservationUpdate,
    FlexSettlement,
    MeteringResponse,
    PayloadMessageResponse,
    AcceptedRejected
)


class ShapeshifterAgrService(ShapeshifterService, ABC):
    """
    Service that represents the Aggregator in the UFTP communication.

    This service can receive requests from the DSO.
    """

    sender_role = "AGR"
    acceptable_messages = [
        AgrPortfolioQueryResponse,
        AgrPortfolioUpdateResponse,
        DPrognosisResponse,
        FlexOfferResponse,
        FlexOfferRevocationResponse,
        FlexOrder,
        FlexRequest,
        FlexReservationUpdate,
        FlexSettlement,
        MeteringResponse,
    ]


    # ------------------------------------------------------------ #
    #      Methods related to processing D Prognosis Response      #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_d_prognosis_response(self, message: DPrognosisResponse) -> PayloadMessageResponse:
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
    def process_d_prognosis_response(self, message: DPrognosisResponse):
        """
        This method is called after the pre_process_flex_offer method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #      Methods related to processing Flex Request messages      #
    # ------------------------------------------------------------ #

    def pre_process_flex_request(self, message: FlexRequest) -> PayloadMessageResponse:
        """
        FlexRequest messages are used by DSOs to request flexibility from AGRs.
        In addition to one or more ISP elements with Disposition=Requested,
        indicating the actual need to reduce consumption or production, the
        message should also include the remaining ISPs for the current period
        where Disposition=Available.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_request(self, message: FlexRequest):
        """
        This function is called after the pre_process_flex_request is completed.
        It gives you the chance to do longer-running computations or operations
        on this message.

        This method should probably end by sending some Flex Offers to the DSO::

            with self.dso_client(message.sender_domain) as client:
                response = client.send_flex_offer(FlexOffer(...)
                # Do something with the response here.
        """


    # ------------------------------------------------------------ #
    #  Methods related to processing Flex Offer Response messages  #
    # ------------------------------------------------------------ #

    def pre_process_flex_offer_response(self, message: FlexOfferResponse) -> PayloadMessageResponse:
        """
        FlexRequest messages are used by DSOs to request flexibility from AGRs.
        In addition to one or more ISP elements with Disposition=Requested,
        indicating the actual need to reduce consumption or production, the
        message should also include the remaining ISPs for the current period
        where Disposition=Available.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_offer_response(self, message: FlexOfferResponse):
        """
        This function is called after the pre_process_flex_request is completed.
        It gives you the chance to do longer-running computations or operations
        on this message.

        This method should probably end by sending some Flex Offers to the DSO::

            with self.dso_client(message.sender_domain) as client:
                response = client.send_flex_offer(FlexOffer(...)
                # Do something with the response here.
        """


    # ------------------------------------------------------------ #
    #     Methods related to processing Flex Offer Revocation      #
    #                      Response messages                       #
    # ------------------------------------------------------------ #


    def pre_process_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a FlexOfferRevocation message, the
        receiving implementation must reply with a FlexOfferRevocationResponse,
        indicating whether the revocation was handled successfully.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_offer_revocation_response(self, message: FlexOfferRevocationResponse):
        """
        This method is called after the pre_process_flex_offer_revocation_response method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context. This method is not expected to return
        anything.

        It is advised that this method ends by sending a FlexSettlementResponse to the DSO::

            with self.dso_client(message.sender_domain):
                response = client.send_flex_settlement_response(FlexSettlementResponse(...))
                # do something with the response here.
        """


    # ------------------------------------------------------------ #
    #       Methods related to processing FlexOrder messages       #
    # ------------------------------------------------------------ #

    def pre_process_flex_order(self, message: FlexOrder) -> PayloadMessageResponse:
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
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_order(self, message: FlexOrder):
        """
        This method is called after the pre_process_flex_order is completed. It
        gives you the cance to perform longer-running operations outside of the
        request context. This method is not expected to return anything.
        """


    # ------------------------------------------------------------ #
    #     Methods related to processing FlexReservationUpdate      #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_flex_reservation_update(self, message: FlexReservationUpdate) -> PayloadMessageResponse:
        """
        For bilateral contracts, FlexReservationUpdate messages are used by DSOs
        to signal to an AGR which part of the contracted volume is still
        reserved and which part is not needed and may be used for other
        purposes. For each ISP, a power value is given which indicates how much
        power is still reserved. Zero power means that no power is reserved for
        that ISP and the sign of the power indicates the direction.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_reservation_update(self, message: FlexReservationUpdate):
        """
        This method is called after the pre_process_flex_reservation_update
        method is completed. It gives you the chance to perform longer-running
        operations outside of the request context. This method is not expected
        to return anything.
        """


    # ------------------------------------------------------------ #
    #    Methods related to processing Flex Settlement messages    #
    # ------------------------------------------------------------ #

    def pre_process_flex_settlement(self, message: FlexSettlement) -> PayloadMessageResponse:
        """
        The FlexSettlement message is sent by DSOs on a regular basis
        (typically monthly) to AGRs, in order to initiate settlement. It
        includes a list of all FlexOrders placed by the originating party
        during the settlement period.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_flex_settlement(self, message: FlexSettlement):
        """
        This method is called after the pre_process_flex_settlement method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context. This method is not expected to return
        anything.

        It is advised that this method ends by sending a FlexSettlementResponse to the DSO::

            with self.get_dso_client(message.sender_domain):
                response = client.send_flex_settlement_response(FlexSettlementResponse(...))
                # do something with the response here.
        """


    # ------------------------------------------------------------ #
    #   Methods related to processing Metering Response messages   #
    # ------------------------------------------------------------ #


    def pre_process_metering_response(self, message: MeteringResponse) -> PayloadMessageResponse:
        """
        Upon receiving and processing a Metering message, the
        receiving implementation must reply with a MeteringResponse,
        indicating whether the update was handled successfully.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_metering_response(self, message: MeteringResponse):
        """
        This method is called after the pre_process_metering_response method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context. This method is not expected to return
        anything.

        It is advised that this method ends by sending a FlexSettlementResponse to the DSO::

            with self.get_dso_client(message.sender_domain):
                response = client.send_flex_settlement_response(FlexSettlementResponse(...))
                # do something with the response here.
        """


    # ------------------------------------------------------------ #
    #    Methods related to processing Portfolio Query Response    #
    #                           messages                           #
    # ------------------------------------------------------------ #

    def pre_process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse) -> PayloadMessageResponse:
        """
        The AgrPortfolioQueryResponse is sent by the CRO after you sent a
        AgrPortfolioQuery. It contains the list of your connections. It is
        recommended that you do not perform any long-running operations inside
        this function, but return a PayloadMessageResponse quickly.
        Longer-running operations (like a database sync) should be done inside
        the process_agr_portfolio_query_response method.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse):
        """
        This method is called after the agr_portfolio_query_response method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context.

        If the list of connections does not match what you expected it
        to be, you can send an AgrPortfolioUpdate message at the end
        of this method::

            with self.get_dso_client(message.sender_domain) as client:
                response = client.send_portfolio_update(AgrPortfolioUpdate(...))
                # Do something with the response here
        """


    # ------------------------------------------------------------ #
    #          Methods related to processing Portfolio Update      #
    #                      Response messages                       #
    # ------------------------------------------------------------ #

    def pre_process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse):
        """
        The AgrPortfolioUptadeResponse is sent by the CRO after you sent a
        AgrPortfolioUpdate. It is merely a status updateIt is
        recommended that you do not perform any long-running operations inside
        this function, but return a PayloadMessageResponse quickly.
        Longer-running operations (like a database sync) should be done inside
        the process_agr_portfolio_query_response method.
        """
        # pylint: disable=unused-argument
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse):
        """
        This method is called after the agr_portfolio_update_response method is
        completed. It gives you the chance to perform longer-running operations
        outside of the request context.
        """


    # ------------------------------------------------------------ #
    #  Convenience methods for getting a client to the designated  #
    #                         participant.                         #
    # ------------------------------------------------------------ #

    def cro_client(self, recipient_domain) -> ShapeshifterAgrCroClient:
        """
        Retrieve a client object for sending messages to the CRO.
        """
        return self._get_client(recipient_domain, 'CRO')


    def dso_client(self, recipient_domain) -> ShapeshifterAgrDsoClient:
        """
        Retrieve a client object for sending messages to the DSO.
        """
        return self._get_client(recipient_domain, 'DSO')

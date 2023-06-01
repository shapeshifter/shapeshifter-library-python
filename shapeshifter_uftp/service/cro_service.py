from abc import ABC, abstractmethod
from .base_service import ShapeshifterService
from ..client import ShapeshifterCroAgrClient, ShapeshifterCroDsoClient
from ..uftp import (
    AcceptedRejected,
    AgrPortfolioQuery,
    AgrPortfolioUpdate,
    DsoPortfolioQuery,
    DsoPortfolioUpdate,
    PayloadMessageResponse
)

class ShapeshifterCroService(ShapeshifterService, ABC):
    """
    Service that represent the Common Reference Operator in the UFTP communication.

    It can receive requests from the Aggregator and from the DSO.
    """

    sender_role = "CRO"
    acceptable_messages = [DsoPortfolioQuery, DsoPortfolioUpdate,
                           AgrPortfolioQuery, AgrPortfolioUpdate]

    # ------------------------------------------------------------ #
    #       Methods related to Agr Portfolio Query messages        #
    # ------------------------------------------------------------ #

    def pre_process_agr_portfolio_query(self, message: AgrPortfolioQuery) -> PayloadMessageResponse:
        """
        The AGRPortfolioQuery is used by the AGR to retrieve
        additional information on the connections.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_agr_portfolio_query(self, message: AgrPortfolioQuery):
        """
        This method is called after the agr_portfolio_query method is
        completed. It gives you the chance to perform longer-running
        operations outside of the request context.
        """


    # ------------------------------------------------------------ #
    #       Methods related to Agr Portfolio Update messages       #
    # ------------------------------------------------------------ #

    def pre_process_agr_portfolio_update(self, message: AgrPortfolioUpdate) -> PayloadMessageResponse:
        """
        The AGRPortfolioUpdate is used by the AGR to indicate on which
        Connections it represents prosumers.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_agr_portfolio_update(self, message: AgrPortfolioUpdate):
        """
        This method is called after the agr_portfolio_update method is
        completed. It gives you the chance to perform longer-running
        operations outside of the request context.
        """


    # ------------------------------------------------------------ #
    #       Methods related to DSO Portfolie Query messages        #
    # ------------------------------------------------------------ #

    def pre_process_dso_portfolio_query(self, message: DsoPortfolioQuery) -> PayloadMessageResponse:
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_dso_portfolio_query(self, message: DsoPortfolioQuery):
        """
        This method is called after the dso_portfolio_query method is
        completed. It gives you the chance to perform longer-running
        operations outside of the request context.

        You should end this method by sending a
        DsoPortfolioQueryResponse back to the DSO::

            with self.get_dso_client(message.sender_domain) as client:
                client.send_portfolio_query_response
        """

    # ------------------------------------------------------------ #
    #       Methods related to DSO Portfolio Query messages        #
    # ------------------------------------------------------------ #

    def pre_process_dso_portfolio_update(self, message: DsoPortfolioUpdate) -> PayloadMessageResponse:
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        return PayloadMessageResponse(result=AcceptedRejected.ACCEPTED)

    @abstractmethod
    def process_dso_portfolio_update(self, message: DsoPortfolioUpdate):
        """
        This method is called after the dso_portfolio_update method is
        completed. It gives you the chance to perform longer-running
        operations outside of the request context.
        """

    # ------------------------------------------------------------ #
    #  Convenience methods for getting a client to the designated  #
    #                         participant.                         #
    # ------------------------------------------------------------ #

    def agr_client(self, recipient_domain) -> ShapeshifterCroAgrClient:
        """
        Retrieve a client object for sending messages to the AGR.
        """
        return self._get_client(recipient_domain, 'AGR')

    def dso_client(self, recipient_domain) -> ShapeshifterCroDsoClient:
        """
        Retrieve a client object for sending messages to the DSO.
        """
        return self._get_client(recipient_domain, 'DSO')

from abc import ABC, abstractmethod

from ..client import ShapeshifterCroAgrClient, ShapeshifterCroDsoClient
from ..uftp import (
    AcceptedRejected,
    AgrPortfolioQuery,
    AgrPortfolioUpdate,
    DsoPortfolioQuery,
    DsoPortfolioUpdate,
    PayloadMessageResponse,
)
from .base_service import ShapeshifterService


class ShapeshifterCroService(ShapeshifterService, ABC):
    """
    Service that represent the Common Reference Operator in the UFTP communication.

    It can receive requests from the Aggregator and from the DSO.
    """

    sender_role = "CRO"
    acceptable_messages = [
        DsoPortfolioQuery,
        DsoPortfolioUpdate,
        AgrPortfolioQuery,
        AgrPortfolioUpdate,
    ]

    # ------------------------------------------------------------ #
    #       Methods related to Agr Portfolio Query messages        #
    # ------------------------------------------------------------ #

    @abstractmethod
    def process_agr_portfolio_query(self, message: AgrPortfolioQuery):
        """
        The AGRPortfolioQuery is used by the AGR to retrieve
        additional information on the connections.
        """

    @abstractmethod
    def process_agr_portfolio_update(self, message: AgrPortfolioUpdate):
        """
        The AGRPortfolioUpdate is used by the AGR to indicate on which
        Connections it represents prosumers.
        """

    @abstractmethod
    def process_dso_portfolio_query(self, message: DsoPortfolioQuery):
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).

        You should end this method by sending a
        DsoPortfolioQueryResponse back to the DSO::

            with self.get_dso_client(message.sender_domain) as client:
                client.send_portfolio_query_response
        """

    @abstractmethod
    def process_dso_portfolio_update(self, message: DsoPortfolioUpdate):
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """

    # ------------------------------------------------------------ #
    #  Convenience methods for getting a client to the designated  #
    #                         participant.                         #
    # ------------------------------------------------------------ #

    def agr_client(self, recipient_domain) -> ShapeshifterCroAgrClient:
        """
        Retrieve a client object for sending messages to the AGR.
        """
        return self._get_client(recipient_domain, "AGR")

    def dso_client(self, recipient_domain) -> ShapeshifterCroDsoClient:
        """
        Retrieve a client object for sending messages to the DSO.
        """
        return self._get_client(recipient_domain, "DSO")

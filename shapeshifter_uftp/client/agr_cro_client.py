from ..uftp import (
    AgrPortfolioQuery,
    AgrPortfolioUpdate,
    PayloadMessageResponse,
    UsefRole,
)
from .base_client import ShapeshifterClient


class ShapeshifterAgrCroClient(ShapeshifterClient):
    """
    Client that allows the Aggregator to connect to the CRO.
    """

    sender_role = UsefRole.AGR
    recipient_role = UsefRole.CRO

    def send_agr_portfolio_update(self, message: AgrPortfolioUpdate) -> PayloadMessageResponse:
        """
        The AGRPortfolioUpdate is used by the AGR to indicate on which
        Connections it represents prosumers.
        """
        return self._send_message(message)

    def send_agr_portfolio_query(self, message: AgrPortfolioQuery) -> PayloadMessageResponse:
        """
        The AGRPortfolioQuery is used by the AGR to retrieve additional
        information on the connections.
        """
        return self._send_message(message)

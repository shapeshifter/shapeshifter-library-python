from ..uftp import AgrPortfolioQueryResponse, AgrPortfolioUpdateResponse
from .base_client import ShapeshifterClient


class ShapeshifterCroAgrClient(ShapeshifterClient):
    """
    Client that allows the CRO to connect to the Aggregator.
    """

    sender_role = "CRO"
    recipient_role = "AGR"

    def send_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse):
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        return self._send_message(message)

    def send_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse):
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        return self._send_message(message)

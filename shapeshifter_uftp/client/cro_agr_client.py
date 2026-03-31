from ..uftp import AgrPortfolioQueryResponse, AgrPortfolioUpdateResponse, UsefRole
from .base_client import ShapeshifterClient


class ShapeshifterCroAgrClient(ShapeshifterClient):
    """
    Client that allows the CRO to connect to the Aggregator.
    """

    sender_role = UsefRole.CRO
    recipient_role = UsefRole.AGR

    def send_agr_portfolio_update_response(self, message: AgrPortfolioUpdateResponse) -> None:
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        self._send_message(message)

    def send_agr_portfolio_query_response(self, message: AgrPortfolioQueryResponse) -> None:
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        self._send_message(message)

from ..uftp import DsoPortfolioQueryResponse, DsoPortfolioUpdateResponse, UsefRole
from .base_client import ShapeshifterClient


class ShapeshifterCroDsoClient(ShapeshifterClient):
    """
    Client that allows the CRO to connect to the DSO.

    There are only two types of messages that the CRO can send to the DSO:

    - DsoPortfolioUpdateResponse
    - DsoPortfolioQueryResponse

    Each of these comes after the DSO sends a DsoPortfolioUpdate or
    DsoPortfolioQuery, respectively.
    """

    sender_role = UsefRole.CRO
    recipient_role = UsefRole.DSO

    def send_dso_portfolio_update_response(self, message: DsoPortfolioUpdateResponse) -> None:
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        self._send_message(message)

    def send_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse) -> None:
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        self._send_message(message)

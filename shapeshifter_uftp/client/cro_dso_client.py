from .base_client import ShapeshifterClient
from ..uftp import DsoPortfolioUpdateResponse, DsoPortfolioQueryResponse


class ShapeshifterCroDsoClient(ShapeshifterClient):
    """
    Client that allows the CRO to connect to the DSO.

    There are only two types of messages that the CRO can send to the DSO:

    - DsoPortfolioUpdateResponse
    - DsoPortfolioQueryResponse

    Each of these comes after the DSO sends a DsoPortfolioUpdate or
    DsoPortfolioQuery, respectively.
    """

    sender_role = "CRO"
    recipient_role = "DSO"

    def send_dso_portfolio_update_response(self, message: DsoPortfolioUpdateResponse):
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        return self._send_message(message)

    def send_dso_portfolio_query_response(self, message: DsoPortfolioQueryResponse):
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        return self._send_message(message)

from .base_client import ShapeshifterClient
from ..uftp import DsoPortfolioUpdate, DsoPortfolioQuery


class ShapeshifterDsoCroClient(ShapeshifterClient):
    """
    Client that allows the DSO to connect to the CRO.
    """

    sender_role = "DSO"
    recipient_role = "CRO"

    def send_dso_portfolio_update(self, message: DsoPortfolioUpdate):
        """
        The DSOPortfolioUpdate is used by the DSO to indicate on which
        congestion points it wants to engage in flexibility trading.
        """
        return self._send_message(message)

    def send_dso_portfolio_query(self, message: DsoPortfolioQuery):
        """
        DSOPortfolioQuery is used by DSOs to discover which AGRs represent
        connections on its registered congestion point(s).
        """
        return self._send_message(message)

import pytest
from shapeshifter_uftp.service.base_service import snake_case


@pytest.mark.parametrize('text,expected_result',
    [('FlexOffer', 'flex_offer'),
     ('AgrPortfolioUpdate', 'agr_portfolio_update'),
     ('HTTPRequest', 'http_request')])
def test_snake_case(text, expected_result):
    assert snake_case(text) == expected_result

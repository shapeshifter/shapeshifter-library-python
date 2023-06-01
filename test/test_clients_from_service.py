import pytest
from itertools import product
from shapeshifter_uftp import (
    ShapeshifterAgrService,
    ShapeshifterCroService,
    ShapeshifterDsoService,
    ShapeshifterAgrCroClient,
    ShapeshifterAgrDsoClient,
    ShapeshifterCroAgrClient,
    ShapeshifterCroDsoClient,
    ShapeshifterDsoAgrClient,
    ShapeshifterDsoCroClient,
)

from .helpers.services import DummyAgrService, DummyCroService, DummyDsoService

@pytest.mark.parametrize('service,client,expected_type',
    [(DummyAgrService, 'cro', ShapeshifterAgrCroClient),
     (DummyAgrService, 'dso', ShapeshifterAgrDsoClient),
     (DummyCroService, 'agr', ShapeshifterCroAgrClient),
     (DummyCroService, 'dso', ShapeshifterCroDsoClient),
     (DummyDsoService, 'agr', ShapeshifterDsoAgrClient),
     (DummyDsoService, 'cro', ShapeshifterDsoCroClient),
     ]
)
def test_clients_from_service(service, client, expected_type):
    service_obj = service()
    assert hasattr(service_obj, f'{client}_client')

    client_obj = getattr(service_obj, f'{client}_client')(recipient_domain="test.dev")
    assert isinstance(client_obj, expected_type)

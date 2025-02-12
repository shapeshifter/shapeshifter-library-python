import itertools

import pytest

from shapeshifter_uftp import (
    ShapeshifterAgrService,
    ShapeshifterCroService,
    ShapeshifterDsoService,
)
from shapeshifter_uftp.service.base_service import snake_case


@pytest.mark.parametrize('service,message_type,stage',
    [
        *itertools.product([ShapeshifterAgrService], ShapeshifterAgrService.acceptable_messages, ['process']),
        *itertools.product([ShapeshifterCroService], ShapeshifterCroService.acceptable_messages, ['process']),
        *itertools.product([ShapeshifterDsoService], ShapeshifterDsoService.acceptable_messages, ['process']),
    ]
)
def test_presence_of_processing_methods(service, message_type, stage):
    processing_method = f"{stage}_{snake_case(message_type.__name__)}"
    assert hasattr(service, processing_method)


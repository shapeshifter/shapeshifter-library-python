import pytest
import itertools
from shapeshifter_uftp.service import snake_case
from shapeshifter_uftp import ShapeshifterAgrService, ShapeshifterDsoService, ShapeshifterCroService

@pytest.mark.parametrize('service,message_type,stage',
    [
        *itertools.product([ShapeshifterAgrService], ShapeshifterAgrService.acceptable_messages, ['pre_process', 'process']),
        *itertools.product([ShapeshifterCroService], ShapeshifterCroService.acceptable_messages, ['pre_process', 'process']),
        *itertools.product([ShapeshifterDsoService], ShapeshifterDsoService.acceptable_messages, ['pre_process', 'process']),
    ]
)
def test_presence_of_processing_methods(service, message_type, stage):
    processing_method = f"{stage}_{snake_case(message_type.__name__)}"
    assert hasattr(service, processing_method)


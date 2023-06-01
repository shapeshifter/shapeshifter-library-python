import pytest
import xmlschema
from shapeshifter_uftp.transport import to_xml
from shapeshifter_uftp.uftp import destination_map
import os
from .helpers.messages import messages

base_url = os.path.join(os.path.dirname(__file__), 'schema')

schemas = {
    "AGR": xmlschema.XMLSchema("UFTP-agr.xsd", base_url=base_url),
    "CRO": xmlschema.XMLSchema("UFTP-cro.xsd", base_url=base_url),
    "DSO": xmlschema.XMLSchema("UFTP-dso.xsd", base_url=base_url),
}


@pytest.mark.parametrize('message', messages, ids=[message.__class__.__name__ for message in messages])
def test_schema_compliance(message):
    xml_message = to_xml(message)
    schema = schemas[destination_map[type(message)]]
    schema.validate(xml_message)

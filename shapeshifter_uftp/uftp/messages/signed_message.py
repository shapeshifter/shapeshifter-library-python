from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..enums import UsefRole


@dataclass(kw_only=True)
class SignedMessage:
    """The SignedMessage element represents the secure wrapper used to submit USEF
    XML messages from the local message queue to the message queue of a remote
    participant.

    It contains minimal metadata (which is distinct from the common
    metadata used for all other messages), allowing the recipient to
    look up the sender's cryptographic scheme and public keys, and the
    actual XML message, as transformed (signed/sealed) using that
    cryptographic scheme.

    :ivar sender_domain: The Internet domain of the USEF participant
        sending this message. Upon receiving a message, the recipient
        should validate that its value matches the corresponding
        attribute value specified in the inner XML message, once un-
        sealed: if not, the message must be rejected as invalid.
    :ivar sender_role: The USEF role of the participant sending this
        message: AGR, BRP, CRO, DSO or MDC. Receive-time validation
        should take place as described for the SenderDomain attribute
        above.
    :ivar body: The Base-64 encoded inner XML message contained in this
        wrapper, as transformed (signed/sealed) using the sender's
        cryptographic scheme. The recipient can determine which scheme
        applies using a DNS or configuration file lookup, based on the
        combination of SenderDomain and SenderRole.
    """

    sender_domain: str = field(
        metadata={
            "name": "SenderDomain",
            "type": "Attribute",
            "required": True,
            "pattern": r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}",
        }
    )
    sender_role: UsefRole = field(
        metadata={
            "name": "SenderRole",
            "type": "Attribute",
            "required": True,
        }
    )
    body: bytes = field(
        metadata={
            "name": "Body",
            "type": "Attribute",
            "required": True,
            "format": "base64",
        }
    )

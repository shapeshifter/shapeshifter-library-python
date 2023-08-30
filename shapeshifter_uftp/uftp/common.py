from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# pylint: disable=missing-class-docstring,duplicate-code


class AcceptedDisputed(Enum):
    ACCEPTED = "Accepted"
    DISPUTED = "Disputed"


class AcceptedRejected(Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class AvailableRequested(Enum):
    AVAILABLE = "Available"
    REQUESTED = "Requested"


@dataclass(kw_only=True)
class PayloadMessage:
    """
    :ivar version: Version of the Shapeshifter specification used by the
        USEF participant sending this message.
    :ivar sender_domain: The Internet domain of the USEF participant
        sending this message. When receiving a message, its value should
        match the value specified in the SignedMessage wrapper:
        otherwise, the message must be rejected as invalid. When
        replying to this message, this attribute is used to look up the
        USEF endpoint the reply message should be delivered to.
    :ivar recipient_domain: Internet domain of the participant this
        message is intended for. When sending a message, this attribute,
        combined with the RecipientRole, is used to look up the USEF
        endpoint the message should be delivered to.
    :ivar time_stamp: Date and time this message was created, including
        the time zone (ISO 8601 formatted as per
        http://www.w3.org/TR/NOTE-datetime).
    :ivar message_id: Unique identifier (UUID/GUID as per IETF RFC 4122)
        for this message, to be generated when composing each message.
    :ivar conversation_id: Unique identifier (UUID/GUID as per IETF RFC
        4122) used to correlate responses with requests, to be generated
        when composing the first message in a conversation and
        subsequently copied from the original message to each reply
        message.
    """

    version: Optional[str] = field(
        default="3.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
            "required": True,
            "pattern": r"(\d+\.\d+\.\d+)",
        }
    )
    sender_domain: Optional[str] = field(
        default=None,
        metadata={
            "name": "SenderDomain",
            "type": "Attribute",
            "required": True,
            "pattern": r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}",
        }
    )
    recipient_domain: Optional[str] = field(
        default=None,
        metadata={
            "name": "RecipientDomain",
            "type": "Attribute",
            "required": True,
            "pattern": r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}",
        }
    )
    time_stamp: Optional[str] = field(
        default=None,
        metadata={
            "name": "TimeStamp",
            "type": "Attribute",
            "required": True,
            "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{0,9})?([+-]\d{2}:\d{2}|Z)",
        }
    )
    message_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )
    conversation_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ConversationID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


class RedispatchBy(Enum):
    AGR = "AGR"
    DSO = "DSO"


class UsefRole(Enum):
    AGR = "AGR"
    CRO = "CRO"
    DSO = "DSO"


@dataclass(kw_only=True)
class PayloadMessageResponse(PayloadMessage):
    """
    :ivar reference_message_id: MessageID of the message that has just
        been accepted or rejected.
    :ivar result: Indication whether the query was executed successfully
        or failed.
    :ivar rejection_reason: In case the query failed, this attribute
        must contain a human-readable description of the failure reason.
    """

    result: Optional[AcceptedRejected] = field(
        default=AcceptedRejected.ACCEPTED,
        metadata={
            "name": "Result",
            "type": "Attribute",
            "required": True,
        }
    )
    rejection_reason: Optional[str] = field(
        default=None,
        metadata={
            "name": "RejectionReason",
            "type": "Attribute",
        },
    )


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


@dataclass(kw_only=True)
class TestMessage(PayloadMessage):
    __test__ = False  # Tell pytest to ignore this class


@dataclass(kw_only=True)
class TestMessageResponse(PayloadMessageResponse):
    __test__ = False  # Tell pytest to ignore this class

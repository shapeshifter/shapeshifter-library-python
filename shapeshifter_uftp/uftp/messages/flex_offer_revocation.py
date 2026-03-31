from dataclasses import dataclass, field

from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class FlexOfferRevocationResponse(PayloadMessageResponse):
    flex_offer_revocation_message_id: str = field(
        metadata={
            "name": "FlexOfferRevocationMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class FlexOfferRevocation(PayloadMessage):
    """
    :ivar flex_offer_message_id: MessageID of the FlexOffer message that
        is being revoked: this FlexOffer must have been accepted
        previously.
    """
    flex_offer_message_id: str = field(
        metadata={
            "name": "FlexOfferMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )

"""
Transport exceptions and functional exceptions that, when raised,
trigger well-defined behaviour from the Shapeshifter UFTP
implementation.

Subclasses of TransportException return the appropriate HTTP Status
Code.

Subclasses of FunctionalException return a proper
PayloadResponseMessage with result = REJECTED and the appropriate
rejection_reason.

More information on these exceptions can be found in the Shapeshifter
Specification. The relevant parts are copied as docstrings for these
exceptions.
"""
from abc import ABC


class TransportException(Exception, ABC):
    """
    Base TransportException class that is used by FastApi to return
    the approprate status code.
    """
    http_status_code: int


class MissingContentLengthException(TransportException):
    """
    Thrown when the content-length is missing from the message headers.
    """

    http_status_code = 411


class InvalidContentTypeException(TransportException):
    """
    Raised when the Content-Type header is not set to text/xml or the
    character set is not utf-8.
    """

    http_status_code = 400


class TooManyRequestsException(TransportException):
    """
    Raised when the originating IP address is making too many requests
    to the service.
    """

    http_status_code = 429


class SchemaException(TransportException):
    """
    Raised when the XML Body cannot be parsed or does not comply to
    the schema.
    """

    http_status_code = 400


class AuthenticationTimeoutException(TransportException):
    """
    Raised when the sender's public key could not be looked up in
    DNS.
    """

    http_status_code = 419


class InvalidSignatureException(TransportException):
    """
    Raised when the signed message could not be unsealed because of an
    invalid signature.
    """

    http_status_code = 401


class FunctionalException(ABC, Exception):
    """
    Base class for gunctional exceptions. When raised in a request
    context, FastAPI will return the appropriate response message to
    the other participant.
    """
    rejection_reason: str


class InvalidMessageException(FunctionalException):
    """
    Despite being schema-compliant, the syntax, type or semantics of
    the message were unacceptable for the receiving implementation.
    """
    def __init__(self, message):
        super().__init__()
        self.rejection_reason = f"Invalid Message: '{message.__class__.__name__}'"


class InvalidSenderException(FunctionalException):
    """
    There is a mismatch between the SenderDomain/Role combination in
    the message wrapper and the inner XML message.
    """
    rejection_reason = "Invalid Sender"


class UnknownRecipientException(FunctionalException):
    """
    The RecipientDomain and/or RecipientRole specified in the inner
    XML message is not handled by this endpoint.
    """
    rejection_reason = "Unknown Recipient"


class BarredSenderException(FunctionalException):
    """
    This endpoint is explicitly blocking messages from this sender.
    """
    rejection_reason = "Barred Sender"


class DuplicateIdentifierException(FunctionalException):
    """
    The MessageID attribute of the inner XML message is not unique,
    and has already been used for a message with different content.
    This message has been rejected.
    """
    rejection_reason = "Duplicate Identifier"


class AlreadySubmittedException(FunctionalException):
    """
    The MessageID attribute of the inner XML message is not unique,
    but since the message content is the same as that of a previously
    accepted message, this copy can be considered to be successfully
    submitted as well.
    """
    rejection_reason = "Already Submitted"


class ISPDurationRejectedException(FunctionalException):
    """
    The message specifies a ISP duration that is not the agreed-upon
    common value for the market in which it is used.
    """
    rejection_reason = "ISP Duration Rejected"


class TimeZoneRejectedException(FunctionalException):
    """
    The message specifies a time zone that has a different UTC offset
    than is the agreed-upon common value for the market.
    """
    rejection_reason = "TimeZone Rejected"


class InvalidCongestionPointException(FunctionalException):
    """
    Unknown congestion point or the recipient is not active at this
    congestion point.
    """
    rejection_reason = "Invalid Congestion Point"


class UnknownReferenceException(FunctionalException):
    """
    The message with the sequence where is referred to is unknown. For
    the concerning reference field name can be filled in (for example
    FlexRequestSequence or PrognosisSequence).
    """
    rejection_reason = "Unknown Reference"


class ReferencePeriodMismatchException(FunctionalException):
    """
    The message(s) with the sequence where is referred to contains a
    different Period.
    """
    rejection_reason = "Reference Period Mismatch"


class ReferenceMessageExpiredException(FunctionalException):
    """
    The message that is referred to is expired.
    """
    rejection_reason = "Reference Message Expired"


class ReferenceMessageRevokedException(FunctionalException):
    """
    The message that is referred to is revoked.
    """
    rejection_reason = "Reference Message Revoked"


class ISPsOutOfBoundsException(FunctionalException):
    """
    One or more ISPs are outside the tolerated boundaries: ISPs do not
    exist.
    """
    rejection_reason = "ISPs Out Of Bounds"


class ISPConflictException(FunctionalException):
    """
    One or more ISPs are defined more than once, possibly because of
    an incorrect duration.
    """
    rejection_reason = "ISP Conflict"


class PeriodOutOfBoundsException(FunctionalException):
    """
    Period of the message is inappropriate. For example: a FlexRequest
    with a Period in the past or a settlement item in a
    FlexSettlement with a Period outside the concerning settlement
    period.
    """
    rejection_reason = "Period Out Of Bounds"


class ExpirationDateTimeOutOfBoundsException(FunctionalException):
    """
    ExpirationDateTime is in the past or exceeds the ISPs in the
    message.
    """
    rejection_reason = "Expiration DateTime Out Of Bounds"


class UnauthorizedException(FunctionalException):
    """
    CRO is operating in closed mode and the DSO is not pre-registered
    as an authorized participant
    """
    rejection_reason = "Unauthorized"


class ConnectionConflictException(FunctionalException):
    """
    A connection is transmitted before at another Congestion Point.
    Return EntityAddress of the concerning Connection and Congestion
    Point where it has been placed before.
    """
    def __init__(self, connection_entity_address, congestion_point_entity_address):
        super().__init__()
        self.rejection_reason = (
            f"Connection conflict: {connection_entity_address} at {congestion_point_entity_address}"
        )


class SubordinateSequenceNumberException(FunctionalException):
    """
    The message sequence is lower than that of a previously received
    DSOPortfolioUpdate
    """
    rejection_reason = "Subordinate Sequence Number"


class ServiceDiscoveryException(Exception):
    """
    Raised when there is an error during service discovery.
    """


class ClientTransportException(Exception):
    """
    Raised when the response to the client is not HTTP 200.
    """
    def __init__(self, *args, response, **kwargs):
        self.response = response
        super().__init__(*args, **kwargs)

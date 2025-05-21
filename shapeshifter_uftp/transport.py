"""
Defines the message transport, including message signatures.
"""
import re
from base64 import b64decode, b64encode
from binascii import Error as BinAsciiError
from datetime import datetime

import dns.resolver
from nacl.bindings import crypto_sign, crypto_sign_open
from nacl.exceptions import BadSignatureError
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import JsonParser, XmlParser
from xsdata.formats.dataclass.serializers import JsonSerializer, XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from .exceptions import (
    AuthenticationTimeoutException,
    InvalidSignatureException,
    SchemaException,
    ServiceDiscoveryException,
)
from .logging import logger
from .uftp import PayloadMessage

_context = XmlContext()
serializer = XmlSerializer(context=_context, config=SerializerConfig(indent="  "))
parser = XmlParser(context=_context)

json_serializer = JsonSerializer()
json_parser = JsonParser()

def seal_message(message: PayloadMessage, private_key: str) -> bytes:
    """
    Sign a message using the provided private key. The message should
    be of type PayloadMessage (or any subtype thereof). The private
    key should be given in base64-encoded form.

    The message will be returned as an opaque blob op base64 bytes.
    (In reality, this is the 64-byte signature prepended to the
    original XML message.)
    """
    if not isinstance(message, PayloadMessage):
        raise TypeError(f"'message', must be of type PayloadMessage, got: {type(message)}")

    serialized_message = to_xml(message)
    logger.debug(f"Signing outgoing message {serialized_message}")
    sealed_message = crypto_sign(serialized_message.encode("utf-8"), b64decode(private_key))
    return sealed_message


def unseal_message(message: bytes, public_key: str) -> PayloadMessage:
    """
    Validate a message's signature using the provided public key.
    The message can be given as a string or as bytes. The public
    key should be given in base64-encoded form.

    The message will be returned as a PayloadMessage object.
    """
    if public_key is None:
        logger.warning(
            "When calling unseal_message, no public key was provided. "
            "Please check that your key_lookup function returns a key."
        )
        raise TypeError("'public_key' must be of type 'str', not None")
    try:
        unsealed_message = crypto_sign_open(message, b64decode(public_key))
        logger.debug(f"Incoming Message: {unsealed_message.decode('utf-8')}")
        return from_xml(unsealed_message)
    except BadSignatureError as exc:
        logger.warning(f"The XML Signature for message {message} does not match the public key {public_key}: {exc}.")
        raise InvalidSignatureException() from exc
    except (ParserError, TypeError, ValueError) as exc:
        logger.warning(f"The incoming XML Message {message} does not conform to the XML schema: {exc}.")
        raise SchemaException(str(exc)) from exc


def to_xml(message: PayloadMessage) -> str:
    """
    Serialize the given PayloadMessage into an XML string.
    """
    return serializer.render(message)


def from_xml(message: str | bytes):
    """
    Parse the given message string into a Shapeshifter UFTP object.
    """
    if isinstance(message, str):
        return parser.from_string(message)
    if isinstance(message, bytes):
        return parser.from_bytes(message)
    raise TypeError(f"Message should be either bytes or str, not {type(message)}")


def to_json(message: PayloadMessage):
    """
    Serializes the given PayloadMessage to json. Useful when
    transferring the message outside of shapeshifter-uftp.
    """
    return json_serializer.render(message)


def from_json(message: str, message_type: type):
    """
    Parse the given json string into a message of the given type.
    """
    return json_parser.from_string(message, message_type)


def ttl_cache(ttl):
    """
    Caching decorator that will cache the result of an operation for 'ttl' seconds.
    """

    def decorator(func):
        cached_values = {}

        def wrapper(*args, **kwargs):
            # Create the cache key from the args and kwargs.
            cache_key = args
            if kwargs:
                cache_key += tuple((kwargs.items()))

            # Look up the cache key in the cache
            if cache_key in cached_values:
                expiration, data = cached_values[cache_key]
                if expiration > datetime.now().timestamp():
                    return data

                # If the key was expired, delete it from the cache.
                del cached_values[cache_key]

            # If not in cache or cache expired, call the original function and return the result
            data = func(*args, **kwargs)
            cached_values[cache_key] = (datetime.now().timestamp() + ttl, data)
            return data

        return wrapper

    return decorator


@ttl_cache(3600)
def get_keys(domain, role):
    """
    Retrieve the sender's public key using a DNS request. These are published at
    the well-known DNS name _usef._role._domain, in the format 'cs1.' +
    base64-encoded value of ([public signing key] + [public decryption key]).
    """

    # Perform the DNS lookup at the well-known DNS name
    try:
        dns_name = f"_{role}._usef.{domain}"
        result = dns.resolver.resolve(dns_name, "TXT").response.answer[0][0].strings[0]
    except dns.resolver.NXDOMAIN as exc:
        # Indicates that the domain does not even exist
        raise AuthenticationTimeoutException(
            f"Could not retrieve public keys at {dns_name}: DNS name not found."
        ) from exc
    except dns.resolver.NoNameservers as exc:
        raise ServiceDiscoveryException(
            f"Could not retrieve public key at {dns_name} because no DNS server was available (SERVFAIL). "
            "Make sure your network setup is working properly. This is not a problem with the receiving participant."
        ) from exc


    # Now verify that the string begins with `cs1.`
    if not result.startswith(b"cs1."):
        raise AuthenticationTimeoutException(
            f"Could not retrieve public keys at {dns_name}: "
            f"invalid string (must start with 'cs1.', was: {result.decode()})"
        )

    # Verify that the string is of the expected length (4 + 44 bytes or 4 + 88 bytes)
    if not len(result) in (48, 92):
        raise AuthenticationTimeoutException(
            f"Could not retrieve public key(s) at {dns_name}: "
            f"string '{result}' was not of appropriate length (48 or 90 characters)"
        )

    # Now try to decode the string using base64
    try:
        combined_keys = b64decode(result[4:])
    except BinAsciiError as exc:
        raise AuthenticationTimeoutException(
            f"Could not retrieve public keys at {dns_name}: "
            f"string '{result[4:].decode()}' is not valid base64."
        ) from exc

    # Now verify that the decoded length is 64
    if not len(combined_keys) in (32, 64):
        raise AuthenticationTimeoutException(
            f"Could not retrieve public keys at {dns_name}: "
            f"decoded base64 data should be 32 or 64 bytes long, "
            f"length is: {len(combined_keys)}."
        )

    # Now split the two bytestrings; the first will be the verify key,
    # the second will be the encryption key.
    if len(combined_keys) == 32:
        return b64encode(combined_keys).decode(), None

    return b64encode(combined_keys[:32]).decode(), b64encode(combined_keys[32:]).decode()


def get_key(domain, role):
    """
    Return only the verification key from what might be two keys.
    """
    return get_keys(domain, role)[0]

@ttl_cache(3600)
def get_endpoint(domain, role):
    """
    Retrieve the recipient's endpoint using DNS. These are published at the
    well-know DNS name _usef._role._domain
    """
    dns_name = f"_http._{role}._usef.{domain}"
    try:
        result = (
            dns.resolver.resolve(dns_name, "CNAME")
            .response.answer[0][0]
            .to_text()
        )
    except dns.resolver.NXDOMAIN as exc:
        raise ServiceDiscoveryException(
            f"Could not retrieve endpoint at {dns_name}: DNS name not found."
        ) from exc

    # To complete the URL, get the endpoint version
    version = get_version(domain)
    major_version = version.split(".")[0]

    # Construct the well-known URL using the retrieved endpoint domain and version
    endpoint_url = f"https://{result.removesuffix('.')}/shapeshifter/api/v{major_version}/message"
    return endpoint_url


@ttl_cache(3600)
def get_version(domain):
    """
    Retrieve the supported Shapeshifter versions by the recipient.
    These are published at the well-known DNS name _usef._domain.
    """
    dns_name = f"_usef.{domain}"
    try:
        result = dns.resolver.resolve(dns_name, "TXT").response.answer[0][0].strings[0].decode().strip()
        if not re.match(r"[0-9]+\.[0-9]+\.[0-9]+", result):
            raise ServiceDiscoveryException(
                f"The retrieved version was not in the format X.Y.Z: {result}"
            )
        return result
    except dns.resolver.NXDOMAIN as exc:
        raise ServiceDiscoveryException(
            f"Could not retrieve version at {dns_name}: DNS name not found."
        ) from exc

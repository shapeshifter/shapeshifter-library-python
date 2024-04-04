"""
A set of command-line-interface functions that are useful during
development of Shapeshifter applications.
"""

from argparse import ArgumentParser
from base64 import b64encode

from nacl.bindings import crypto_sign_keypair

from . import transport
from .exceptions import AuthenticationTimeoutException, ServiceDiscoveryException


def generate_signing_keypair():
    """
    Generate a signing keypair (private and public) and print them as
    base64-encoded strings. These are the strings that you'd use for
    signing and verifying messages; you pass these to the signing_key
    and recipient_signing_key parameters of the Service or Client
    objects.
    """
    public, private = crypto_sign_keypair()
    print("-" * 66)
    print("Private key (base64):", b64encode(private).decode())
    print("Public key (base64): ", b64encode(public).decode())
    print("-" * 66)

def perform_lookup():
    """
    Perform a DNS lookup of a participant's version, endpoint and
    public key details. These use the well-known DNS names described
    in the UFTP specification.
    """
    parser = ArgumentParser()
    parser.add_argument("-d", "--domain", required=True, type=str, help="The sender domain for the other party")
    parser.add_argument("-r", "--role", required=True, type=str, help="The sender role for the other party")
    args = parser.parse_args()

    print("-" * 65)

    try:
        version = transport.get_version(args.domain)
        print(f"Shapeshifer version: {version}")
    except ServiceDiscoveryException as err:
        print(err)

    try:
        endpoint = transport.get_endpoint(args.domain, args.role)
        print(f"Endpoint URL:        {endpoint}")
    except ServiceDiscoveryException as err:
        print(err)

    try:
        signing_key, decryption_key = transport.get_keys(args.domain, args.role)
        print(f"Signing key:         {signing_key}")
        if decryption_key:
            print(f"Decryption Key:      {decryption_key}")
    except AuthenticationTimeoutException as err:
        print(err)

    print("-" * 65)

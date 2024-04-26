import pytest
import subprocess
import re


# These tests will not work in a pipeline due to local requirements, and are thus disabled for now
def xtest_generate_keypair():
    output = subprocess.check_output(["shapeshifter-keypair"])
    assert re.match(rb"""------------------------------------------------------------------
Private key \(base64\): [0-9A-Za-z+/=]{88}
Public key \(base64\):  [0-9A-Za-z+/=]{44}
------------------------------------------------------------------""", output.replace(b"\r\n", b"\n"))

def xtest_lookup():
    output = subprocess.check_output(["shapeshifter-lookup", "-d", "enexis.dev", "-r", "dso"])
    assert re.match(rb"""-----------------------------------------------------------------
Shapeshifer version: [0-9]+\.[0-9]+\.[0-9]+
Endpoint URL:        https://shapeshifter-dso.enexis.dev/shapeshifter/api/v3/message
Signing key:         [0-9A-Za-z+/=]{44}
Decryption Key:      [0-9A-Za-z+/=]{44}
-----------------------------------------------------------------""", output.replace(b"\r\n", b"\n"))

def xtest_lookup_invalid_domain():
    output = subprocess.check_output(["shapeshifter-lookup", "-d", "example.com", "-r", "dso"])
    assert output.replace(b"\r\n", b"\n").decode() == """-----------------------------------------------------------------
Could not retrieve version at _usef.example.com: DNS name not found.
Could not retrieve endpoint at _http._dso._usef.example.com: DNS name not found.
Could not retrieve public keys at _dso._usef.example.com: DNS name not found.
-----------------------------------------------------------------
"""

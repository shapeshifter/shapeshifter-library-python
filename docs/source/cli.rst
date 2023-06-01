CLI (Command Line Interface)
============================

These utilities are provided to developers to speed up the development process.


Create a new keypair
--------------------

You can generate a signing keypair using the shapeshifter-keypair command line tool:

.. code-block:: bash

    $ shapeshifter-keypair
    Private key (base64): Wyg81Lki5Ib4YkEFtqfkR6edTFQywjXoZybtBQLbNJbOz+ZRPsx4RptptEDEd9Pn4UE/RWuYP/gmlbYX8Kgr8g==
    Public key (base64):  zs/mUT7MeEababRAxHfT5+FBP0VrmD/4JpW2F/CoK/I=


Perform a DNS-lookup for a party's endpoints and keys
-----------------------------------------------------

The UFTP specification deals a way of publishing service discovery information over DNS. This CLI tool will quicly look up the well-known DNS endpoints and tell you the information that is available:

.. code-block:: bash

    $ shapeshifter-lookup -d enexis.dev -r dso
    --------------------------------------------------------------------------------
    Shapeshifer version: 3.0.0
    Endpoint URL:        https://shapeshifter-dso.enexis.dev/shapeshifter/api/v3/message
    Signing key:         zs/mUT7MeEababRAxHfT5+FBP0VrmD/4JpW2F/CoK/I=
    Decryption Key:      dW+UWxFrGVE1eu1OkPSMl+qXT5/rwKzVSRoU0XSJ0RY=
    --------------------------------------------------------------------------------


If no information is found, it will tell you the DNS names it was looking at, to make it easier to publish your own DNS records:

.. code-block:: bash

    $ shapeshifter-lookup --domain example.com --role dso
    --------------------------------------------------------------------------------
    Could not retrieve version at _usef.example.com: DNS name not found
    Could not retrieve endpoint at _http._dso._usef.example.com: DNS name not found.
    Could not retrieve public keys at _dso._usef.example.com: DNS name not found.
    --------------------------------------------------------------------------------

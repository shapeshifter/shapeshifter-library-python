Shapeshifter library for Python
===============================

This is a Python implementation of the ShapeShifter UFTP protocol.

Installation
------------

.. code-block:: python3

    pip install shapeshifter-uftp


Documentation
-------------

You can read the documentation at readthedocs_.

.. _readthedocs: https://shapeshifter-uftp.readthedocs.io


Overview
--------

This library implements the full UFTP protocol that you can use for Shapeshifter communications. It implements all three roles: Distribution System Operator (**DSO**), Aggregator (**AGR**) and Common Reference Operator (**CRO**) in both directions (client and service).

Features of this package:

- Building, parsing and validation of the XML messages
- Signing and verifying of the XML messages using signatures
- DNS for service discovery and key retrieval
- Convenient clients for each role-pair
- Convenient services for each role
- JSON-serializable dataclasses for easy transport to other systems
- Fully internal queing system for full-duplex communication with minimal user code required
- Compatible with the 3.0.0 version of the Shapeshifter protocol.

Version History
---------------

+-------------+-------------------+----------------------------------+
| Version     | Release Date      | Release Notes                    |
+=============+===================+==================================+
| 1.1.0       | 2023-08-30        | Use the published 3.0.0 spec     |
|             |                   | for the XSD validation and       |
|             |                   | objects.                         |
+-------------+-------------------+----------------------------------+
| 1.0.1       | 2023-08-23        | Fixes the following two issues:  |
|             |                   |                                  |
|             |                   | - Outgoing signed messages would |
|             |                   |   be twice-encoded into base64   |
|             |                   | - Support for empty response     |
|             |                   |   messages                       |
+-------------+-------------------+----------------------------------+
| 1.0.0       | 2023-07-20        | Initial release version          |
+-------------+-------------------+----------------------------------+

Concepts
========

Communication Structure
-----------------------

This library provides all the parts you need to build a Shapeshifter-compliant participant.

Each request is a subclass of :code:`PayloadMessage`. The python library performs some checks on the validity of the message, and responds with an appropriate HTTP status code. If the message was valid, it is then handed to one of your functions, so that you can send the response to this message.

After receiving the message, the receiving party usually wants to send an actual response of some kind. For instance, a :code:`FlexRequest` message from the Distribution System Operator DSO might be replied to using a :code:`FlexOffer` message from the Aggregator (AGR). In shapeshifter-uftp this is called the **processing** step, and happens separately from the request context. A typical post-processing step might look like this:

.. code-block:: python3

    from shapeshifter_uftp import (
        ShapeshifterAgrService,
        AcceptedRejected,
        FlexRequest,
        FlexOffer,
        PayloadMessageResponse
    )

    class MyAggregatorService(ShapeshifterAggregatorService):

        ...

        def process_flex_request(self, message: FlexRequest):
            # Do some work to determine what flexibility we can offer to the DSO
            available_flex = my_backend.get_available_flexibility(...)

            # Send the FlexOffer message to the DSO
            with self.dso_client(message.sender_domain) as client:
                response = client.send_flex_offer(FlexOffer(...))

        ...

This pattern repeats for all the messages that are exchanged between the participants:


**Aggregator (AGR) Service:**

- Messages from the DSO:
    - :code:`process_d_prognosis_response`
    - :code:`process_flex_request`
    - :code:`process_flex_offer_response`
    - :code:`process_flex_offer_revocation_response`
    - :code:`process_flex_order`
    - :code:`process_flex_reservation_update`
    - :code:`process_flex_settlement`
    - :code:`process_metering_response`
- Messages from the CRO:
    - :code:`process_agr_portfolio_query_response`
    - :code:`process_agr_portfolio_update_response`

**Common Reference Operator (CRO) Service:**

- Messages from the Aggregator
    - :code:`process_agr_portfolio_query`
    - :code:`process_agr_portfolio_update`
- Messages from the DSO
    - :code:`process_dso_portfolio_query`
    - :code:`process_dso_portfolio_update`


**Distribution System Operator (DSO) Service:**

- Messages from the Aggregator:
    - :code:`process_d_prognosis`
    - :code:`process_flex_request_response`
    - :code:`process_flex_offer`
    - :code:`process_flex_order_response`
    - :code:`process_flex_offer_revocation`
    - :code:`process_flex_reservation_update_response`
    - :code:`process_flex_settlement_response`
    - :code:`process_metering`
- Messages from the CRO:
    - :code:`process_dso_portfolio_query_response`
    - :code:`process_dso_portfolio_update_response`


Identification of participants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shapeshifter Messages always come inside and envelope called SignedMessage. This envelope contains the following items:
- :code:`sender_domain`: the canonical domain name of the sender. This is not a full URL, but merely an identificiation.
- :code:`sender_role`: the role of the sender of the message, either :code:`AGR` for Aggregator, :code:`CRO` for Common Reference Operator, or :code:`DSO` for Distribution System Operator.
- :code:`body`: a base64-encoded signed message that can be decoded using the sender's public key.

The recipient of a message will look at the sender_domain and sender_role and determine if they know this party. If they do, they can use some key lookup function to retrieve the public key with which the message can be opened. See: Looking up keys.

Looking up participant keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When encountering a combination of sender_domain and sender_role, you can look up their public key in two ways:

- Using DNS: a well-known system of DNS names is specified in the UFTP protocol definition. Shapsehifter-UFTP implements this en encourages you to use it.
- USing a custom key-lookup method that takes the sender_role and sender_domain as arguments, and should return the public key in base64 format. This way, you can implement your own lookup function, which might look up the information in your own database, or perform an external API call to the GOPACS Shapeshifter Address Book, for example.

.. code-block:: python3

    from shapeshifter_uftp.exceptions import AuthenticationTimeoutException

    def key_lookup(sender_domain, sender_role):
        cursor = database.cursor()
        cursor.execute("SELECT public_key FROM shapeshifter_participants WHERE sender_role = %s AND sender_domain = %s", (sender_role, sender_domain))
        if cursor.rowcount == 0:
            raise AuthenticationTimeoutException()
        public_key = cursor.fetchone()[0]
        return public_key



Message Schema and Default Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The structure of UFTP messages looks like this:

- SignedMessage
    - SenderDomain
    - SenderRole
    - Body: a base64-encoded blob that contains the PayloadMessage and the signature.

These :code:`SignedMessage` s are never exposed to you, the developer, and are taken care of within shapeshifter-uftp.

What you deal with is the contents of the body of that message, which is always a subclass of :code:`PayloadMessage`.

Each :code:`PayloadMessage` contains the following default properties:

- :code:`Version`: the protocol version that this message complies to
- :code:`SenderDomain`: the domain of the sending participant
- :code:`RecipientDomain`: the demain of the recipient
- :code:`TimeStamp`: the timestamp at which the message was created
- :code:`MessageID`: a unique identifier for this message
- :code:`ConversationID`: an identifier of the conversation this message belongs to

All of these are required properties, but all of these can be calculated by the framework during message transmission. You as a developer don't need to supply these arguments for each message you create. If you want to override any of these, you can.

Decoupled Aggregator Example
============================

This example decouples message ingestion, application logic, and message sending into three separate applications, connected together by an external queing system. in this case, the queing system is implemented in Python, but you can see how to easily adapt this to connect to a message bus like RabbitMQ, ZeroMQ, or cloud systems like AWS SQS and Lambdas or Azure Service Bus.

The application contains the following components:

- An inbound_worker, which contains the Aggregator Service and HTTP endpoints. This application reads messages, validates the signature, extracts the contents, comes up with an initial preprocessing response (Accepted or Rejected), and puts the message onto the message queue for further processing.
- A Business Logic component, which takes incoming messages off the message queue, processes them, and puts new messages on the outgoing message queue if neccessary.
- An outbond worker, which contains clients for talking to the DSO and to the CRO, which reads outgoing messages off the outbound queue, delivers them to the relevant participant, and stores their result.

The 'simple' example that is also available combines these three functions into a single application, driven by the internal message queue inside Shapeshifter-UFTP.


Starting
--------

To run this application, you run the four files in this folder in separate python processes.

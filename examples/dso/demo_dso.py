from datetime import datetime, timezone
from uuid import uuid4

from shapeshifter_uftp import ShapeshifterDsoService
from shapeshifter_uftp.uftp import (AvailableRequested, FlexRequest,
                                    FlexRequestISP)
from xsdata.models.datatype import XmlDate


class DemoDSO(ShapeshifterDsoService):
    def process_d_prognosis(self, message):
        print(f"Received a message: {message}")

    def process_dso_portfolio_query_response(self, message):
        print(f"Received a message: {message}")

    def process_dso_portfolio_update_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_offer(self, message):
        print(f"Received a message: {message}")

    def process_flex_offer_revocation(self, message):
        print(f"Received a message: {message}")

    def process_flex_order_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_request_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_reservation_update_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_settlement_response(self, message):
        print(f"Received a message: {message}")

    def process_metering(self, message):
        print(f"Received a message: {message}")


# The Key Lookup function is used to look up the
# (public) signing key of other senders. You either
# implement a database-lookup or query to the GOPACS
# Shapeshifter Address Book here, or  use some other method
# to find the appropriate public keys for the other
# participants.
def key_lookup(sender_domain, sender_role):
    known_senders = {
        ("aggregator.demo", "AGR"): "kSyHrhqSGtSgLegJW1Rqib3sHfL9SdLlVE6qRrexfLc=",
        ("cro.demo", "CRO"): "ySUYU87usErRFKGJafwvVDLGhnBVJCCNYfQvmwv8ObM=",
    }
    return known_senders.get((sender_domain, sender_role))


# The Endpoint Lookup function is used to look up the
# endpoint URL for other participants.
def endpoint_lookup(sender_domain, sender_role):
    known_senders = {
        ("aggregator.demo", "AGR"): "http://localhost:8080/shapeshifter/api/v3/message",
        ("cro.demo", "CRO"): "http://localhost:8082/shapeshifter/api/v3/message",
    }
    return known_senders.get((sender_domain, sender_role))


if __name__ == "__main__":

    # Create a DemoDSO object that contains all the logic for
    # responding to messages. In our case, we simply print incoming
    # messages.
    dso = DemoDSO(
        sender_domain="dso.demo",
        signing_key="OLgpAnYyZmskhCKGmFAj1tysKgGjwehK0msC6NoAg9g2xNur+IAFTq1uyOuIGD9nl1J9Cy26UPQakwjZ8sNZ5w==",
        key_lookup_function=key_lookup,
        endpoint_lookup_function=endpoint_lookup,
        port=8081,
    )

    # Start the DSO service in a separate thread
    dso.run_in_thread()

    # Create a client object to talk to an aggregator at the given domain.
    agr_client = dso.agr_client("aggregator.demo")

    # Prepare a FlexRequest message
    flex_request_message = FlexRequest(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        isps=[
            FlexRequestISP(
                disposition=AvailableRequested.REQUESTED,
                min_power=0,
                max_power=10,
                start=1,
                duration=1,
            )
        ],
        revision=1,
        expiration_date_time=datetime.now(timezone.utc).isoformat(),
        contract_id=str(uuid4()),
        service_type="MyService",
    )

    # As a demo, press enter to send another FlexRequset message.
    while True:
        try:
            input("Press return to send a FlexRequest message to the AGR")
            response = agr_client.send_flex_request(flex_request_message)
            print(f"Response was: {response}")
        finally:
            dso.stop()

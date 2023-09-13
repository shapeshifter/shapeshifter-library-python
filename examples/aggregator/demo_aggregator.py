from datetime import datetime, timedelta, timezone

from shapeshifter_uftp import ShapeshifterAgrService
from shapeshifter_uftp.uftp import (FlexOffer, FlexOfferOption,
                                    FlexOfferOptionISP)
from xsdata.models.datatype import XmlDate


class DemoAggregator(ShapeshifterAgrService):
    def process_agr_portfolio_query_response(self, message):
        print(f"Received a message: {message}")

    def process_agr_portfolio_update_response(self, message):
        print(f"Received a message: {message}")

    def process_d_prognosis_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_offer_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_offer_revocation_response(self, message):
        print(f"Received a message: {message}")

    def process_flex_order(self, message):
        print(f"Received a message: {message}")

    def process_flex_request(self, message):
        print(f"Received a message: {message}")

    def process_flex_reservation_update(self, message):
        print(f"Received a message: {message}")

    def process_flex_settlement(self, message):
        print(f"Received a message: {message}")

    def process_metering_response(self, message):
        print(f"Received a message: {message}")


def key_lookup(sender_domain, sender_role):
    known_senders = {
        ("dso.demo", "DSO"): "NsTbq/iABU6tbsjriBg/Z5dSfQstulD0GpMI2fLDWec=",
        ("cro.demo", "CRO"): "ySUYU87usErRFKGJafwvVDLGhnBVJCCNYfQvmwv8ObM=",
    }
    return known_senders.get((sender_domain, sender_role))


def endpoint_lookup(sender_domain, sender_role):
    known_senders = {
        ("dso.demo", "DSO"): "http://localhost:8081/shapeshifter/api/v3/message",
        ("cro.demo", "CRO"): "http://localhost:8082/shapeshifter/api/v3/message",
    }
    return known_senders.get((sender_domain, sender_role))


# Aggregator keys:
# private: mz5XYCNKxpx48K+9oipUhsjBZed3L7rTVKLsWmG1HOqRLIeuGpIa1KAt6AlbVGqJvewd8v1J0uVUTqpGt7F8tw==
# public: kSyHrhqSGtSgLegJW1Rqib3sHfL9SdLlVE6qRrexfLc=

# DSO Keys:
# Private key (base64): OLgpAnYyZmskhCKGmFAj1tysKgGjwehK0msC6NoAg9g2xNur+IAFTq1uyOuIGD9nl1J9Cy26UPQakwjZ8sNZ5w==
# Public key (base64):  NsTbq/iABU6tbsjriBg/Z5dSfQstulD0GpMI2fLDWec=


# CRO Keys:
# Private key (base64): yEZ38dlslmCzv8qxDerngNIbiqmeoQOn8nYnjD4fVenJJRhTzu6wStEUoYlp/C9UMsaGcFUkII1h9C+bC/w5sw==
# Public key (base64):  ySUYU87usErRFKGJafwvVDLGhnBVJCCNYfQvmwv8ObM=

if __name__ == "__main__":
    aggregator = DemoAggregator(
        sender_domain="aggregator.demo",
        signing_key="mz5XYCNKxpx48K+9oipUhsjBZed3L7rTVKLsWmG1HOqRLIeuGpIa1KAt6AlbVGqJvewd8v1J0uVUTqpGt7F8tw==",
        key_lookup_function=key_lookup,
        endpoint_lookup_function=endpoint_lookup,
        port=8080,
    )

    # Start the Aggregator Service
    aggregator.run_in_thread()

    # Create a client object to talk to a DSO
    dso_client = aggregator.dso_client("dso.demo")

    # Create a Flex Offer Message
    flex_offer_message = FlexOffer(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        expiration_date_time=datetime.now(timezone.utc).isoformat(),
        offer_options=[
            FlexOfferOption(
                isps=[FlexOfferOptionISP(power=1, start=1, duration=1)],
                option_reference="MyOption",
                price=2.30,
                min_activation_factor=0.5,
            )
        ],
    )

    # As a demo, press enter to send another FlexOffer message to the DSO.
    while True:
        try:
            input("Press return to send a FlexOffer message to the DSO")
            response = dso_client.send_flex_offer(flex_offer_message)
            print(f"Response was: {response}")
        finally:
            aggregator.stop()

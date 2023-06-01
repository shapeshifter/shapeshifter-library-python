from shapeshifter_uftp import ShapeshifterAgrService, ShapeshifterCroService, ShapeshifterDsoService
from concurrent.futures import Future
from base64 import b64encode, b64decode
from nacl.bindings import crypto_sign_keypair
from shapeshifter_uftp.logging import logger
import itertools
from shapeshifter_uftp.service.base_service import snake_case


AGR_DOMAIN = "agr.dev"
CRO_DOMAIN = "cro.dev"
DSO_DOMAIN = "dso.dev"

AGR_TEST_PORT = 9001
CRO_TEST_PORT = 9002
DSO_TEST_PORT = 9003

AGR_PUBLIC_KEY, AGR_PRIVATE_KEY = [b64encode(key).decode() for key in crypto_sign_keypair()]
CRO_PUBLIC_KEY, CRO_PRIVATE_KEY = [b64encode(key).decode() for key in crypto_sign_keypair()]
DSO_PUBLIC_KEY, DSO_PRIVATE_KEY = [b64encode(key).decode() for key in crypto_sign_keypair()]


def endpoint_lookup_function(domain, role):
    if domain == "agr.dev":
        return f"http://localhost:{AGR_TEST_PORT}/shapeshifter/api/v3/message"
    elif domain == "cro.dev":
        return f"http://localhost:{CRO_TEST_PORT}/shapeshifter/api/v3/message"
    elif domain == "dso.dev":
        return f"http://localhost:{DSO_TEST_PORT}/shapeshifter/api/v3/message"


def key_lookup_function(domain, role):
    if domain == "agr.dev":
        return AGR_PUBLIC_KEY
    elif domain == "cro.dev":
        return CRO_PUBLIC_KEY
    elif domain == "dso.dev":
        return DSO_PUBLIC_KEY


class DummyAgrService(ShapeshifterAgrService):

    def __init__(self):
        super().__init__(
            sender_domain=AGR_DOMAIN,
            signing_key=AGR_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=AGR_TEST_PORT
        )

        self.request_futures = {
            f"{stage}_{name}": Future()
            for stage, name in itertools.product(
                ["pre_process", "process"],
                [
                    name
                    for name in [
                        snake_case(message.__name__)
                        for message in self.acceptable_messages
                    ]
                ],
            )
        }

        self.response_futures = {
            name: Future()
            for name in [
                f"pre_process_{snake_case(message.__name__)}"
                for message in self.acceptable_messages
            ]
        }

    def pre_process_flex_request(self, message):
        self.request_futures["pre_process_flex_request"].set_result(message)
        return self.response_futures["pre_process_flex_request"].result()

    def process_flex_request(self, message):
        self.request_futures["process_flex_request"].set_result(message)

    def pre_process_flex_order(self, message):
        self.request_futures["pre_process_flex_order"].set_result(message)
        return self.response_futures["pre_process_flex_order"].result()

    def process_flex_order(self, message):
        self.request_futures["process_flex_order"].set_result(message)

    def pre_process_flex_reservation_update(self, message):
        self.request_futures["pre_process_flex_reservation_update"].set_result(message)
        return self.response_futures["pre_process_flex_reservation_update"].result()

    def process_flex_reservation_update(self, message):
        self.request_futures["process_flex_reservation_update"].set_result(message)

    def pre_process_flex_settlement(self, message):
        self.request_futures["pre_process_flex_settlement"].set_result(message)
        return self.response_futures["pre_process_flex_settlement"].result()

    def process_flex_settlement(self, message):
        self.request_futures["process_flex_settlement"].set_result(message)

    def pre_process_flex_offer_revocation_response(self, message):
        self.request_futures["pre_process_flex_offer_revocation_response"].set_result(message)
        return self.response_futures["pre_process_flex_offer_revocation_response"].result()

    def process_flex_offer_revocation_response(self, message):
        self.request_futures["process_flex_offer_revocation_response"].set_result(message)

    def pre_process_agr_portfolio_query_response(self, message):
        self.request_futures["pre_process_agr_portfolio_query_response"].set_result(message)
        return self.response_futures["pre_process_agr_portfolio_query_response"].result()

    def process_agr_portfolio_query_response(self, message):
        self.request_futures["process_agr_portfolio_query_response"].set_result(message)

    def pre_process_agr_portfolio_update_response(self, message):
        self.request_futures["pre_process_agr_portfolio_update_response"].set_result(message)
        return self.response_futures["pre_process_agr_portfolio_update_response"].result()

    def process_agr_portfolio_update_response(self, message):
        self.request_futures["process_agr_portfolio_update_response"].set_result(message)

    def pre_process_d_prognosis_response(self, message):
        self.request_futures["pre_process_d_prognosis_response"].set_result(message)
        return self.response_futures["pre_process_d_prognosis_response"].result()

    def process_d_prognosis_response(self, message):
        self.request_futures["process_d_prognosis_response"].set_result(message)

    def pre_process_flex_offer_response(self, message):
        self.request_futures["pre_process_flex_offer_response"].set_result(message)
        return self.response_futures["pre_process_flex_offer_response"].result()

    def process_flex_offer_response(self, message):
        self.request_futures["process_flex_offer_response"].set_result(message)

    def pre_process_metering_response(self, message):
        self.request_futures["pre_process_metering_response"].set_result(message)
        return self.response_futures["pre_process_metering_response"].result()

    def process_metering_response(self, message):
        self.request_futures["process_metering_response"].set_result(message)


class DummyCroService(ShapeshifterCroService):

    def __init__(self):
        super().__init__(
            sender_domain=CRO_DOMAIN,
            signing_key=CRO_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=CRO_TEST_PORT
        )

        self.request_futures = {
            f"{stage}_{name}": Future()
            for stage, name in itertools.product(
                ["pre_process", "process"],
                [
                    name
                    for name in [
                        snake_case(message.__name__)
                        for message in self.acceptable_messages
                    ]
                ],
            )
        }

        self.response_futures = {
            name: Future()
            for name in [
                f"pre_process_{snake_case(message.__name__)}"
                for message in self.acceptable_messages
            ]
        }

    def pre_process_agr_portfolio_query(self, message):
        logger.info("Dummy Service: got AGR Portfolio Query")
        self.request_futures["pre_process_agr_portfolio_query"].set_result(message)
        logger.info("Dummy CRO Service: waiting for result")
        return self.response_futures["pre_process_agr_portfolio_query"].result()

    def process_agr_portfolio_query(self, message):
        self.request_futures["process_agr_portfolio_query"].set_result(message)

    def pre_process_agr_portfolio_update(self, message):
        self.request_futures["pre_process_agr_portfolio_update"].set_result(message)
        return self.response_futures["pre_process_agr_portfolio_update"].result()

    def process_agr_portfolio_update(self, message):
        self.request_futures["process_agr_portfolio_update"].set_result(message)

    def pre_process_dso_portfolio_query(self, message):
        self.request_futures["pre_process_dso_portfolio_query"].set_result(message)
        return self.response_futures["pre_process_dso_portfolio_query"].result()

    def process_dso_portfolio_query(self, message):
        self.request_futures["process_dso_portfolio_query"].set_result(message)

    def pre_process_dso_portfolio_update(self, message):
        self.request_futures["pre_process_dso_portfolio_update"].set_result(message)
        return self.response_futures["pre_process_dso_portfolio_update"].result()

    def process_dso_portfolio_update(self, message):
        self.request_futures["process_dso_portfolio_update"].set_result(message)


class DummyDsoService(ShapeshifterDsoService):

    def __init__(self):
        super().__init__(
            sender_domain=DSO_DOMAIN,
            signing_key=DSO_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=DSO_TEST_PORT
        )

        self.request_futures = {
            f"{stage}_{name}": Future()
            for stage, name in itertools.product(
                ["pre_process", "process"],
                [
                    name
                    for name in [
                        snake_case(message.__name__)
                        for message in self.acceptable_messages
                    ]
                ],
            )
        }

        self.response_futures = {
            name: Future()
            for name in [
                f"pre_process_{snake_case(message.__name__)}"
                for message in self.acceptable_messages
            ]
        }

    def pre_process_flex_offer(self, message):
        self.request_futures["pre_process_flex_offer"].set_result(message)
        return self.response_futures["pre_process_flex_offer"].result()

    def process_flex_offer(self, message):
        self.request_futures["process_flex_offer"].set_result(message)

    def pre_process_flex_order_response(self, message):
        self.request_futures["pre_process_flex_order_response"].set_result(message)
        return self.response_futures["pre_process_flex_order_response"].result()

    def process_flex_order_response(self, message):
        self.request_futures["process_flex_order_response"].set_result(message)

    def pre_process_d_prognosis(self, message):
        self.request_futures["pre_process_d_prognosis"].set_result(message)
        return self.response_futures["pre_process_d_prognosis"].result()

    def process_d_prognosis(self, message):
        self.request_futures["process_d_prognosis"].set_result(message)

    def pre_process_flex_offer_revocation(self, message):
        self.request_futures["pre_process_flex_offer_revocation"].set_result(message)
        return self.response_futures["pre_process_flex_offer_revocation"].result()

    def process_flex_offer_revocation(self, message):
        self.request_futures["process_flex_offer_revocation"].set_result(message)

    def pre_process_flex_settlement_response(self, message):
        self.request_futures["pre_process_flex_settlement_response"].set_result(message)
        return self.response_futures["pre_process_flex_settlement_response"].result()

    def process_flex_settlement_response(self, message):
        self.request_futures["process_flex_settlement_response"].set_result(message)

    def pre_process_dso_portfolio_update_response(self, message):
        self.request_futures["pre_process_dso_portfolio_update_response"].set_result(message)
        return self.response_futures["pre_process_dso_portfolio_update_response"].result()

    def process_dso_portfolio_update_response(self, message):
        self.request_futures["process_dso_portfolio_update_response"].set_result(message)

    def pre_process_dso_portfolio_query_response(self, message):
        self.request_futures["pre_process_dso_portfolio_query_response"].set_result(message)
        return self.response_futures["pre_process_dso_portfolio_query_response"].result()

    def process_dso_portfolio_query_response(self, message):
        self.request_futures["process_dso_portfolio_query_response"].set_result(message)

    def pre_process_flex_request_response(self, message):
        self.request_futures["pre_process_flex_request_response"].set_result(message)
        return self.response_futures["pre_process_flex_request_response"].result()

    def process_flex_request_response(self, message):
        self.request_futures["process_flex_request_response"].set_result(message)

    def pre_process_flex_reservation_update_response(self, message):
        self.request_futures["pre_process_flex_reservation_update_response"].set_result(message)
        return self.response_futures["pre_process_flex_reservation_update_response"].result()

    def process_flex_reservation_update_response(self, message):
        self.request_futures["process_flex_reservation_update_response"].set_result(message)

    def pre_process_metering(self, message):
        self.request_futures["pre_process_metering"].set_result(message)
        return self.response_futures["pre_process_metering"].result()

    def process_metering(self, message):
        self.request_futures["process_metering"].set_result(message)


class DefaultResponseAgrService(ShapeshifterAgrService):
    def __init__(self):
        super().__init__(
            sender_domain=AGR_DOMAIN,
            signing_key=AGR_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=AGR_TEST_PORT
        )

    def process_flex_request(self, message):
        pass

    def process_flex_order(self, message):
        pass

    def process_flex_reservation_update(self, message):
        pass

    def process_flex_settlement(self, message):
        pass

    def process_flex_offer_revocation_response(self, message):
        pass

    def process_agr_portfolio_query_response(self, message):
        pass

    def process_agr_portfolio_update_response(self, message):
        pass

    def process_d_prognosis_response(self, message):
        pass

    def process_flex_offer_response(self, message):
        pass

    def process_metering_response(self, message):
        pass


class DefaultResponseCroService(ShapeshifterCroService):
    def __init__(self):
        super().__init__(
            sender_domain=CRO_DOMAIN,
            signing_key=CRO_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=CRO_TEST_PORT
        )

    def process_agr_portfolio_query(self, message):
        pass

    def process_agr_portfolio_update(self, message):
        pass

    def process_dso_portfolio_query(self, message):
        pass

    def process_dso_portfolio_update(self, message):
        pass



class DefaultResponseDsoService(ShapeshifterDsoService):
    def __init__(self):
        super().__init__(
            sender_domain=DSO_DOMAIN,
            signing_key=DSO_PRIVATE_KEY,
            key_lookup_function=key_lookup_function,
            endpoint_lookup_function=endpoint_lookup_function,
            port=DSO_TEST_PORT
        )

    def process_flex_offer(self, message):
        pass

    def process_flex_order_response(self, message):
        pass

    def process_d_prognosis(self, message):
        pass

    def process_flex_offer_revocation(self, message):
        pass

    def process_flex_settlement_response(self, message):
        pass

    def process_dso_portfolio_update_response(self, message):
        pass

    def process_dso_portfolio_query_response(self, message):
        pass

    def process_flex_request_response(self, message):
        pass

    def process_flex_reservation_update_response(self, message):
        pass

    def process_metering(self, message):
        pass

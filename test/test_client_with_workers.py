from concurrent.futures import Future
from functools import partial
from time import sleep

from shapeshifter_uftp.uftp import AgrPortfolioUpdate, PayloadMessageResponse

from .helpers.messages import messages_by_type
from .helpers.services import DummyAgrService, DummyCroService


def callback(response, future):
    future.set_result(response)

def test_client_with_workers():
    with DummyAgrService() as agr_service:
        with DummyCroService() as cro_service:
            with agr_service.cro_client(cro_service.sender_domain) as client:
                message = messages_by_type[AgrPortfolioUpdate]
                main_future = Future()
                client._queue_message(message, partial(callback, future=main_future))
                result = main_future.result()
                assert result is None

def test_client_with_workers_retries():
    with DummyAgrService() as agr_service:
        with DummyCroService() as cro_service:
            with agr_service.cro_client(cro_service.sender_domain) as client:
                client.exponential_retry_base = 1.1
                client.exponential_retry_factor = 0.1
                old_endpoint_url = client.recipient_endpoint
                client.recipient_endpoint = "http://example.com"
                message = messages_by_type[AgrPortfolioUpdate]
                main_future = Future()
                client._queue_message(message, partial(callback, future=main_future))

                sleep(1.0)

                print("Left sleep")

                client.recipient_endpoint = old_endpoint_url
                assert main_future.result() is None

def test_client_with_workers_retries_never_finishes():
    with DummyAgrService() as agr_service:
        with DummyCroService() as cro_service:
            with agr_service.cro_client(cro_service.sender_domain) as client:
                client.num_delivery_attempts = 2
                client.exponential_retry_base = 1.1
                client.exponential_retry_factor = 0.1
                old_endpoint_url = client.recipient_endpoint
                client.recipient_endpoint = "http://example.com"
                message = messages_by_type[AgrPortfolioUpdate]
                main_future = Future()
                client._queue_message(message, partial(callback, future=main_future))

                sleep(2.0)

                client.recipient_endpoint = old_endpoint_url
                assert main_future.done() is False


def test_client_with_workers_error_in_callback():
    def faulty_callback(response, future):
        future.set_result(response)
        raise ValueError("BOOM")

    with DummyAgrService() as agr_service:
        with DummyCroService() as cro_service:
            with agr_service.cro_client(cro_service.sender_domain) as client:
                message = messages_by_type[AgrPortfolioUpdate]
                main_future = Future()
                client._queue_message(message, partial(faulty_callback, future=main_future))
                assert main_future.result() is None

from .helpers.services import DummyAgrService, DummyCroService
from .helpers.messages import messages_by_type
from functools import partial
from concurrent.futures import Future
from shapeshifter_uftp.uftp import PayloadMessageResponse, AgrPortfolioUpdate
from time import sleep

def callback(response, future):
    future.set_result(response)

def test_client_with_workers():
    with DummyAgrService() as agr_service:
        with DummyCroService() as cro_service:
            with agr_service.cro_client(cro_service.sender_domain) as client:
                message = messages_by_type[AgrPortfolioUpdate]
                main_future = Future()
                client._queue_message(message, partial(callback, future=main_future))
                assert cro_service.request_futures["pre_process_agr_portfolio_update"].result() == message
                response_message = PayloadMessageResponse()
                cro_service.response_futures["pre_process_agr_portfolio_update"].set_result(PayloadMessageResponse())
                assert isinstance(main_future.result(), PayloadMessageResponse)

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
                assert cro_service.request_futures["pre_process_agr_portfolio_update"].result() == message
                response_message = PayloadMessageResponse()
                cro_service.response_futures["pre_process_agr_portfolio_update"].set_result(PayloadMessageResponse())
                assert isinstance(main_future.result(), PayloadMessageResponse)

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

                print("Left sleep")

                client.recipient_endpoint = old_endpoint_url

                sleep(1.0)
                assert not cro_service.request_futures["pre_process_agr_portfolio_update"].done()



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
                assert cro_service.request_futures["pre_process_agr_portfolio_update"].result() == message
                response_message = PayloadMessageResponse()
                cro_service.response_futures["pre_process_agr_portfolio_update"].set_result(PayloadMessageResponse())
                assert isinstance(main_future.result(), PayloadMessageResponse)


import time
from shapeshifter_uftp.transport import ttl_cache


@ttl_cache(0.10)
def dummy_function(*args, **kwargs):
    return time.time()


def test_ttl_cache():
    result_1 = dummy_function()
    time.sleep(0.05)
    result_2 = dummy_function()
    assert result_1 == result_2
    time.sleep(0.06)
    result_3 = dummy_function()
    assert result_3 != result_2


def test_ttl_cache_with_args():
    result_1 = dummy_function("hello")
    time.sleep(0.05)
    result_2 = dummy_function("hello")
    result_3 = dummy_function("world")
    assert result_1 == result_2
    assert result_1 != result_3

    time.sleep(0.06)
    result_4 = dummy_function("hello")
    assert result_1 != result_4


def test_ttl_cache_with_kwargs():
    result_1 = dummy_function("hello", key="one")
    time.sleep(0.05)
    result_2 = dummy_function("hello", key="one")
    time.sleep(0.02)
    result_3 = dummy_function("hello", key="two")
    time.sleep(0.02)
    result_4 = dummy_function("world", key="one")

    assert result_1 == result_2
    assert result_1 != result_3
    assert result_1 != result_4
    assert result_3 != result_4

    time.sleep(0.06)
    result_5 = dummy_function("hello", key="one")
    assert result_1 != result_5

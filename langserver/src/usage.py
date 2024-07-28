import logging
logger = logging.getLogger(__name__)
import requests


# TODO: add some security to this endpoint, PLEASE
def deduct_with_usage(configurable: dict, tokens_used: int):
    lud16 = configurable['lud16']
    thread_id = configurable['thread_id']

    logger.debug(f"deduct_with_usage called with username: {lud16}, thread_id: {thread_id}, tokens_used: {tokens_used}")

    # url = "http://localhost:8000/api/v1/users/usage/deduct/"
    url = "http://localhost:5101/tx/"
    payload = {
        "username": lud16,
        "thread_id": thread_id,
        "tokens_used": tokens_used
    }

    response = requests.put(url, json=payload)
    response.raise_for_status()
    logger.debug(f"deduct_with_usage response: {response.json()}")

    return response.json()

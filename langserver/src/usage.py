import math
import logging
logger = logging.getLogger(__name__)
import requests


# TODO: add some security to this endpoint, PLEASE
def deduct_with_usage(configurable: dict, tokens_used: int):
    lud16 = configurable['lud16']
    # thread_id = configurable['thread_id'] # this makes LangSmith look funny... so leave it out until I can figure it out
    thread_id = configurable['chat_id']

    logger.debug(f"deduct_with_usage called with username: {lud16}, thread_id: {thread_id}, tokens_used: {tokens_used}")

    # url = "http://localhost:8000/api/v1/users/usage/deduct/"
    url = "http://localhost:5101/tx/"
    payload = {
        "username": lud16,
        "thread_id": thread_id,
        "tokens_used": math.ceil(tokens_used)
    }

    response = requests.put(url, json=payload)
    response.raise_for_status()
    logger.debug(f"deduct_with_usage response: {response.json()}")

    return response.json()



def deduct_usage(config: dict, usage_metadata: dict, OpenAIPricingModel: bool = False):
    i = usage_metadata['input_tokens']
    o = usage_metadata['output_tokens']

    if not config['configurable'].get('is_admin', False):
        if OpenAIPricingModel:
            deduct_with_usage(configurable=config['configurable'], tokens_used=(i + o * 3))
        else:
            deduct_with_usage(configurable=config['configurable'], tokens_used=(i + o * 1.5))






"""

response_metadata=
    {
        'model': 'phi3:latest',
        'created_at': '2024-07-29T02:02:51.098022Z',
        'message':
        {
            'role': 'assistant',
            'content': ''
        },
        'done_reason': 'stop',
        'done': True,
        'total_duration': 9875631042,
        'load_duration': 17385333,
        'prompt_eval_count': 1103,
        'prompt_eval_duration': 904553000,
        'eval_count': 106,
        'eval_duration': 8885692000
    }
    id='run-64079da4-1d3a-4341-aba8-239a3dacb947'
    usage_metadata={'input_tokens': 1103, 'output_tokens': 106, 'total_tokens': 1209}

"""
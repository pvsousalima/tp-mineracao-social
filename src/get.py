import requests
from itertools import count
from logging import getLogger
from json import JSONDecodeError
from time import sleep
from typing import Callable, Iterator
from requests.exceptions import ReadTimeout

api_base_url = "https://api.gettr.com"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/14.1.2",
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
]

logger = getLogger(__name__)

def get(
    url: str, params: dict = None, retries: int = float("inf"), key: str = "result"
) -> dict:
    """Makes a request to the given API endpoint and returns the 'results' object.
    Supports retries. Soon will support authentication."""
    tries = 0
    errors = []  # keeps track of the errors we've encountered
    data = {}  # Define 'data' with a default value
    user_agent_index = 0  # Index to keep track of the current user agent

    def handle_error(issue):
        logger.warning(
            "Unable to pull from API: %s. Waiting %s seconds before retrying (%s/%s)...",
            issue,
            4**tries,
            tries,
            retries,
        )
        sleep(4**tries)
        errors.append(issue)

    while tries < retries:
        logger.info("Requesting %s (params: %s)...", url, params)
        tries += 1

        try:
            resp = requests.get(
                api_base_url + url,
                params=params,
                timeout=5,
                headers={"User-Agent": USER_AGENTS[user_agent_index]},
            )
            user_agent_index = (user_agent_index + 1) % len(USER_AGENTS)  # Rotate user agent
        except requests.exceptions.ConnectionError as e:
            print("Connection refused")
            continue
        except ReadTimeout as err:
            handle_error({"timeout": err})
            continue
        except Exception as e:
            handle_error({"error is": str(e)})
            continue

        logger.info("%s gave response: %s", url, resp.text)

        if resp.status_code in [429, 500, 502, 503, 504]:
            handle_error({"status_code": resp.status_code})
            continue

        logger.debug("GET %s with params %s yielded %s", url, params, resp.content)

        try:
            print(resp.text)
            data = resp.json()
            if key in data:
                return data[key]
        
        except JSONDecodeError as e:
            print(f"JSON decoding error: {e}")

        errors.append(data)  # Retry but without sleep.

def get_paginated(
    *args,
    offset_param: str = "offset",
    offset_start: int = 0,
    offset_step: int = 20,
    result_count_func: Callable[[dict], int] = lambda k: len(k["data"]["list"]),
    **kwargs
) -> Iterator[dict]:
    """Paginates requests to the given API endpoint."""
    for i in count(start=offset_start, step=offset_step):
        params = kwargs.get("params", {})
        params[offset_param] = i
        kwargs["params"] = params
        data = get(*args, **kwargs)
        yield data

        # End if no more results
        if result_count_func(data) == 0:
            return

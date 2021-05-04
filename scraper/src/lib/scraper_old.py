import sys
import time

import requests
import numpy as np
from bs4 import BeautifulSoup

MAX_CRAWL_SLEEP_TIME = 0


def get_by_url(url: str, session: requests.Session = requests.session(), payload=None) -> requests.Response:
    headers = {  # Identify as Google Bot
        "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    try:
        res = session.get(url, headers=headers, params=payload)
        res.raise_for_status()
        if MAX_CRAWL_SLEEP_TIME == 0:
            return res

        # Wait a random amount of time requests.
        time.sleep(MAX_CRAWL_SLEEP_TIME - round(np.random.random(), 4))

        return res
    except requests.exceptions.HTTPError as http_err:
        print("An Http Error occurred:", repr(http_err))
        sys.exit(1)
    except requests.exceptions.ConnectionError as conn_err:
        print("An Error Connecting to the API occurred:", repr(conn_err))
        sys.exit(1)
    except requests.exceptions.Timeout as timeout_err:
        print("A Timeout Error occurred:", repr(timeout_err))
        sys.exit(1)
    except requests.exceptions.RequestException as req_err:
        print("An Unknown Error occurred", repr(req_err))
        sys.exit(1)

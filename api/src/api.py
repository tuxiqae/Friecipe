import sys
import time
from typing import Dict, Optional, Iterable, Union
from queue import Queue

import numpy as np
import pymongo as pymongo
from requests import session, exceptions, Response

from constants import API_OPTIONS, MAX_CRAWL_SLEEP_TIME, EMPTY_PROFILE_URL, BASE_URL
from lib import DB
from lib.endpoint import Endpoint


def get_token_from_url(url: str) -> Optional[str]:
    for h in SESSION.get(url).headers.get("set-cookie").split(";"):
        if len(match := h.split("ARToken=")) > 1:
            return match[1]  # Return token

    return None  # No token was generated


def get_from_api(item_id: int, endpoint: Endpoint) -> Optional[list]:
    if not isinstance(endpoint, Endpoint):
        raise Exception('An invalid Endpoint type was sent.')

    url = BASE_URL + endpoint.value["prefix"] + str(item_id) + endpoint.value["route"] + API_OPTIONS

    items_list = []
    print(f"Scraping {endpoint.name.lower()} from profile {item_id}")
    while True:  # Every page contains <= 100 items
        res = get_by_url(url=url)
        if res is None:
            return res
        json_res: Dict = res.json()
        next_url = json_res["links"]["next"]["href"] if "next" in json_res["links"] else None

        items = json_res[endpoint.value["top_level"]]
        if endpoint == Endpoint.RECIPE:
            return endpoint.value["encoder"](item_id, items)
        else:
            items_list.extend([endpoint.value["encoder"](item_id, item) for item in items])

        print(".", end="", flush=True)  # Progress indication

        if next_url is None:
            print(f"\n{len(items_list)} {endpoint.name.lower()} were found.")
            return items_list
        else:
            url = next_url


def bench_api(profile_id: int, endpoint: Endpoint, to_print: bool = False) -> list:
    start_time = time.time()
    items = get_from_api(profile_id, endpoint)
    print(f"{endpoint.name.capitalize()} took {time.time() - start_time} seconds to run")
    print(items)

    if to_print:
        print(f"{len(items)} followers were fetched.")

    return items


SESSION = session()
TOKEN = get_token_from_url(EMPTY_PROFILE_URL)


def populate_data_structure(ds: Optional[Union[Queue, set]], *iterables: Iterable, tag: str = "id") -> None:
    if isinstance(ds, Queue):
        insert = ds.put_nowait
    elif isinstance(ds, set):
        insert = ds.add
    else:
        print(f"{type(ds)} is not yet supported.")
        return None

    for ls in iterables:
        for item in ls:
            insert(item[tag])

    print("*" * 60)


def insert_many(collection: pymongo.collection, items: list):
    try:
        if len(items) > 0:
            collection.insert_many(items)
    except pymongo.errors.BulkWriteError as e:
        panic = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
        if len(panic) > 0:
            print("really panic")
            print(e)


def fetch_from_db(coll: str, tag: str) -> list[Union[int, str]]:
    return [item[tag] for item in DB[coll].find({}, {"_id": 0, tag: 1})]


def main():
    profiles_queue = Queue()
    profiles_queue.put(12696989)  # "404 not found" profile
    profiles_queue.put(16007298)  # AllRecipes Magazine
    profiles_queue.put(2012871)  # "thiswifecooks"
    # inserted_to_db = set(fetch_from_db())
    visited = {"db": set(fetch_from_db("profiles", "id")), "scraped": set()}

    while profile_id := profiles_queue.get():
        followers = get_from_api(profile_id, Endpoint.FOLLOWERS)
        following = get_from_api(profile_id, Endpoint.FOLLOWING)

        if profile_id not in visited["scraped"]:
            print(f"~~{profile_id} was not visited prior.~~")
            insert_many(DB["favorites"], get_from_api(profile_id, Endpoint.FAVORITES))
            insert_many(DB["reviews"], get_from_api(profile_id, Endpoint.REVIEWS))

        to_insert = []
        for profile in followers + following:
            if profile["id"] not in visited["db"]:
                visited["db"].add(profile["id"])
                to_insert.append(profile)

        print(f"Inserting {len(to_insert)} profiles to DB")
        insert_many(DB["profiles"], to_insert)
        populate_data_structure(profiles_queue, to_insert)  # Add unvisited profiles to queue.
        visited["scraped"].add(profile_id)

    print("*" * 60)


def get_by_url(url: str, payload: Dict[str, str] = None,
               headers: Dict[str, str] = None) -> Optional[Response]:
    global TOKEN
    if headers is None:
        headers = {}
    headers["user-agent"] = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    if TOKEN is not None:
        headers["Authorization"] = f"Bearer {TOKEN}"

    try:
        res = SESSION.get(url, headers=headers, params=payload)
        if res.status_code == 401:
            TOKEN = get_token_from_url(EMPTY_PROFILE_URL)
            return get_by_url(url=url, payload=payload, headers=headers)
        elif res.status_code == 404:
            return None

        res.raise_for_status()

    except exceptions.HTTPError as http_err:
        print("An Http Error occurred:", repr(http_err))
        sys.exit(1)
    except exceptions.ConnectionError as conn_err:
        print("An Error Connecting to the API occurred:", repr(conn_err))
        sys.exit(1)
    except exceptions.Timeout as timeout_err:
        print("A Timeout Error occurred:", repr(timeout_err))
        sys.exit(1)
    except exceptions.RequestException as req_err:
        print("An Unknown Error occurred", repr(req_err))
        sys.exit(1)

    if MAX_CRAWL_SLEEP_TIME == 0:
        return res

    # Wait a random amount of time requests.
    time.sleep(MAX_CRAWL_SLEEP_TIME - round(np.random.random(), 4))

    return res


if __name__ == "__main__":
    main()

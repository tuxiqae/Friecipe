#!/root/.pyenv/versions/ipython/bin/python

import api
from lib import DB, Endpoint


def main():
    # recipes: set = set(DB["favorites"].distinct("recipe_id") + DB["reviews"].distinct("recipe_id"))
    recipes: set = set(DB["recipes"].distinct("recipe_id"))

    while (recipe_id := recipes.pop()) is not None:
        print(f"{recipe_id}")
        recipe = api.get_from_api(recipe_id, Endpoint.RECIPE)
        if recipe is None:
            continue
        DB["recipes"].insert_one(recipe)
        print(f"Inserted into the DB")
        print("*" * 60)


# def main_old():
#     scraped_profiles = set()
#
#     favorites = DB["favorites"].find_one({}, {"_id": True, "recipe_id": True})
#     reviews = DB["reviews"].find_one({}, {"_id": True, "recipe_id": True})
#
#     last_fetched = {"favorites": favorites[0]["_id"],
#                     "reviews": reviews[0]["_id"]}
#
#     to_scrape = set(favorites)
#     to_scrape.update(reviews)
#
#     while recipe_id := to_scrape.pop():
#         api.get_from_api(recipe_id, Endpoint.RECIPE)
#
#     profiles_queue = Queue()
#     # inserted_to_db = set(fetch_from_db())
#
#     visited = {"db": set(api.fetch_from_db("reviews", "recipe_id")), "scraped": set()}
#
#     while profile_id := profiles_queue.get():
#         followers = get_from_api(profile_id, Endpoint.FOLLOWERS)
#         following = get_from_api(profile_id, Endpoint.FOLLOWING)
#
#         if profile_id not in visited["scraped"]:
#             print(f"~~{profile_id} was not visited prior.~~")
#             insert_many(DB["favorites"], get_from_api(profile_id, Endpoint.FAVORITES))
#             insert_many(DB["reviews"], get_from_api(profile_id, Endpoint.REVIEWS))
#
#         to_insert = []
#         for profile in followers + following:
#             if profile["id"] not in visited["db"]:
#                 visited["db"].add(profile["id"])
#                 to_insert.append(profile)
#
#         print(f"Inserting {len(to_insert)} profiles to DB")
#         api.insert_many(DB["profiles"], to_insert)
#         populate_data_structure(profiles_queue, to_insert)  # Add unvisited profiles to queue.
#         visited["scraped"].add(profile_id)
#
#     print("*" * 60)


if __name__ == "__main__":
    main()

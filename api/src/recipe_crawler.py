#!/root/.pyenv/versions/ipython/bin/python

import api
from lib import DB, Endpoint


def main():
    recipes: set = set(DB["favorites"].distinct("recipe_id") + DB["reviews"].distinct("recipe_id"))

    while (recipe_id := recipes.pop()) is not None:
        print(f"{recipe_id}")
        recipe = api.get_from_api(recipe_id, Endpoint.RECIPE)
        if recipe is None:
            continue
        DB["recipes"].insert_one(recipe)
        print(f"Inserted into the DB")
        print("*" * 60)


if __name__ == "__main__":
    main()

from typing import Dict, Optional, Union


def cook_encoder(profile_id: int, profile: Dict[str, Optional[Union[int, str]]]) -> Dict:
    return dict(id=profile["userID"], name=profile["name"], handle=profile["handle"],
                country=profile["country"], region=profile["region"], city=profile["city"])


def review_encoder(profile_id: int, review: Dict[str, Union[Dict, int, str]]) -> Dict:
    return dict(id=review["reviewID"], rating=review["rating"], date=review["dateLastModified"],
                profile_id=profile_id, recipe_id=review["recipe"]["recipeID"])


def favorite_encoder(profile_id: int, fave: Dict[str, Union[Dict, int, str]]) -> Dict:
    return dict(recipe_id=fave["recipeSummary"]["recipeID"], profile_id=profile_id, date=fave["dateLastModified"])


# def recipe_encoder(recipe_id: int, ingredients: Dict) -> Dict:
#     return dict(recipe_id=recipe_id, ingredients=[ingredient_encoder(ing) for ing in ingredients])

def ingredient_encoder(ingredient: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
    return dict(id=ingredient["ingredientID"], text=ingredient["displayValue"], quantity=ingredient["grams"])


def recipe_encoder(recipe_id: int, ingredients: Dict) -> Dict:
    res = {ing["ingredientID"]: ing["grams"] for ing in ingredients}
    res["recipe_id"] = recipe_id
    return res
    # return dict(recipe_id=recipe_id, ingredients=[ingredient_encoder(ing) for ing in ingredients])


# def ingredient_encoder(ingredient: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
#     return ingredient["ingredientID"], ingredient["grams"]
    # return dict(id=ingredient["ingredientID"], text=ingredient["displayValue"], quantity=ingredient["grams"])

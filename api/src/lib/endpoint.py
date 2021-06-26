from enum import Enum

from .encoders import cook_encoder, review_encoder, favorite_encoder, recipe_encoder


class Endpoint(Enum):
    FOLLOWERS = {"prefix": r"/users/", "route": r"/followers", "top_level": "users", "encoder": cook_encoder}
    FOLLOWING = {"prefix": r"/users/", "route": r"/following", "top_level": "users", "encoder": cook_encoder}
    REVIEWS = {"prefix": r"/users/", "route": r"/reviews", "top_level": "reviews", "encoder": review_encoder}
    FAVORITES = {"prefix": r"/users/", "route": r"/recipe-box/shared-recipes", "top_level": "items", "encoder": favorite_encoder}
    RECIPE = {"prefix": r"/recipes/", "route": r"", "top_level": "ingredients", "encoder": recipe_encoder}

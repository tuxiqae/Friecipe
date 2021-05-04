class Review:
    def __init__(self, recipe_id: int, recipe_name: str, user_id: str, text: str, rating: int):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.user_id = user_id
        self.text = text
        self.rating = rating

    def __repr__(self):
        return f"'id: {self.recipe_id}," \
               f"'Recipe': {self.recipe_name}," \
               f" 'Reviewed by':  {self.user_id}," \
               f" 'Rating': {self.rating}\n"

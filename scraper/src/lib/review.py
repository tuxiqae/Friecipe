class Review:
    def __init__(self, recipe_id: int, user_id: str, text: str, stars: int):
        self.recipe_id = recipe_id
        self.user_id = user_id
        self.text = text
        self.stars = stars

    def __repr__(self):
        return f"'ID: {self.recipe_id}," \
               f" 'Reviewer':  {self.user_id}," \
               f" 'Stars': {self.stars}\n"

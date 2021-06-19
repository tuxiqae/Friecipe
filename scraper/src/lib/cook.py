from typing import Optional


class Cook:
    def __init__(self, user_id: int, name: str, handle: str,
                 city: Optional[str], region: Optional[str], country: Optional[str]):
        self.user_id = user_id
        self.name = name
        self.handle = handle
        self.city = city
        self.region = region
        self.country = country

from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from ID import ID


class Attributes(Enum):
    uid = "uid"
    bid = "bid"
    rating = "rating"



RATING_TABLE_NAME = "Friend"
RATING_SELECTION_CONDITION = f"WHERE {Attributes.bid.value} LIKE "


temp_Friend = set()  # This will be deleted once the database is up

def get_UIDS():
    uid = str(random.randint(0,1000))
    bid = str(random.randint(0,1000))
    return uid,bid

class Rating:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = RATING_TABLE_NAME

    def __init__(self, uid: ID,bid: ID, rating: int):
        self.uid = uid
        self.bid = bid
        self.rating = rating

    @classmethod
    def generate_random(cls):
        uid,bid = get_UIDS()
        return Rating(ID(uid), ID(bid), random.randint(0,5))

    def __str__(self):
        return f"{str(self.uid), str(self.bid), self.rating}"

    def __iter__(self):
        return iter([str(self.uid), str(self.bid), self.rating])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        rating = Rating.generate_random()
        print(rating)

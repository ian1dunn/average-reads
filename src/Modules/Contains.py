from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from ID import ID


class Attributes(Enum):
    collection_id = "collection_id"
    bid = "bid"




CONTAINS_TABLE_NAME = "Contains"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.collection_id.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_IDS():
    return str(random.randint(0,10000)),str(random.randint(0,10000))
class Contains:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, collection_id: ID,bid: ID):
        self.collection_id = collection_id
        self.bid = bid

    @classmethod
    def generate_random(cls):
        collection_id,bid = get_IDS()
        return Contains(ID(collection_id), ID(bid), )

    def __str__(self):
        return f"{str(self.collection_id), str(self.bid)}"

    def __iter__(self):
        return iter([str(self.collection_id), str(self.bid)])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        contain = Contains.generate_random()
        print(contain)

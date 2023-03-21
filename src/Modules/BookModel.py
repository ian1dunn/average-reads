from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    bid = "bid"
    ctid = "ctid"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.bid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_IDS():
    return str(random.randint(0,10000)),str(random.randint(0,10000))
class BookModel:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, bid: ID,ctid: ID):
        self.bid = bid
        self.ctid = ctid

    @classmethod
    def generate_random(cls):
        bid,ctid = get_IDS()
        return BookModel(ID(bid), ID(ctid))

    def __str__(self):
        return f"{str(self.bid), str(self.ctid)}"

    def __iter__(self):
        return iter([str(self.bid), str(self.ctid)])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        bookModel = BookModel.generate_random()
        print(bookModel)

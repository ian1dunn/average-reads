from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    aid = "aid"
    bid = "bid"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.cid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_IDS():
    return str(random.randint(0,10000)),str(random.randint(0,10000))
class AppealToBook:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, aid: ID,bid: ID):
        self.aid = aid
        self.bid = bid

    @classmethod
    def generate_random(cls):
        aid, bid = get_IDS()
        return AppealToBook(ID(aid), ID(bid))

    def __str__(self):
        return f"{str(self.aid), str(self.bid)}"


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        appealToBook = AppealToBook.generate_random()
        print(appealToBook)

from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import FIRST_NAMES , LAST_NAMES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    cid = "cid"
    bid = "bid"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.cid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_ID():
    return str(random.randint(0,10000))
def get_Name():
    return str(random.choice(FIRST_NAMES)+" "+random.choice(LAST_NAMES))
class Contributor:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, cid: ID,c_name: str):
        self.cid = cid
        self.c_name = c_name

    @classmethod
    def generate_random(cls):
        cid = get_ID()
        name = get_Name()
        return Contributor(ID(cid), name)

    def __str__(self):
        return f"{str(self.cid), self.c_name}"

    def __iter__(self):
        return iter([str(self.cid), self.c_name])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        contributor = Contributor.generate_random()
        print(contributor)

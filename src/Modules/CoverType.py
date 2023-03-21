from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from ID import ID


class Attributes(Enum):
    ctid = "ctid"
    ct_name = "ct_name"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.ctid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_ID():
    return str(random.randint(0,10000))
def get_Name():
    return str(random.choice(TITLES))
class CoverType:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, ctid: ID, ct_name: str):
        self.ctid = ctid
        self.ct_name = ct_name

    @classmethod
    def generate_random(cls):
        ctid = get_ID()
        ct_name = get_Name()
        return CoverType(ID(ctid), ct_name)

    def __str__(self):
        return f"{str(self.ctid), self.ct_name}"

    def __iter__(self):
        return iter([str(self.ctid), self.ct_name])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        coverType = CoverType.generate_random()
        print(coverType)

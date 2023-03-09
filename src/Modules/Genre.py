from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    gid = "gid"
    g_name = "g_name"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.cid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_ID():
    return str(random.randint(0,10000))
def get_Name():
    return str(random.choice(TITLES))
class Genre:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, gid: ID, g_name: str):
        self.gid = gid
        self.g_name = g_name

    @classmethod
    def generate_random(cls):
        gid = get_ID()
        g_name = get_Name()
        return Genre(ID(gid), g_name)

    def __str__(self):
        return f"{str(self.gid), self.g_name}"


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        genre = Genre.generate_random()
        print(genre)

from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import FIRST_NAMES, LAST_NAMES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    aid = "aid"
    name = "name"
    age = "age"




CONTAINS_TABLE_NAME = "Author"
CONTAINS_SELECTION_CONDITION = f"WHERE {Attributes.aid.value} LIKE "


temp_Contains = set()  # This will be deleted once the database is up

def get_ID():
    return str(random.randint(0,10000))
def get_Name():
    return str(random.choice(FIRST_NAMES)+" "+random.choice(LAST_NAMES))
def get_Age():
    return str(random.randint(1,100))
class Audience:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = CONTAINS_TABLE_NAME

    def __init__(self, aid: ID,name: str,age: int):
        self.aid = aid
        self.name = name
        self.age = age

    @classmethod
    def generate_random(cls):
        aid = get_ID()
        name = get_Name()
        age = get_Age()
        return Audience(ID(aid), name, age)

    def __str__(self):
        return f"{str(self.aid), self.name, str(self.age)}"
    def __iter__(self):
        return iter([str(self.aid), self.name, str(self.age)])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        audience = Audience.generate_random()
        print(audience)

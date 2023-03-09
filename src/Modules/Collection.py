from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    collection_id = "collection_id"
    uid = "uid"
    collection_name = "collection_name"



COLLECTION_TABLE_NAME = "Collection"
COLLECTION_SELECTION_CONDITION = f"WHERE {Attributes.collection_id.value} LIKE "


temp_Collections = set()  # This will be deleted once the database is up

def getUID():
    return str(random.randint(0,10000))
def getName():
    return random.choice(TITLES)
class Collection:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = COLLECTION_TABLE_NAME

    def __init__(self, collection_id: ID,uid: ID, collection_name: str):
        self.collection_id = collection_id
        self.uid = uid
        self.collection_name = collection_name

    @classmethod
    def generate_random(cls, last_uid: str | None):
        uid = getUID()
        return Collection(ID(last_uid), ID(uid), getName())

    def __str__(self):
        return f"{str(self.collection_id), str(self.uid), self.collection_name}"

    def __iter__(self):
        return iter([str(self.collection_id), str(self.uid), self.collection_name])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        collection = Collection.generate_random(last)
        last = collection.collection_id.value
        print(collection)

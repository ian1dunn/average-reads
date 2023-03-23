from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from src.Modules.GlobalStuff import increment_str
from src.Modules.ID import ID


class Attributes(Enum):
    follower_uid = "follower_uid"
    followee_uid = "followee_uid"
    date_friended = "date_friended"



Friendship_TABLE_NAME = "Friend"
FRIENDS_SELECTION_CONDITION = f"WHERE {Attributes.follower_uid.value} LIKE "


temp_Friend = set()  # This will be deleted once the database is up

def get_UIDS():
    follower_uid = str(random.randint(0,1000))
    followee_uid = str(random.randint(0,1000))
    return follower_uid,followee_uid

class Friendship:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = Friendship_TABLE_NAME

    def __init__(self, follower_uid: ID,followee_uid: ID, date_friended: datetime):
        self.follower_uid = follower_uid
        self.followee_uid = followee_uid
        self.date_friended = date_friended

    @classmethod
    def generate_random(cls):
        follower_uid,followee_uid = get_UIDS()
        return Friendship(ID(follower_uid), ID(followee_uid), datetime.now())
    def getIds(self):
        return f"{str(self.follower_uid)},{str(self.followee_uid)}"
    def __str__(self):
        return f"{str(self.follower_uid), str(self.followee_uid), self.date_friended}"

    def __iter__(self):
        return iter([str(self.follower_uid), str(self.followee_uid), self.date_friended])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        friendship = Friendship.generate_random()
        print(friendship)

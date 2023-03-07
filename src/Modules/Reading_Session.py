from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID
from Book import BOOK_TABLE_NAME
from User import USER_TABLE_NAME

class Attributes(Enum):
    sid = "sid"
    uid = "uid"
    bid = "bid"
    session_start = "session_start"
    session_end = "session_end"
    start_page = "start_page"
    end_page = "end_page"




READING_SESSION_TABLE_NAME = "Reading_Session"
TITLES_SELECTION_CONDITION = f"WHERE {Attributes.bid.value} LIKE "


temp_title = set()  # This will be deleted once the database is up


def get_Book_User():
    bid = str(random.randint(0,1000))
    uid = str(random.randint(0,1000))
    return bid,uid
def getPages():
    start = random.randint(0,400)
    end = random.randint(start,500)
    return start,end




class Reading_Session:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = READING_SESSION_TABLE_NAME

    def __init__(self, sid: ID,uid: ID,bid: ID, session_start: str, session_end: str, start_page: str,end_page : str):
        self.id = sid
        self.uid = uid
        self.bid = bid
        self.session_start = session_start
        self.session_end = session_end
        self.start_page = start_page
        self.end_page = end_page

    @classmethod
    def generate_random(cls, last_id: str | None):
        bid,uid = get_Book_User()
        start,end = getPages()
        return Reading_Session(ID(last_id), ID(bid), ID(uid), datetime.now(),datetime.now(),start,end)

    def __str__(self):
        return f"{str(self.id),str(self.uid),str(self.bid), self.session_start, self.session_end, self.start_page,self.end_page}"


if __name__ == '__main__':
    for i in range(10000):
        reading_session = Reading_Session.generate_random(str(random.randint(0,1000)))
        print(reading_session)



from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import TITLES
from src.Modules.GlobalStuff import increment_str
from src.Modules.ID import ID


class Attributes(Enum):
    bid = "bid"
    title = "title"
    pages = "pages"
    release_date = "release_date"



BOOK_TABLE_NAME = "User"
TITLES_SELECTION_CONDITION = f"WHERE {Attributes.bid.value} LIKE "


temp_title = set()  # This will be deleted once the database is up


def random_Title():
    return random.choice(TITLES)
def random_page_total():
    return random.randint(20,700)

def generate_title(title: str):
    """
    :param first_name: user first name
    :param last_name: user last name
    :return: a unique username based on a user's first and last name. Uses values in the database to ensure unique.
    """
    cur_str = random_Title().lower()
    #matches = select_from_table(BOOK_TABLE_NAME, Attributes.title.value, TITLES_SELECTION_CONDITION + cur_str + "%")
    return cur_str #+ increment_str(matches[-1][3:]) if matches else cur_str

def generate_title_temporary(title: str):
    cur_str = random_Title().lower()
    str_additions = ""
    while cur_str + str_additions in temp_title:
        str_additions = increment_str(str_additions)
    cur_str += str_additions
    temp_title.add(cur_str)
    return cur_str
class Book:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = BOOK_TABLE_NAME

    def __init__(self, bid: ID, title: str, pages: int, release_date: datetime):
        self.id = bid
        self.title = title
        self.pages = pages
        self.release_date = release_date
        #Should I create within the inait or as a seperate create probably within init


    @classmethod
    def generate_random(cls, last_bid: str | None):
        titles = generate_title_temporary(random_Title())
        return Book(ID(last_bid), titles, random_page_total(), datetime.now())

    def __str__(self):
        return f"{str(self.id), self.title, self.pages, self.release_date}"

    def __iter__(self):
        return iter([str(self.id), self.title, self.pages, self.release_date])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        book = Book.generate_random(last)
        last = book.id.value
        print(book)

from datetime import datetime
import math
import random
from enum import Enum
from src.DataCreation.PremadeData import FIRST_NAMES, LAST_NAMES, EMAIL_DOMAINS
from GlobalStuff import increment_str
from src.AverageReadsMain import select_from_table
from ID import ID


class Attributes(Enum):
    uid = "uid"
    username = "username"
    password = "password"
    f_name = "f_name"
    l_name = "l_name"
    email = "email"
    creation_date = "creation_date"
    last_access_date = "last_access_date"


USER_TABLE_NAME = "User"
USERNAME_SELECTION_CONDITION = f"WHERE {Attributes.uid.value} LIKE "

SPECIAL_CHARACTERS = "@$!%*#?&"

ALPHABET_START_UPPER_ASCII = 65
ALPHABET_LOWER_DIFFERENCE = 33
ALPHABET_RANGE = 26

MAX_PASSWORD_LENGTH = 8
MIN_PASSWORD_SPECIAL_CHARS = 1

temp_usernames = set()  # This will be deleted once the database is up


def random_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def generate_username(first_name: str, last_name: str):
    """
    :param first_name: user first name
    :param last_name: user last name
    :return: a unique username based on a user's first and last name. Uses values in the database to ensure unique.
    """
    cur_str = (first_name[0] + last_name[0:2]).lower()
    matches = select_from_table(USER_TABLE_NAME, Attributes.username.value, USERNAME_SELECTION_CONDITION + cur_str + "%")
    return cur_str + increment_str(matches[-1][3:]) if matches else cur_str


def generate_username_temporary(first_name: str, last_name: str):
    cur_str = (first_name[0] + last_name[0:2]).lower()
    str_additions = ""
    while cur_str + str_additions in temp_usernames:
        str_additions = increment_str(str_additions)
    cur_str += str_additions
    temp_usernames.add(cur_str)
    return cur_str


def generate_password(min_chars=1, max_chars=1, minimum_special=0):
    """
    Generate a random password between n and m number of total characters, and desired number of special chars
    :param min_chars: Minimum number of characters for the password
    :param max_chars: Maximum number of characters for the password
    :param minimum_special: Minimum number of special characters
    :return: A password fitting the criteria
    """
    num_special_chars = random.randint(minimum_special,
                                       math.floor(max_chars / 10) + minimum_special)  # Chose 10 just cuz
    num_normal_chars = random.randint(min_chars, max_chars) - num_special_chars
    password = ""
    for i in range(num_normal_chars + num_special_chars):
        if (random.random() < .5 and num_special_chars > 0) or num_normal_chars <= 0:
            password += random.choice(SPECIAL_CHARACTERS)
            num_special_chars -= 1
        else:
            password += chr(ALPHABET_START_UPPER_ASCII + random.randint(0, ALPHABET_RANGE) + random.randint(0, 1) *
                            ALPHABET_LOWER_DIFFERENCE)
            num_normal_chars -= 1
    return password


class User:
    """
    Class for a user which contains all their basic information.
    """
    TABLE_NAME = USER_TABLE_NAME

    def __init__(self, uid: ID, username: str, password: str, f_name: str, l_name: str, email: str, creation_date: datetime, last_access_date: datetime):
        self.id = uid
        self.username = username
        self.password = password
        self.f_name = f_name
        self.l_name = l_name
        self.email = email
        self.creation_date = creation_date
        self.last_access_date = last_access_date

    @classmethod
    def generate_random(cls, last_uid: str | None):
        f_name, l_name = random_name()
        username = generate_username_temporary(f_name, l_name)
        email = username + '@' + random.choice(EMAIL_DOMAINS) + ".com"
        return User(ID(last_uid), username, generate_password(3, MAX_PASSWORD_LENGTH, MIN_PASSWORD_SPECIAL_CHARS), f_name, l_name, email, datetime.now(), datetime.now())

    def __str__(self):
        return f"{str(self.id), self.username, self.password, self.f_name, self.l_name, self.email, self.creation_date, self.last_access_date}"

    def __iter__(self):
        return iter([str(self.id), self.username, self.password, self.f_name, self.l_name, self.email, self.creation_date, self.last_access_date])


if __name__ == '__main__':
    last = ""
    for i in range(10000):
        user = User.generate_random(last)
        last = user.id.value
        print(user)

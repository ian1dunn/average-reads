import math
import hashlib
import time
from enum import Enum

from DBInteraction import Connection
from Modules.BookResults import BookResults
import re
import datetime
import random

SPECIAL_CHARACTERS = "#?!@$%^&*-"
PASSWORD_REGEX = f"^(?=.*?[{SPECIAL_CHARACTERS}]).+$"
EMAIL_REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

DATABASE = Connection()
BookResults.DATABASE = DATABASE
CURRENT_UID = -1
MIN_SALT_LENGTH = 5
SALT_USER_THRESHOLD = 500  # Once we have n amount of users, we'll add more words to the salt
SALT_DEVIATION = 4  # The amount of extra random words we can add to the salt
MAX_SALT = 36  # The maximum length of the salt


class States(Enum):
    VALID = 0
    INVALID = 1
    EXISTS = 2
    INVALID_PASSWORD = 3


def hash_password(password, salt):
    salty_pw = ""
    # Add some more salt
    for i in range(len(salt)):
        salt = salt[:i] + chr(ord((salt[i].swapcase() if i % 2 == 0 else salt[i].lower())) // (i + len(salt))) + salt[
                                                                                                                 i + 1:]

    mult = math.ceil(len(salt) / len(password))

    # SALTY 💯
    for i in range(len(password)):
        salted = salt[i * mult % len(salt): i * mult % len(salt) + mult]
        salty_pw += chr(ord(password[i]) * ord(salted[-1])) + salted

    return hashlib.sha3_256(salty_pw.encode()).hexdigest()


def generate_salt(users=DATABASE.Query("SELECT COUNT(*) FROM users", fetch_all=False)[0]):
    salt = "".join(chr(random.randrange(48, 122)) for _ in range(0, min(1 + math.floor(
        users / SALT_USER_THRESHOLD + MIN_SALT_LENGTH + random.random() * SALT_DEVIATION), MAX_SALT)))
    return salt if DATABASE.Query(f"SELECT 1 FROM users WHERE salt = %s", fetch_all=False,
                                  data=(salt,)) is None else generate_salt(users)


def get_validation_enum(valid: bool):
    return States.VALID if valid else States.INVALID


def validate_email(email: str):
    if re.search(EMAIL_REGEX, email) is None:
        return States.INVALID
    return States.EXISTS if DATABASE.Query(f"SELECT email FROM users WHERE email = %s",
                                           fetch_all=False, data=(email,)) is not None else States.VALID


def validate_password(password: str):
    return get_validation_enum(re.search(PASSWORD_REGEX, password) is not None)


def validate_sign_in(email: str, password: str):
    valid_pw = validate_password(password)
    email_valid = validate_email(email)
    return email_valid, valid_pw if valid_pw == States.INVALID else States.VALID if email_valid == States.EXISTS and DATABASE.Query(
        f"SELECT email FROM users WHERE email = %s AND password = %s",
        fetch_all=False, data=(email, hash_password(password, DATABASE.Query("SELECT salt FROM users WHERE email = %s",
                                                                             data=(email,), fetch_all=False)[
            0]))) is not None else States.INVALID_PASSWORD


def validate_username(username: str):
    return States.INVALID if len(username) == 0 else States.EXISTS if DATABASE.Query(
        f"SELECT email FROM users WHERE username = %s", fetch_all=False, data=(username,)) is not None else States.VALID


def validate_sign_up(email: str, password: str, first_name: str, last_name: str, username: str):
    return validate_email(email), validate_password(password), get_validation_enum(
        len(first_name) > 0), get_validation_enum(len(last_name) > 0), validate_username(username)


def sign_in_user(email: str):
    # Do database stuff here to set the current user and record login datetime. We assume password is correct.
    global CURRENT_UID
    CURRENT_UID = DATABASE.Query(f"SELECT user_id FROM users WHERE email = %s", fetch_all=False, data=(email,))[0]
    DATABASE.Query(f"UPDATE users SET last_access_date = CURRENT_TIMESTAMP WHERE user_id = {CURRENT_UID}")
    print("User with the UID", CURRENT_UID, "has been signed in.")


def sign_up_new_user(email: str, password: str, first_name: str, last_name: str, username: str):
    # add user to db here
    salt = generate_salt()
    DATABASE.Query(
        f"INSERT INTO users (username, email, password, f_name, l_name, salt) VALUES (%s, %s, %s, %s, %s, %s)",
        data=(username, email, hash_password(password, salt), first_name.capitalize(), last_name.capitalize(), salt))
    print("Signed up user")


def sign_out_user():
    # Do database stuff here to log out the current user
    global CURRENT_UID
    CURRENT_UID = -1
    print("User has been signed out.")


# ------------------------------------------------- SQL DATA METHODS ------------------------------------------------- #
def read_book(book_id, start_page, end_page):
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(seconds=(end_page - start_page) * random.randint(30, 60))
    DATABASE.Query(
        f"INSERT INTO reading_session (user_id,book_id,session_start,session_end,start_page,end_page) VALUES ({CURRENT_UID},{book_id},'{start_time}','{end_time}', {start_page}, {end_page})")


def rate_book(book_id, rating):
    result = DATABASE.Query(f"SELECT rating FROM rating WHERE user_id = {CURRENT_UID} AND book_id = {book_id}",
                            fetch_all=False)
    if result is None:
        DATABASE.Query(f"INSERT INTO rating (user_id,book_id,rating) VALUES ({CURRENT_UID},{book_id},{rating})")
    else:
        DATABASE.Query(f"UPDATE rating SET rating = {rating} WHERE user_id = {CURRENT_UID} AND book_id = {book_id}")


def add_to_collection(book_id, collection_id):
    DATABASE.Query(f"INSERT INTO contains (collection_id, book_id) VALUES ({collection_id},{book_id})")


def remove_from_collection(book_id, collection_id):
    DATABASE.Query(f"DELETE FROM contains WHERE collection_id = {collection_id} AND book_id = {book_id}")


def delete_collection(collection_id):
    DATABASE.Query(
        f"DELETE FROM contains WHERE collection_id = {collection_id}")  # Delete all books from the collection
    DATABASE.Query(f"DELETE FROM collection WHERE collection_id = {collection_id}")  # Delete the collection


def get_rating_on_book(book_id):
    # Book local rating
    result = DATABASE.Query(f"SELECT rating FROM rating WHERE user_id = {CURRENT_UID} AND book_id = {book_id}",
                            fetch_all=False)

    return round(float(result[0]), 1) if result is not None else ""


def book_in_collection(book_id, collection_id):
    return DATABASE.Query(f"SELECT book_id FROM contains WHERE collection_id = {collection_id} AND book_id = {book_id}",
                          fetch_all=False) is not None


def create_collection(collection_name):
    # Create a collection with the given name and return its ID
    return DATABASE.Query(
        f"INSERT INTO collection (user_id,collection_name) VALUES ({CURRENT_UID}, %s) RETURNING collection_id",
        fetch_all=False, data=(collection_name,))[0]


def change_collection_name(collection_id, name):
    DATABASE.Query(f"UPDATE collection SET collection_name = %s WHERE collection_id = %s", data=(name, collection_id))


def get_following():
    # Get a list of the users, this person is following
    return DATABASE.Query(
        "SELECT followee_uid, u.username FROM friend INNER join users u on friend.followee_uid = u.user_id where "
        f"follower_uid = {CURRENT_UID}")


def get_user(uid):
    # Get user information based on their uid
    return DATABASE.Query("SELECT users.user_id, users.username, users.f_name, users.l_name, users.email, "
                          "users.creation_date, (SELECT COUNT(collection_id) FROM collection WHERE "
                          "collection.user_id = users.user_id), (SELECT COUNT(friend.followee_uid) FROM friend WHERE "
                          "friend.followee_uid = users.user_id), (SELECT COUNT(friend.follower_uid) FROM friend "
                          f"WHERE friend.follower_uid = users.user_id) from users WHERE users.user_id = {uid};",
                          fetch_all=False), get_user_top_books(uid)


def get_user_top_books(user_id):
    results = DATABASE.Query(
        f"SELECT book.title, COALESCE((SELECT r.rating FROM rating AS r WHERE (r.book_id = book.book_id AND user_id = {user_id})), 0), (SELECT COUNT(rss.user_id) FROM reading_session AS rss WHERE (rss.book_id = book.book_id AND user_id = {user_id})) FROM book LEFT OUTER JOIN rating r on (book.book_id = r.book_id) LEFT OUTER JOIN reading_session on (book.book_id = reading_session.book_id) WHERE (reading_session.user_id = {user_id} OR r.user_id = {user_id}) GROUP BY book.book_id ORDER BY COALESCE((SELECT r.rating FROM rating AS r WHERE (r.book_id = book.book_id AND user_id = {user_id})), 0) DESC, COUNT(book.book_id) DESC LIMIT 10;")
    return results


def unfollow_user(uid):
    DATABASE.Query(f"DELETE FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {uid}")


def get_cur_user_id():
    return CURRENT_UID


def try_follow_user(other_email):
    # Try to follow the user. 0 if valid, 1 if user invalid, 2 if already following
    other_uid = DATABASE.Query(f"SELECT user_id FROM users WHERE email = %s", fetch_all=False, data=(other_email,))
    if other_uid is None:
        return 1
    other_uid = other_uid[0]
    is_following = DATABASE.Query(
        f"SELECT 1 FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {other_uid}",
        fetch_all=False)
    if is_following is not None:
        return 2
    # Follow the user
    DATABASE.Query(
        f"INSERT INTO friend(follower_uid, followee_uid) VALUES ({CURRENT_UID}, {other_uid})")
    return 0


def get_collections():
    return DATABASE.Query(
        f"SELECT collection_name, collection_id FROM collection WHERE user_id = {CURRENT_UID} ORDER BY collection_name")


def get_num_books_and_pages(collection_id):
    results = DATABASE.Query(
        f"SELECT COUNT(book.book_id), SUM(book.pages) FROM contains INNER JOIN book ON (contains.book_id = book.book_id) WHERE contains.collection_id = {collection_id}",
        fetch_all=False)
    return results[0], results[1]


def process_finished():
    DATABASE.ConnectionClose()


# def update_passwords():
# # DO NOT USE THIS ANYMORE !@
#     # Update all the passwords to be hashed
#     # Get all the passwords
#     passwords = DATABASE.Query("SELECT user_id, password FROM users")
#     for user in passwords:
#         # Hash the password
#         salt = generate_salt()
#         hashed = hash_password(user[1], salt)
#         # Update the password
#         DATABASE.Query(f"UPDATE users SET password = %s, salt = %s WHERE user_id = {user[0]}", data=(hashed, salt))


# Test here.
if __name__ == '__main__':
    try:
        start = time.time()
        for book in BookResults.query_recommended_for_user(204):
            print(book.title, book.book_id)
    finally:
        DATABASE.ConnectionClose()

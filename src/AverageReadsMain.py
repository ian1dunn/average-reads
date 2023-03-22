from enum import Enum

from src.DBInteraction import Connection
import re

SPECIAL_CHARACTERS = "#?!@$%^&*-"
PASSWORD_REGEX = f"^(?=.*?[{SPECIAL_CHARACTERS}]).+$"
EMAIL_REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

DATABASE = Connection()
CURRENT_UID = -1


class States(Enum):
    VALID = 0
    INVALID = 1
    EXISTS = 2
    INVALID_PASSWORD = 3


def get_validation_enum(valid: bool):
    return States.VALID if valid else States.INVALID


def validate_email(email: str):
    if re.search(EMAIL_REGEX, email) is None:
        return States.INVALID
    return States.EXISTS if DATABASE.Query(f"SELECT email FROM users WHERE email = '{email}'",
                                           fetch_all=False) is not None else States.VALID


def validate_password(password: str):
    return get_validation_enum(re.search(PASSWORD_REGEX, password) is not None)


def validate_sign_in(email: str, password: str):
    valid_pw = validate_password(password)
    return validate_email(email), valid_pw if valid_pw == States.INVALID else States.VALID if DATABASE.Query(
        f"SELECT email FROM users WHERE email = '{email}' AND password = '{password}'",
        fetch_all=False) is not None else States.INVALID_PASSWORD


def validate_username(username: str):
    return States.INVALID if len(username) == 0 else States.EXISTS if DATABASE.Query(
        f"SELECT email FROM users WHERE username = '{username}'", fetch_all=False) is not None else States.VALID


def validate_sign_up(email: str, password: str, first_name: str, last_name: str, username: str):
    return validate_email(email), validate_password(password), get_validation_enum(
        len(first_name) > 0), get_validation_enum(len(last_name) > 0), validate_username(username)


def sign_in_user(email: str):
    # Do database stuff here to set the current user and record login datetime. We assume password is correct.
    global CURRENT_UID
    CURRENT_UID = DATABASE.Query(f"SELECT user_id FROM users WHERE email = '{email}'", fetch_all=False)[0]
    print("User with the UID", CURRENT_UID, "has been signed in.")


def sign_up_new_user(email: str, password: str, first_name: str, last_name: str, username: str):
    # add user to db here
    DATABASE.Query(
        f"INSERT INTO users (username, email, password, f_name, l_name) VALUES ('{username}','{email}','{password}', '{first_name.capitalize()}', '{last_name.capitalize()}')")
    print("Signed up user")


def sign_out_user():
    # Do database stuff here to log out the current user
    global CURRENT_UID
    CURRENT_UID = -1
    print("User has been signed out.")


################################################### SQL DATA METHODS ###################################################
# TODO We need collection name, book.book_id, book.title, book.pages, genres, book local rating, book authors, book publishers, book audience, book released date
def get_collection_view_data(collection_id):
    # Get data from collection in db and return it
    return DATABASE.Query(f"SELECT * FROM collection WHERE collection_id = {collection_id}",
                          fetch_all=False), DATABASE.Query(
        f"SELECT * FROM book WHERE book_id = (SELECT book_id FROM contains WHERE collection_id = {collection_id})")


# TODO idk exactly what the format of the time should be
def read_book(book_id, start_page, end_page):
    start_time, end_time = "", ""
    DATABASE.Query(
        f"INSERT INTO reading_session (user_id,book_id,session_start,session_end,start_page,end_page) VALUES ({CURRENT_UID},{book_id},{start_time},{end_time}, {start_page}, {end_page})")


# TODO either update or insert a new rating for the user on the book
def rate_book(book_id, rating):
    DATABASE.Query(f"INSERT INTO reading_session (user_id,book_id,rating) VALUES ({CURRENT_UID},{book_id},{rating})")


def add_to_collection(book_id, collection_id):
    DATABASE.Query(f"INSERT INTO contains (collection_id, bid) VALUES ({collection_id},{book_id})")


def remove_from_collection(book_id, collection_id):
    DATABASE.Query(f"DELETE FROM contains WHERE collection_id = {collection_id} AND bid = {book_id}")


def delete_collection(collection_id):
    DATABASE.Query(f"DELETE FROM contains WHERE collection_id = {collection_id}")


def get_rating_on_book(book_id):
    # Book local rating
    return \
        DATABASE.Query(f"SELECT rating FROM rating WHERE user_id = {CURRENT_UID} AND book_id = {book_id}",
                       fetch_all=False)[
            0]


def book_in_collection(book_id, collection_id):
    return DATABASE.Query(f"SELECT book_id FROM contains WHERE collection_id = {collection_id} AND book_id = {book_id}",
                          fetch_all=False) is not None


# TODO We need book.book_id, book.title, book.pages, genres, book global rating, book authors, book publishers, book audience, book released date
def get_book(book_id):
    return DATABASE.Query(f"SELECT * FROM books WHERE book_id = {book_id}", fetch_all=False)


# TODO does this automatically go into contains? could we create a trigger
def create_collection(collection_name):
    # Create a collection with the given name and return its ID
    return DATABASE.Query(
        f"INSERT INTO collection (user_id,collection_name) VALUES ({CURRENT_UID},'{collection_name}') RETURNING collection_id",
        fetch_all=False)[0]


def change_collection_name(collection_id, name):
    DATABASE.Query(f"UPDATE collection SET collection_name = '{name}' WHERE collection_id = {collection_id}")


# Create a joint table
# TODO We need book.book_id, book.title, book.pages, genres, book global rating, book authors, book publishers, book audience, book released date
# filter_by is what we're filtering by it will be one of these string (Title,Author,Publisher,Genre,Release Year)
# sort_by is how the items should be sorted it will be one of the strings above
# sort_order is one of these strings (Ascending,Descending)
def query_search(query, filter_by, sort_by, sort_order):
    return DATABASE.Query(
        f"SELECT bid, title, pages, release_date  FROM books Where bid LIKE \"%{query}%\" OR title LIKE \"%{query}%\" OR pages LIKE \"%{query}%\" OR release_date LIKE \"%{query}%\";")


def get_following():
    # Get a list of the users, this person is following
    return DATABASE.Query(f"SELECT followee_uid FROM friend where follower_uid = '{CURRENT_UID}'")


def get_user(uid):
    # Get user information based on their uid
    return DATABASE.Query(f"SELECT * from user WHERE user_id = {uid}")


def unfollow_user(uid):
    DATABASE.Query(f"DELETE FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {uid}")


# FIXME Check is_following... idk if I wrote that query correct.
def try_follow_user(other_email):
    # Try to follow the user. 0 if valid, 1 if user invalid, 2 if already following
    other_uid = DATABASE.Query(f"SELECT user_id FROM users WHERE email = '{other_email}'", fetch_all=False)[0]
    if other_uid is None:
        return 1
    is_following = DATABASE.Query(
        f"SELECT EXISTS(SELECT 1 FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {other_uid})",
        fetch_all=False)[0]
    if is_following:
        return 2
    # Follow the user
    DATABASE.Query(
        f"INSERT INTO friend(follower_uid, followee_uid) VALUES ({CURRENT_UID}, {other_uid})")
    return 0


# TODO sort_by will be (Title,Author,Publisher,Genre,Release Year), sort_order will be (Ascending,Descending)
def get_collections(sort_by, sort_order):
    return DATABASE.Query(f"SELECT * FROM collection ORDER BY '{sort_by}' '{sort_order}' ")


# TODO I think this will work...
def get_num_books_and_pages(collection_id):
    results = DATABASE.Query(
        f"SELECT COUNT(b.book_id), SUM(b.pages) FROM book AS b WHERE (SELECT c.book_id FROM collection AS c WHERE "
        f"c.collection_id = {collection_id}) = b.book_id",
        fetch_all=False)
    return results[0], results[1]


def process_finished():
    DATABASE.ConnectionClose()

# Test here.
if __name__ == '__main__':

    DATABASE.ConnectionClose()
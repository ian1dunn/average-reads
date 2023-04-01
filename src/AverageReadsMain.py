import math
import hashlib
from enum import Enum

from DBInteraction import Connection
import re
import datetime
import random

SPECIAL_CHARACTERS = "#?!@$%^&*-"
PASSWORD_REGEX = f"^(?=.*?[{SPECIAL_CHARACTERS}]).+$"
EMAIL_REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

DATABASE = Connection()
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
    salt = "".join(chr(random.randrange(48, 122)) for _ in range(0, min(1 + math.floor(users / SALT_USER_THRESHOLD + MIN_SALT_LENGTH + random.random() * SALT_DEVIATION), MAX_SALT)))
    return salt if DATABASE.Query(f"SELECT 1 FROM users WHERE salt = %s", fetch_all=False, data=(salt,)) is None else generate_salt(users)


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
        fetch_all=False, data=(email, hash_password(password, DATABASE.Query("SELECT salt FROM users WHERE email = %s", data=(email,), fetch_all=False)[0]))) is not None else States.INVALID_PASSWORD


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


def string_to_db_date(string):
    # Dates in the db are in the format yyyy-mm-dd
    # Normal dates are usually in the format mm/dd/yyyy
    # This function converts the normal date to the db date
    split_datas = string.replace(" ", "").replace("/", "-").split("-")
    if len(split_datas) > 3 or len(split_datas) == 0 or (len(split_datas[0]) != 4 and len(split_datas[-1]) != 4):
        return "0000000000"

    year, month, day = "", "", ""

    for s in split_datas:
        if len(s) < 4:
            if len(month) == 0:
                month = s
            else:
                day = s
        else:
            year = s

    month = "0" + month if len(month) == 1 else month
    day = "0" + day if len(day) == 1 else day

    if len(month) == 0:
        return f"{year}"

    return f"{year}-{month}-{day}"


################################################### SQL DATA METHODS ###################################################
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


def get_book(book_id):
    rating = DATABASE.Query(f"SELECT AVG(rating.rating) FROM rating WHERE rating.book_id = {book_id}", fetch_all=False)
    return (DATABASE.Query(f"SELECT book.book_id, book.title, book.pages FROM book WHERE book.book_id = {book_id}",
                           fetch_all=False),  # gets book id title and pages
            DATABASE.Query(
                f"SELECT genre.g_name FROM genre where genre.genre_id IN (SELECT BG.genre_id FROM book AS B INNER JOIN book_genres AS BG ON B.book_id = BG.book_id where B.book_id = {book_id}) ORDER BY genre.g_name"),
            # gets genre names attached to book
            round(float(rating[0]), 1) if rating is not None and rating[0] is not None else "",
            # gets average rating of book
            DATABASE.Query(
                f"SELECT contributors.c_name FROM contributors where contributors.contributor_id IN (SELECT A.contributor_id from author AS A INNER JOIN book AS B ON B.book_id = A.book_id WHERE B.book_id = {book_id}) ORDER BY contributors.c_name"),
            # gets author names attached to book
            DATABASE.Query(
                f"SELECT contributors.c_name FROM contributors WHERE contributors.contributor_id IN (SELECT P.contributor_id FROM publisher AS P INNER JOIN book AS B ON B.book_id = P.book_id WHERE B.book_id = {book_id}) ORDER BY contributors.c_name"),
            # gets publisher names attached to book
            DATABASE.Query(
                f"SELECT audience.a_name FROM audience WHERE audience.audience_id IN (SELECT AB.audience_id FROM appeal_to_book as AB INNER JOIN book AS B ON B.book_id = AB.book_id WHERE B.book_id = {book_id}) ORDER BY audience.a_name"),
            # gets audience name attached to book
            DATABASE.Query(f"SELECT MIN(book_model.release_date) FROM book_model WHERE book_model.book_id = {book_id}",
                           fetch_all=False)[0])  # gets min release date of book


def create_collection(collection_name):
    # Create a collection with the given name and return its ID
    return DATABASE.Query(
        f"INSERT INTO collection (user_id,collection_name) VALUES ({CURRENT_UID}, %s) RETURNING collection_id",
        fetch_all=False, data=(collection_name,))[0]


def change_collection_name(collection_id, name):
    DATABASE.Query(f"UPDATE collection SET collection_name = '{name}' WHERE collection_id = %s", data=(name,))


# Create a joint table
# filter_by is what we're filtering by it will be one of these string (Title,Author,Publisher,Genre,Release Year)
# sort_by is how the items should be sorted it will be one of the strings above
# sort_order is one of these strings (Ascending,Descending)
def query_search(query="", filter_by="", sort_by="", sort_order="", collection_id=None):
    sort_order = "ASC" if sort_order == "Ascending" else "DESC"

    query_extras = ["", "", ""]

    sort_by = "book.title" if sort_by == "Title" else "book_model.release_date" if sort_by == "Release Year" else "genre.g_name" if sort_by == "Genre" else "ca.c_name" if sort_by == "Author" else "cp.c_name"
    filter_by = "book.title" if filter_by == "Title" else "book_model.release_date" if filter_by == "Release Year" else "genre.g_name" if filter_by == "Genre" else "ca.c_name" if filter_by == "Author" else "cp.c_name"

    query = query.strip().lower()

    query_end = f"lower({filter_by}) LIKE %s"

    data = None

    if filter_by == "book_model.release_date" or sort_by == "book_model.release_date":
        query_extras[0] = "INNER JOIN book_model ON (book_model.book_id = book.book_id)"
        query_extras[1] = "INNER JOIN book_model ON (book_model.book_id = book.book_id)"
        if filter_by == "book_model.release_date":
            query_end = f"CAST({filter_by} AS char(10)) LIKE %s"
            query = string_to_db_date(query)

    if filter_by == "genre.g_name" or sort_by == "genre.g_name":
        query_extras[
            1] += "INNER JOIN book_genres ON (book_genres.book_id = book.book_id) INNER JOIN genre ON (genre.genre_id = book_genres.genre_id)"
        query_extras[
            2] += "INNER JOIN book_genres ON (book_genres.book_id = book.book_id) INNER JOIN genre ON (genre.genre_id = book_genres.genre_id)"
        if filter_by == "genre.g_name":
            query_end = f"EXISTS(SELECT 1 FROM book_genres AS bg INNER JOIN genre AS gr ON (bg.genre_id = gr.genre_id) WHERE lower(gr.g_name) LIKE %s AND bg.book_id = book.book_id)"

    if filter_by == "ca.c_name" or sort_by == "ca.c_name":
        query_extras[
            0] += "INNER JOIN author on (book.book_id = author.book_id) INNER JOIN contributors AS ca ON (author.contributor_id = ca.contributor_id)"
        query_extras[
            2] += "INNER JOIN author on (book.book_id = author.book_id) INNER JOIN contributors AS ca ON (author.contributor_id = ca.contributor_id)"
        if filter_by == "ca.c_name":
            query_end = f"EXISTS(SELECT 1 FROM contributors AS zca INNER JOIN author AS zsee ON (zca.contributor_id = zsee.contributor_id) WHERE lower(zca.c_name) LIKE %s AND zsee.book_id = book.book_id)"

    if filter_by == "cp.c_name" or sort_by == "cp.c_name":
        query_extras[
            0] += "INNER JOIN publisher on (book.book_id = publisher.book_id) INNER JOIN contributors AS cp ON (publisher.contributor_id = cp.contributor_id)"
        query_extras[
            2] += "INNER JOIN publisher on (book.book_id = publisher.book_id) INNER JOIN contributors AS cp ON (publisher.contributor_id = cp.contributor_id)"
        if filter_by == "cp.c_name":
            query_end = f"EXISTS(SELECT 1 FROM contributors AS zca INNER JOIN publisher AS zsee ON (zca.contributor_id = zsee.contributor_id) WHERE lower(zca.c_name) LIKE %s AND zsee.book_id = book.book_id)"

    if collection_id is not None:
        query_extras[
            0] += "INNER JOIN contains ON (contains.book_id = book.book_id) INNER JOIN collection ON (collection.collection_id = contains.collection_id)"
        query_extras[
            1] += "INNER JOIN contains ON (contains.book_id = book.book_id) INNER JOIN collection ON (collection.collection_id = contains.collection_id)"
        query_extras[
            2] += "INNER JOIN contains ON (contains.book_id = book.book_id) INNER JOIN collection ON (collection.collection_id = contains.collection_id)"
        query_end = f"contains.collection_id = {collection_id} "
    else:
        data = ("%" + query + "%",)

    query_end += f" GROUP BY book.book_id ORDER BY MIN({sort_by}) {sort_order}"

    bid_title_pages_genres = DATABASE.Query(f"SELECT book.book_id, book.title, book.pages, array_agg(DISTINCT genre.g_name) FROM book \
                    INNER JOIN book_genres ON (book_genres.book_id = book.book_id) \
                    INNER JOIN genre ON (genre.genre_id = book_genres.genre_id) \
                    {query_extras[0]} WHERE {query_end}", data=data)

    authors_publisher_audience = DATABASE.Query(
        f"SELECT array_agg(DISTINCT ca.c_name), array_agg(DISTINCT cp.c_name), array_agg(DISTINCT audience.a_name) FROM book \
                    INNER JOIN author on (book.book_id = author.book_id) \
                    INNER JOIN contributors AS ca ON (author.contributor_id = ca.contributor_id) \
                    INNER JOIN publisher ON (book.book_id = publisher.book_id) \
                    INNER JOIN contributors AS cp ON (publisher.contributor_id = cp.contributor_id) \
                    LEFT OUTER JOIN appeal_to_book AS atb ON (book.book_id = atb.book_id) \
                    LEFT OUTER JOIN audience ON (audience.audience_id = atb.audience_id)\
                    {query_extras[1]} WHERE {query_end}", data=data)

    avg_rate_release_date = DATABASE.Query(
        f"SELECT AVG(rating), MIN(book_model.release_date) FROM book \
                    INNER JOIN book_model ON (book_model.book_id = book.book_id) \
                    LEFT OUTER JOIN rating ON (rating.book_id = book.book_id) \
                    INNER JOIN appeal_to_book AS atb ON (book.book_id = atb.book_id)\
                    {query_extras[2]} WHERE {query_end}", data=data)

    if collection_id is None:
        return bid_title_pages_genres, authors_publisher_audience, avg_rate_release_date
    else:
        return bid_title_pages_genres, authors_publisher_audience, avg_rate_release_date, \
        DATABASE.Query(f"SELECT collection_name FROM collection WHERE collection_id = {collection_id}",
                       fetch_all=False)[0]


# Truly a gamer moment right here


def get_following():
    # Get a list of the users, this person is following
    return DATABASE.Query(
        f"SELECT followee_uid, u.username FROM friend INNER join users u on friend.followee_uid = u.user_id where follower_uid = {CURRENT_UID}")


def get_user(uid):
    # Get user information based on their uid
    return DATABASE.Query(f"SELECT * from users WHERE user_id = {uid}", fetch_all=False)


def unfollow_user(uid):
    DATABASE.Query(f"DELETE FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {uid}")


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
        f"SELECT COUNT(b.book_id), SUM(b.pages) FROM book AS b INNER JOIN collection c2 on c2.collection_id = {collection_id} INNER JOIN contains c on (b.book_id = c.book_id AND c.collection_id = c2.collection_id)",
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
        pass
    finally:
        DATABASE.ConnectionClose()

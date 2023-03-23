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
    DATABASE.Query(f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = {CURRENT_UID}")
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

# TODO idk exactly what the format of the time should be
def read_book(book_id, start_page, end_page):

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(seconds=(end_page - start_page) * random.randint(30, 60))
    
    DATABASE.Query(
        f"INSERT INTO reading_session (user_id,book_id,session_start,session_end,start_page,end_page) VALUES ({CURRENT_UID},{book_id},'{start_time}','{end_time}', {start_page}, {end_page})")
    


# TODO either update or insert a new rating for the user on the book
def rate_book(book_id, rating):
    result = DATABASE.Query(f"SELECT rating FROM rating WHERE user_id = {CURRENT_UID} AND book_id = {book_id}", fetch_all=False)
    if result is None:
        DATABASE.Query(f"INSERT INTO rating (user_id,book_id,rating) VALUES ({CURRENT_UID},{book_id},{rating})")
    else:
        DATABASE.Query(f"UPDATE rating SET rating = {rating} WHERE user_id = {CURRENT_UID} AND book_id = {book_id}")


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



def get_book(book_id):
    
    return (DATABASE.Query(f"SELECT book.book_id, book.title, book.pages FROM book WHERE book.book_id = {book_id}", fetch_all=False), #gets book id title and pages
    DATABASE.Query(f"SELECT genre.g_name FROM genre where genre.genre_id IN (SELECT BG.genre_id FROM book AS B INNER JOIN book_genres AS BG ON B.book_id = BG.book_id where B.book_id = {book_id})"), #gets genre names attached to book
    DATABASE.Query(f"SELECT AVG(rating.rating) FROM rating WHERE rating.book_id = {book_id}", fetch_all=False)[0], #gets average rating of book
    DATABASE.Query(f"SELECT contributors.c_name FROM contributors where contributors.contributor_id IN (SELECT A.contributor_id from author AS A INNER JOIN book AS B ON B.book_id = A.book_id WHERE B.book_id = {book_id})"), #gets author names attached to book
    DATABASE.Query(f"SELECT contributors.c_name FROM contributors WHERE contributors.contributor_id IN (SELECT P.contributor_id FROM publisher AS P INNER JOIN book AS B ON B.book_id = P.book_id WHERE B.book_id = {book_id})"), #gets publisher names attached to book
    DATABASE.Query(f"SELECT audience.a_name FROM audience WHERE audience.audience_id IN (SELECT AB.audience_id FROM appeal_to_book as AB INNER JOIN book AS B ON B.book_id = AB.book_id WHERE B.book_id = {book_id})"), #gets audience name attached to book
    DATABASE.Query(f"SELECT MIN(book_model.release_date) FROM book_model WHERE book_model.book_id = {book_id}", fetch_all=False)[0]) #gets min release date of book


def get_collection_view_data(collection_id, sort_by, sort_order):
    # Get data from collection in db and return it
    # return(DATABASE.Query(f"SELECT collection_name FROM collection WHERE collection_id = {collection_id}", fetch_all=False)[0],
    # [get_book(book_id[0]) for book_id in DATABASE.Query(f"SELECT book_id FROM contains WHERE collection_id = {collection_id}")])
    sort_order = "ASC" if sort_order == "Ascending" else "DESC"
    sort_by = "book.title" if sort_by == "Title" else "book_model.release_date" if sort_by == "Release Year" else "genre.g_name" if sort_by == "Genre" else "contributors.c_name" if sort_by == "Author" else "publisher.c_name"

    book_id_tuple = DATABASE.Query(f"SELECT book.book_id FROM book INNER JOIN author on (book.book_id = author.book_id) \
                                        INNER JOIN contributors ON (author.contributor_id = contributors.contributor_id) \
                                        INNER JOIN publisher ON (book.book_id = publisher.book_id) \
                                        INNER JOIN contributors AS C ON (publisher.contributor_id = C.contributor_id) \
                                        INNER JOIN book_genres ON (book_genres.book_id = book.book_id) \
                                        INNER JOIN genre ON (genre.genre_id = book_genres.genre_id) \
                                        INNER JOIN contains ON (contains.book_id = book.book_id) WHERE contains.collection_id = {collection_id} ORDER BY {sort_by} {sort_order}") 

    return (DATABASE.Query(f"SELECT collection_name FROM collection WHERE collection_id = {collection_id}", fetch_all=False)[0],[get_book(book_id[0]) for book_id in book_id_tuple])


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
    sort_order = "ASC" if sort_order == "Ascending" else "DESC"
    sort_by = "book.title" if sort_by == "Title" else "book_model.release_date" if sort_by == "Release Year" else "genre.g_name" if sort_by == "Genre" else "contributors.c_name" if sort_by == "Author" else "publisher.c_name"
    filter_by = "book.title" if filter_by == "Title" else "book_model.release_date" if filter_by == "Release Year" else "genre.g_name" if filter_by == "Genre" else "contributors.c_name" if filter_by == "Author" else "publisher.c_name"
   
   
    book_id_tuple = DATABASE.Query(f"SELECT book.book_id FROM book INNER JOIN author on (book.book_id = author.book_id) \
                                        INNER JOIN contributors ON (author.contributor_id = contributors.contributor_id) \
                                        INNER JOIN publisher ON (book.book_id = publisher.book_id) \
                                        INNER JOIN contributors AS C ON (publisher.contributor_id = C.contributor_id) \
                                        INNER JOIN book_genres ON (book_genres.book_id = book.book_id) \
                                        INNER JOIN genre ON (genre.genre_id = book_genres.genre_id) WHERE {filter_by} LIKE '%{query}%' ORDER BY {sort_by} {sort_order}") 
    return [get_book(book_id[0]) for book_id in book_id_tuple]





def get_following():
    # Get a list of the users, this person is following
    return DATABASE.Query(f"SELECT followee_uid FROM friend where follower_uid = '{CURRENT_UID}'")


def get_user(uid):
    # Get user information based on their uid
    return DATABASE.Query(f"SELECT * from user WHERE user_id = {uid}")


def unfollow_user(uid):
    DATABASE.Query(f"DELETE FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {uid}")


def try_follow_user(other_email):
    # Try to follow the user. 0 if valid, 1 if user invalid, 2 if already following
    other_uid = DATABASE.Query(f"SELECT user_id FROM users WHERE email = '{other_email}'", fetch_all=False)[0]
    if other_uid is None:
        return 1
    is_following = DATABASE.Query(
        f"SELECT 1 FROM friend WHERE follower_uid = {CURRENT_UID} AND followee_uid = {other_uid})",
        fetch_all=False)[0]
    if is_following is None:
        return 2
    # Follow the user
    DATABASE.Query(
        f"INSERT INTO friend(follower_uid, followee_uid) VALUES ({CURRENT_UID}, {other_uid})")
    return 0


# TODO sort_by will be (Title,Author,Publisher,Genre,Release Year), sort_order will be (Ascending,Descending) ISSUE #3?
def get_collections():
    return DATABASE.Query(f"SELECT collection_name, collection_id FROM collection WHERE user_id = {CURRENT_UID}")

    


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
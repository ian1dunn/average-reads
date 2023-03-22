
import sys
import os


from DBInteraction import Connection

DATABASE = Connection()

USER_ID = 00000000
# Placeholder validation methods
def is_valid_email(email: str):
    return '@' in email


def is_valid_password(password: str):
    return password == "p@ssword"


def is_valid_placeholder(whatever_attributes) -> bool:
    """
    This is a placeholder, similar to the validation methods above and should be replaced
    """
    return len(whatever_attributes) != 0


def validate_sign_in(email: str, password: str):
    return is_valid_email(email), is_valid_password(password)


def validate_sign_up(email: str, password: str, first_name: str, last_name: str, username: str):
    return is_valid_email(email), is_valid_password(password), is_valid_placeholder(first_name), is_valid_placeholder(
        last_name), is_valid_placeholder(username)


def sign_in_user(email: str, password: str):
    # Do database stuff here to set the current user and record login datetime
    print("User with the email", email, "has been signed in.")
    USER_ID = DATABASE.Query("SELECT user_id from users WHERE email = ''{email}''")
    print(USER_ID)

def sign_up_new_user(email: str, password: str, first_name: str, last_name: str, username: str):
    # add user to db here
    print("Signed up user with:", email, password, first_name, last_name, username)
    DATABASE.Query(f"INSERT INTO users(username,email,password,f_name,l_name) OUTPUT INSERTED.user_id  VALUES ({username},{email}, {password}, {first_name}, {last_name}))")


def sign_out_user():
    # Do database stuff here to log out the current user
    print("User has been signed out.")

#################### SQL DATA METHODS #############################################################
books = []
test_collections = {}

def get_collection_view_data(collection_id):
    # Get data from collection in db and return it
    return DATABASE.Query(f"SELECT * FROM collection WHERE collection_id = {collection_id}")


def read_book(book_id,start_time,end_time, start_page, end_page):
    DATABASE.Query(f"INSERT INTO reading_session (user_id,book_id,session_start,session_end,start_page,end_page) VALUES ({USER_ID},{book_id},{start_time},{end_time}, {start_page}, {end_page})")

#TODO Make distinct
def rate_book(book_id, rating):
    DATABASE.Query(f"INSERT INTO reading_session (user_id,book_id,rating) VALUES ({USER_ID},{book_id},{rating})")


def add_to_collection(book_id, collection_id):
    DATABASE.Query(f"INSERT INTO contains (\"collection_id\",\"bid\") VALUES ({collection_id},{book_id})")


def remove_from_collection(book_id, collection_id):
    DATABASE.Query(f"DELETE FROM contains WHERE collection_id = {collection_id} AND bid = {book_id}")


def delete_collection(collection_id):
    DATABASE.Query(f"DELETE FROM contains WHERE collection_id = {collection_id}")


def get_rating_on_book(book_id):
    DATABASE.Query(f"SELECT AVG(rating) FROM rating WHERE book_id = {book_id}")


def book_in_collection(book_id, collection_id):
    for book in get_collection_view_data(collection_id):
        if book.id == book_id:
            return True
    return False

#TODO What is getBook
def get_book(book_id):
    return DATABASE.Query(f"SELECT * FROM books WHERE book_id = {book_id}")
    #
    # Get the details of the book
    #for i in test_collections:
    #    for book in test_collections[i]:
    #        if book.id == book_id:
    #            return book

#TODO does this automatically go into contains? could we create a trigger
def create_collection(collection_name):
    # Create a collection with the given name and return its ID
    return DATABASE.Query(f"INSERT INTO collections ('uid','collectionName') OUTPUT collection_id VALUES ({collection_name},{USER_ID})")


def change_collection_name(collection_id, name):
    DATABASE.Query(f"UPDATE collection SET collection_name = '{name}' WHERE ")

#Create a joint table
def query_search(query, search_for, sort_by, sort_order):
    return DATABASE.Query(f"SELECT bid,title,pages,release_date  FROM books Where bid LIKE \"%{query}%\" OR title LIKE \"%{query}%\" OR pages LIKE \"%{query}%\" OR release_date LIKE \"%{query}%\";")

temp_following = []

#FIXME Should i get users after getting user id's Where specific properties
def get_following():
    # Get the user's following, return a list of users.
    return DATABASE.Query(f"SELECT follower_uid FROM friend where followee_uid = '{USER_ID}'")


def get_user(uid):
    return DATABASE.Query(f"SELECT * from user WHERE user_id = {uid}")


def unfollow_user(uid):
    DATABASE.Query(f"DELETE FROM friend WHERE follower_uid = {USER_ID} AND followee_uid = {uid}")

#FIXME Definitly doesnt check if the email is valid or if already following need to add EXIST statement
def try_follow_user(other_email):
    # Try to follow the user. 0 if valid, 1 if user invalid, 2 if already following
    DATABASE.Query(f"INSERT INTO friend(follower_uid,followee_uid) VALUES('{USER_ID}',SELECT user_id FROM users WHERE email = '{other_email}';)");
    #is_valid_uid = True  # Search the database for the user first "is_valid_uid(other_email)"
    #if not is_valid_uid:
    #    return 1
    #is_following = False  # Check if already friends  "is_following(other_email)"
    #if is_following:
    #    return 2
    ## Follow the user
    #print("Followed user", other_email)
    #return 0


def get_collections(sort_by, sort_order):
    return DATABASE.Query(f"SELECT * FROM collection ORDER BY {sort_by} {sort_order} ")

def get_num_books_and_pages(collection_id):
    books = DATABASE.Query(f"SELECT book_id FROM collection WHERE collection_id = '{collection_id}'")
    pageNum = DATABASE.Query(f"SELECT SUM(pages) FROM book WHERE book_id IN {books}")
    return books.size(),pageNum
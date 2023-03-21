
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


def sign_up_new_user(email: str, password: str, first_name: str, last_name: str, username: str):
    # add user to db here
    print("Signed up user with:", email, password, first_name, last_name, username)


def sign_out_user():
    # Do database stuff here to log out the current user
    print("User has been signed out.")


books = []
test_collections = {}

def get_collection_view_data(collection_id):
    # Get data from collection in db and return it
    return "Collection " + str(collection_id), test_collections[collection_id]


def read_book(book_id, start_page, end_page):
    # Add to reading sessions
    print("read book", book_id, start_page, "to", end_page)
    pass


def rate_book(book_id, rating):
    # Add to reading sessions
    print("rated book", book_id, rating)


def add_to_collection(book_id, collection_id):
    # Add to collection
    test_collections[collection_id].append(books[book_id])


def remove_from_collection(book_id, collection_id):
    # Add to collection
    for book in test_collections[collection_id]:
        if book.id == book_id:
            test_collections[collection_id].remove(book)
            return


def delete_collection(collection_id):
    # Delete a collection
    print("Deleted collection", collection_id)
    del test_collections[collection_id]


def get_rating_on_book(book_id):
    # Get the user's rating on the book
    return -1


def book_in_collection(book_id, collection_id):
    for book in test_collections[collection_id]:
        if book.id == book_id:
            return True
    return False


def get_book(book_id):
    # Get the details of the book
    for i in test_collections:
        for book in test_collections[i]:
            if book.id == book_id:
                return book


def create_collection(collection_name):
    # Create a collection with the given name and return its ID
    collection_id = len(test_collections)
    test_collections[collection_id] = []
    return collection_id


def change_collection_name(collection_id, name):
    # Change a collections name
    print("totally changed the collection's name!")


def query_search(query, search_for, sort_by, sort_order):
    # Query and return the results, yeahh
    return []


temp_following = []


def get_following():
    # Get the user's following, return a list of users.
    return temp_following


def get_user(uid):
    # Get the data for a user with the given uid
    for user in temp_following:
        if user.id.value == uid:
            return user


def unfollow_user(uid):
    # Unfollow the user with the given id
    for user in temp_following:
        if user.id.value == uid:
            temp_following.remove(user)
            return


def try_follow_user(other_email):
    # Try to follow the user. 0 if valid, 1 if user invalid, 2 if already following
    is_valid_uid = True  # Search the database for the user first "is_valid_uid(other_email)"
    if not is_valid_uid:
        return 1
    is_following = False  # Check if already friends  "is_following(other_email)"
    if is_following:
        return 2
    # Follow the user
    print("Followed user", other_email)
    return 0


def get_collections(sort_by, sort_order):
    return test_collections

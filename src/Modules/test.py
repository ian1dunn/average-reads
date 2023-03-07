from Book import *
from User import *
from Reading_Session import *
if __name__ == '__main__':
    last_user = ""
    last_reading_session = ""
    last_book = ""
    for i in range(10000):
        user = User.generate_random(last_user)
        last_user = user.id.value
        book = Book.generate_random(last_book)
        last_book = book.id.value

    for i in range(10000):
        reading_session = Reading_Session.generate_random(ID.getRandom(10000))



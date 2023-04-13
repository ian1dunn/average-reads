"""
Class which stores, and queries book results cuz there was lots for that.
I regret being lazy before.
Like the 9847th revision of querying books. HOPEFULLY THE LAST ONE.
I like this one though. It's pretty clean.

Author: Ethan Hartman
"""

from enum import Enum

RATING_DECIMALS = 1

LAST_90_DAYS_POPULAR_QUERY = "SELECT book.book_id FROM book INNER JOIN reading_session ON (book.book_id = reading_session.book_id) WHERE session_start > CAST(CURRENT_DATE - 90 AS TIMESTAMP) GROUP BY book.book_id ORDER BY COUNT(book.book_id) DESC LIMIT 20;"
POPULAR_FRIEND_QUERY = "SELECT b.book_id FROM friend INNER JOIN reading_session ON (friend.followee_uid = reading_session.user_id) INNER JOIN rating on (rating.user_id = friend.followee_uid) LEFT OUTER JOIN book b on (reading_session.book_id = b.book_id or rating.book_id = b.book_id) WHERE friend.follower_uid = {0} GROUP BY b.book_id ORDER BY COALESCE(AVG(rating.rating), 0) DESC, COUNT(b.book_id) DESC LIMIT 20;"
TOP_MONTHLY_RELEASED_QUERY = "SELECT book.book_id FROM book INNER JOIN book_model ON (book.book_id = book_model.book_id) LEFT OUTER JOIN rating on (rating.book_id = book.book_id) WHERE (EXTRACT(YEAR FROM book_model.release_date) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM book_model.release_date) = EXTRACT(MONTH FROM CURRENT_DATE)) GROUP BY book.book_id ORDER BY COALESCE(AVG(rating.rating), 0) DESC LIMIT 5;"

# TODO: recommendation query
RECOMMENDED_FOR_USER_QUERY = "WITH friends_books AS ( SELECT DISTINCT b.book_id, b.title, r.rating FROM friend f INNER JOIN reading_session rs ON f.followee_uid = rs.user_id INNER JOIN book b ON rs.book_id = b.book_id INNER JOIN rating r ON rs.book_id = r.book_id AND rs.user_id = r.user_id WHERE f.follower_uid = {0} AND r.rating >= 2 ), top_genres AS (     SELECT bg.genre_id, COUNT(*) as genre_count     FROM reading_session rs     INNER JOIN book_genres bg ON rs.book_id = bg.book_id     WHERE rs.user_id = {0}     GROUP BY bg.genre_id     ORDER BY genre_count DESC     LIMIT 3 ), books_by_top_genres AS (     SELECT DISTINCT b.book_id, b.title     FROM book b     INNER JOIN book_genres bg ON b.book_id = bg.book_id     WHERE bg.genre_id IN (SELECT genre_id FROM top_genres) ) SELECT fb.book_id, fb.title FROM friends_books fb UNION SELECT btg.book_id, btg.title FROM books_by_top_genres btg ORDER BY book_id;"

BOOK_DATA_QUERY = "SELECT book.book_id, book.title, book.pages, (SELECT array_agg(DISTINCT genre.g_name) FROM genre INNER JOIN book_genres bg on (bg.book_id = book.book_id AND genre.genre_id = bg.genre_id)), \
       (SELECT array_agg(DISTINCT contributors.c_name) FROM contributors INNER JOIN author a on (a.book_id = book.book_id AND contributors.contributor_id = a.contributor_id)), \
       (SELECT array_agg(DISTINCT contributors.c_name) FROM contributors INNER JOIN publisher p on (p.book_id = book.book_id AND contributors.contributor_id = p.contributor_id)), \
       (SELECT array_agg(DISTINCT audience.a_name) FROM appeal_to_book INNER JOIN audience ON (appeal_to_book.book_id = book.book_id AND appeal_to_book.audience_id = audience.audience_id)), \
       (SELECT AVG(rating.rating) FROM rating WHERE rating.book_id = book.book_id), \
       (SELECT MIN(bm.release_date) FROM cover_type INNER JOIN book_model bm on (bm.book_id = book.book_id AND cover_type.cover_type_id = bm.cover_type_id)) FROM book \
    WHERE book.book_id IN {0} GROUP BY book.book_id;"


class Recommendations(Enum):
    LAST_90_DAYS = "Last 90 Days - Top 20"
    TOP_AMONG_FRIENDS = "Top 20 Among Friends"
    TOP_NEW_RELEASES = "Top 5 New Releases"
    FOR_YOU = "For You"


def concat_list(l: list):
    final_str = ""
    for result in l:
        final_str += (", " if len(final_str) > 0 else "") + str(result)
    return final_str


def result_to_books(bid_title_pages_genres, authors_publisher_audience, avg_rate_release_date):
    return [Book(*bid_title_pages_genres[i], *authors_publisher_audience[i], *avg_rate_release_date[i]) for i in
            range(len(bid_title_pages_genres))]


def get_books_from_tuple(db, book_id_results: tuple[tuple[int]]):
    """
    Gets books from the database in ascending order based on book_id
    :param db: db object
    :param book_id_results: id's directly from a database query or in the form ((1,), (2,))
    :return: list of books in the order of tupled book ids
    """
    if len(book_id_results) == 0:
        return []
    elif len(book_id_results) == 1:
        return [Book(*db.Query(BOOK_DATA_QUERY.format("(" + str(book_id_results[0][0]) + ")"))[0])]

    book_dict = dict()
    for i in range(len(book_id_results)):
        book_dict[book_id_results[i][0]] = i

    books = [None] * len(book_id_results)
    for book_data in db.Query(BOOK_DATA_QUERY.format(tuple(book_dict))):
        books[book_dict[book_data[0]]] = Book(*book_data)

    return books


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


class Book:
    book_id: int
    title: str
    pages: int
    genre: str
    author: str
    publisher: str
    audience: str
    rating: str
    release_date: str

    def __init__(self, book_id: int, title: str, pages: int, genre: list, author: list, publisher: list,
                 audience: list, avg_rate: float, release_date: str):
        self.book_id = book_id
        self.title = title
        self.pages = pages
        self.genre = concat_list(genre)
        self.author = concat_list(author)
        self.publisher = concat_list(publisher)
        self.audience = concat_list(audience) if audience is not None else "N/A"
        self.rating = str(round(avg_rate, RATING_DECIMALS)) if avg_rate is not None else "N/A"
        self.release_date = release_date


class BookResults:
    DATABASE = None

    @classmethod
    def get_book_from_id(cls, book_id: int):
        return get_books_from_tuple(cls.DATABASE, ((book_id,),))[0]

    @classmethod
    def search_for(cls, search, filter_by, sort_by, sort_order, collection_id=None):
        sort_order = "ASC" if sort_order == "Ascending" else "DESC"

        search = search.strip().lower()
        query = "SELECT book.book_id FROM book "
        query_end = ""
        if filter_by == "Release Year" or sort_by == "Release Year":
            query += "INNER JOIN book_model on (book.book_id = book_model.book_id) "
            if filter_by == "Release Year":
                search = string_to_db_date(search)

        if filter_by == "Genre" or sort_by == "Genre":
            query += "INNER JOIN book_genres on (book.book_id = book_genres.book_id) INNER JOIN genre ON (book_genres.genre_id = genre.genre_id) "
            if filter_by == "Genre":
                query_end = "WHERE EXISTS(SELECT 1 FROM book_genres AS bg INNER JOIN genre AS gr ON (bg.genre_id = gr.genre_id) WHERE lower(gr.g_name) LIKE %s AND bg.book_id = book.book_id) "

        if filter_by == "Author" or sort_by == "Author":
            query += "INNER JOIN author on (book.book_id = author.book_id) INNER JOIN contributors c on (author.contributor_id = c.contributor_id) "
            if filter_by == "Author":
                query_end = "WHERE EXISTS(SELECT 1 FROM contributors AS zca INNER JOIN author AS zsee ON (zca.contributor_id = zsee.contributor_id) WHERE lower(zca.c_name) LIKE %s AND zsee.book_id = book.book_id) "

        if filter_by == "Publisher" or sort_by == "Publisher":
            query += "INNER JOIN publisher on (book.book_id = publisher.book_id) INNER JOIN contributors cp on (publisher.contributor_id = cp.contributor_id) "
            if filter_by == "Publisher":
                query_end = "WHERE EXISTS(SELECT 1 FROM contributors AS zca INNER JOIN publisher AS zsee ON (zca.contributor_id = zsee.contributor_id) WHERE lower(zca.c_name) LIKE %s AND zsee.book_id = book.book_id) "

        sort_by = "book.title" if sort_by == "Title" else "book_model.release_date" if sort_by == "Release Year" else "genre.g_name" if sort_by == "Genre" else "c.c_name" if sort_by == "Author" else "cp.c_name"
        filter_by = "book.title" if filter_by == "Title" else "book_model.release_date" if filter_by == "Release Year" else "genre.g_name" if filter_by == "Genre" else "c.c_name" if filter_by == "Author" else "cp.c_name"

        if filter_by == "book.title":
            query += f"WHERE LOWER({filter_by}) LIKE %s "
        elif filter_by == "book_model.release_date":
            query += f"WHERE CAST({filter_by} AS char(10)) LIKE %s "
        elif collection_id is not None:
            query += f"INNER JOIN contains ON (contains.book_id = book.book_id) INNER JOIN collection ON (collection.collection_id = contains.collection_id) WHERE contains.collection_id = {collection_id}"
        else:
            query += query_end

        query += f"GROUP BY book.book_id ORDER BY MIN({sort_by}) {sort_order}, COUNT({sort_by}) {sort_order};"

        books = get_books_from_tuple(BookResults.DATABASE,
                                     BookResults.DATABASE.Query(query, data=("%" + search + "%",)))
        if collection_id is None:
            return books
        else:
            return books, BookResults.DATABASE.Query(
                f"SELECT collection_name FROM collection WHERE collection_id = {collection_id}",
                fetch_all=False)[0]

    @classmethod
    def get_recommended_books(cls, uid: int, recommendation_type: str):
        match recommendation_type:
            case Recommendations.LAST_90_DAYS.value:
                # 20 Most popular books in the last 90 days (Based on reading sessions)
                query = LAST_90_DAYS_POPULAR_QUERY
            case Recommendations.TOP_AMONG_FRIENDS.value:
                # 20 Most popular books (Based on rating, then reading session) among friends
                query = POPULAR_FRIEND_QUERY.format(uid)
            case Recommendations.TOP_NEW_RELEASES.value:
                # Top 5 new releases of the month based on rating
                query = TOP_MONTHLY_RELEASED_QUERY
            case Recommendations.FOR_YOU.value:
                # Recommendations for the user based on their reading history
                results = get_books_from_tuple(BookResults.DATABASE, BookResults.DATABASE.Query(RECOMMENDED_FOR_USER_QUERY.format(uid), special_return=True))
                if len(results) != 0:
                    return results
                else:
                    return get_books_from_tuple(BookResults.DATABASE, BookResults.DATABASE.Query(LAST_90_DAYS_POPULAR_QUERY, special_return=True))
            case _:
                return []

        return get_books_from_tuple(BookResults.DATABASE, BookResults.DATABASE.Query(query, special_return=True))

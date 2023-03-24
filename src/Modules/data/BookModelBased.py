import csv
import random
from src.Modules.Book import Book
import datetime
def random_date(start_date, end_date):
    delta = end_date - start_date
    #print(f"{start_date}  ,  {end_date}   ,  {delta}   ,  {delta.days}")
    days = delta.days
    if(delta.days <= 0 ):
        #print("ASDASDWQEQWDQWDASD")
        days =1
    random_days = random.randrange(days)
    random_seconds = random.randrange(86400)  # 24 * 60 * 60 seconds
    return start_date + datetime.timedelta(days=random_days, seconds=random_seconds)

def getBookModels():
    books = []
    count = 0
    with open("/src/Modules/data/BookAlex.csv", 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(len(row)==0 or row[0]=='Title'):
                continue
            books.append(Book(row[0],row[1],row[2],row[3]))
            count+=1
    coverTypes = ["Audiobook","Ebook","Folio","Hardcover","Pamphlet","Paperback","Standard manuscript format","TextBook"]
    bookModels=[]
    #cid,bid,release
    for book in books:
        randomCover = random.randint(1,8)
        bookModels.append([randomCover,book.id,datetime.datetime.strptime(book.release_date,'%Y-%m-%d %H:%M:%S.%f').date()])
        ids = [randomCover]
        for i in range(random.randint(1,5)):
            while(randomCover in ids):
                randomCover = random.randint(1, 8)
            bookModels.append([randomCover, book.id, random_date(datetime.datetime.strptime(book.release_date,'%Y-%m-%d %H:%M:%S.%f'),datetime.datetime.now()).date()])
            ids.append(randomCover)
    return bookModels
models = getBookModels()

with open("bookCoverTypes.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(models)
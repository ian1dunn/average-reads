import datetime
import random
import csv
from src.Modules.Rating import Rating
from src.Modules.Reading_Session import Reading_Session
from src.Modules.User import User
from src.Modules.Book import Book


'''                                     Books                           '''
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

twoYears = datetime.datetime.now() - datetime.timedelta(days=365*2)
fourYears = datetime.datetime.now() - datetime.timedelta(days=365*4)
def getBooks():
    books = []
    count = 0
    with open("/src/Modules/data/booksdata.csv", 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0]=='Title'):
                continue
            books.append(Book(count,row[0],row[3],random_date(fourYears, twoYears)))
            count+=1
    return books
totalUsers = []
totalBooks = getBooks()
print("Books done")
'''                                     Users                           '''


for i in range(200):
    testUser = User.generate_random(0)
    totalUsers.append(testUser)
print("Users done")
'''                                     RATINGS                             '''
def createRatings(amount):
    ratings = []
    uidStart = 1
    uidEnd = len(totalUsers)
    bidStart = 1
    bidEnd = len(totalBooks)
    while(len(ratings)<amount):
        newRate = Rating( random.randint(uidStart,uidEnd),random.randint(bidStart,bidEnd), round(random.uniform(0.0, 5.0), 1))
        if not ratingContains(ratings,newRate):
            ratings.append(newRate)
    return ratings
def ratingContains(list,object:Rating):
    for items in list:
        if object.getIDsValue() == items.getIDsValue():
            return True
    return False


totalRatings = createRatings(800)
print("Ratings done")

'''                                     Reading Sessions                           '''
def createReadingSessions(amount):
    readingSession = []
    uidStart = 1
    uidEnd = 200
    bidStart = 1
    bidEnd = 211
    while(len(readingSession)<amount):
        randomBook = random.randint(bidStart,bidEnd)
        randomUser = random.randint(uidStart,uidEnd)
        #print(f"{totalUsers[randomUser-1].creation_date}   ,   {totalUsers[randomUser-1].last_access_date}")
        startTime = random_date(totalUsers[randomUser-1].creation_date,totalUsers[randomUser-1].last_access_date)
        #print(f"{startTime}   ,   {totalUsers[randomUser - 1].last_access_date}")
        endTime = random_date(startTime,totalUsers[randomUser-1].last_access_date)

        startPage = random.randint(1,int(totalBooks[randomBook-1].pages))
        endPage = random.randint(startPage, int(totalBooks[randomBook - 1].pages))
        readingSesh = Reading_Session(random.randint(0,23),randomUser ,randomBook,startTime,endTime,startPage,endPage)
        readingSession.append(readingSesh)
    return readingSession

totalReadingSession = createReadingSessions(800)
print("ReadingSessions done")


"""             Friend          """
from src.Modules.Friendship import Friendship
def createfriendShips(amount):
    friendShips = []
    uidStart = 1
    uidEnd = len(totalUsers)

    while (len(friendShips) < amount):
        randomUser1 = random.randint(uidStart, uidEnd)
        randomUser2 = random.randint(uidStart, uidEnd)
        newestDate=None
        while(randomUser2 == randomUser1):
            randomUser2 = random.randint(uidStart, uidEnd)
        #print("aeeeae\n\n\n\n\n\n\n")
        if(totalUsers[randomUser1-1].creation_date>=totalUsers[randomUser2-1].creation_date):
            newestDate = totalUsers[randomUser1-1].creation_date
        else:
            newestDate = totalUsers[randomUser2-1].creation_date
        newFriend = Friendship(randomUser1,randomUser2,random_date(newestDate,datetime.datetime.now()))
        if not (friendContains(friendShips,newFriend)):

            friendShips.append(newFriend)



    return friendShips

def friendContains(list,object:Friendship):

    for items in list:
        if object.getIds() == items.getIds():

            return True
    return False
totalFriends = createfriendShips(900)
print("Friends done")
""""Collections"""

from src.Modules.Collection import Collection
from src.Modules.Contains import Contains
import requests
def getRandomWords():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

    response = requests.get(word_site)
    WORDS = response.content.splitlines()
    return WORDS
def getCollections(amount):
    contains = []
    collections=[]
    uidStart = 1
    uidEnd = len(totalUsers)
    bidStart = 1
    bidEnd = len(totalBooks)
    count = 1
    containsAmount = 0
    while (len(collections) < amount):
        randomUser = random.randint(uidStart, uidEnd)
        newCollection = Collection(count,randomUser, getRandomWords())
        if not (objectContains(collections, newCollection)):
            collections.append(newCollection)
        containsAmount+=random.randint(0,10)
        print(f"{len(contains)}    ,    {len(collections)}")
        while (len(contains) < containsAmount):
            randomBid = random.randint(bidStart, bidEnd)
            newContain = Contains(count,randomBid)
            if not objectContains(contains,newContain):
                #print(objectContains(contains,newContain))
                contains.append(newContain)

        count +=1
    return collections,contains

def objectContains(list,objectToTest):
    for items in list:
        if objectToTest.getIds() == items.getIds():
            return True
    return False
totalCollections,totalContains = getCollections(50)
print("Collections/Contains done")
with open("Contains.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalContains)
with open("User.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalUsers)
with open("Book.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalBooks)
with open("Friend.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalFriends)
with open("Collection.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalCollections)
with open("ReadingSessions.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalReadingSession)
with open("Rating.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(totalRatings)




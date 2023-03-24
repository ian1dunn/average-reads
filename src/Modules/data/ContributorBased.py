import random
import csv
from  src.DataCreation.PremadeData import FIRST_NAMES, LAST_NAMES
def getBookGenres():
    bidStart = 1
    bidEnd=211
    genreStart=1
    genreEnd=24
    genrePairing=[]
    for i in range(bidStart,bidEnd+1):
        for j in range(1,random.randint(genreStart,genreEnd)):
            currentGenre = random.randint(genreStart,genreEnd)
            genrePairing.append([i,currentGenre])
            print(f"{i}   ,   {currentGenre}")
    return genrePairing
#getIds = getBookGenres()
#
#with open("./GenreBookAlex.csv", "w") as stream:
#    writer = csv.writer(stream)
#    writer.writerows(getIds)



def random_name():
    return random.choice(FIRST_NAMES)+" "+ random.choice(LAST_NAMES)
def createContributors():
    authors = []
    editors = []
    publishers = []
    contributor = []
    usedIDs = []
    bidStart = 1
    bidEnd = 211
    booksWithAuthors = []
    booksWithPublishers = []
    count=1
    while(len(authors)<bidEnd or len(editors)<bidEnd or len(publishers)<bidEnd or not len(booksWithPublishers)  == 210 or not len(booksWithAuthors)  == 210  ):
        contributor.append( [count,random_name()])
        randomJob = random.randint(0,100)
        randomBook = random.randint(bidStart,bidEnd)
        if randomJob<33:
            authors.append([count,randomBook])
            if(randomBook not in booksWithAuthors):
                booksWithAuthors.append(randomBook)
        elif randomJob>66:
            editors.append([count,randomBook])
        else:
            publishers.append([count,randomBook])
            if (randomBook not in booksWithPublishers):
                booksWithPublishers.append(randomBook)
        count+=1
    return contributor,authors,editors,publishers

contributor,authors,editors,publishers = createContributors()

with open("Contributors.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(contributor)
with open("authors.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(authors)
with open("editors.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(editors)
with open("publishers.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(publishers)

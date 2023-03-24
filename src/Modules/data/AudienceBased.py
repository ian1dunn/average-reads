import random
import csv
import pandas as pd
def getAudience(amount):
    bidStart = 1
    bidEnd = 211
    genreStart = 1
    genreEnd = 24
    audiences = []
    appealToGenres = []
    appealToBooks = []
    count = 1
    for i in range(amount):
        randomFirst = random.randint(0, 100)
        randomLast = random.randint(randomFirst, 125)
        targetString = f"Age Group: {randomFirst} - {randomLast}"
        while([targetString] in audiences):
            randomFirst = random.randint(0,100)
            randomLast = random.randint(randomFirst, 125)
            targetString = f"Age Group: {randomFirst} - {randomLast}"
        audiences.append([targetString])
        for j in range(random.randint(2,genreEnd)):
            appealToGenres.append([count,random.randint(1,genreEnd)])
        for k in range(random.randint(bidStart,bidEnd)):
            appealToBooks.append([count,random.randint(bidStart,bidEnd)])
        count += 1
    return audiences,appealToGenres,appealToBooks

a,b,c = getAudience(300)
with open("audiences.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(a)

df = pd.read_csv('audiences.csv')
df.to_csv('audiences.csv', index=False)


with open("appealtoGenre.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(b)
with open("appealtoBook.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(c)
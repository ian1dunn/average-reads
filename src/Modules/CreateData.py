import csv
from Book import *
from User import *
from Reading_Session import *
from src.Modules.BookGenres import BookGenres
from src.Modules.AppealToBook import AppealToBook
from src.Modules.AppealToGenre import AppealToGenre
from src.Modules.Audience import Audience
from src.Modules.Author import Author
from src.Modules.BookModel import BookModel
from src.Modules.Collection import Collection
from src.Modules.Contains import Contains
from src.Modules.Contributor import Contributor
from src.Modules.CoverType import CoverType
from src.Modules.Editor import Editor
from src.Modules.Friendship import Friendship
from src.Modules.Genre import Genre
from src.Modules.Publisher import Publisher
from src.Modules.Rating import Rating


if __name__ == '__main__':

    creationAmounts = 10000
    for i in [User,Reading_Session,Collection,Book]:
        listTmp = []
        for j in range(creationAmounts):
            listTmp.append(i.generate_random(ID.getRandom(0,creationAmounts)))
        with open("./data/"+(str(i.__name__)+".csv"), "w") as stream:
            writer = csv.writer(stream)
            writer.writerows(listTmp)
    for i in [AppealToBook,AppealToGenre,Audience,Author,BookGenres,BookModel,Contains,Contributor,CoverType,Editor,Friendship,Genre,Publisher,Rating]:
        listTmp = []
        for j in range(creationAmounts):
            listTmp.append(i.generate_random())
        with open("./data/"+(str(i.__name__)+".csv"), "w") as stream:
            writer = csv.writer(stream)
            writer.writerows(listTmp)



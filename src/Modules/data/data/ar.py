import random

import requests
import csv

def getRandomWords():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

    response = requests.get(word_site)
    WORDS = response.content.splitlines()
    return WORDS
words = getRandomWords()
def getWord():
    length = random.randint(1,5)
    word=""
    for i in range(length):
        word+=str(words[random.randint(0,len(words))]).replace("b'","").replace("'","")+" "
    return word[:len(word)-1]

collection = []
with open("C:\\Users\\Alexb\\PycharmProjects\\average-reads2\\src\\Modules\\data\\data\\CollectionAlex.csv", 'r') as f:
    csv_reader = csv.reader(f)

    for row in csv_reader:
        if(len(row)==0):
            continue
        newRow = row
        newRow[2] = getWord()
        collection.append(newRow)
with open("./CollectionAlexer.csv", "w") as stream:
    writer = csv.writer(stream)
    writer.writerows(collection)

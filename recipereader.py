import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
import spacy
nlp = spacy.load("en_core_web_sm")
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 
  
htmldata = getdata("https://www.allrecipes.com/recipe/8493351/grain-free-broccoli-fritters/") 
soup = BeautifulSoup(htmldata, 'html.parser') 
data = '' 


body = soup.find_all("p")
title = soup.find_all("h1")
title = title[0]
title = str(title)
newtitle = ""
counter=0
flag = False

while counter<len(title):
    if title[counter]=="<":
        flag = True
    if title[counter]==">":
        flag = False
    else:
        if flag == False:
            newtitle+=title[counter]
    counter+=1


ingredients = []
steps = []
print(" ")
print(newtitle)
print(" ")
print("Ingredients:")

for data in body:
    origstring = data.get_text()
    thestring = origstring[0]
    if thestring.__contains__("1") or thestring.__contains__("2") or thestring.__contains__("3") or thestring.__contains__("4") or thestring.__contains__("5") or thestring.__contains__("6") or thestring.__contains__("7") or thestring.__contains__("8") or thestring.__contains__("9") or thestring.__contains__("½") or thestring.__contains__("¼"):
        ingredients.append(origstring)
    else:
        splitstring = origstring.split()
        text = splitstring[0]
        doc = nlp(text)
        #print(text, doc[0].tag_)
        if doc[0].tag_ == 'VB' or doc[0].tag_ == 'NN' or doc[0].tag_ == 'NNP':
            steps.append(origstring)

for ingredient in ingredients:
    print(ingredient)

print(" ")
print("Directions:")

for step in steps:
    print(step)
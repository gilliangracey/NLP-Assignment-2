import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
import spacy
from fractions import Fraction
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

print(ingredients) 

def ingredient_info(ingredients):
    ingredient_dict = {}
    units = ['cup', 'cups', 'ml', 'mls', 'liters', 'L', 'ounces', 'oz', 'lb', 'lbs', 'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp']
    # if quant is 3 1/2, is that 1 or 2 elements?
    for ingredient in ingredients:
        split_str = ingredient.lower().split()
        quant = split_str[0]
        i = 1
        try:
            curr_quant = (float(split_str[1]))
            quant = split_str[0:2]
            i = 2
        except:
            if split_str[1] == 'or':
                quant = split_str[0:3]
                i = 3
            if split_str[1].__contains__('/'):
                quant = split_str[0:2]
                i = 2
        unit = ''
        # account for words between quant & units
        while split_str[i] in units: # or just use if
            if unit == '':
                unit = unit + split_str[i]
            else:
                unit = unit + ' ' + split_str[i]
            i = i + 1
        ingredient = ''
        looking_for_prep = False
        prep = ''
        while i < len(split_str):
            if split_str[i] == 'of' or split_str[i] == 'or':
                i = i + 1
            elif looking_for_prep:
                if prep == '':
                    prep = prep + split_str[i]
                else:
                    prep = prep + ' ' + split_str[i]
                i = i + 1
            elif split_str[i][len(split_str[i])-1] == ',':
                if ingredient == '':
                    ingredient = ingredient + split_str[i][0:len(split_str[i])-1]
                else:
                    ingredient = ingredient + ' ' + split_str[i][0:len(split_str[i])-1]
                i = i + 1
                looking_for_prep = True
            else:
                if ingredient == '':
                    ingredient = ingredient + split_str[i]
                else:
                    ingredient = ingredient + ' ' + split_str[i]
                i = i + 1
        ingredient_dict[ingredient] = [quant, unit, prep]
    return ingredient_dict

#def ingredient_parser(question): # if question contains "how many" or "how much"
print(ingredient_info(ingredients))

# questions
'''
store quantity as str or number? - make conversion helper function in case people want to double or half recipe
better way to identify units?
better way to build ingredients/units/preparation (store them as tuple of current start & end index?) - start as [0,0], instead of adding word just increment 
    2nd index & grab at the end
    - would still have to check if start index is 0 (like checking if str == '') to know that 1st index should become i
how to handle "plus more for garnish"? - parse for "plus" but how do we account for this in the quantities
what if preparation comes before food, like "minced garlic"? does it matter? - check if it's in past tense, check if words end in 'ed' 
'''
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
        prep_before = False
        prep = ''
        while i < len(split_str):
            if split_str[i] == 'of' or split_str[i] == 'or':
                i = i + 1
            elif looking_for_prep:
                if prep == '':
                    prep = split_str[i]
                else:
                    if prep_before:
                        prep = prep + ', ' + split_str[i]
                        prep_before = False
                    else:
                        prep = prep + ' ' + split_str[i]
                i = i + 1
            elif split_str[i][len(split_str[i])-1] == ',':
                if ingredient == '':
                    ingredient = split_str[i][0:len(split_str[i])-1]
                else:
                    ingredient = ingredient + ' ' + split_str[i][0:len(split_str[i])-1]
                i = i + 1
                looking_for_prep = True
            elif split_str[i][len(split_str[i])-2:len(split_str[i])] == 'ed' and nlp(split_str[i])[0].pos_ == 'VERB':
                if prep_before:
                    prep = prep + ', ' + split_str[i]
                else:
                    prep = split_str[i]
                prep_before = True
                i = i + 1
            else:
                if ingredient == '':
                    ingredient = split_str[i]
                else:
                    ingredient = ingredient + ' ' + split_str[i]
                i = i + 1
        ingredient_dict[ingredient] = [quant, unit, prep]
    return ingredient_dict

def ingredient_questions(question):
    question = question.lower()
    ingredient_dict = ingredient_info(ingredients)
    quant = False
    if question.__contains__("how much"):
        quant = True
        kw = "how much"
    if question.__contains__("how many"):
        quant = True
        kw = "how many"
    if quant:
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(ingredient + 's') or (question.__contains__(ingredient[0:len(ingredient-1)]) and ingredient[len(ingredient) == 's']):
                lst = ingredient_dict[ingredient]
                response = lst[0] + ' ' + lst[1]
                return response
        for ingredient in ingredient_dict:
            if len(ingredient.split()) == 2:
                if question.__contains__(ingredient.split()[0]):
                    # if word is in multiple ingredients, see what matches (aka if question is "how many", unit should be '')
                    lst = ingredient_dict[ingredient]
                    if kw == "how many":
                        if lst[1] == '':
                            response = lst[0] + ' ' + lst[1]
                    elif kw == "how much":
                        if lst[1] != '':
                            response = lst[0] + ' ' + lst[1]
                    return response  
                if question.__contains__(ingredient.split()[1]):
                    lst = ingredient_dict[ingredient]
                    if kw == "how many":
                        if lst[1] == '':
                            response = lst[0] + ' ' + lst[1]
                    elif kw == "how much":
                        if lst[1] != '':
                            response = lst[0] + ' ' + lst[1]
                    return response
    if question.__contains__("prep"):
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(ingredient + 's') or (question.__contains__(ingredient[0:len(ingredient-1)]) and ingredient[len(ingredient) == 's']):
                lst = ingredient_dict[ingredient]
                response = lst[3]
                return response
        for ingredient in ingredient_dict:
            if len(ingredient.split()) == 2:
                if question.__contains__(ingredient.split()[0]):
                    # if word is in multiple ingredients, see what matches (aka if question is "how many", unit should be '')
                    lst = ingredient_dict[ingredient]
                    response = lst[3]
                    return response  
                if question.__contains__(ingredient.split()[1]):
                    lst = ingredient_dict[ingredient]
                    response = lst[3]
                    return response
    elif question.__contains__("double") or question.__contains__("doubled"):
        kw = "factor"
        factor = 2
    elif question.__contains__("triple") or question.__contains__("tripled"):
        kw = "factor"
        factor = 3
    if kw == "factor":
        find_ingr = []
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient):
                find_ingr = find_ingr.append(ingredient)
        if len(find_ingr) == 0:
            for ingredient in ingredient_dict:
                lst = ingredient_dict[ingredient]
                quantity = multiply(lst[0],factor)
                # checks for whether anything is empty to ensure structure of sentence is correct
                print(quantity + lst[1] + ingredient + ', ' + lst[2])
        else:
            for ingredient in find_ingr:
                lst = ingredient_dict[ingredient]
                quantity = multiply(lst[0],factor)
                # checks for whether anything is empty to ensure structure of sentence is correct
                print(quantity + lst[1] + ingredient + ', ' + lst[2])                


def multiply(num,factor):
    num = num.split()
    if num.__contains__('or'):
        for i in range(len(num)):
            digit = num[i]
            if digit != 'or':
                try:
                    converted = int(digit)
                    mult = converted*factor
                    num[i] = str(mult)
                except:
                    try:
                        converted = float(digit)
                        mult = converted*factor
                        if str(mult)[len(str(mult))-2:len(str(mult))] == '.0':
                            num[i] = str(mult)[0:len(str(mult))-2]
                        else:
                            num[i] = str(mult)
                    except:
                        if digit.__contains__('/'):
                            middle_index = digit.index('/')
                            dividend = int(digit[0:middle_index])
                            divisor = int(digit[middle_index+1:len(digit)])
                            quotient = factor*dividend/divisor
                            if str(quotient)[len(str(quotient))-2:len(str(quotient))] == '.0':
                                num[i] = str(quotient)[0:len(str(quotient))-2]
                            else:
                                num[i] = str(quotient)                            
                        else:
                            num[i] = digit
        return ' '.join(num)
    sum = 0
    for digit in num:
        try:
            converted = int(digit)
            mult = converted*factor
            sum = sum + mult
        except:
            try:
                converted = float(digit)
                mult = converted*factor
                sum = sum + mult 
            except:
                if digit.__contains__('/'):
                    middle_index = digit.index('/')
                    dividend = int(digit[0:middle_index])
                    divisor = int(digit[middle_index+1:len(digit)])
                    sum = sum + factor*dividend/divisor 
                else:
                    if sum == 0:
                        sum = digit
                    else:
                        sum = str(sum) + digit
    if len(str(sum).split()) > 1:
        return ' '.join(str(sum))
    else:
        if len(str(sum)) > 2 and str(sum)[len(str(sum))-2:len(str(sum))] == '.0':
            return str(sum)[0:len(str(sum))-2]
        return str(sum)

# check if end of str == .0, then convert to int, then str
print(multiply("3/3 or ½",2))              
#print(ingredient_questions("If I double the recipe, how many eggs do I need?"))
#def ingredient_parser(question): # if question contains "how many" or "how much"
#print(ingredient_info(ingredients))
# questions
'''
store quantity as str or number? - make conversion helper function in case people want to double or half recipe
better way to identify units?
better way to build ingredients/units/preparation (store them as tuple of current start & end index?) - start as [0,0], instead of adding word just increment 
    2nd index & grab at the end
    - would still have to check if start index is 0 (like checking if str == '') to know that 1st index should become i
how to handle "plus more for garnish"? - parse for "plus" but how do we account for this in the quantities
what if preparation comes before food, like "minced garlic"? does it matter? - check if it's in past tense, check if words end in 'ed' 
can we ask user clarifying questions? like "which cheese?" 
'''
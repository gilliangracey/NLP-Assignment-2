import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
import spacy
import numerizer
nlp = spacy.load("en_core_web_sm")
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 
  
htmldata = getdata('https://www.allrecipes.com/recipe/222589/simple-deviled-eggs/') 
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

for data in body:
    origstring = data.get_text()
    thestring = origstring[0]
    if thestring.__contains__("1") or thestring.__contains__("2") or thestring.__contains__("3") or thestring.__contains__("4") or thestring.__contains__("5") or thestring.__contains__("6") or thestring.__contains__("7") or thestring.__contains__("8") or thestring.__contains__("9") or thestring.__contains__("½") or thestring.__contains__("¼"):
        ingredients.append(origstring)
    else:
        splitstring = origstring.split()
        text = splitstring[0]
        doc = nlp(text)
        if doc[0].tag_ == 'VB' or doc[0].tag_ == 'NN' or doc[0].tag_ == 'NNP':
            origstring = origstring.split(".")
            for element in origstring:
                if element != "\n":
                    element = element.strip()
                    steps.append(element)
print("Ingredients:")

for ingredient in ingredients:
    print(ingredient)

print(" ")
print("Directions:")

counter=1
for step in steps:
    stepcounter = "Step "
    stepcounter += str(counter)
    stepcounter+=":"
    print(stepcounter)
    print(step)
    counter+=1

print(" ")


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
            if split_str[i] == 'of':# or split_str[i] == 'or':
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
            #elif split_str[i][len(split_str[i])-2:len(split_str[i])] == 'ed' and (nlp(split_str[i])[0].pos_ == 'VBN' or nlp(split_str[i])[0].pos_ == 'VBD'): # or just VERB
            elif nlp(split_str[i])[0].tag_ == 'VBN' or nlp(split_str[i])[0].tag_ == 'VBD': # or just VERB
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

def plural(ingredient):
    if len(ingredient.split()) == 0:
        if nlp(ingredient)[0].tag_ == 'NN': # singular
            return ingredient+'s'
        elif nlp(ingredient)[0].tag_ == 'NNS' or ingredient[len(ingredient)-1] == 's': # plural
            return ingredient[0:len(ingredient)-1]  
    else:      
        lastword = ingredient.split()[len(ingredient.split())-1]
        if nlp(lastword)[0].tag_ == 'NN': # singular
            return ingredient+'s'
        elif nlp(lastword)[0].tag_ == 'NNS' or lastword[len(lastword)-1] == 's': # plural
            return ingredient[0:len(ingredient)-1]
    return ingredient

def ingredient_questions(question):
    question = question.lower()
    ingredient_dict = ingredient_info(ingredients)
    quant = False
    if question.__contains__("double"):
        kw = "factor"
        factor = 2
    elif question.__contains__("triple"):
        kw = "factor"
        factor = 3
    elif question.__contains__("how much"):
        quant = True
        kw = "how much"
    elif question.__contains__("how many"):
        quant = True
        kw = "how many"
    elif question.__contains__("prep"):
        kw = "prep"
    if quant:
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                lst = ingredient_dict[ingredient]
                t1 = ' '
                t2 = ' of '
                if lst[1] == '':
                    t1 = ''
                    t2 = ' '
                print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                return
                '''
                if kw == "how many":
                    if lst[1] == '':
                        print("You need " + lst[0] + ' ' + ingredient)
                        return
                elif kw == "how much":
                    if lst[1] != '':
                        print("You need " + lst[0] + ' ' + lst[1] + ' of ' + ingredient)
                        return
                '''
        for ingredient in ingredient_dict:
            if len(ingredient.split()) > 1:
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN':
                    # if word is in multiple ingredients, see what matches (aka if question is "how many", unit should be '')
                        lst = ingredient_dict[ingredient]
                        t1 = ' '
                        t2 = ' of '
                        if lst[1] == '':
                            t1 = ''
                            t2 = ' '
                        print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                        return
                        '''
                        if kw == "how many":
                            if lst[1] == '':
                                print("You need " + lst[0] + ' ' + ingredient)
                                return
                        elif kw == "how much":
                            if lst[1] != '':
                                print("You need " + lst[0] + ' ' + lst[1] + ' of ' + ingredient)
                                return
                        '''
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])):
                    lst = ingredient_dict[ingredient]
                    t1 = ' '
                    t2 = ' of '
                    if lst[1] == '':
                        t1 = ''
                        t2 = ' '
                    print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                    return
                    '''
                    if kw == "how many":
                        if lst[1] == '':
                            print("You need " + lst[0] + ' ' + ingredient)
                            return
                    elif kw == "how much":
                        if lst[1] != '':
                            print("You need " + lst[0] + ' ' + lst[1] + ' of ' + ingredient)
                            return         
                    '''       
    if kw == "prep":
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                lst = ingredient_dict[ingredient]
                print("You should " + lst[2][0:len(lst[2])-2] + ' the ' + ingredient)
                return
        for ingredient in ingredient_dict: # see what happens in for loops are combined
            if len(ingredient.split()) > 1:
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN': # permit VERB too
                    # if word is in multiple ingredients, see what matches
                    # look for ingredient in steps
                        lst = ingredient_dict[ingredient]
                        print("You should " + lst[2][0:len(lst[2])-2] + ' the ' + ingredient)
                        return
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])):
                    lst = ingredient_dict[ingredient]
                    print("You should " + lst[2][0:len(lst[2])-2] + ' the ' + ingredient)
    if kw == "factor":
        find_ingr = []
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                find_ingr.append(ingredient)
            elif len(ingredient.split()) > 1:
                found = 0
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN':
                    # if word is in multiple ingredients, see what matches (aka if question is "how many", unit should be '')
                    # look for ingredient in steps
                        find_ingr.append(ingredient)
                        found = 1
                        break
                if not found and question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])):
                    find_ingr.append(ingredient)
        if len(find_ingr) == 0:
            response = []
            for ingredient in ingredient_dict:
                lst = ingredient_dict[ingredient]
                quantity = multiply(lst[0],factor)
                unit = lst[1]
                prep = lst[2]
                t1 = ' '
                t2 = ' '
                t3 = ', '
                if unit == '':
                    t1 = ''
                    if quantity != '1' and nlp(ingredient[len(ingredient)-1])[0].tag_ == 'NN':#ingredient[len(ingredient)-1] != 's':
                        ingredient = ingredient + 's'
                else:
                    if quantity != '1' and nlp(unit)[0].tag_ == 'NN':#unit[len(unit)-1] != 's':
                        unit = unit + 's'
                if prep == '':
                    t3 = ''
                curr_response = quantity + t1 + unit + t2 + ingredient + t3 + prep
                response.append(curr_response)
            for a_response in response:
                print(a_response)
            return
        else:
            response = []
            for ingredient in find_ingr:
                lst = ingredient_dict[ingredient]
                quantity = multiply(lst[0],factor)
                unit = lst[1]
                t1 = ' '
                t2 = ' '
                if unit == '':
                    t1 = ''
                    if quantity != '1' and nlp(ingredient[len(ingredient)-1])[0].tag_ == 'NN':#ingredient[len(ingredient)-1] != 's':
                        ingredient = ingredient + 's'
                else:
                    if quantity != '1' and nlp(unit)[0].tag_ == 'NN':#unit[len(unit)-1] != 's':
                        unit = unit + 's'
                print('You need ' + quantity + t1 + unit + t2 + ingredient)     
            return        

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

print(steps)

ansArr = ['Nothing','Step','Ingredient']
stepI = 0
print("step 1:", steps[0])
while(True):

    preAns = ansArr[0]
    inpt = input("Enter text: ")
    doc = nlp(inpt)
    numDict = doc._.numerize()
    
    for k,v in numDict.items():
        if int(v) < len(steps) and "step" in inpt.lower():
            print(steps[int(v) - 1])
            stepI = int(v) - 1

    if "next" in inpt.lower():
        if stepI < len(steps) - 1:
            stepI += 1
            print ("step", (stepI + 1), ": ", steps[stepI])
        else:
            print("There are no more steps!")

    if "back" in inpt.lower() or "prev" in inpt.lower():
        if stepI >= 1:
            stepI -= 1
            print ("step", (stepI + 1), ": ", steps[stepI])
        else:
            print("There are no steps before this!")


# check if end of str == .0, then convert to int, then str
#print(multiply("3/3 or ½",2)) 
#print(nlp("chives")[0].pos_) 
#ingredient_questions("how much chive do i add")
ingredient_questions("how much paprika")
ingredient_questions("how much cheese")
ingredient_questions("how many carrots")
#print(get_plural(ingredient_info(ingredients)))
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
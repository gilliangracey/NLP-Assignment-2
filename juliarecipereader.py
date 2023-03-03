import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
import spacy
import numerizer
from fractions import Fraction
nlp = spacy.load("en_core_web_sm")
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 


#htmldata = getdata("https://www.allrecipes.com/recipe/24771/basic-mashed-potatoes/")
htmldata = getdata("https://www.allrecipes.com/recipe/8493351/grain-free-broccoli-fritters/") 
#htmldata = getdata("https://www.allrecipes.com/recipe/79543/fried-rice-restaurant-style/")
#htmldata = getdata("https://www.allrecipes.com/recipe/60923/portobello-mushroom-stroganoff/")
#htmldata = getdata("https://www.foodnetwork.com/recipes/ina-garten/meat-loaf-recipe-1921718")
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
    units = ['cup', 'cups', 'ml', 'mls', 'liters', 'L', 'ounces', 'oz', 'lb', 'lbs', 'pounds', 'pound', 'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp']
    for ingredient in ingredients:
        split_str = ingredient.lower().split()
        quant = split_str[0]
        i = 1
        try:
            curr_quant = float(split_str[1])
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
        while split_str[i] in units:
            if unit == '':
                unit = unit + split_str[i]
            else:
                unit = unit + ' ' + split_str[i]
            i = i + 1
        ingredient = ''
        looking_for_end = False
        prep = ''
        while i < len(split_str):
            if split_str[i] == 'of':
                i = i + 1
            elif looking_for_end:
                if nlp(split_str[i])[0].tag_ == 'VBN' or nlp(split_str[i])[0].tag_ == 'VBD':
                    word = split_str[i]
                    if nlp(word[len(word)-1])[0].pos_ == 'PUNCT':
                        word = word[0:len(word)-1]
                    if prep == '':
                        prep = word
                    else:
                        prep = prep + ' and ' + word
                    i = i + 1
                else:
                    i = i + 1
            elif split_str[i][len(split_str[i])-1] == ',':
                if ingredient == '':
                    ingredient = split_str[i][0:len(split_str[i])-1]
                else:
                    ingredient = ingredient + ' ' + split_str[i][0:len(split_str[i])-1]
                i = i + 1
                looking_for_end = True
            elif nlp(split_str[i])[0].tag_ == 'VBN' or nlp(split_str[i])[0].tag_ == 'VBD':
                if prep == '':
                    prep = split_str[i]
                else:
                    prep = prep + ' and ' + split_str[i]
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

def ingredient_questions(question,curr_ingr):
    units = ['cup', 'cups', 'ml', 'mls', 'liters', 'L', 'ounces', 'oz', 'lb', 'lbs', 'pounds', 'pound', 'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp']
    question = question.lower()
    ingredient_dict = ingredient_info(ingredients)
    quant = False 
    kw = ''
    if question.__contains__("double"):
        kw = "factor"
        factor = 2
    elif question.__contains__("triple"):
        kw = "factor"
        factor = 3
    elif question.__contains__("amount"):
        quant = True
    elif question.__contains__("how much"):
        quant = True
        kw = "how much"
    elif question.__contains__("how many"):
        quant = True
        kw = "how many"
    elif question.__contains__("prep"):
        kw = "prep"
    if quant:
        split_q = question.split()
        if kw == "how many":
            index = split_q.index("many")  
            if len(split_q) < 3:
                if curr_ingr == '':
                    print("Please specify the ingredient")
                    return ''
                find_kw = curr_ingr
                for ingredient in ingredient_dict:
                    if ingredient == find_kw:
                        lst = ingredient_dict[ingredient]
                        t1 = ' '
                        t2 = ' of '
                        if lst[1] == '':
                            t1 = ''
                            t2 = ' '
                        curr_ingr = ingredient
                        print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                        return curr_ingr                     
            find_ingr = split_q[index+1]
            if find_ingr in units:
                if split_q[index+2] == 'of':
                    find_ingr = split_q[index+3]
                else:
                    find_ingr = split_q[index+2]
        if kw == "how much":
            index = split_q.index("much")
            if len(split_q) < 3:
                if curr_ingr == '':
                    print("Please specify the ingredient")
                    return ''
                find_kw = curr_ingr
                for ingredient in ingredient_dict:
                    if ingredient == find_kw:
                        lst = ingredient_dict[ingredient]
                        t1 = ' '
                        t2 = ' of '
                        if lst[1] == '':
                            t1 = ''
                            t2 = ' '
                        curr_ingr = ingredient
                        print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                        return curr_ingr
            find_ingr = split_q[index+1]
            if find_ingr == 'of':
                find_ingr = split_q[index+2]
        counter = 0
        mult_ingrs = []
        if nlp(find_ingr)[0].pos_ == 'NOUN' or nlp(find_ingr)[0].pos_ == 'PROPN': # check if word after kw is ingredient name 
            for ingredient in ingredient_dict:
                if ingredient.__contains__(find_ingr):
                    counter = counter + 1
                    mult_ingrs.append(ingredient)
            for ingredient in mult_ingrs:
                lst = ingredient_dict[ingredient]
                t1 = ' '
                t2 = ' of '
                if lst[1] == '':
                    t1 = ''
                    t2 = ' '
                curr_ingr = ingredient
                print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
            if counter != 0:
                return curr_ingr
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)): # check if question contains entire ingredient name
                lst = ingredient_dict[ingredient]
                t1 = ' '
                t2 = ' of '
                if lst[1] == '':
                    t1 = ''
                    t2 = ' '
                curr_ingr = ingredient
                print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                return curr_ingr
        for ingredient in ingredient_dict: 
            if len(ingredient.split()) > 1:
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN': # check if question contains noun part of ingredient name
                        lst = ingredient_dict[ingredient]
                        t1 = ' '
                        t2 = ' of '
                        if lst[1] == '':
                            t1 = ''
                            t2 = ' '
                        curr_ingr = ingredient
                        print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                        return curr_ingr
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])): # check if question contains plural version of noun part
                    lst = ingredient_dict[ingredient]
                    t1 = ' '
                    t2 = ' of '
                    if lst[1] == '':
                        t1 = ''
                        t2 = ' '
                    curr_ingr = ingredient
                    print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                    return curr_ingr
        if curr_ingr == '':
            print("Please specify the ingredient")
            return ''
        find_kw = curr_ingr
        for ingredient in ingredient_dict:
            if ingredient == find_kw:
                lst = ingredient_dict[ingredient]
                t1 = ' '
                t2 = ' of '
                if lst[1] == '':
                    t1 = ''
                    t2 = ' '
                curr_ingr = ingredient
                print("You need " + lst[0] + t1 + lst[1] + t2 + ingredient)
                return curr_ingr           
    if kw == "prep":
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                lst = ingredient_dict[ingredient]
                verbs = lst[2]
                if verbs == '':
                    curr_ingr = ingredient
                    print('No prep needs to be done')
                    return curr_ingr
                else:
                    curr_ingr = ingredient
                    print('The ' + ingredient + ' should be ' + verbs)
                    return curr_ingr
        for ingredient in ingredient_dict:
            if len(ingredient.split()) > 1:
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN': # permit VERB too
                        lst = ingredient_dict[ingredient]
                        verbs = lst[2]
                        if verbs == '':
                            curr_ingr = ingredient
                            print('No prep needs to be done')
                            return curr_ingr
                        else:
                            curr_ingr = ingredient
                            print('The ' + ingredient + ' should be ' + verbs)
                            return curr_ingr
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])):
                    lst = ingredient_dict[ingredient]
                    verbs = lst[2]
                    if verbs == '':
                        curr_ingr = ingredient
                        print('No prep needs to be done')
                        return curr_ingr
                    else:
                        curr_ingr = ingredient
                        print('The ' + ingredient + ' should be ' + verbs)
                        return curr_ingr
        if curr_ingr == '':
            print("Please specify the ingredient")
            return ''
        find_kw = curr_ingr
        for ingredient in ingredient_dict:
            if ingredient == find_kw:
                lst = ingredient_dict[ingredient]
                verbs = lst[2]
                if verbs == '':
                    curr_ingr = ingredient
                    print('No prep needs to be done')
                    return curr_ingr
                else:
                    curr_ingr = ingredient
                    print('The ' + ingredient + ' should be ' + verbs)
                    return curr_ingr     
    if kw == "factor":
        find_ingr = []
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                find_ingr.append(ingredient)
            elif len(ingredient.split()) > 1:
                found = 0
                for element in ingredient.split():
                    if question.__contains__(element) and nlp(element)[0].pos_ == 'NOUN':
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
            return ''
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
            return ''  
    return ''   

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


ansArr = ['Nothing','Step','Ingredient']
stepI = 0
print("step 1:", steps[0])
#global curr_ingr
curr_ingr = ''
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
            curr_ingr = ''
            print ("step", (stepI + 1), ": ", steps[stepI])
        else:
            print("There are no more steps!")

    if "back" in inpt.lower() or "prev" in inpt.lower():
        if stepI >= 1:
            stepI -= 1
            curr_ingr = ''
            print ("step", (stepI + 1), ": ", steps[stepI])
        else:
            print("There are no steps before this!")

    else:
        new_curr_ingr = ingredient_questions(inpt,curr_ingr)
        curr_ingr = new_curr_ingr

# check if end of str == .0, then convert to int, then str
#print(multiply("3/3 or ½",2)) 
#print(nlp("chives")[0].pos_) 
#print(ingredient_info(ingredients))
#ingredient_questions("how do i prepare the garlic")
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
import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
import spacy
import numerizer
from fractions import Fraction
from recipe_scrapers import scrape_me
nlp = spacy.load("en_core_web_sm")
  

# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 

htmldata = getdata('https://www.foodnetwork.com/recipes/ingredient-substitution-guide') 
soup = BeautifulSoup(htmldata, 'html.parser') 
data = '' 


body = soup.find_all("p")
body = body[2:77]
keys = []
replacements = []
replacementdict = {}
for data in body:
    data = data.text
    data = data.lower()
    data = data.split(":")
    data[-1] = data[-1][1:]
    if data[0].__contains__("("):
        data[0] = data[0].split("(")
        data[0] = data[0][0][:-1]
    keys.append(data[0])
    replacements.append(data[1])
    replacementdict[data[0]] = data[1]

replacementdict["flour"] = 'flour alternatives include chickpea flour, rice flour, almond flour, and buckwheat flour'


#htmldata = getdata("https://www.allrecipes.com/recipe/24771/basic-mashed-potatoes/")
#htmldata = getdata("https://www.allrecipes.com/recipe/8493351/grain-free-broccoli-fritters/") 
#htmldata = getdata("https://www.allrecipes.com/recipe/79543/fried-rice-restaurant-style/")
#htmldata = getdata("https://www.allrecipes.com/recipe/60923/portobello-mushroom-stroganoff/")
#htmldata = getdata("https://www.foodnetwork.com/recipes/ina-garten/meat-loaf-recipe-1921718")


def print_ingredients():
    print("Ingredients:")
    for ingredient in ingredients:
        print(ingredient)

def print_directions():
    print("Directions:")
    counter=1
    for step in steps:
        stepcounter = "Step "
        stepcounter += str(counter)
        stepcounter+=":"
        print(stepcounter)
        print(step)
        counter+=1


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

def has_kw(question):
    kw = ['time','how long','temperature','degrees','amount','how much','how many','prep']
    for w in kw:
        if question.__contains__(w):
            return True
    return False

def ingredient_questions(question,step,curr_ingr):
    units = ['cup', 'cups', 'ml', 'mls', 'liters', 'L', 'ounces', 'oz', 'lb', 'lbs', 'pounds', 'pound', 'teaspoon', 'teaspoons', 'tsp', 'tablespoon', 'tablespoons', 'tbsp']
    question = question.lower()
    step = step.lower()
    ingredient_dict = ingredient_info(ingredients)
    quant = False 
    time = False
    temp = False
    kw = ''
    elif question.__contains__("time") or question.__contains__("how long") or question.__contains__("minutes"):
        time = True
    elif question.__contains__("temperature") or question.__contains__("degrees"):
        temp = True
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
    if temp:
        unit = ''
        if step.split().__contains__("f") or step.split().__contains__("fahrenheit"):
            unit = "Fahrenheit"
        elif step.split().__contains__("c") or step.split().__contains__("celsius"):
            unit = "Celsius"
        for word in step.split():
            try:
                f = float(word)
                if int(word) > 50:
                    stri = word + ' degrees ' + unit
                    return ['',stri]
            except:
                continue
        return ['',"This step does not provide a temperature"]
    if time:
        hasmin = False
        if step.__contains__("for"):
            index = step.split().index("for") + 1
            time = "for"
            while index < len(step.split()):
                word = step.split()[index]
                time = time + ' ' + word
                index = index + 1
                if word[len(word)-1] == ',':
                    return ['',time[0:len(time)-1]]
                if word.__contains__('hour'):
                    if not step.__contains__('min'):
                        return ['',time]
                    else:
                        continue
                if word.__contains__('min'):
                    return ['',time]  
        elif step.__contains__("mins"):
            kw = "mins"
            hasmin = True
            try:
                index = step.split().index("mins") - 1
            except:
                if step.__contains__("mins,"):
                    index = step.split().index("mins,") - 1
                elif step.__contains__("mins."):
                    index = step.split().index("mins.") - 1
        elif step.__contains__("minutes"):
            kw = "minutes"
            hasmin = True
            try:
                index = step.split().index("minutes") - 1
            except:
                if step.__contains__("minutes,"):
                    index = step.split().index("minutes,") - 1
                elif step.__contains__("minutes."):
                    index = step.split().index("minutes.") - 1  
        elif step.__contains__("minute"):
            kw = "minute"
            hasmin = True
            try:
                index = step.split().index("minute") - 1
            except:
                if step.__contains__("minute,"):
                    index = step.split().index("minute,") - 1
                elif step.__contains__("minute."):
                    index = step.split().index("minute.") - 1 
        elif step.__contains__("min"):
            kw = "min"
            hasmin = True
            try:
                index = step.split().index("min") - 1
            except:
                if step.__contains__("min,"):
                    index = step.split().index("min,") - 1
                elif step.__contains__("min."):
                    index = step.split().index("min.") - 1 
        elif step.__contains__("hours"):
            kw = "hours"
            try:
                index = step.split().index("hours") - 1
            except:
                if step.__contains__("hours,"):
                    index = step.split().index("hours,") - 1
                elif step.__contains__("hours."):
                    index = step.split().index("hours.") - 1 
        elif step.__contains__("hour"):
            kw = "hour"
            try:
                index = step.split().index("hour") - 1
            except:
                if step.__contains__("hour,"):
                    index = step.split().index("hour,") - 1
                elif step.__contains__("hour."):
                    index = step.split().index("hour.") - 1 
        elif step.__contains__("until"):
            index = step.split().index("until") + 1
            total = 'Until'
            while index < len(step.split()):
                word = step.split()[index]
                if nlp(word[len(word)-1])[0].pos_ == 'PUNCT':
                    total = total + ' ' + word
                    return ['',total]
                total = total + ' ' + word
                index = index + 1
            return ['',total]
        else:
            return ['',"This step does not provide a time"]
        time = ''
        if step.__contains__("hours") and hasmin:
            timeindex = step.split().index("hours")
            time = str(step.split()[timeindex-1]) + " hours, "
        elif step.__contains__("hour") and hasmin:
            timeindex = step.split().index("hour")
            time = str(step.split()[timeindex-1]) + " hour, "
        while index > -1:
            try:
                num = step.split()[index]
                f = float(num)
                time = time + num + " " + kw
                index = index - 1
                break
            except:
                index = index - 1
        if step.split()[index] == 'or':
            time = step.split()[index-1] + ' or ' + time
        elif step.split()[index] == 'to':
            time = step.split()[index-1] + ' to ' + time
        return ['',time]  
    if quant:
        split_q = question.split()
        if kw == "how many":
            index = split_q.index("many")  
            if len(split_q) < 3:
                if curr_ingr == '':
                    return ['',"Please specify the ingredient"]
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
                        stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                        return [curr_ingr,stri]               
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
                    stri = "Please specify the ingredient"
                    return ['',stri]
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
                        stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                        return [curr_ingr,stri]
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
                return [curr_ingr,1]
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)): # check if question contains entire ingredient name
                lst = ingredient_dict[ingredient]
                t1 = ' '
                t2 = ' of '
                if lst[1] == '':
                    t1 = ''
                    t2 = ' '
                curr_ingr = ingredient
                stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                return [curr_ingr,stri]
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
                        stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                        return [curr_ingr,stri]
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])): # check if question contains plural version of noun part
                    lst = ingredient_dict[ingredient]
                    t1 = ' '
                    t2 = ' of '
                    if lst[1] == '':
                        t1 = ''
                        t2 = ' '
                    curr_ingr = ingredient
                    stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                    return [curr_ingr,stri]
        if curr_ingr == '':
            stri = "Please specify the ingredient"
            return ['',stri]
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
                stri = "You need " + lst[0] + t1 + lst[1] + t2 + ingredient
                return [curr_ingr,stri]        
    if kw == "prep":
        for ingredient in ingredient_dict:
            if question.__contains__(ingredient) or question.__contains__(plural(ingredient)):
                lst = ingredient_dict[ingredient]
                verbs = lst[2]
                if verbs == '':
                    curr_ingr = ingredient
                    stri = 'No prep needs to be done'
                    return [curr_ingr, stri]
                else:
                    curr_ingr = ingredient
                    stri = 'The ' + ingredient + ' should be ' + verbs
                    return [curr_ingr,stri]
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
                            stri = 'The ' + ingredient + ' should be ' + verbs
                            return [curr_ingr,stri]
                if question.__contains__(plural(ingredient.split()[len(ingredient.split())-1])):
                    lst = ingredient_dict[ingredient]
                    verbs = lst[2]
                    if verbs == '':
                        curr_ingr = ingredient
                        stri = 'No prep needs to be done'
                        return [curr_ingr, stri]
                    else:
                        curr_ingr = ingredient
                        stri = 'The ' + ingredient + ' should be ' + verbs
                        return [curr_ingr,stri]
        if curr_ingr == '':
            stri = "Please specify the ingredient"
            return ['',stri]
        find_kw = curr_ingr
        for ingredient in ingredient_dict:
            if ingredient == find_kw:
                lst = ingredient_dict[ingredient]
                verbs = lst[2]
                if verbs == '':
                    curr_ingr = ingredient
                    stri = 'No prep needs to be done'
                    return [curr_ingr, stri]
                else:
                    curr_ingr = ingredient
                    stri = 'The ' + ingredient + ' should be ' + verbs
                    return [curr_ingr,stri]    
    return ['','']   




print("My name is KitchenBot and I am here to help you understand the recipe you would like to make. \nAt any point, you may enter 'ingredients' to view the ingredients list or 'directions' to navigate the recipe's directions.")
url = input("Please enter the URL of a recipe: ")

scraper = scrape_me(url)
title = scraper.title()
ingredients = scraper.ingredients()
steps = scraper.instructions()
steps = steps.split('.')
counter = 0
while counter < len(steps):
    step = steps[counter]
    step = step.strip()
    steps[counter] = step
    counter+=1 


print("I see that you would like to make " + title[0:len(title)] + '.')
print("Right now, would you like to go through the ingredients or the directions?")

ansArr = ['Nothing','Step','Ingredient']
stepI = 0
curr_ingr = ''

while(True):

    preAns = ansArr[0]
    inpt = input("Enter text: ")

    doc = nlp(inpt)
    numDict = doc._.numerize()

    for k,v in numDict.items():
        if int(v) < len(steps) and "step" in inpt.lower():
            print("step " + v + ": " + steps[int(v) - 1])
            stepI = int(v) - 1

    if "ingredient" in inpt.lower():
        print_ingredients()

    if "directions" in inpt.lower():
        print("step 1:", steps[0])

    if "next" in inpt.lower():
        if stepI < len(steps) - 1:
            stepI += 1
            curr_ingr = ''
            print ("step", str(stepI + 1) + ":", steps[stepI])
        else:
            print("There are no more steps!")

    if "back" in inpt.lower() or "prev" in inpt.lower():
        if stepI >= 1:
            stepI -= 1
            curr_ingr = ''
            print ("step", str(stepI + 1) + ":", steps[stepI])
        else:
            print("There are no steps before this!")

    if "substitute" in inpt.lower() or "replace" in inpt.lower():
        newinpt = inpt.lower()
        newinpt = newinpt.split()
        flag = False
        for word in newinpt:
            if word in replacementdict:
                print("Substitute", word, "with:")
                print(replacementdict[word])
                flag = True
        if flag==False:
            print("No replacements were found")

    flag = 0
    if has_kw(inpt.lower()):
        output = ingredient_questions(inpt,steps[stepI],curr_ingr)
        if output[1] != None and output[1] != '' and output[1] != 1:
            print(output[1])
            flag = 1
        if output[1]:
            flag = 1
        curr_ingr = output[0]


#https://www.allrecipes.com/recipe/24771/basic-mashed-potatoes/
#https://www.allrecipes.com/recipe/8493351/grain-free-broccoli-fritters/
    if not flag:
        if ("how do i" in inpt.lower() or "how do you" in inpt.lower()) and "do that" not in inpt.lower():
            myUrl = "https://www.youtube.com/results?search_query="
            sentArr = inpt.split()
            for i in range(len(sentArr)):
                myUrl = myUrl + sentArr[i]
                if i != len(sentArr) - 1:
                    myUrl = myUrl + "+"
            print("This may help you!")
            print(myUrl)
        elif "how" in inpt.lower() or "how do i do that" in inpt.lower():
            myUrl = "https://www.youtube.com/results?search_query="
            stepArr = steps[stepI].split()
            for i in range(len(stepArr)):
                myUrl = myUrl + stepArr[i]
                if i != len(stepArr) - 1:
                    myUrl = myUrl + "+"
            print("This may help you!")
            print(myUrl)
        if "what is" in inpt.lower():
            myUrl = "https://www.google.com/search?q="
            sentArr = inpt.split()
            for i in range(len(sentArr)):
                myUrl = myUrl + sentArr[i]
                if i != len(sentArr) - 1:
                    myUrl = myUrl + "+"
            print("This may help you!")
            print(myUrl)

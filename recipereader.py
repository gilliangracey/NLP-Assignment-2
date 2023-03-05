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
    if len(data)>2:
        counter=1
        newvalue = ""
        while counter<len(data):
            newvalue+=data[counter]
            newvalue+=":"
            counter+=1
        newvalue = newvalue[:-1]
        data[1] = newvalue
    data[-1] = data[-1][1:]
    if data[0].__contains__("("):
        data[0] = data[0].split("(")
        data[0] = data[0][0][:-1]
    keys.append(data[0])
    replacements.append(data[1])
    replacementdict[data[0]] = data[1]

replacementdict["flour"] = 'flour alternatives include chickpea flour, rice flour, almond flour, and buckwheat flour'
replacementdict["cheese"] = "replace cheese with nutritional yeast or the following cheeses: Parmesan, pecorino, mozzarella, goat, brie, feta, Monterey Jack, cheddar, pepper jack, American, provolone"
replacementdict["pasta"] = "couscous, potatoes, egg noodles, zucchini noodles, spaghetti squash, eggplant"
replacementdict["rice"] = "barley, quinoa, cauliflower"
replacementdict["carrots"] = "potatoes, celery"
replacementdict["potatoes"] = "carrots, celery"
replacementdict["garlic"] = "onion"
replacementdict["onions"] = "shallots, leeks, scallions"
replacementdict["oil"] = "can be replaced with ghee, butter, or various other oils such as canola, avocado, olive, and coconut"
replacementdict["vegetarian"] = "meats may be replaced with other meats, veggie/bean patties, seitan, lentils, and tofu"
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


def has_kw(question):
    kw = ['time','how long','temperature','degrees','amount','how much','how many','prep','tool','utensil','done','know']
    if question.__contains__("use") and question.__contains__("what"):
        return True
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
    tool = False
    done = False
    kw = ''
    if question.__contains__("time") or question.__contains__("how long") or question.__contains__("minutes"):
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
    elif question.__contains__("tool") or question.__contains__("utensil") or (question.__contains__("use") and question.__contains__("what")):
        tool = True
    elif question.__contains__("done") or question.__contains__("know"):
        done = True
    if done:
        if step.__contains__("until"):
            index = step.split().index("until") + 1
            total = 'It is done when'
            while index < len(step.split()):
                word = step.split()[index]
                if word[len(word)-1] == ',':
                    return ['',total+ ' ' + word[0:len(word)-1]]
                total = total + ' ' + word
                index = index + 1
            return ['',total]
        '''
        elif step.__contains__("when"):
            index = step.split().index("when") + 1
            total = 'It is done when'
            while index < len(step.split()):
                word = step.split()[index]
                if word[len(word)-1] == ',':
                    return ['',total+ ' ' + word[0:len(word)-1]]
                total = total + ' ' + word
                index = index + 1
            return ['',total]
        '''
        return ['',"I'm not sure if your question applies to this step"]
    if tool:
        if step.__contains__("when"):
            index = step.split().index("when") + 1
            total = 'It is done when'
            while index < len(step.split()):
                word = step.split()[index]
                total = total + ' ' + word
                if word[len(word)-1] == ',':
                    return ['',total]
                index = index + 1
            return ['',total]
    if tool:
        if step.__contains__("use"):
            try:
                index = step.split().index("use") + 1
            except: 
                index = step.split().index("using") + 1
            total = 'You should use'
            while index < len(step.split()):
                word = step.split()[index]
                if word == 'until':
                    return ['',total]
                total = total + ' ' + word
                if word[len(word)-1] == ',':
                    return ['',total]
                index = index + 1
            return ['',total]
        elif step.__contains__("with"):
            index = step.split().index("with") + 1
            total = 'You should use'
            while index < len(step.split()):
                word = step.split()[index]
                if word == 'until':
                    return ['',total]
                total = total + ' ' + word
                if word[len(word)-1] == ',':
                    return ['',total]
                index = index + 1
            return ['',total]
        else:
            return ['',"There are no tools used in this step"]
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

    if "substitute" in inpt.lower() or "replace" in inpt.lower() or "substitution" in inpt.lower() or "replacement" in inpt.lower():
        newinpt = inpt.lower()
        newinpt = newinpt.split()
        theingredient = ""
        flag = False
        if newinpt.__contains__("cheese"):
            print(replacementdict["cheese"])
        elif newinpt.__contains__("oil"):
            print(replacementdict["oil"])
        elif newinpt.__contains__("turkey") or newinpt.__contains__("chicken") or newinpt.__contains__("beef") or newinpt.__contains__("pork"):
            print(replacementdict["vegetarian"])
        else:
            for word in newinpt:
                if flag==True:
                    theingredient+=word
                    theingredient+=" "
                if newinpt.__contains__("for"):
                    if word=="for":
                        flag = True
                else:
                    if word == "replace" or word=="substitute":
                        flag = True
            
            theingredient = theingredient[:-1]
            flag = False
            if theingredient in replacementdict:
                    print("Substitute", theingredient, "with:")
                    print(replacementdict[theingredient])
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
            splitted = inpt.lower().split()
            theverb = splitted[3]
            lastpart = splitted[3:]
            flag = False
            directions_referred_to = {}
            themax = 0
            maxdir = ""
            for step in steps:
                splitstep = step.split()
                for word in splitstep:
                    if word.__contains__(theverb):
                        flag = True
            if flag == False:
                for word in lastpart:
                    for step in steps:
                        if word in step:
                            if step in directions_referred_to:
                                directions_referred_to[step]+=1
                                if directions_referred_to[step]>themax:
                                    themax = directions_referred_to[step]
                                    maxdir = step
                            else:
                                directions_referred_to[step]=1
                                if directions_referred_to[step]>themax:
                                    themax = directions_referred_to[step]
                                    maxdir = step
            if len(directions_referred_to)>0:
                #print("THIS IS THE DIRECTION")
                print(maxdir)
                sentArr = ['how', 'do', 'i']
                splitdir = maxdir.split()
                for word in splitdir:
                    sentArr.append(word)
            else:
                sentArr = inpt.split()
            myUrl = "https://www.youtube.com/results?search_query="
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
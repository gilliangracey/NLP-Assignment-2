import requests 
import pandas as pd 
from bs4 import BeautifulSoup 
  
# link for extract html data 
def getdata(url): 
    r = requests.get(url) 
    return r.text 
  
htmldata = getdata("https://www.allrecipes.com/recipe/8493351/grain-free-broccoli-fritters/") 
soup = BeautifulSoup(htmldata, 'html.parser') 
data = '' 


body = soup.find_all("p")
title = soup.find_all("h1")

all_data = [title, body]

for element in all_data:
    for data in element:
        print(data.get_text()) 
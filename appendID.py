import requests
import json
from bs4 import BeautifulSoup
from importlib import reload
import time
import random
import sys
reload(sys)
#sys.setdefaultencoding('utf8')

TypesOfRecipes = {
    "curry": 28,
    "sweets": 42,
    "breakfast-brunch": 17,
    "salad": 14,
    "snacks": 10
}

listTypes = []

for item in TypesOfRecipes:
    listTypes.append(item)

for i, item in enumerate(listTypes):

    recipesWithID = open("recipesID-" + listTypes[i] + ".txt", "a")

    with open("receitas-" + listTypes[i] +".txt") as file:

        for line in file:
            if "}" in line:
                newline = line.replace("}", ", \"id\": [5]}")
                recipesWithID.write(newline)

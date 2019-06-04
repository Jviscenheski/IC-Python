import requests
import json
from bs4 import BeautifulSoup
from importlib import reload
import time
import random
import sys
import browser_cookie3

reload(sys)

TypesOfRecipes = {
    "dinner": [612, 17562],
    "breakfast-and-brunch": [193, 78],
    "desserts": [77, 79],
    "salad": [186, 96],
    "appetizers-and-snacks": [127, 76]
}

logErros = open("logErros.txt", "w")

listTypes = []

for item in TypesOfRecipes:
    listTypes.append(item)

# i = 0
# while i < len(listTypes):
#
#     category = listTypes[i]
#     text = open(category + ".txt", "w")
#
#     for item in range(1, TypesOfRecipes[category][0]):
#         url = "https://www.allrecipes.com/recipes/"+ str(TypesOfRecipes[category][1]) + "/"+ category + "?page=" + str(item)
#
#         try:
#             cj = browser_cookie3.chrome()
#         except:
#             logErros.write("problema na url: " + str(url) + '\n')
#
#         req = requests.get(url, cookies=cj)
#
#         soupLink = BeautifulSoup(req.content, 'html.parser')
#         listH3 = soupLink.find_all("h3")
#
#         for l in listH3:
#             link = l.find_all("a", href=True)
#
#             if len(link) != 0:
#                 valor = link[0].get('href')
#                 text.write(valor + "\n")
#                 print("escreveu: " + valor)
#     i += 1

# pega cada link e cadastra as receitas

listAttributesRecipe = []

for i, item in enumerate(listTypes):

    category = listTypes[i]
    recipes = open("receitas-" + listTypes[i] + ".txt", "a")
    htmlRecipes = open("HTMLreceitas-" + listTypes[i] + ".txt", "a")

    with open(listTypes[i] + ".txt") as file:

        for line in file:

            url = line.strip("\n")
            req = ""

            try:
                c = browser_cookie3.chrome()
            except:
                logErros.write("problema na url: " + str(url) + '\n')

            try:
                req = requests.get(url, cookies=c)
            except:
                logErros.write("problema na url: " + str(url) + '\n')
                aleatorio = random.uniform(0.9, 1.8)
                time.sleep(aleatorio)
                continue

            soupRecipe = BeautifulSoup(req.content, 'html.parser')

            name = soupRecipe.find(class_="recipe-summary__h1").text.strip()
            listAttributesRecipe.append(name)

            pagina = str(req.text.encode("utf-8"))

            # Novidade
            pagina = pagina.replace('\r', '')
            pagina = pagina.replace('\n', '')

            htmlRecipes.write(pagina)
            htmlRecipes.write("$$$&&&@@@\n")

            numberOfStars = soupRecipe.find("meta", {"itemprop": "ratingValue"})['content']
            listAttributesRecipe.append(numberOfStars)

            timePreparationTemp = soupRecipe.find_all("span", {"class": "ready-in-time__container"})

            for o in timePreparationTemp:
                timePreparation = o.find(class_="ready-in-time").text

            listAttributesRecipe.append(timePreparation)

            listIngredientsTemp = []
            ingredients = soupRecipe.find_all(class_="checklist dropdownwrapper list-ingredients-1")

            if len(ingredients) != 0:
                for l in ingredients:
                    novo = l.find_all(class_="recipe-ingred_txt added")
                    for m in novo:
                        listIngredientsTemp.append(m.text)

            listAttributesRecipe.append(listIngredientsTemp)

            pptemp = soupRecipe.find_all(class_="read--reviews")

            for m in pptemp:
                peopleWhoMade = m.find_all("span")[1].text.strip("\xa0made it")

            listAttributesRecipe.append(peopleWhoMade)

            evaluations = soupRecipe.find("meta", {"itemprop": "reviewCount"})['content']
            listAttributesRecipe.append(evaluations)

            prepTime = 0
            cookTime = 0

            timing = soupRecipe.find_all("ul", class_="prepTime")

            if len(timing) != 0:
                q = 0
                while q < len(timing):
                    if "Prep time" in str(timing[q]):
                        prepTime = timing[q].find(class_="prepTime__item--time").text
                    if "Cook time" in str(timing[q]):
                        cookTime = timing[q].find(class_="prepTime__item--time").text
                    q += 1

            listAttributesRecipe.append(prepTime)
            listAttributesRecipe.append(cookTime)
            listAttributesRecipe.append(category)

            attributesRecipe = {
                "name": [listAttributesRecipe[0]],
                "numberOfStars": [listAttributesRecipe[1]],
                "timeTotal": [listAttributesRecipe[2]],
                "ingredients": [listAttributesRecipe[3]],
                "peopleWhoMade": [listAttributesRecipe[4]],
                "numberOfEvaluations": [listAttributesRecipe[5]],
                "prepTime:": [listAttributesRecipe[6]],
                "cookTime:": [listAttributesRecipe[7]],
                "category:": [listAttributesRecipe[8]]
            }

            for item in attributesRecipe:
                print(str(item), attributesRecipe[item])

            jsonRecipe = json.dumps(attributesRecipe, ensure_ascii=False)
            recipes.write(str(jsonRecipe.encode("utf-8")) + "\n")
            # except:
            #     logErros.write("problema na url: " + str(url) + '\n')
            #     aleatorio = random.uniform(0.9, 1.8)
            #     time.sleep(aleatorio)
            #     continue

            aleatorio = random.uniform(0.9, 1.8)

            time.sleep(aleatorio)
            listAttributesRecipe = []

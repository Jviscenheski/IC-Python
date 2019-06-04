import requests
import json
from bs4 import BeautifulSoup
from importlib import reload
import time
import random
import sys
import browser_cookie3
reload(sys)

#
# TypesOfRecipes = {
#     "plat-principal": 422,
#     "dessert": 224,
#     "brunch": 24,
#     "salade": 103,
#     "entree": 184
# }


TypesOfRecipes = {   
    "brunch": 24,
    "salade": 103,
    "entree": 184
}

logErros = open("logErros.txt","w")
linkBrunch = "tag-1363/recette-brunch"

listTypes = []

for item in TypesOfRecipes:
    listTypes.append(item)

# i = 0
# while i < len(listTypes):
#
#     category = listTypes[i]
#     text = open(category + ".txt", "w")
#
#     for item in range(134, TypesOfRecipes[category]):
#         url = "http://allrecipes.fr/recettes/" + category + "-recettes.aspx?page=" + str(item)
#
#         if listTypes[i] == "brunch":
#             url = "http://allrecipes.fr/recettes/" + linkBrunch + ".aspx?page=" + str(item)
#
#         # novo
#         cj = browser_cookie3.chrome()
#
#         req = requests.get(url, cookies=cj)
#         soupLink = BeautifulSoup(req.content, 'html.parser')
#         listH3 = soupLink.find_all("h3")
#
#         for l in listH3:
#             link = l.find_all("a", href=True)
#
#             if len(link) != 0:
#                 valor = link[0].get('href')
#                 text.write(valor + "\n")
#     i += 1

# pega cada link e cadastra as receitas

listAttributesRecipe = []

for i, item in enumerate(listTypes):

    category = listTypes[i]
    recipes = open("receitas-" + listTypes[i] + ".txt", "a")
    htmlRecipes = open("HTMLreceitas-" + listTypes[i] + ".txt", "a")

    with open(listTypes[i] +".txt") as file:

        for line in file:

            url = line
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

            name = soupRecipe.find("span", {"itemprop": "name"}).text.strip()
            listAttributesRecipe.append(name)

            pagina = str(req.text.encode("utf-8"))

            # Novidade
            pagina = pagina.replace('\r', '')
            pagina = pagina.replace('\n', '')

            htmlRecipes.write(pagina)
            htmlRecipes.write("$$$&&&@@@\n")

            stars = soupRecipe.find_all("span", {"class": "icon-star"})
            numberOfStars = len(stars)
            listAttributesRecipe.append(numberOfStars)

            timePreparation = soupRecipe.find("div", {"class": "stat1"}, "span")
            if timePreparation is not None:
                listAttributesRecipe.append(timePreparation.text.strip())

            listIngredientsTemp = []
            ingredients = soupRecipe.find_all("span", {"itemprop": "ingredients"})

            if len(ingredients) != 0:
                for l in ingredients:
                    novo = l.text
                    if "\t" in l.text:
                        novo = l.text.replace("\t", " ")

                    listIngredientsTemp.append(novo)

            listAttributesRecipe.append(listIngredientsTemp)

            peopleWhoMade = soupRecipe.find_all(class_="imiContainer")
            w = 0

            while w < len(peopleWhoMade):
                numberPeopleWhoMade = peopleWhoMade[w].find("span").text.strip("utilisateurs ont fait cette recette")
                listAttributesRecipe.append(numberPeopleWhoMade)
                w += 1

            evaluations = soupRecipe.find_all(class_="stars")
            j = 0

            while j < len(evaluations):
                numberOfEvaluations = evaluations[j].find(class_="review-count")
                if numberOfEvaluations is not None:
                    listAttributesRecipe.append(numberOfEvaluations.text)
                else:
                    listAttributesRecipe.append(0)

                j += 1

            listTime = soupRecipe.find_all("h2")
            prepTime = 0
            cookTime = 0
            m = 0

            while m < len(listTime):
                timing = listTime[m].find_all(class_="epsilon")
                if len(timing) != 0:
                    q = 0
                    while q < len(timing):
                        parameters = timing[q].find_all("span")
                        v = 0
                        if len(parameters) != 0:
                            while v < len(parameters):

                                print(str(parameters[v]))
                                if "Préparation" in str(parameters[v]):
                                    prepTime = parameters[q].find(class_="accent").text
                                if "Cuisson" in str(parameters[v]):
                                    cookTime = parameters[q].find(class_="accent").text

                                v += 1
                        q += 1
                m += 1

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
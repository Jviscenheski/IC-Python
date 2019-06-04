from pymongo import MongoClient
import json

# Use MongoClient to create a connection:
client = MongoClient()

# To assign the database named primer to the local variable db
db = client['AllrecipesDB']

# You can access collection objects directly using dictionary-style


listRecipes = open('Erros.txt', 'r')
logErro = open("ErroNovamente.txt", "a")

for jsonData in listRecipes:
    try:
        jsonCorrigido = jsonData.replace("problem with the recipe: ", "").replace("\"\"]", "\"]")
        print(jsonCorrigido)
        result = db.recipesInfo.insert_one(json.loads(jsonCorrigido))
    except:
        logErro.write(jsonCorrigido)





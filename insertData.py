from pymongo import MongoClient
import json

# Use MongoClient to create a connection:
client = MongoClient()

# To assign the database named primer to the local variable db
db = client['AllrecipesDB']
# You can access collection objects directly using dictionary-style

TypesOfRecipes = {
    "appetizers-and-snacks": [612, 17562],
    "breakfast-and-brunch": [193, 78],
    "desserts": [77, 79],
    "dinner": [186, 96],
    "salad": [127, 76]
}

for item in TypesOfRecipes:
    listRecipes = open('recipesID-' + item + '.txt', 'r')
    logErro = open("Erro.txt", "a")

    for jsonData in listRecipes:
        try:
            formated = (jsonData.replace("[\"", "\"").replace("\"]", "\"").replace("(", "").replace(")", "").replace("b'", "").replace("\\", "").replace("}'", "}"))
            formatedID = formated.replace("[0]", "\"0\"").replace("[1]", "\"1\"").replace("[2]", "\"2\"").replace("[3]", "\"3\"").replace("[4]", "\"4\"").replace("[5]", "\"5\"").replace("[6]", "\"6\"")
            formatedKey = formatedID.replace("[", "[\"").replace("]", "\"]").replace("[\"\"", "[\"").replace("\"\"]", "\"]").replace(":\":", "\":")
            print(formatedKey)
            result = db.recipesFormated.insert_one(json.loads(formatedKey))
        except:
            logErro.write("problem with the recipe: " + jsonData)




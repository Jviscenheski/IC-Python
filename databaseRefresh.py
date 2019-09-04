from pymongo import MongoClient
import math
import pandas as pd
from bson.objectid import ObjectId

def calculaScore(dataframeBR, i):

    score1 = math.log(float(dataframeBR.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframeBR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeBR.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    print("Score: "+ str(score))

    return score

# Use MongoClient to create a connection:
client = MongoClient()
db = client['AllrecipesDB']

#db.get_collection('recipesDatabase').update_many({}, {'$set': {"score": 1}})
dataframeBR = pd.DataFrame(list(db.recipesDatabase.find({})))

for i in range(0, 37489):
    print(dataframeBR.loc[i, "_id"])
    print(calculaScore(dataframeBR, i))
    db.get_collection('recipesDatabase').update_many({"_id": ObjectId(dataframeBR.loc[i, "_id"])},
                                                     {'$set': {"score": calculaScore(dataframeBR, i)}})


'''
db.get_collection('recipesDatabase').update_many({}, {"$rename": {"category:": "category"}})
db.get_collection('recipesDatabase').update_many({}, {"$rename": {"cookTime:": "cookTime"}})
db.get_collection('recipesDatabase').update_many({}, {"$rename": {"prepTime:": "prepTime"}})
'''


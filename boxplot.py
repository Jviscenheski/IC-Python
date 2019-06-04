from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import seaborn

client = MongoClient()
db = client['AllrecipesDB']
data = db.recipesFormated.find()        #pega todos os valores do banco

dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))
dataframeBR.insert(10, "Score", 0)

for i in range(0,7794):
    score1 = math.log(float(dataframeBR.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeBR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
        #dataframeBR[i, "peopleWhoMade"] = 0
    else:
        score2 = (math.log(float(dataframeBR.loc[i, "peopleWhoMade"]) + 1.0, 10))


    score3 = ((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeBR.loc[i,"Score"] = score

dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"})))
dataframeFR.insert(10, "Score", 0)

for i in range(0,5568):
    score1 = math.log(float(dataframeFR.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeFR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeFR.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeFR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeFR.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeFR.loc[i,"Score"] = score

dataframeGR = pd.DataFrame(list(db.recipesFormated.find({"id": "3"})))
dataframeGR.insert(10, "Score", 0)

for i in range(0,6984):
    score1 = math.log(float(dataframeGR.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeGR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
      score2 = (math.log(float(dataframeGR.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeGR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeGR.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeGR.loc[i,"Score"] = score

dataframeIT = pd.DataFrame(list(db.recipesFormated.find({"id": "4"})))
dataframeIT.insert(10, "Score", 0)

for i in range(0,4005):
    score1 = math.log(float(dataframeIT.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeIT.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeIT.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeIT.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeIT.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeIT.loc[i,"Score"] = score

dataframeIN = pd.DataFrame(list(db.recipesFormated.find({"id": "5"})))
dataframeIN.insert(10, "Score", 0)

for i in range(0,966):
    score1 = math.log(float(dataframeIN.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeIN.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeIN.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeIN.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeIN.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeIN.loc[i,"Score"] = score

dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))
dataframeUSA.insert(10, "Score", 0)

for i in range(0,12166):
    score1 = math.log(float(dataframeUSA.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeUSA.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
        #dataframeUSA[i, "peopleWhoMade"] = 0
    else:
        score2 = (math.log(float(dataframeUSA.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    dataframeUSA.loc[i,"Score"] = score

#dataframeBR.boxplot(column="Score", positions=0.2, return_type='axes')
#dataframeUSA.boxplot(column="Score", positions=0.6, return_type='axes')

fig, axes = plt.subplots(nrows=1, ncols=2)

'''
dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))
dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"})))
dataframeGR = pd.DataFrame(list(db.recipesFormated.find({"id": "3"})))
dataframeIT = pd.DataFrame(list(db.recipesFormated.find({"id": "4"})))
dataframeIN = pd.DataFrame(list(db.recipesFormated.find({"id": "5"})))
dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))

for i in range(0,7794):

    if("fazer" in (dataframeBR.loc[i,"peopleWhoMade"])):
        dataframeBR.loc[i, "peopleWhoMade"] = 0

    dataframeBR.loc[i, "peopleWhoMade"] = str(dataframeBR.loc[i,"peopleWhoMade"]).replace("k", "000")

for i in range(0,12166):
    if ("do" in (dataframeUSA.loc[i, "peopleWhoMade"])):
        dataframeUSA.loc[i, "peopleWhoMade"] = 0

    dataframeUSA.loc[i, "peopleWhoMade"] = str(dataframeUSA.loc[i, "peopleWhoMade"]).replace("k", "000")

for i in range(0,5568):
    if ("fait" in (dataframeFR.loc[i, "peopleWhoMade"])):
        dataframeFR.loc[i, "peopleWhoMade"] = 0

    dataframeFR.loc[i, "peopleWhoMade"] = str(dataframeFR.loc[i, "peopleWhoMade"]).replace("k", "000")

for i in range(0,6984):
    if ("mal" in (dataframeGR.loc[i, "peopleWhoMade"])):
        dataframeGR.loc[i, "peopleWhoMade"] = 0

    dataframeGR.loc[i, "peopleWhoMade"] = str(dataframeGR.loc[i, "peopleWhoMade"]).replace("k", "000")

for i in range(0,4006):
    if ("Facci sapere se hai provato questa ricetta!" in (dataframeIT.loc[i, "peopleWhoMade"])):
        print("alou")
        dataframeIT.loc[i, "peopleWhoMade"] = 0

    dataframeIT.loc[i, "peopleWhoMade"] = str(dataframeIT.loc[i, "peopleWhoMade"]).replace("k", "000")

for i in range(0,966):
    if ("do" or "person" in (dataframeIN.loc[i, "peopleWhoMade"])):
        dataframeIN.loc[i, "peopleWhoMade"] = 0

    dataframeIN.loc[i, "peopleWhoMade"] = str(dataframeIN.loc[i, "peopleWhoMade"]).replace("k", "000")
'''

data = [dataframeBR["Score"].astype(float),dataframeFR["Score"].astype(float), dataframeGR["Score"].astype(float), dataframeIT["Score"].astype(float), dataframeIN["Score"].astype(float), dataframeUSA["Score"].astype(float)]
fig, ax = plt.subplots()
ax.boxplot(data, 0, "")

#axes[0].boxplot(dataframeBR["peopleWhoMade"].astype(float), 0, "", bin(5))
#axes[1].boxplot(dataframeUSA["peopleWhoMade"].astype(float),0, "", bin(5))

# plt.legend(loc='upper left')
plt.title('Score')
# plt.xlabel('Score')
#plt.ylabel('Score')

plt.show()


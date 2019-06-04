from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

client = MongoClient()
db = client['AllrecipesDB']
data = db.recipesFormated.find()        #pega todos os valores do banco

dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))
dataframeBR.insert(10, "Score", 0)

abacaxiBR = 0
abacaxiFR = 0
abacaxiGR = 0
abacaxiIT = 0
abacaxiIN = 0
abacaxiUSA = 0


for i in range(0,7794):
    score1 = math.log(float(dataframeBR.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeBR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeBR.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    if (score > 28):
        abacaxiBR = abacaxiBR + 1
    dataframeBR.loc[i,"Score"] = score

dataframeBR.boxplot(column="Score", by=None, ax=None, fontsize=None, rot=0, grid=True, figsize=None, layout=None, return_type=None)


#plt.hist(dataframeBR["Score"], bins=50, normed=True, cumulative=True, label='CDF DATA',
          #histtype='step', alpha=0.55, color='blue')

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
    if (score > 28):
        abacaxiFR = abacaxiFR + 1
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
    if (score > 28):
        abacaxiGR = abacaxiGR + 1
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
    if (score > 28):
        abacaxiIT = abacaxiIT + 1
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
    if(score > 28):
        abacaxiIN = abacaxiIN + 1
    dataframeIN.loc[i,"Score"] = score


dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))
dataframeUSA.insert(10, "Score", 0)

for i in range(0,12166):
    score1 = math.log(float(dataframeUSA.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeUSA.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeUSA.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    if (score > 28):
        abacaxiUSA = abacaxiUSA + 1
    dataframeUSA.loc[i,"Score"] = score


# ax1 = plt.hist(dataframeBR["Score"], bins=50, normed=True, cumulative=True, label='Brazil',
#           histtype='step', alpha=0.55, color='blue')
# ax2 = plt.hist(dataframeFR["Score"], bins=50, normed=True, cumulative=True, label='France',
#           histtype='step', alpha=0.55, color='orange')
# ax3 = plt.hist(dataframeGR["Score"], bins=50, normed=True, cumulative=True, label='Germany',
#           histtype='step', alpha=0.55, color='green')
# ax4 = plt.hist(dataframeIT["Score"], bins=50, normed=True, cumulative=True, label='Italy',
#           histtype='step', alpha=0.55, color='red')
# ax5 = plt.hist(dataframeIN["Score"], bins=50, normed=True, cumulative=True, label='India',
#           histtype='step', alpha=0.55, color='purple')
# ax6 = plt.hist(dataframeUSA["Score"], bins=50, normed=True, cumulative=True, label='USA',
#           histtype='step', alpha=0.55, color='pink')
#
# plt.legend(loc='upper left')
# plt.title('CDF')
# plt.xlabel('Score')
# plt.ylabel('P(X<=x)')
# plt.show()

print(abacaxiBR)
print(abacaxiFR)
print(abacaxiGR)
print(abacaxiIT)
print(abacaxiIN)
print(abacaxiUSA)





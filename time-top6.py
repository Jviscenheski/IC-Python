import networkx as nx
import pandas as pd
import math
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client['AllrecipesDB']

dataframe = pd.DataFrame(list(db.recipesFormated.find()))               # pega dados de todos


def calculaScore(dataframe, i):

    score1 = math.log(float(dataframe.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframe.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframe.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframe.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframe.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    print("Score: "+ str(score))

    return score


def selectDataframe(arquivo):

    grafo = nx.drawing.nx_pydot.read_dot(arquivo)
    print(len(grafo))
    allRecipes = (grafo.nodes(data='receitas'))
    timeList = []
    scoreList = []

    for recipesID in allRecipes:
        allIDs = recipesID[1]
        listOfAllID = allIDs.split(",")
        for idRecipe in listOfAllID:
            query = idRecipe.split("'")[1]
            dataframe = pd.DataFrame(list(db.recipesFormated.find({"_id": ObjectId(query)})))
            totalTimeString = dataframe.loc[0, "timeTotal"]
            totalTimeFormated = totalTimeString.replace("hours", "::").replace("hour", "::").replace("h", "::").\
                    replace("minutes", "").replace("mins", "").\
                    replace("minute", "").replace("min", "").replace("days", "d::").replace("day", "d::")
            '''
                    replace("ora", "::").replace("'", "").replace("dias","d::").\
                    replace("s", "::").replace("1 dday", "24::").replace(":::", "::").replace("m", "").replace("horas", "::").\
                    replace("hora", "::").replace("h", "::").replace("minutos", ""). \
                    replace("minuto", "").replace("min", "").replace("ora", "::").replace("'", "").replace("dias","d::").\
                    replace("s", "::").replace("1 dia", "24::").replace(":::", "::").replace("m", "").strip()
            '''
            finalTotalTime = []
            if "::" in totalTimeFormated:
                if totalTimeFormated:
                    print(len(totalTimeFormated.split("::")))
                    if "d:" in totalTimeFormated:
                        finalTotalTime = (float(totalTimeFormated.split("::")[0].strip().replace("d", ""))*24 +
                                             (float((totalTimeFormated.split("::")[1].strip())) / 60))
                    elif totalTimeFormated.split("::")[0].strip() and totalTimeFormated.split("::")[1].strip():
                        finalTotalTime = (float(totalTimeFormated.split("::")[0].strip()) +
                                            (float((totalTimeFormated.split("::")[1].strip()))/60))
                    else:
                        finalTotalTime = float((totalTimeFormated.split("::")[0].strip()))/60

            timeList.append(finalTotalTime)
            scoreList.append(calculaScore(dataframe, 0))

        return timeList, scoreList



def de_mean(serie):
    x_bar = sum(serie)/len(serie)
    return [x_i - x_bar for x_i in serie]


def dot(v, w):
    return sum(v_i*w_i for v_i, w_i in zip(v, w))


def sum_of_squares(v):
    return dot(v, v)


def variance(serie):
    n = len(serie)
    deviations = de_mean(serie)
    return sum_of_squares(deviations)/(n-1)


def standard_variation(serie):
    return math.sqrt(variance(serie))


def covariance(timeSerie, scoreSerie):
    n = len(timeSerie)
    return dot(de_mean(timeSerie), de_mean(scoreSerie))/(n-1)


def correlation(timeSerie, scoreSerie):
    stdev_x = standard_variation(timeSerie)
    stdev_y = standard_variation(scoreSerie)
    if stdev_x >0 and stdev_y > 0:
        return covariance(timeSerie, scoreSerie)/stdev_x/stdev_y
    else:
        return 0


file = open("correlations.txt", "a")

#filesList = ["Brasil.dot", "França.dot", "Alemanha.dot", "Itália.dot", "Índia.dot", "EUA.dot"]

filesList = ["INDIA-BAIXO.dot"]

for country in filesList:
    tList, sList = selectDataframe(country)
    print(correlation(tList, sList))
    #file.write(country + str(correlation(tList, sList)))

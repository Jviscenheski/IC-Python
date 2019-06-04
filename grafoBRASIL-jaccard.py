import networkx as nx
import pandas as pd
import math
from pymongo import MongoClient
from networkx.drawing.nx_pydot import write_dot
import pygraphviz
import matplotlib.pyplot as plt
import matplotlib.cm as matcm

# cria a aresta se o jaccard entre os ingredientes das receitas é maior que 0.8
def criaArestas(grafoBR):
    counter = 0
    for i in range(0,2):
        for j in range(0,2):
            if(grafoBR.nodes[i]['ingredients'] != grafoBR.nodes[j]['ingredients']):
                score1 = grafoBR.nodes[i]['score']
                score2 = grafoBR.nodes[j]['score']
                if (score1 > 35.0):
                    if(score2 > 35.0):
                        '''
                        grafoAux.add_node(i, name=grafoBR.nodes[i]['name'], category=grafoBR.nodes[i]['category'],
                                         countryID=grafoBR.nodes[i]['countryID'],
                                         prepTime=grafoBR.nodes[i]['prepTime'],
                                         cookTime=grafoBR.nodes[i]['cookTime'],
                                         ingredients=grafoBR.nodes[i]['ingredients'],
                                         totalTime=grafoBR.nodes[i]['totalTime'],
                                         stars=grafoBR.nodes[i]['stars'],
                                         numberOfEvaluations=grafoBR.nodes[i]['numberOfEvaluations'],
                                         peopleWhoMade=grafoBR.nodes[i]['peopleWhoMade'],
                                         score=grafoBR.nodes[i]['score'])
                        grafoAux.add_node(j, name=grafoBR.nodes[j]['name'], category=grafoBR.nodes[j]['category'],
                                          countryID=grafoBR.nodes[j]['countryID'],
                                          prepTime=grafoBR.nodes[j]['prepTime'],
                                          cookTime=grafoBR.nodes[j]['cookTime'],
                                          ingredients=grafoBR.nodes[j]['ingredients'],
                                          totalTime=grafoBR.nodes[j]['totalTime'],
                                          stars=grafoBR.nodes[j]['stars'],
                                          numberOfEvaluations=grafoBR.nodes[j]['numberOfEvaluations'],
                                          peopleWhoMade=grafoBR.nodes[j]['peopleWhoMade'],
                                          score=grafoBR.nodes[j]['score'])
                        '''
                        coef = jaccard_similarity(grafoBR.nodes[i]['ingredients'], grafoBR.nodes[j]['ingredients'])
                        if coef > 0.4:
                            if(grafoBR.has_edge(i,j)):
                                print("Já tem aresta")
                            else:
                                grafoBR.add_edge(i,j)
                                print(str(coef) + ' Criada aresta!!')
                                print(grafoBR.nodes[i]['name'])
                                print(grafoBR.nodes[i]['score'])
                                print(grafoBR.nodes[i]['ingredients'])
                                print(grafoBR.nodes[j]['name'])
                                print(grafoBR.nodes[j]['score'])
                                print(grafoBR.nodes[j]['ingredients'])
                                counter = counter + 1
    return counter

# calcula a similaridade entre os nós com base no coeficiente de Jaccard
def jaccard_similarity(list1, list2):

    stopwords = ["colheres","pitada", "suco","molho", "picado","2'", "2 '" "picada'","pó", "colher", "xícara", "xícaras", "\'", "sopa", "lata", "caixinha", "caixa", "chá", "dentes", "gosto", ",", "1", "2", "2 '", "3", "4", "5", "6", "creme", "reino", "branco", "ml", "kg", "g", "dente"]

    if stopwords in list1:
        s1 = set(list1.remove(stopwords))
    else:
        s1 = set(list1)

    if stopwords in list2:
        s2 = set(list2.remove(stopwords))
    else:
        s2 = set(list2)

    return len(s1.intersection(s2)) / len(s1.union(s2))

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

def salvaGrafo(grafoBR):
    pos = nx.nx_agraph.graphviz_layout(grafoBR)
    nx.draw(grafoBR, pos=pos)
    write_dot(grafoBR, 'grafoBR.dot')


client = MongoClient()
db = client['AllrecipesDB']
dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"}))) #pega somente os dados do Brasil
grafoBR = nx.petersen_graph()
grafoAux = nx.Graph()
dataframeBR.insert(10, "Score", 0)

for i in range(0,2):
    grafoBR.add_node(i, name=dataframeBR.loc[i, "name"], category=dataframeBR.loc[i, "category:"], countryID=dataframeBR.loc[i, "id"],
                     prepTime=dataframeBR.loc[i, "prepTime:"], cookTime=dataframeBR.loc[i, "cookTime:"],
                     ingredients=dataframeBR.loc[i, "ingredients"], totalTime=dataframeBR.loc[i, "timeTotal"],
                     stars=dataframeBR.loc[i, "numberOfStars"], numberOfEvaluations=dataframeBR.loc[i, "numberOfEvaluations"],
                     peopleWhoMade=dataframeBR.loc[i, "peopleWhoMade"], score=calculaScore(dataframeBR, i))

print(criaArestas(grafoBR))
salvaGrafo(grafoBR)






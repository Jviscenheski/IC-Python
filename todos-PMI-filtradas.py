import networkx as nx
import pandas as pd
from pymongo import MongoClient
import math
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')


def insereIDreceitasAndScore(dataframe, grafo, qtdadeReceitas):

    # primeiro analisa as receitas brasileiras
    for i in range(0, qtdadeReceitas):                                                                     # controla o dataframe                                                                # controla o grafo
        listIngredient = dataframe.loc[i, "ingredients"]    # pega os ingredientes de uma receita
        for item in listIngredient:                                                             # controla a lista de ingredientes
            for j in range(0, len(grafo)):
                if grafo.nodes[j]['ingredienteLL'] == item:                                    # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if dataframe.loc[i, 'score'] >= 0.0:
                        recipeList.append(dataframe.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                   # guarda o id desta receita dentro do nó
                    vetorReceitasPais[0] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = dataframe.loc[i, 'score']
    return grafo


def criaListaIngredientes(listIngredients, dicFinalIngredients, id):

    for i in range(len(listIngredients)):
        ingrediente = listIngredients[i].replace("Á", "á").replace("A", "a").replace("B", "b").\
            replace("C", "c").replace("F", "f").replace("M", "m").replace("N", "n").replace("O", "o").\
            replace("Ó", "ó").replace("P", "p").replace("Q", "q").replace("R", "r").replace("S", "s").replace("V", "v").\
            replace("'s", "s").replace("Water", "water").replace("'pfeffer", "pfeffer").replace("'butter", "butter")

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas


def criaNos(grafo, dicFinalIngredients, country):

    index = 0
    for item in dicFinalIngredients:
        grafo.add_node(index, ingredient=item, qtdadeReceitas=country, vreceitas=dicFinalIngredients[item], score=0)
        index = index + 1

    print("NUMERO DE NÓS: " + str(index))
    return len(grafo)


# Calcula a quantidade, não é qualitativo!
def calculaReceitasComuns(ingre1, ingre2, dicFinal):

    qtdade = 0
    list1Ingre1 = dicFinal[ingre1]
    list1Ingre2 = dicFinal[ingre2]
    for m in list1Ingre1:
        for n in list1Ingre2:
            if m == n:
                qtdade = qtdade + 1
    return qtdade


def criaLinks(grafo, tam , dicFinal):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if grafo.nodes[m]['ingredient'] != grafo.nodes[j]['ingredient'] and grafo.has_edge(m,j) == False:
                pA = int(sum(grafo.nodes[m]['qtdadeReceitas']))/tam
                pB = int(sum(grafo.nodes[j]['qtdadeReceitas']))/tam
                pAB = (calculaReceitasComuns(grafo.nodes[m]['ingredient'], grafo.nodes[j]['ingredient'], dicFinal))/tam
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    grafo.add_edge(m, j, weight=PMI)
                    count = count + 1
                    print(str(PMI))

    print("NUMERO DE ARESTAS: " + str(count))


def salvaGrafo(grafo, name):
    nx.drawing.nx_pydot.write_dot(grafo, name)


def calculaCentralidade(grafo):

    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafo)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade


def defineTops(dicionario, fileName):

    top = open(fileName, "a")
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        print(grafo.nodes[item]['ingredient'])
        top.write(str(grafo.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")


# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']

dataframeBR = pd.DataFrame(list(db.recipesIngredients.find({"id": "1"})))          # pega dados do Brasil
dataframeFR = pd.DataFrame(list(db.recipesIngredients.find({"id": "2"})))         # pega dados da França
dataframeAL = pd.DataFrame(list(db.recipesIngredients.find({"id": "3"})))         # pega dados da Alemanha
dataframeIT = pd.DataFrame(list(db.recipesIngredients.find({"id": "4"})))         # pega dados da Italia
dataframeIN = pd.DataFrame(list(db.recipesIngredients.find({"id": "5"})))         # pega dados da India
dataframeEUA = pd.DataFrame(list(db.recipesIngredients.find({"id": "6"})))         # pega dados dos USA


countries = {"Brasil": [7794, dataframeBR, [1, 0, 0, 0, 0, 0]],
             "França": [5568, dataframeFR, [0, 1, 0, 0, 0, 0]],
             "Alemanha": [6984, dataframeAL, [0, 0, 1, 0, 0, 0]],
            "Itália": [4005, dataframeIT, [0, 0, 0, 1, 0, 0]],
             "Índia": [966, dataframeIN, [0, 0, 0, 0, 1, 0]],
             "EUA": [12167, dataframeEUA, [0, 0, 0, 0, 0, 1]]}

for country in countries:
    grafo = nx.Graph()
    ingredientsDictionary = []
    dicFinal = dict(ingredientsDictionary)
    for i in range(0, countries[country][0]):
        if countries[country][1].loc[i, 'score'] >= 0.0:
            ingredients = countries[country][1].loc[i, "ingredients"]
            criaListaIngredientes(ingredients, dicFinal, countries[country][1].loc[i, "_id"])

    graphSize = criaNos(grafo, dict(dicFinal), countries[country][2])
    criaLinks(grafo, graphSize, dicFinal)
    defineTops(calculaCentralidade(grafo), country + "-TOTAL.txt")
    salvaGrafo(grafo, country + ".dot")
    grafo.clear()

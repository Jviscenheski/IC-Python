import networkx as nx
import pandas as pd
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
import math
from matplotlib import pyplot as plt
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')

class ingredienteCategoria:
    def __init__(self, ingrediente, category):
        self.nome = ingrediente
        self.dicCategoria = category

    def setIngredient(self, ingrediente):
        self.nome = ingrediente

    def setCategoria(self, dic):
        self.dicCategoria = dic

    def getIngrediente(self):
        return self.nome

    def getCategoria(self):
        return self.dicCategoria

def calculaScore(dataframeAL, i):

    score1 = math.log(float(dataframeAL.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframeAL.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeAL.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeAL.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframeAL.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    print("Score: "+ str(score))

    return score

def filtraIngredientes(ingredients,stopWords):
    wordsFiltered = []
    for sent in sent_tokenize(str(ingredients)):
        words = word_tokenize(sent)
        filtered_sentence = [w for w in words if not w in stopWords]

        for i in range(len(filtered_sentence)):
            if len(filtered_sentence[i]) > 3 or filtered_sentence[i] == "rum" or filtered_sentence[i] == "sal":
                filtered_sentence[i].replace(filtered_sentence[i], "").replace("\'", "")
                wordsFiltered.append(filtered_sentence[i])
    return wordsFiltered

def criaListaCategorias(ingrediente, category, listaCategoria):
    dicionario = dict(listaCategoria)
    novoIngrediente = ingredienteCategoria(ingrediente, category)
    dicionario = novoIngrediente.getCategoria()
    dicionario[category] = dicionario[category] + 1
    novoIngrediente.setCategoria(dicionario)

def criaListaIngredientes(listIngredients, dicFinalIngredients, id):
    for i in range(len(listIngredients)):
        ingrediente = listIngredients[i].replace("Á", "á").replace("A", "a").replace("B", "b").\
            replace("C", "c").replace("F", "f").replace("M", "m").replace("N", "n").replace("O", "o").\
            replace("Ó", "ó").replace("P", "p").replace("Q", "q").replace("R", "r").replace("S", "s").replace("V", "v").\
            replace("'s", "s").replace("Water", "water").replace("'pfeffer", "pfeffer").replace("'butter", "butter")

        #criaListaCategorias(ingrediente,category, listaCategoria)

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas

def criaNos(grafoUSA, dicFinalIngredients, teste):
    indice = 0
    for i in dicFinalIngredients:
        if(len(dicFinalIngredients[i]) > 11):
            teste.write(i + "\n")
            grafoUSA.add_node(indice, ingredient=i, qtdadeReceitas=len(dicFinalIngredients[i]))
            indice = indice +1

    print("NUMERO DE NÓS: " + str(indice))
    return len(grafoUSA)

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

def criaLinks(grafoUSA, tam ,dicFinal):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafoUSA.nodes[m]['ingredient'] != grafoUSA.nodes[j]['ingredient'] and grafoUSA.has_edge(m,j) == False):
                pA = int(grafoUSA.nodes[m]['qtdadeReceitas'])/7794
                pB = int(grafoUSA.nodes[j]['qtdadeReceitas'])/7794
                pAB = (calculaReceitasComuns(grafoUSA.nodes[m]['ingredient'], grafoUSA.nodes[j]['ingredient'], dicFinal))/7794
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafoUSA.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI))

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList

def salvaGrafo(grafoUSA):
    nx.drawing.nx_pydot.write_dot(grafoUSA, "grafoALEMANHA-BAIXO.dot")
    #nx.write_gml(grafoUSA, "grafoUSA.gml")

def criaHistograma(pmiList):
    data = pmiList

    bins = np.linspace(math.ceil(min(data)),
                       math.floor(max(data)),
                       20)  # fixed number of bins

    plt.xlim([min(data) - 5, max(data) + 5])

    plt.hist(data, bins=bins, alpha=0.5)
    plt.title('PMI distribution')
    plt.xlabel('variable X (20 evenly spaced bins)')
    plt.ylabel('count')

    plt.show()

def calculaCentralidade(grafoUSA):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafoUSA)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade

def defineTops(dicionario):
    top50 = open("top50-ALEMANHA-baixo.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 65):
            top = top + 1
            print(grafoUSA.nodes[item]['ingredient'])
            top50.write(str(grafoUSA.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")

# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']
dataframeAL = pd.DataFrame(list(db.recipesFormated.find({"id": "3"}))) #pega somente os dados dos USA
grafoUSA = nx.Graph()
stopWords = set(stopwords.words('german'))

stopWords.update(["'450", "brauner", "weiche", "entfernt", "scheiben", "geschnitten", "'200", "prise", "griechischer",
                  "frische", "'250", "schwarzer", "bestreuen", "kernige", "'ein", "siehe", "'eine", "gute", "'100",
                  "geschmolzen", "'300", "pfanne", "'160", "sahne", "schuss", "Waffeleisen", "'puderzucker", "'180",
                  "heller", "'125", "'etwas", "packung", "rote", "warme", "Zimmertemperatur", "'600", "'225",
                  "'375", "'115", "scheiben", "'150", "prise", "pfanne", "bestreuen", "sahne", "schuss", "packung",
                  "gehackte", "Tasse", "'500", "Type", "warmes", "Geschmack", "fettarme", "'350", "'400", "fein",
                  "abgeriebene", "magerquark", "reife", "gehackt", "'frisch", "gemahlener", "bedarf", "optional",
                  "mehr", "bund", "feine", "gehackter", "geriebener", "frisch", "'175", "'475", "gekochter", "klein",
                  "saure", "gerieben", "kalte", "geriebene", "'pfeffer", "zerlassen", "halbiert", "Zwiebeln",
                  "Handvoll", "abgetropft", "paar", "gemischte", "Wxc3xbcrfel", "unbehandelte", "'240", "Eiweixc3x9f",
                  "getrennt", "braten", "kleine", "Gelierzucker", "'120", "scheibe", "schwarze", "schwarzer", "'prise",
                  "grob", "extra", "lauwarme", "'170", "rosinen", "Zitronenschale", "Emmentaler", "geschmolzene",
                  "saft", "gemahlene", "Dose", "frischer", "Dill", "geputzt", "gewaschen", "'einige,", "orangensaft",
                  "'750", "schale", "'220", "muskat", "nelken", "streifen", "Glas", "bestreichen",  "'Zucker",
                  "unbehandelten", "'Zimt", "'abgeriebene", "form", "Tassen", "samen", "belieben", "becher", "quark",
                  "getrocknete", "geschxc3xa4lt", "Kerngehxc3xa4use", "Txc3xbctchen","fuxc3x9fnote", "pxc3xa4ckchen",
                  "xc2xbd", "zerdrxc3xbcckt","fxc3xbcr", "bestxc3xa4uben", "groxc3x9fe", "olivenxc3xb6l", "gewxc3xbcrfelt",
                  "weixc3x9fe", "mxc3xbchle", "stxc3xbcck", "stxc3xbccke", "grxc3xbcne", "mittelgroxc3x9fe",
                  "scheiben", "prise", "'xc2xbd:", "pxc3xa4ckchen", "olivenxc3xb6l", "stxc3xbcck", "becher",
                  "bedarf", "xc3x96l","verquirlt", "'xc3x96l","packung", "xc3x84pfel"])

maisUma = []
for i in range(99,100):
    maisUma.append("'"+str(i))
    maisUma.append("'"+str(i)+"g")
stopWords.update(maisUma)

ingredientsDictionary = []
dicFinal = dict(ingredientsDictionary)

#12167
for i in range(0,6985):
    if(calculaScore(dataframeAL, i) <= 15.0):
        ingredients = dataframeAL.loc[i, "ingredients"]
        criaListaIngredientes(filtraIngredientes(ingredients, stopWords), dicFinal, dataframeAL.loc[i, "_id"])

teste = open("testeAlemanha.txt", "a")

graphSize = criaNos(grafoUSA, dict(dicFinal), teste)
criaLinks(grafoUSA, graphSize, dicFinal)
defineTops(calculaCentralidade(grafoUSA))
salvaGrafo(grafoUSA)


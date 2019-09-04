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

def calculaScore(dataframeFR, i):

    score1 = math.log(float(dataframeFR.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframeFR.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeFR.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeFR.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframeFR.loc[i, "numberOfStars"])) + 1.0)
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


def criaListaIngredientes(listIngredients, dicFinalIngredients, id, category):
    for i in range(len(listIngredients)):
        ingrediente = listIngredients[i].replace("'","").replace("as", "a").\
            replace("os", "o").replace("Á", "á").replace("A", "a").replace("B", "b").\
            replace("C", "c").replace("F", "f").replace("M", "m").replace("N", "n").replace("O", "o").\
            replace("Ó", "ó").replace("P", "p").replace("Q", "q").replace("R", "r").replace("S", "s").replace("V", "v").\
            replace("xc3xa8", "è").replace("xc5x93", "oe").replace("xc3xa9", "é").replace("gousse", "gousse d'ail").\
            replace("dail", "gousse d'ail").replace("deau", "eau")

        #criaListaCategorias(ingrediente,category, listaCategoria)

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas

def criaNos(grafoFR, dicFinalIngredients):
    indice = 0
    for i in dicFinalIngredients:
        if(len(dicFinalIngredients[i]) > 11):
            print(i)
            grafoFR.add_node(indice, ingredient=i, qtdadeReceitas=len(dicFinalIngredients[i]))
            indice = indice +1

    print("NUMERO DE NÓS: " + str(indice))
    return len(grafoFR)

def calculaReceitasComuns(ingre1, ingre2, dicFinal):
    qtdade = 0
    list1Ingre1 = dicFinal[ingre1]
    list1Ingre2 = dicFinal[ingre2]
    for m in list1Ingre1:
        for n in list1Ingre2:
            if m == n:
                qtdade = qtdade + 1
    return qtdade

def criaLinks(grafoFR, tam ,dicFinal):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafoFR.nodes[m]['ingredient'] != grafoFR.nodes[j]['ingredient'] and grafoFR.has_edge(m,j) == False):
                pA = int(grafoFR.nodes[m]['qtdadeReceitas'])/7794
                pB = int(grafoFR.nodes[j]['qtdadeReceitas'])/7794
                pAB = (calculaReceitasComuns(grafoFR.nodes[m]['ingredient'], grafoFR.nodes[j]['ingredient'], dicFinal))/7794
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafoFR.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI))

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList

def salvaGrafo(grafoFR):
    nx.drawing.nx_pydot.write_dot(grafoFR, "grafoFRBAIXO.dot")
    #nx.write_gml(grafoBR, "grafoBRTESTEPEQUENO.gml")

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

def calculaCentralidade(grafoBR):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafoBR)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade

def defineTops(dicionario):
    top50 = open("top100-FRANCA-alto.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 150):
            top = top + 1
            print(grafoFR.nodes[item]['ingredient'])
            top50.write(str(grafoFR.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")


# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']
dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"}))) #pega somente os dados do Brasil
grafoFR = nx.Graph()
stopWords = set(stopwords.words('french'))

maisUma = []
for i in range(99,999):
    maisUma.append("'"+str(i))
    maisUma.append("'"+str(i)+"g")
stopWords.update(maisUma)

stopWords.update(["gro", "dxc3xa9s", "quelques", "grose", "groses", "poivre", "concasxc3xa9es",
                  "du", "soupe", "cuillères", "pincée", "frais", "coupées", "cuillxc3xa8re", "coupés", "coupé",
                  "entier", "sans", "poivre", "feuilles", "cuillère", "du", "dxe2x80x99huile", "dxe2x80x99olive",
                  "rouges", "coupés", "fines", "lanières", "poignées", "moulin", "écraées", "grose", "poignée",
                  "écraées", "grose", "poigné", "haché", "pincées", "flocons", "séché", "finement", "émincé",
                  "groses", "crevettes", "cuillères", "rxc3xb4ti", "dxe2x80x99environ", "dxe2x80x99ail", "gro",
                  "coupées","quartiers", "dés", "xc3xa0", "cuillères", "rxc3xa2pé", "hachées", "poudre", "boxc3xaete", "Des", "provence", "rae", "maxc3xafzenaxe2x84xa2",
                  "verres", "dxe2x80x99eau", "cuillerée", "coupé", "dés", "épluchées", "julienne", "épluchés",
                  "douce", "coupée", "rouge", "chiches", "sauce", "xc2xbc", "pincée", "exemple", "chiche", "conserve",
                  "rincés", "égouttés", "moyens", "émincés", "pelées", "épluché", "cubes", "lavées", "rondelles",
                  "dxe2x80x99épaisseur", "morceaux", "belles", "tronxc3xa7ons", "branche", "asez", "oulu", "quelques",
                  "pilées", "litres", "blancs", "secs", "émincées", "blanc", "dxe2x80x99origan", "rais", "cuill",
                  "hachées", "feta", "brins", "dorigan", "hachée", "beaux", "posible", "peau", "mélange", "cajun", "gousses",
                  "voir", "séchée", "vert", "épépiné", "branches", "long", "litre", "préférence", "fumé", "concasées",
                  "Tabacoxe2x84xa2", "mélangées", "ciselé", "chaud", "fraxc3xaechement", "rxc3xa2pé", "bottes", "quelques",
                  "égouttées", "petits", "concentré", "cxc3xa2pres", "vertes", "dénoyautées", "grosièrement", "haché",
                  "séchés", "écraés", "blanche", "émincée", "tagliatelles", "petite", "fraxc3xaeches","émincé",
                  "décortiquées", "cuillerées", "tout", "recette", "verts", "épépinés", "épépinées", "léger", "coupée",
                  "bouquet", "fraxc3xaeche", "verre", "environ", "xc2xbd", "purée", "facultatif", "convenance",
                  "hachés", "romaines", "laurier", "22,5", "deau", "déveinées", "moules", "nettoyées", "dorange",
                  "zeste", "ramolli", "racine", "rxc3xa2pée", "tranches", "dxe2x80x99olives", "noires", "Une", "doeuf",
                  "friture", "plus", "nécessaire", "cuil", "petit", "lavé", "égoutté", "allégé", "naturel", "douces", "cuit",
                  "déshydraté", "maxc3xafs", "surgelé", "botte", "magrets", "ferme", "type", "salé", "dxe2x80x99agneau",
                  "épaisses", "roux", "ciselée", "divisées", "paris", "boule", "escalopes", "dinde", "découpé",
                  "pousses", "fort", "grillées", "battus", "tiges", "doignons", "boite", "fraiche", "liquide",
                  "gruyère", "rasis", "Granny", "smith", "surgelés", "décongelés", "cèpes", "beau", "pxc3xa2tes",
                  "dxe2x80x99épinards", "échalotes", "boxc3xaetes", "maigre", "bombée", "dherbes", "noir", "paquet",
                  "laagnes", "cuites", "17,5", "menu", "brin", "feuille", "dxe2x80x99orange", "bouillante", "gamba",
                  "morceau", "butternut", "épluchée", "pxc3xa2te", "goxc3xbbt", "poitrine", "fumée", "décoration",
                  "copeaux", "doux", "demi-écrémé", "jaunes", "dxe2x80x99oeufs", "légèrement", "pressé", "nature",
                  "1xe2x81x842", "jeunes", "écraée", "plat", "comté", "salade", "Xérès", "brosées", "cuite", "petites",
                  "grattées", "denviron", "chacun", "gigot", "entières", "coulis", "lamelles", "fait", "frire",
                  "poxc3xaale", "terre", "bocal", "moulue", "tranchées", "Environ", "deux", "lancienne", "autre",
                  "boites", "saint", "jacques", "gra", "lail", "dénoyautés", "lxe2x80x99eau", "dxe2x80x99amandes",
                  "effilées", "pressée", "piqué", "clous", "bonne", "jaune", "dun", "tranchés", "concasé", "lhuile",
                  "durs", "brisée", "moule", "tarte", "graisser", "barquette", "alimentaire", "échalote", "dxe2x80x99aneth",
                  "chimique", "vierge", "extra", "présentation", "bxc3xa2tons", "moins", "fonction", "goxc3xbbts",
                  "tiède", "babeurre", "très", "dxe2x80x991", "égouttée", "une", "trait", "pimentée", "Worcestershire",
                  "pulpe", "calamars", "nettoyés", "dxe2x80x99oeuf", "moyen", "cidre", "destragon", "belle", "nouvelles",
                  "dEspelette", "chaude", "1,25", "arborio", "kilo", "crues", "taille", "moyenne", "pendant", "minutes",
                  "rincées", "saint-Jacques", "lavés", "fond", "extra-vierge", "désosé", "détaillé", "grains", "Tabaco",
                  "émietté", "lxe2x80x99huile", "noirs", "dxe2x80x99escalopes", "germes", "sucré", "écraé", "chinois",
                  "allégée", "entière", "pointe", "sirop", "dérable", "épiceries", "blonds", "effeuillée", "sèches",
                  "épaisse", "Jacques", "pressés", "détaillées", "grandes", "battu", "cube", "carrés", "rond", "prxc3xaat",
                  "cuire", "prendre", "uniquement", "congelés", "garnir", "dxe2x80x99oignons", "fumés", "équeutées",
                  "boulanger", "séchées", "besoin", "casis", "salées", "12,5", "maxc3xafzena", "foncée", "nouveaux",
                  "décorer", "feuilletée", "entiers", "carré", "dxe2x80x98huile", "dxe2x80x98olive", "dxe2x80x98ail",
                  "dégraissée", "chxc3xa2taignes", "galettes", "zestes", "dxe2x80x99oignon", "concasés", "raes",
                  "cerneaux", "moyennes", "forte", "fondu", "fleurette", "coquilles", "doeufs", "froid", "chili",
                  "madère", "gourmands", "doignon", "saké", "cuisses", "danana", "brun", "personne", "peut", "cxc3xb4tes",
                  "penne", "coquillettes", "déjdu", "rxc3xa2pées", "sens", "clou", "garam", "maala", "court-bouillon",
                  "écrémé", "daneth", "tranche", "bouteille", "dilué", "chacune", "queues", "dégraissé", "dépaisseur",
                  "tige", "maison", "céleri-rave", "cxc3xb4té", "confit", "nuoc", "campagne", "choix", "autres", "pelé",
                  "xc3xa9grainxc3xa9", "ciselées", "quatre", "pavés", "ciselés", "traité", "bulbe", "japonais", "bxc3xa2ton",
                  "daperges", "sauvage", "mélangés", "évidées", "bois", "feuilletées", "grose", "hachée",
                  "bouillon", "émincées", "groses", "poivron", "hachés", "poivre", "émincés", "pelées", "concasées",
                  "cuillxc3xa8res", "coupxc3xa9es", "cuillère", "coupxc3xa9", "gro", "coupxc3xa9s", "pincxc3xa9e", "dés",
                  "rxc3xa2pxc3xa9", "hachxc3xa9es", "xc3xa9mincxc3xa9e", "xc3xa9craxc3xa9es", "grosixc3xa8rement",
                  "xc3xa9mincxc3xa9", "quelques", "coupxc3xa9e", "hachxc3xa9", "grose", "hachxc3xa9e", "xc3xa9mincxc3xa9es",
                  "poivre", "groses", "hachxc3xa9s", "poignxc3xa9e", "ciselxc3xa9", "trxc3xa8s", "ciselxc3xa9e", "concentrxc3xa9" 
                  "xc3xa9mincxc3xa9s", "pelxc3xa9es", "concasxc3xa9es", "bien", "rxc3xa2pxc3xa9e"])

ingredientsDictionary = []
dicFinal = dict(ingredientsDictionary)

for i in range(0,5568):
    if(calculaScore(dataframeFR, i) >= 35):
        ingredients = dataframeFR.loc[i, "ingredients"]
        category =dataframeFR.loc[i, "category"]
        criaListaIngredientes(filtraIngredientes(ingredients, stopWords), dicFinal, dataframeFR.loc[i, "_id"], category)

graphSize = criaNos(grafoFR, dict(dicFinal))
criaLinks(grafoFR, graphSize, dicFinal)
defineTops(calculaCentralidade(grafoFR))
#criaHistograma(pmiList)
salvaGrafo(grafoFR)


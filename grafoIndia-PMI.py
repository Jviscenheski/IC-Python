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

def calculaScore(dataframeIN, i):

    score1 = math.log(float(dataframeIN.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframeIN.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeIN.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeIN.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframeIN.loc[i, "numberOfStars"])) + 1.0)
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
            replace("'s", "s").replace("cloves", "clove").replace("peppers", "pepper").replace("olives", "olive").\
            replace("tomatoes", "tomato"). replace("'Water", "water")

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas

def criaNos(grafoUSA, dicFinalIngredients):
    indice = 0
    for i in dicFinalIngredients:
        if(len(dicFinalIngredients[i]) > 11):
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
    nx.drawing.nx_pydot.write_dot(grafoUSA, "grafoINDIA-BAIXO.dot")
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
    top50 = open("top50-INDIA-baixo.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 50):
            top = top + 1
            print(grafoUSA.nodes[item]['ingredient'])
            top50.write(str(grafoUSA.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")

# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']
dataframeIN = pd.DataFrame(list(db.recipesFormated.find({"id": "5"}))) #pega somente os dados dos USA
grafoUSA = nx.Graph()
stopWords = set(stopwords.words('english'))

stopWords.update(["'xc2xbd","tbsp","'75g","spoon","pinch", "juice", "gravy", "chopped", "2", "2" "cups", "soup", "can",
                  "box", "box", "tea", "'50g", "'250ml", "'225ml",
                  "teeth", "taste", "wine", " 2, 2, 3, 4, 5, 6, cream, kingdom, ml, kg, g, tooth, / 2 "," 2/3 "," 1/4 ",
                  "Gems","Fresh","Extract","Ready","Strong","Environment ","Temperature","Biscuit", "package",
                  "flavor", "any", "boiling", "melted", "cans", "200g", "juice", "rasps", "3/4",
                  "'150", "250", "450 ", "170", "gelatin", "biscuits", "slices", "ripe", "full", "optional", "average",
                  "raw", "chemical", "optional", "same", "measure", "liters", "sticks", "grated","roasted",
                  "decorate", "liter", "confectioner", "cream", "fat", "dye", "food", "packaging", "concentrate","ice cream",
                  "cow", "pulp", "fresh", "some", "'syrup", "1kg", "cupcake", "syrup", "red","green", "see", "vegetable",
                  "miscellaneous", "pellets", "cut", "crushed","ground","gut", "total", "pie", "toast", "strips",
                  "'200ml'", "30g", "50g", "Yellow", "yellow", "bitter", "crumpled","kneaded","american", "softened", "angel",
                  "trimmed", "about", "arboreal", "wings", "roast", "baked", "bales", "bar", "base", "baste",
                  "beat", "beats", "beaten", "milkshakes","head", "heads", "hair", "cabins", "goat", "each", "boxes",
                  "caracelinho", "caramelizar", "lump", "cores", "house", "bark", "peels", "fence","clear", "cover", "bought",
                  "length", "common", "conch", "frozen", "frozen", "preserves", "consistency", "cup","cut", "thigh", "thigh",
                  "cooked","cooking", "creamy", "candied", "raw", "cubes", "cube", "cuisine", "short", "decoration",
                  " smoked ", "peeled", "thawed", "deglazed", "shredded", "dehydrated", "dessicated", "diet", "disc",
                  "divided", "sweet", "hard", "bread","drained", "brushed", "dark","crushed", "squeezed", "sliced", "made",
                  "boiling","fine", "finally", "firm", "flakes", "flower", "flowers", "florets","French", "fresh", "form",
                  "cold", "fry", "fruit", "cattle", "bottle", "ice","germ", "gum", "buds", "drops", "grams", "large",
                  "Greek", "thick", "roughly", "hour", "colorless", "English", "integer", "italian", "washed", "vegetables",
                  "lightly", "light","clean", "blender", "liquid", "flat","wood", "mature", "thin", "hands", "mary","medium",
                  "half", "half-bitter", "mint", "best", "Mexican", "mines", "crumb", "crushed", "other", "kids", "mix", "warm",
                  "natural", "needed", "snow","packs", "straw", "sticks", "screw", "paris", "part", "parts", "raisins", "paste",
                  "pectin", "pieces", "chest", "breasts", "peeled", "skin", "sifted", "penne", "small","chopped", "spicy", "brush",
                  "can", "sprinkle", "point", "pot", "little", "plate", "precooked", "preference","black", "ready", "protein",
                  "handful", "quality", "how much", "rooms", "four", "hot","root", "grated","branches","shallow", "ripped",
                  "recipe", "stuffed", "filling","dried", "selective", "semi-skimmed", "separated", "serve", "leftovers",
                  "dessert", "soluble", "assorted","soft", "sufficient", "tablet", "tablets", "stem", "stalks", "size",
                  "seasoning", "tempered","spices", "type", "strips", "glass", "fresh", "tablespoons", "powder",
                  "cups","pounds","boneless","skinless","teapoon","white","minced","ounce","pata","diced","pound","all-purpose",
                  "teaspoons","breat","halve", "teaspoon", "tablespoon", "halved", "leaves", "freshly", "ounces", "bunch",
                  "coarsely", "quartered", "thinly", "finely", "rinsed", "crumbled", "removed", "baby", "bell", "pitted",
                  "Italian", "broth", "extra-virgin", "cubed", "packages", "halves", "juiced", "1-inch", "uncooked",
                  "mixed", "toasted", "'Dressing", "spray", "seeded", "'cooking", "inch", "plain", "1/2-inch", "container",
                  "cored", "whole"])

maisUma = []
for i in range(99,999):
    maisUma.append("'"+str(i))
    maisUma.append("'"+str(i)+"g")
stopWords.update(maisUma)

ingredientsDictionary = []
dicFinal = dict(ingredientsDictionary)

#12167
for i in range(0,967):
    if(calculaScore(dataframeIN, i) <= 15.0):
        ingredients = dataframeIN.loc[i, "ingredients"]
        criaListaIngredientes(filtraIngredientes(ingredients, stopWords), dicFinal, dataframeIN.loc[i, "_id"])

graphSize = criaNos(grafoUSA, dict(dicFinal))
criaLinks(grafoUSA, graphSize, dicFinal)
defineTops(calculaCentralidade(grafoUSA))
salvaGrafo(grafoUSA)


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

def calculaScore(dataframeIT, i):

    score1 = math.log(float(dataframeIT.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if (type(dataframeIT.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeIT.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeIT.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframeIT.loc[i, "numberOfStars"])) + 1.0)
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
            replace("tomatoes", "tomato").replace("d'aglio", "aglio").replace("d'acqua", "acqua").\
            replace("tomates","tomate")

        #criaListaCategorias(ingrediente,category, listaCategoria)

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas

def criaNos(grafoIT, dicFinalIngredients, teste):
    indice = 0
    for i in dicFinalIngredients:
        if(len(dicFinalIngredients[i]) > 11):
            teste.write(i + "\n")
            grafoIT.add_node(indice, ingredient=i, qtdadeReceitas=len(dicFinalIngredients[i]))
            indice = indice +1

    print("NUMERO DE NÓS: " + str(indice))
    return len(grafoIT)

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

def criaLinks(grafoIT, tam ,dicFinal):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafoIT.nodes[m]['ingredient'] != grafoIT.nodes[j]['ingredient'] and grafoIT.has_edge(m,j) == False):
                pA = int(grafoIT.nodes[m]['qtdadeReceitas'])/7794
                pB = int(grafoIT.nodes[j]['qtdadeReceitas'])/7794
                pAB = (calculaReceitasComuns(grafoIT.nodes[m]['ingredient'], grafoIT.nodes[j]['ingredient'], dicFinal))/7794
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafoIT.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI))

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList

def salvaGrafo(grafoIT):
    nx.drawing.nx_pydot.write_dot(grafoIT, "grafoITALIA-BAIXO.dot")
    #nx.write_gml(grafoIT, "grafoIT.gml")

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

def calculaCentralidade(grafoIT):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafoIT)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade

def defineTops(dicionario):
    top50 = open("top100-ITALIA-alto.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 150):
            top = top + 1
            print(grafoIT.nodes[item]['ingredient'])
            top50.write(str(grafoIT.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")

# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']
dataframeIT = pd.DataFrame(list(db.recipesFormated.find({"id": "4"}))) #pega somente os dados da Italia
grafoIT = nx.Graph()
stopWords = set(stopwords.words('italian'))

stopWords.update(["cucchiaio", "pizzico", "succo", "sugo", "tritato", "2", "2" "tazze", "zuppa", "scatola", "scatola",
                  "crema", "regno", "ml", "kg", "g", "dente", "2","2/3","1/4",
                  "Gemme", "Fresco", "Estrai", "Pronto", "Forte", "Ambiente", "Temperatura", "Biscotto", "pacchetto",
                  "flavor", "any", "boiling", "melted", "cans", "200g", "juice", "rasps", "3/4", "gelatina", "biscotti",
                  "fette", "maturo", "pieno", "facoltativo", "medio",
                  "grezzo", "chimico", "opzionale", "stesso", "misura", "litri", "bastoncini", "grattugiato", "arrostito",
                  "decorare", "litro", "confettiere", "crema", "grasso", "tinta", "cibo", "imballaggio", "concentrato",
                  "mucca", "polpa", "fresca", "un po", "sciroppo", "cupcake", "sciroppo", "rosso", "verde", "vedi", "vegetale",
                  "miscellaneous", "pellets", "cut", "crushed", "ground", "gut", "total", "foot", "toast"
                  "Giallo", "giallo", "amaro", "accartocciato", "impastato", "americano", "ammorbidito", "angelo",
                  "tagliato", "circa", "arborea", "ali", "arrosto", "cotto", "balle", "barra",
                  "beat", "beats", "beaten", "milkshakes", "head", "heads", "hair", "cabins", "goat", "each",
                  "caracelinho", "caramelizar", "lump", "colors", "house", "bark", "peels", "fence", "clear", "cover",
                  "lunghezza", "comune", "conchiglia", "congelato", "congelato", "conserva", "consistenza", "tazza",
                  "taglio", "coscia", "cotto", "cucina", "cremoso", "candito", "crudo", "cubetti", "cubo", "cucina", "corto",
                  "affumicato", "sbucciato", "scongelato", "deglazed", "shredded", "disidratato", "disseccato", "diet",
                  "split", "sweet", "hard", "bread", "drenato", "brushed", "dark", "crushed", "squeezed", "sliced",
                  "bollire", "fine", "infine", "fermo", "scaglie", "fiore", "fiori", "ornamenti", "francese", "fresco", "forma",
                  "freddo", "frittura", "frutto", "bovino", "bottiglia", "ghiaccio", "germe", "gomma", "boccioli",
                  "gocce", "grammi","Greco", "spesso", "approssimativamente", "ora", "incolore", "inglese", "intero",
                  "italiano", "lavato", "verdure", "leggero", "leggero", "pulito", "frullatore", "liquido", "piatto",
                  "legno", "maturo", "magro", "mani", "maria", "medio",
                  "mezzo", "mezzo amaro", "menta", "migliore", "messicano", "miniere", "crumb", "schiacciato",
                  "altro", "bambini", "mescolare",
                  "naturale", "necessario", "neve", "pacchetti", "paglia", "bastoncini", "vite", "paris", "parte",
                  "parti", "uvetta", "preferenza", "nero", "pronto", "proteina",
                  "pectina","pezzi", "petto", "petto", "pelati", "pelle", "setacciata", "penne", "piccoli", "tritati",
                  "speziati", "pennello", "può", "cospargere", "puntare", "pentola", "poco", "piatto", "precotto",
                  "manciata", "qualità", "quanto", "stanze", "quattro", "caldo", "radice", "grattugiato", "rami",
                  "superficiale", "strappato",
                  "recipe", "stuffed", "filling", "dried", "selective", "semi-skimmed", "separated", "serve", "leftovers",
                  "dessert", "solubile", "assortito", "morbido", "sufficiente", "tablet", "compresse", "gambo",
                  "steli", "dimensioni", "condimento", "temperato", "spezie", "tipo", "strisce", "vetro", "fresco",
                  "cucchiai", "polvere", "tazze", "libbre", "disossate", "senza pelle", "cucchiai", "bianco", "tritato",
                  "oncia", "zampa", "a cubetti", "sterlina", "per tutti gli usi", "cucchiaini", "respirare", "dimezzare",
                  "cucchiaino", "cucchiaio", "dimezzare", "foglie", "appena", "once","grossolanamente", "squartato",
                  "sottilmente", "finemente", "risciacquato", "sbriciolato", "rimosso", "bambino", "campana",
                  "Italiano", "brodo", "extra vergine", "cubetto", "pacchetti", "metà", "juiced", "1 pollice", "non cotto",
                  "misto", "tostato", "condimento", "spray", "seminato", "cottura", "pollice", "normale", "1/2",
                  "contenitore", "animato", "intero", "extra","uovo", "d'oliva", "tagliate", "vergine", "grattugiata",
                  "freschi","tritate","secco","bicchiere","'olio", "senza","extravergine","'1kg","grandi","tagliata",
                  "fettine","'qualche","spicchi","affettata","pezzettini","spicchio","gixc3xa0","'250ml",
                  "secchi", "velo", "tritata", "'100ml", "pezzetti", "sottili", "macinato", "d'olio", "bustina",
                  "tagliati", "scorza", "medie", "mazzetto", "abbondante", "buccia", "grande", "metxc3xa0", "affettate",
                  "'200ml", "fuso", "dolce", "piccola", "estratto", "semolato", "fresche","salsa", "mais",
                  "noci", "bianca", "nota", "'120ml"])

maisUma = []
for i in range(1,900):
    maisUma.append("'"+str(i))
    maisUma.append("'"+str(i)+"g")
    maisUma.append(("'"+str(i)+"g"))
stopWords.update(maisUma)

ingredientsDictionary = []
dicFinal = dict(ingredientsDictionary)

for i in range(0,4006):
    if(calculaScore(dataframeIT, i) >= 35.0):
        ingredients = dataframeIT.loc[i, "ingredients"]
        criaListaIngredientes(filtraIngredientes(ingredients, stopWords), dicFinal, dataframeIT.loc[i, "_id"])

teste = open("testeITALIA.txt", "a")

graphSize = criaNos(grafoIT, dict(dicFinal), teste)
criaLinks(grafoIT, graphSize, dicFinal)
defineTops(calculaCentralidade(grafoIT))
salvaGrafo(grafoIT)


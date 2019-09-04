import networkx as nx
import pandas as pd
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import math


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


def criaNos(arquivoIN, grafo, lista_todos_total):

    listaTotal =[]
    # ingredienteLL = na lingua local

    fr = 0
    with open(arquivoIN) as fileFR:
        for lineFR in fileFR:
            flag = 1
            for item in listaTotal:
                if(lineFR.split(":")[0].replace("\n", "") == item):
                    for i in range(0, len(grafo)):
                        if(grafo.nodes[i]['ingredienteEN'] == item):
                            grafo.nodes[i]['franca'] = 1
                            flag = 0
                            break
                    break

            if(flag):
                grafo.add_node(fr, ingredienteLL=lineFR.split(":")[0], ingredienteEN=lineFR.split(":")[0].replace("\n", ""),
                               qtdadeReceitas=[0, 0, 0, 0, 0, 0], brasil=0, franca=0, alemanha=0, italia=0, india=1, eua=0, receitas=[])
                fr = fr + 1
                lista_todos_total.write(str(lineFR.split(":")[1]))
                listaTotal.append(lineFR.split(":")[1].replace("\n", ""))
                print("criou na franca: " + lineFR.split(":")[1])


def insereIDreceitasAndScore(dataframeIN):

    # analisando as receitas indianas
    for i in range(0, 967):                                                                    # controla o dataframe
        for j in range(0, len(grafo)):                                                          # controla o grafo
            listIngredient = filtraIngredientes(dataframeIN.loc[i, "ingredients"],
                                                stopWordsIN)                                   # pega os ingredientes de uma receita
            for item in listIngredient:                                                         # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteLL'] == item):                                   # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframeIN, i) <= 15):
                        recipeList.append(dataframeIN.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                     # guarda o id desta receita dentro do nó
                    vetorReceitasPais[1] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeIN, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente in")


# Calcula a quantidade, não é qualitativo!
def calculaReceitasComuns(listIngre1, listIngre2):
    qtdade = 0
    for m in listIngre1:
        for n in listIngre2:
            if m == n:
                qtdade = qtdade + 1
    return qtdade


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


# Com base no PMI
def criaLinks(grafo, tam):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafo.nodes[m]['ingredienteEN'] != grafo.nodes[j]['ingredienteEN'] and grafo.has_edge(m,j) == False):
                pA = int(sum(grafo.nodes[m]['qtdadeReceitas']))/967
                pB = int(sum(grafo.nodes[j]['qtdadeReceitas']))/967
                pAB = (calculaReceitasComuns(grafo.nodes[m]['receitas'], grafo.nodes[j]['receitas']))/967
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafo.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI) + " criou aresta")

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList


def salvaGrafo(grafo):
    nx.drawing.nx_pydot.write_dot(grafo, "INDIA-BAIXO.dot")


def calculaCentralidade(grafo):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafo)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade


def defineTops(dicionario):

    top6 = open("top6-INDIA-baixo.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if (top < 7):
            top6.write(grafo.nodes[item]['ingredienteEN'] + ":" + str(sum(grafo.nodes[item]['qtdadeReceitas'])) + "\n")
            top = top + 1



def geraArquivoTXT(grafo):
    """

    :param grafo: grafo com os links do PMI feitos
    :return: arquivo txt com a quantidade de receitas

    """
    qtdadeReceitas = open("INDIA-qtdadeReceitas-baixo.txt", "a")

    for i in range(len(grafo) - 1):
        print(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "").replace("[", ""))
        qtdadeReceitas.write(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "") + "\n")


def changeArchive(arquivoQuantidade):
    """
    pega o arquivo com a quantidade de receitas e transforma em arquivo binário
    :param arquivoQuantidade:
    :return:
    """
    binarioReceitas = open("INDIA-binarioReceitas-baixo.txt", "a")

    with open(arquivoQuantidade) as file:
        for line in file:
            newLine = 0
            if line != "0":
                newLine = 1

            binarioReceitas.write(str(newLine).replace("[", "").replace(", ", ":").replace("]", "") + "\n")


def makeCombinations(arquivo6top, grafo):

    relations2 = open("INDIA-relations-baixo.txt", "a")
    list6 = []
    dicIngredientes = {}

    with open(arquivo6top) as file:
        for l in file:
            list6.append(l.split(":")[0])

        for item in list6:                               # pega cada linha do arquivo dos 6 top ingredientes - maior centralidade no grafo total
            for m in range(0, len(grafo)):              # pega cada nó do grafo completo
                print(grafo.nodes[m]['ingredienteEN'])
                if (item == grafo.nodes[m]['ingredienteEN']):             # encontra o ingrediente do txt no grafo
                    print("achou desgraça")
                    neighbors = [n for n in grafo.neighbors(m)]     # lista dos vizinhos daquele nó - saber com quais eles têm conexão
                    dicIngredientes[item] = neighbors
                    for n in neighbors:                             # para cada linha do arquivo 6 top txt
                        for ingredient in list6:
                            if(grafo.nodes[n]['ingredienteEN']== ingredient):
                                relations2.write(item+":"+grafo.nodes[n]['ingredienteEN']+":"+str(grafo[n][m]['weight'])+"\n")

    return list6, dicIngredientes


def relations3by3(relations2, grafo, list6, dicionarioIngredientes):

    list6_dupla = []

    print(list6_dupla)


# MAIN

client = MongoClient()
db = client['AllrecipesDB']

dataframeIN = pd.DataFrame(list(db.recipesFormated.find({"id": "5"})))         # pega dados da India

grafo = nx.Graph()

stopWordsIN = set(stopwords.words("english"))
stopWordsIN.update(["'xc2xbd","tbsp","'75g","spoon","pinch", "juice", "gravy", "chopped", "2", "2" "cups", "soup", "can",
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
                  "cored", "whole", "chunk", "boiled", "baking",  "chilli", "chillies", "frying", "piece", "clove"])


lista_todos_total = open("lista-total-todos.txt", "a")
criaNos("top100-INDIA-baixo.txt", grafo, lista_todos_total)
insereIDreceitasAndScore(dataframeIN)
geraArquivoTXT(grafo)
criaLinks(grafo, len(grafo))
salvaGrafo(grafo)
defineTops(calculaCentralidade(grafo))
changeArchive("INDIA-qtdadeReceitas-baixo.txt")
lista6, dicionarioIngredientes = makeCombinations("top6-INDIA-baixo.txt", grafo)
relations3by3("INDIA-relations-baixo.txt", grafo, lista6, dicionarioIngredientes)














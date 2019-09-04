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


def criaNos(arquivoFR, arquivoAL, arquivoIT, grafo, lista_todos_total):
    listaTotal =[]
    # ingredienteLL = na lingua local

    fr = 0
    with open(arquivoFR) as fileFR:
        for lineFR in fileFR:
            flag = 1
            for item in listaTotal:
                if(lineFR.split(":")[1].replace("\n", "") == item):
                    for i in range(0, len(grafo)):
                        if(grafo.nodes[i]['ingredienteEN'] == item):
                            grafo.nodes[i]['franca'] = 1
                            flag = 0
                            break
                    break

            if(flag):
                grafo.add_node(fr, ingredienteLL=lineFR.split(":")[0], ingredienteEN=lineFR.split(":")[1].replace("\n", ""),
                               qtdadeReceitas=[0, 0, 0, 0, 0, 0], brasil=0, franca=1, alemanha=0, italia=0, india=0, eua=0, receitas=[])
                fr = fr + 1
                lista_todos_total.write(str(lineFR.split(":")[1]))
                listaTotal.append(lineFR.split(":")[1].replace("\n", ""))
                print("criou na franca: " + lineFR.split(":")[1])

    al = fr
    with open(arquivoAL) as fileAL:
        for lineAL in fileAL:
            outraFlag = 2
            for k in listaTotal:
                if(lineAL.split(":")[1].replace("\n", "") == k):              # se este ingrediente já estiver adicionado
                    for m in range(0, len(grafo)):
                        if(grafo.nodes[m]['ingredienteEN'] == k):
                            grafo.nodes[m]['alemanha'] = 1
                            outraFlag = 0
                            break
                    break

            if(outraFlag):
                grafo.add_node(al, ingredienteLL=lineAL.split(":")[0], ingredienteEN=lineAL.split(":")[1].replace("\n", ""),
                               qtdadeReceitas=[0, 0, 0, 0, 0, 0], brasil=0, franca=0, alemanha=1, italia=0, india=0, eua=0,
                               receitas=[], score=0)
                al = al + 1
                lista_todos_total.write(str(lineAL.split(":")[1]))
                listaTotal.append(lineAL.split(":")[1].replace("\n", ""))
                print("criou na Alemanha: " + lineAL.split(":")[1])

    it = al
    with open(arquivoIT) as fileIT:
        for lineIT in fileIT:
            outraFlag1 = 3
            for k in listaTotal:
                if(lineIT.split(":")[1].replace("\n","") == k):              # se este ingrediente já estiver adicionado
                    for m in range(0, len(grafo)):
                        if(grafo.nodes[m]['ingredienteEN'] == k):
                            grafo.nodes[m]['italia'] = 1
                            outraFlag1 = 0
                            break
                    break

            if(outraFlag1):
                grafo.add_node(it, ingredienteLL=lineIT.split(":")[0], ingredienteEN=lineIT.split(":")[1].replace("\n",""),
                               qtdadeReceitas=[0, 0, 0, 0, 0, 0], brasil=0, franca=0, alemanha=0, italia=1, india=0, eua=0,
                               receitas=[], score=0)
                it = it + 1
                lista_todos_total.write(str(lineIT.split(":")[1]))
                listaTotal.append(lineIT.split(":")[1].replace("\n", ""))
                print("criou na Italia: " + lineIT.split(":")[1])


def insereIDreceitasAndScore(dataframeFR, dataframeAL, dataframeIT):

    # analisando as receitas francesas
    for i in range(0, 5568):                                                                    # controla o dataframe
        for j in range(0, len(grafo)):                                                          # controla o grafo
            listIngredient = filtraIngredientes(dataframeFR.loc[i, "ingredients"],
                                                stopWordsFR)                                   # pega os ingredientes de uma receita
            for item in listIngredient:                                                         # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteLL'] == item):                                   # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframeFR, i) >= 35):
                        recipeList.append(dataframeFR.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                     # guarda o id desta receita dentro do nó
                    vetorReceitasPais[1] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeFR, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente FR")

    # analisando as receitas alemãs
    for i in range(0, 6985):                                                                    # controla o dataframe
        for j in range(0, len(grafo)):                                                          # controla o grafo
            listIngredient = filtraIngredientes(dataframeAL.loc[i, "ingredients"],
                                                stopWordsAL)                                    # pega os ingredientes de uma receita
            for item in listIngredient:                                                         # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteLL'] == item):                                   # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    if (calculaScore(dataframeAL, i) >= 35):
                        recipeList.append(dataframeAL.loc[i, "_id"])
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    grafo.nodes[j]['receitas'] = recipeList                                     # guarda o id desta receita dentro do nó
                    vetorReceitasPais[2] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeAL, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente AL")

    # analisando as receitas italianas
    for i in range(0, 4006):                                                            # controla o dataframe
        for j in range(0, len(grafo)):                                                  # controla o grafo
            listIngredient = filtraIngredientes(dataframeIT.loc[i, "ingredients"],
                                                stopWordsIT)                            # pega os ingredientes de uma receita
            for item in listIngredient:                                                 # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteLL'] == item):                           # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframeIT, i) <= 15):
                        recipeList.append(dataframeIT.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                            # guarda o id desta receita dentro do nó
                    vetorReceitasPais[3] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeIT, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente IT")


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
                pA = int(sum(grafo.nodes[m]['qtdadeReceitas']))/16560
                pB = int(sum(grafo.nodes[j]['qtdadeReceitas']))/16560
                pAB = (calculaReceitasComuns(grafo.nodes[m]['receitas'], grafo.nodes[j]['receitas']))/16650
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafo.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI) + " criou aresta")

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList


def salvaGrafo(grafo):
    nx.drawing.nx_pydot.write_dot(grafo, "europe-ALTO.dot")


def calculaCentralidade(grafo):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafo)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade


def defineTops(dicionario):

    top6 = open("top6-europe-alto.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if (top < 7):
            top6.write(grafo.nodes[item]['ingredienteEN'] + ":" + str(sum(grafo.nodes[item]['qtdadeReceitas'])) + "\n")
            top = top + 1


def arrayToTSNE(grafo):
    arrayGeral = open("arrayGeral-baixo.txt", "a")

    for i in range(len(grafo) - 1):
        print(str(grafo.nodes[i]['brasil']) + str(grafo.nodes[i]['ingredienteEN']))
        arrayGeral.write(
            str(grafo.nodes[i]['brasil']) + ":" + str(grafo.nodes[i]['franca']) + ":" + str(grafo.nodes[i]['alemanha']) + ":" +
            str(grafo.nodes[i]['italia']) + ":" + str(grafo.nodes[i]['india']) + ":" + str(grafo.nodes[i]['eua']) + "\n")


def geraArquivoTXT(grafo):
    """

    :param grafo: grafo com os links do PMI feitos
    :return: arquivo txt com a quantidade de receitas

    """
    qtdadeReceitas = open("europe-qtdadeReceitas-alto.txt", "a")

    for i in range(len(grafo) - 1):
        print(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "").replace("[", ""))
        qtdadeReceitas.write(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "") + "\n")


def changeArchive(arquivoQuantidade):
    """
    pega o arquivo com a quantidade de receitas e transforma em arquivo binário
    :param arquivoQuantidade:
    :return:
    """
    binarioReceitas = open("europe-binarioReceitas-alto.txt", "a")

    with open(arquivoQuantidade) as file:
        for line in file:
            newLine = [0, 0, 0]
            lineFormated = line.replace(", ",":").replace("]", "").replace("[", "")
            for i in range(0,3):
                print(lineFormated.split(":")[i])
                if lineFormated.split(":")[i] != "0":
                    newLine[i] = 1

            binarioReceitas.write(str(newLine).replace("[", "").replace(", ", ":").replace("]", "") + "\n")


def makeCombinations(arquivo6top, grafo):

    relations2 = open("europe-relations-alto.txt", "a")
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

dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"})))         # pega dados da França
dataframeAL = pd.DataFrame(list(db.recipesFormated.find({"id": "3"})))         # pega dados da Alemanha
dataframeIT = pd.DataFrame(list(db.recipesFormated.find({"id": "4"})))         # pega dados da Italia

grafo = nx.Graph()

stopWordsFR = set(stopwords.words('french'))
stopWordsFR.update(["gro", "dxc3xa9s", "quelques", "grose", "groses", "poivre", "concasxc3xa9es",
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

stopWordsAL = set(stopwords.words("german"))
stopWordsAL.update(["'450", "brauner", "weiche", "entfernt", "scheiben", "geschnitten", "'200", "prise", "griechischer",
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

stopWordsIT = set(stopwords.words("italian"))
stopWordsIT.update(["cucchiaio", "pizzico", "succo", "sugo", "tritato", "2", "2" "tazze", "zuppa", "scatola", "scatola",
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

lista_todos_total = open("lista-total-todos.txt", "a")
criaNos("FR-fr-en-alto.txt", "AL-al-en-alto.txt", "IT-it-en-alto.txt", grafo, lista_todos_total)
#arrayToTSNE(grafo)
insereIDreceitasAndScore(dataframeFR, dataframeAL, dataframeIT)
geraArquivoTXT(grafo)
criaLinks(grafo, len(grafo))
salvaGrafo(grafo)
defineTops(calculaCentralidade(grafo))
changeArchive("europe-qtdadeReceitas-alto.txt")
lista6, dicionarioIngredientes = makeCombinations("top6-europe-alto.txt", grafo)
relations3by3("europe-relations-alto.txt", grafo, lista6, dicionarioIngredientes)














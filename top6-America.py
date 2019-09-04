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


def criaNos(arquivoBR, arquivoUSA, grafo, lista_todos_total):
    br = 0
    listaTotal =[]
    # ingredienteLL = na lingua local

    with open(arquivoBR) as file:
        for line in file:
            lista_todos_total.write(str(line.split(":")[1]))
            grafo.add_node(br, ingredienteLL=line.split(":")[0], ingredienteEN=line.split(":")[1].replace("\n", ""),
                           qtdadeReceitas=[0, 0, 0, 0, 0, 0], brasil=1, franca=0, alemanha=0, italia=0, india=0, eua=0,
                           receitas=[], score=0)
            print("criou no BR: " + line.split(":")[0] + " ou " + line.split(":")[1])
            listaTotal.append(line.split(":")[1].replace("\n", ""))
            br = br + 1

    us = br
    with open(arquivoUSA) as fileUSA:
        for lineUSA in fileUSA:
            outraFlag3 = 2
            for k in listaTotal:
                if(lineUSA.split(":")[0].replace("\n", "") == k):              # se este ingrediente já estiver adicionado
                    for m in range(0, len(grafo)):
                        if(grafo.nodes[m]['ingredienteEN'] == k):
                            grafo.nodes[m]['eua'] = 1
                            outraFlag3 = 0
                            break
                    break

            if(outraFlag3):
                grafo.add_node(us, ingredienteLL=lineUSA.split(":")[0].replace("\n", ""),
                               ingredienteEN=lineUSA.split(":")[0].replace("\n", ""),
                               qtdadeReceitas=[0, 0], brasil=0, franca=0, alemanha=0, italia=0, india=0, eua=1,
                               receitas=[], score=0)
                us = us + 1
                lista_todos_total.write(str(lineUSA.split(":")[0]) + "\n")
                listaTotal.append(lineUSA.split(":")[0].replace("\n", ""))
                print("criou nos EUA: " + lineUSA.split(":")[0])


def insereIDreceitasAndScore(dataframeBR, dataframeUSA):

    # primeiro analisa as receitas brasileiras
    for i in range(0,7794):                                                                     # controla o dataframe                                                                # controla o grafo
        listIngredient = filtraIngredientes(dataframeBR.loc[i, "ingredients"], stopWordsBR)     # pega os ingredientes de uma receita
        for item in listIngredient:                                                             # controla a lista de ingredientes
            for j in range(0, len(grafo)):
                if(grafo.nodes[j]['ingredienteLL'] == item):                                    # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframeBR, i) >= 35):
                        recipeList.append(dataframeBR.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                   # guarda o id desta receita dentro do nó
                    vetorReceitasPais[0] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeBR, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas'] ))
                    print("achou ingrediente BR!")

    # analisa as receitas estadunidenses
    for i in range(0, 12167):                                                                             # controla o dataframe
        for j in range(0, len(grafo)):                                                                    # controla o grafo
            listIngredient = filtraIngredientes(dataframeUSA.loc[i, "ingredients"], stopWordsUSA)         # pega os ingredientes de uma receita
            for item in listIngredient:                                                                   # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteEN'] == item):                                             # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframeUSA, i) >= 35):
                        recipeList.append(dataframeUSA.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                               # guarda o id desta receita dentro do nó
                    vetorReceitasPais[1] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframeUSA, i)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente USA")


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
                pA = int(sum(grafo.nodes[m]['qtdadeReceitas']))/19961
                pB = int(sum(grafo.nodes[j]['qtdadeReceitas']))/19961
                pAB = (calculaReceitasComuns(grafo.nodes[m]['receitas'], grafo.nodes[j]['receitas']))/19961
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafo.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI) + " criou aresta")

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList


def salvaGrafo(grafo):
    nx.drawing.nx_pydot.write_dot(grafo, "BR-USA-TOP6-ALTO.dot")


def calculaCentralidade(grafo):
    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafo)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade


def defineTops(dicionario):

    top6 = open("top6-BR-USA-alto.txt", "a")
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
    qtdadeReceitas = open("BR-USA-TOP6-qtdadeReceitas-alto.txt", "a")

    for i in range(len(grafo) - 1):
        print(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "").replace("[", ""))
        qtdadeReceitas.write(str(grafo.nodes[i]['qtdadeReceitas']).replace(", ",":").replace("]", "") + "\n")

def changeArchive(arquivoQuantidade):
    """
    pega o arquivo com a quantidade de receitas e transforma em arquivo binário
    :param arquivoQuantidade:
    :return:
    """
    binarioReceitas = open("BR-USA-TOP6-binarioReceitas-alto.txt", "a")

    with open(arquivoQuantidade) as file:
        for line in file:
            newLine = [0, 0]
            lineFormated = line.replace(", ",":").replace("]", "").replace("[", "")
            for i in range(0,2):
                print(lineFormated.split(":")[i])
                if lineFormated.split(":")[i] != "0":
                    newLine[i] = 1

            binarioReceitas.write(str(newLine).replace("[", "").replace(", ", ":").replace("]", "") + "\n")

def makeCombinations(arquivo6top, grafo):

    relations2 = open("br-usa-top6-relations-alto.txt", "a")
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

dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))          # pega dados do Brasil
dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))         # pega dados dos USA

grafo = nx.Graph()

stopWordsBR = set(stopwords.words('portuguese'))
stopWordsBR.update(["colheres","pitada", "suco","molho", "picado","2'", "2 '" "picada'","pó", "colher", "extravirgem",
                  "xícara", "xícaras", "\'", "sopa", "lata", "caixinha", "caixa", "chá", "dentes", "gosto", "vinho",
                  ",", "1", "2", "2 '", "3", "4", "5", "6", "creme", "reino", "ml", "kg", "g", "dente", "1/2","2/3", "1/4",
                  "gemas", "fresco", "extrato", "pronto", "forte", "ambiente", "temperatura", "biscoito", "]", "[",
                  "pacote","sabor", "qualquer","fervente", "derretida", "latas", "200g", "'Suco", "raspas", "3/4", "'150", "'250",
                  "'450", "'170", "gelatina", "biscoitos", "rodelas", "maduras", "cheia", "opcional", "levemente",
                  "médias", "cruas", "químico", "opcional", "mesma", "medida", "litros", "paus", "ralado",
                  "torrado", "decorar", "litro", "confeiteiro","cream", "gordura", "corante", "alimentício", "embalagem", "concentrado",
                  "gelado", "vaca", "polpa", "frescos", "'Algumas", "'Calda", "'1kg", "xicara", "xarope", "vermelhos",
                  "vermelho","vermelhas", "vermelha", "verdes", "verde", "veja","vegetal", "variados", "variadas",
                  "untar", "unidades", "umedecer","triturados", "triturado", "trituradas", "triturada",
                  "tripa", "total", "torta", "torrada", "torradas", "tirinhas", "'200ml", "'30g", "'50g", "'60g", "'Caldo", "'Casca",
                  "'Cerca", "'Fatias", "'Folhas", "'Gotas", "'Massa", "'Molho", "'Para", "'Raspas", "'Rodelas", "'Tempero",
                  "1-1/2", "agulhinha", "amanhecido", "amanhecidos", "amarelo", "amarela", "amargo", "amassada", "amassada",
                  "amassadas", "amassado", "amassados", "amaericana", "americano", "americanos", "amolecida", "amolecido",
                  "anéis", "anjo", "aparadas","aproximadamente", "árboreo", "árborio", "asas", "assado", "",
                  "azedo", "balas", "barra", "base", "baste", "batida", "batidas", "batido", "batidos", "biológico", "bolacha",
                  "bolachas", "bolas", "bolo", "bordo", "bovina", "branca", "brancas", "broto", "brotos", "bulbo", "buquês",
                  "cabeça", "cabeças", "cabelo", "cabinhos", "cabra", "cada", "caixas", "caixinhas", "calda", "caldo", "cálice",
                  "caracolinho", "caramelizar", "caroço", "caroços", "casa", "casca", "cascas", "cerca", "clara", "claras",
                  "claro", "cobrir", "comprada", "comprado", "comprimento", "comum", "concha", "conchinha", "condensado",
                  "conforme", "congelada", "congeladas", "congelado", "congelados", "conserva", "consistência", "copo",
                  "copos", "cortada", "cortadas", "cortado", "cortados", "coxa", "coxão", "coxas", "cozida", "cozidas",
                  "cozimento", "cozidos", "cozinhar", "cremoso", "cristal", "cristalizadas", "cruas", "cubinhos", "cubos",
                  "cubo", "culinária", "curto", "decoração", "defumada", "defumado", "descascada", "descascadas",
                  "descascado", "descascados", "descongelada", "descongolado", "desfiada", "desfiado", "desidratada",
                  "desidratado", "desnatado", "desossado", "desossados", "dessalgado", "dica", "diet", "disco", "discos",
                  "dividida", "divididas", "dividido", "divididos", "doce", "duro", "empanar", "enfeitar", "ensopado",
                  "envelope", "envelopes", "escorridas", "escorrida", "escorrido", "escorridos", "escovadas", "escuro",
                  "esfarelado", "esmigalhado", "espessura", "espremido", "espremidos", "espremida", "espremidas", "essência",
                  "estourada", "farelo", "fatia", "fatiada", "fatiadas", "fatiado", "fatiados", "fatias", "feito", "fervendo",
                  "fina", "finas", "fino", "finos", "finalmente", "firme", "firmes", "flocos", "flor", "flores", "floretes",
                  "folha", "folhas", "folhadas", "forma", "formato", "forno", "francês", "francesa", "franceses", "fresca",
                  "fria", "frio", "fritar", "fritura", "fruta", "frutas", "gado", "garrafa", "gelada", "gelo", "generosa",
                  "germe", "goma", "gomos", "gotas", "gramas", "grande", "grandes", "granulado", "granulada", "gravatinha",
                  "grego", "grossas", "grosseiramente", "grosso", "grossos", "hora", "incolor", "inglês", "instantânea",
                  "instantâneo", "integral", "inteira", "inteiras", "inteiro", "inteiros", "italianas", "italiano",
                  "japonês", "lascas", "lavados", "lavado", "lavadas", "lavada", "legumes", "ligeiramente", "light",
                  "limpa", "limpas", "limpo", "limpos", "liquidificador", "líquido", "lisa", "louro", "maço", "maços",
                  "madeira", "madura", "maduras", "maduro", "maduros", "magra", "magro", "mãos", "maria", "massa", "média",
                  "médio", "médios", "médias", "meia", "meio", "meio-amargo", "menta", "melhor", "metade", "metades",
                  "mexicana", "mexicanas", "minas", "miolo", "mirin", "moídas", "moída", "mole", "moído",
                  "miúdos", "mistura", "morno", "morna", "natural", "necessário", "neve", "nota", "osso", "outro", "outra",
                  "pacotes", "palha", "palitos", "parafuso", "paris", "parte", "partes", "passas", "pasta", "peça",
                  "pectina", "pedaçinhos", "pedaço", "pedaços", "peito", "peitos", "pelado", "pelados", "pele", "peneira",
                  "peneirada", "peneiradas", "peneirado", "penne", "pequena", "pequenas", "pequeno", "pequenos",
                  "picada", "picadas", "picadinha", "picadinhas", "picadinho", "picadinhos", "picante", "pincelar", "pitadas",
                  "pode", "polvilhar", "ponto", "pote", "pouco", "povilhar", "prato", "pré-cozida", "preferência", "preta",
                  "pretas", "pronta", "proteína", "punhado", "qualidade", "quanto", "quartos", "quatro", "quente", "quilo",
                  "quiser", "raiz", "raiz-forte", "ralada", "raladas", "ralado", "ralados", "ralo", "rama", "raminho",
                  "raminhos", "ramo", "ramos", "rasa", "rasas", "raso", "rasgadas", "receita", "recheadas", "recheio",
                  "refinada", "refogar", "reservar", "regar", "rodela", "rosa", "rosca", "roxa", "roxas", "roxo", "roxas",
                  "salada", "salgado", "salpicar", "seco", "secos", "seca", "secas", "seleta", "semi-desnatado", "semidesnatado",
                  "sentido", "separadas", "separada", "separados", "servir", "sobras", "sobremesa", "solúvel", "sortidas",
                  "suave", "suficiente", "tablete", "tabletes", "talo", "talos", "tamanho", "tempero", "temperada",
                  "temperado", "temperar", "temperos", "tipo", "tiras", "vidro", "fresca", "cozido", "picado"])

stopWordsUSA = set(stopwords.words('english'))
stopWordsUSA.update(["spoon","pinch", "juice", "gravy", "chopped", "2", "2" "cups", "soup", "can", "box", "box", "tea",
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
                  "cored", "whole", "chunk", "boiled", "baking", "chilli", "chillies", "frying", "clove", "brown"])

lista_todos_total = open("lista-total-todos.txt", "a")
criaNos("BR-pt-en-alto.txt","top100-USA-alto.txt", grafo, lista_todos_total)
#arrayToTSNE(grafo)
insereIDreceitasAndScore(dataframeBR, dataframeUSA)

geraArquivoTXT(grafo)
criaLinks(grafo, len(grafo))
salvaGrafo(grafo)
defineTops(calculaCentralidade(grafo))
changeArchive("BR-USA-TOP6-qtdadeReceitas-alto.txt")
lista6, dicionarioIngredientes = makeCombinations("top6-BR-USA-alto.txt", grafo)
relations3by3("br-usa-top6-relations-alto.txt", grafo, lista6, dicionarioIngredientes)










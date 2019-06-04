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
            replace("branco", "vinho branco").replace("tinto", "vinho tinto").replace("galinha", "caldo de galinha").\
            replace("porco", "carne de porco").replace("suína", "carne de porco").replace("bovina", "carne").\
            replace("cheese", "cream cheese").replace("es", "e").replace("mot", "most")

        #criaListaCategorias(ingrediente,category, listaCategoria)

        if ingrediente not in dicFinalIngredients:
            receitas = []
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas
        else:
            receitas = dicFinalIngredients[ingrediente]
            receitas.append(id)
            dicFinalIngredients[ingrediente] = receitas

def criaNos(grafoBR, dicFinalIngredients):
    indice = 0
    for i in dicFinalIngredients:
        if(len(dicFinalIngredients[i]) > 11):
            grafoBR.add_node(indice, ingredient=i, qtdadeReceitas=len(dicFinalIngredients[i]))
            indice = indice +1

    print("NUMERO DE NÓS: " + str(indice))
    return len(grafoBR)

def calculaReceitasComuns(ingre1, ingre2, dicFinal):
    qtdade = 0
    list1Ingre1 = dicFinal[ingre1]
    list1Ingre2 = dicFinal[ingre2]
    for m in list1Ingre1:
        for n in list1Ingre2:
            if m == n:
                qtdade = qtdade + 1
    return qtdade

def criaLinks(grafoBR, tam ,dicFinal):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafoBR.nodes[m]['ingredient'] != grafoBR.nodes[j]['ingredient'] and grafoBR.has_edge(m,j) == False):
                pA = int(grafoBR.nodes[m]['qtdadeReceitas'])/7794
                pB = int(grafoBR.nodes[j]['qtdadeReceitas'])/7794
                pAB = (calculaReceitasComuns(grafoBR.nodes[m]['ingredient'], grafoBR.nodes[j]['ingredient'], dicFinal))/7794
                if pB != 0 and pA != 0 and pAB != 0:
                    PMI = math.log(pAB/(pA*pB))
                    if PMI >= 0.0 and PMI <= 2.0:
                        grafoBR.add_edge(m, j, weight=PMI)
                        count = count + 1
                        print(str(PMI))

    print("NUMERO DE ARESTAS: " + str(count))
    #return pmiList

def salvaGrafo(grafoBR):
    nx.drawing.nx_pydot.write_dot(grafoBR, "grafoBRBAIXO.dot")
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
    top50 = open("top50BAIXO.txt", "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 50):
            top = top + 1
            print(grafoBR.nodes[item]['ingredient'])
            top50.write(str(grafoBR.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")


# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']
dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"}))) #pega somente os dados do Brasil
grafoBR = nx.Graph()
stopWords = set(stopwords.words('portuguese'))

# Dando um jeito na CRATIVIDADE DO BRASILEIRO
stopWords.update(["colheres","pitada", "suco","molho", "picado","2'", "2 '" "picada'","pó", "colher", "extravirgem",
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
maisUma = []
for i in range(99,999):
    maisUma.append("'"+str(i))
    maisUma.append("'"+str(i)+"g")
stopWords.update(maisUma)

ingredientsDictionary = []
dicFinal = dict(ingredientsDictionary)

for i in range(0,7794):
    if(calculaScore(dataframeBR, i) < 15):
        ingredients = dataframeBR.loc[i, "ingredients"]
        category =dataframeBR.loc[i, "category:"]
        criaListaIngredientes(filtraIngredientes(ingredients, stopWords), dicFinal, dataframeBR.loc[i, "_id"], category)

graphSize = criaNos(grafoBR, dict(dicFinal))
criaLinks(grafoBR, graphSize, dicFinal)
defineTops(calculaCentralidade(grafoBR))
#criaHistograma(pmiList)
salvaGrafo(grafoBR)


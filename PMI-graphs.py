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


def calculaScore(dataframe, i):

    score1 = math.log(float(dataframe.loc[i, "numberOfEvaluations"]) + 1.0, 10)

    if type(dataframe.loc[i, "peopleWhoMade"]) != int:
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframe.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframe.loc[i, "numberOfStars"])) + 1.0) * (
                    (float(dataframe.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    print("Score: "+ str(score))

    return score


def filtraIngredientes(ingredients, stopWords):

    wordsFiltered = []
    for sent in sent_tokenize(str(ingredients)):
        words = word_tokenize(sent)
        filtered_sentence = [w for w in words if not w in stopWords]

        for i in range(len(filtered_sentence)):
            if len(filtered_sentence[i]) > 3 or filtered_sentence[i] == "rum" or filtered_sentence[i] == "sal":
                filtered_sentence[i].replace(filtered_sentence[i], "").replace("\'", "")
                wordsFiltered.append(filtered_sentence[i])
    return wordsFiltered


def insereIDreceitasAndScore(dataframe, grafo, qtdadeReceitas, stopWords):

    # primeiro analisa as receitas brasileiras
    for i in range(0, qtdadeReceitas):                                                                     # controla o dataframe                                                                # controla o grafo
        listIngredient = filtraIngredientes(dataframe.loc[i, "ingredients"], stopWords)     # pega os ingredientes de uma receita
        for item in listIngredient:                                                             # controla a lista de ingredientes
            for j in range(0, len(grafo)):
                if(grafo.nodes[j]['ingredienteLL'] == item):                                    # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    vetorReceitasPais = grafo.nodes[j]['qtdadeReceitas']
                    if (calculaScore(dataframe, i) >= 0.0):
                        recipeList.append(dataframe.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                   # guarda o id desta receita dentro do nó
                    vetorReceitasPais[0] = len(recipeList)
                    grafo.nodes[j]['qtdadeReceitas'] = vetorReceitasPais
                    grafo.nodes[j]['score'] = calculaScore(dataframe, i)

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
            if(grafo.nodes[m]['ingredient'] != grafo.nodes[j]['ingredient'] and grafo.has_edge(m,j) == False):
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


def calculaCentralidade(grafoUSA):

    dicCentralidade = nx.algorithms.centrality.degree_centrality(grafoUSA)
    for item in dicCentralidade:
        print(dicCentralidade[item])

    return dicCentralidade


def defineTops(dicionario, fileName):

    top50 = open(fileName, "a")
    top = 0
    for item in sorted(dicionario, key=dicionario.get, reverse=True):
        if(top < 150):
            top = top + 1
            print(grafo.nodes[item]['ingredient'])
            top50.write(str(grafo.nodes[item]['ingredient']) + ": " + str(dicionario[item]) + "\n")


# "main" a partir daqui
client = MongoClient()
db = client['AllrecipesDB']

dataframeBR = pd.DataFrame(list(db.recipesDatabase.find({"id": "1"})))          # pega dados do Brasil
dataframeFR = pd.DataFrame(list(db.recipesDatabase.find({"id": "2"})))         # pega dados da França
dataframeAL = pd.DataFrame(list(db.recipesDatabase.find({"id": "3"})))         # pega dados da Alemanha
dataframeIT = pd.DataFrame(list(db.recipesDatabase.find({"id": "4"})))         # pega dados da Italia
dataframeIN = pd.DataFrame(list(db.recipesDatabase.find({"id": "5"})))         # pega dados da India
dataframeEUA = pd.DataFrame(list(db.recipesDatabase.find({"id": "6"})))         # pega dados dos USA


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
                  "temperado", "temperar", "temperos", "tipo", "tiras", "vidro", "fresca", "cozido", "picado",
                    "finamente", "partido", "dedo", "moça", "cheias", "refinado", "cobertura", "usar", "vontade",
                    "substituir", "papel", "americana", "corda", "frito", "caso", "fica", "rolo", "escamas", "reserve",
                    "menos", "e/ou", "diagonais", "defumados", "tostadas", "preto", "porto", "torrados", "crespa",
                    "significa", "origem", "nome", "produto", "porque", "aromatizado", "desse", "real", "mini",
                    "alguns", "agosto", "aguardente", "dourada", "dourado", "colocar", "cima", "abaixo", "prefiro",
                    "fininha", "dormidos", "embebidos", "escolha", "escovados", "barbas", "grossamente", "passada",
                    "outras", "iguais", "namorado", "próprio", "dissolvidos", "quadradinho", "conservada",
                    "canecas", "caneca", "terra", "longitudinais", "recobrir", "discreta", "misturar", "hidratar",
                    "toalha", "dose", "gossas", "preparar", "misturadas", "precisar", "parboilizado", "pastoso",
                    "casquinhas", "cheiro", "macia", "engrossar", "diluído", "pouquinho", "aferventados", "peneirados",
                    "vidros", "pistola", "lâminas", "derretidas", "isolada", "quadradinhos", "folhada", "coloridos",
                    "espinho", "salada", "colherchá", "baiano", "barrigada", "moido", "frutos", "semtes", "usado",
                    "esfarele", "totalmente", "fiquem", "visíveis", "potes", "pessoas", "entrecosto",
                    "guarnecer", "primeira", "cerefólio", "durante", "noite", "joelhos", "maria®", "doces",
                    "cura", "derretido", "culinário", "enrolar", "colhere", "caramelizadas", "filetadas",
                    "quebrado", "moídos", "pequana", "próprias", "assar", "natural®", "royal", "possa",
                    "fogo", "grossa", "esmagados", "marca", "deste", "ingrediente", "deve - se", "derreta",
                    "calor", "amarelos", "sobre", "raíz", "bolinha", "cavala", "iraniano", "cubinho",
                    "músculo", "italianos", "bombons", "adoçado", "variar", "brandy", "crua", "tigo", "copinhos",
                    "tirinha", "anis", "estrelado", "mação", "separado", "fradinho", "conhecido", "lugares",
                    "catado", "limao", "folhados", "proteína", "Isolada", "condimento", "estrogonofe", "igual",
                    "sobras", "refogados", "raspada", "escaldado", "poró", "miudinha", "picles", "desossada",
                    "xantana", "pontas", "roxos", "durinha", "talinhos", "kama", "missô", "dúzia", "dúzias",
                    "debtes", "laminado", "toscanas", "pronto / sal", "grosso / sal", "capa", "temperados",
                    "patas", "king", "crab", "gigante", "taiti", "itália", "nanicas", "rosas", "queimado",
                    "moça®", "femento", "teor", "espiral", "bico", "carioquinha", "mulatinho", "espigas", "fraldinha",
                    "texturizada", "holandesa", "ementhal", "bengala", "grano", "leia", "vertical", "macios",
                    "minivagens", "pedacinho", "selvagem", "redonda", "guardanapos", "pano", "amarrar", "bengalas",
                    "amanhecidas", "pedacinhos", "branco®", "tira", "frangélico", "mista", "salgada", "azul",
                    "miúda", "toscana", "impalpável", "acrescente", "cores", "bandeja", "paris", "moela", "quadrados",
                    "pequi", "vegetais", "pecorino", "coxas / sobrecoxas", "passarinho", "fininhas", "enlatado",
                    "geléia", "fundo", "forminha", "forminhas", "passar", "docinhos", "baguete", "media", "moscatel",
                    "coulis", "ambos", "glúten", "colhers", "quibe", "garganta", "manjeicão", "Tirolez®", "apenas",
                    "munguzá", "cozinhá - la", "maior", "alumínio", "largura", "empacotar", "pesadas", "coma",
                    "adoçada", "dois", "fava", "porção", "descongeladas", "vanille", "buquê", "envelhecida",
                    "compre", "prepare", "umas", "refogado", "Emmental", "fibra", "costelinhas", "churrasco",
                    "Knorr®", "pescadas", "cracker", "cozinha", "receitas", "removidos", "redondo", "superfície",
                    "choco", "Krispies®", "esmagado", "pitadinha", "filtrada", "materno", "fórmula", "frade",
                    "rubi", "recheados", "crepe", "tradicional", "mesclado", "normal", "depende", "refratário",
                    "ninho®", "codensado", "nestlé®", "cupuaçu", "unidade", "colorido", "pudim", "punhados",
                    "plástico", "saco", "dianteiro", "especial", "dura", "passatempo®", "maltesers", "confeitos",
                    "coisa", "cheio", "morno / frio", "nanica", "sabores", "diferentes", "dietética", "kefir",
                    "horizontal", "confeitos"])

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

stopWordsEUA = set(stopwords.words('english'))
stopWordsEUA.update(["spoon","pinch", "juice", "gravy", "chopped", "2", "2" "cups", "soup", "can", "box", "box", "tea",
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

unitValidation = []

for i in range(1, 2000):
    unitValidation.append(str(i))
    unitValidation.append("'"+str(i))
    unitValidation.append(str(i)+"ml")
    unitValidation.append("'"+str(i)+"g")


stopWordsBR.update(unitValidation)
stopWordsFR.update(unitValidation)
stopWordsAL.update(unitValidation)
stopWordsIT.update(unitValidation)
stopWordsIN.update(unitValidation)
stopWordsEUA.update(unitValidation)


#countries = {"Brasil": [7794, stopWordsBR, dataframeBR, [1, 0, 0, 0, 0, 0]], "França": [5568, stopWordsFR, dataframeFR,
 #           [0, 1, 0, 0, 0, 0]], "Alemanha": [6984, stopWordsAL, dataframeAL, [0, 0, 1, 0, 0, 0]],
countries = {"Itália": [4005, stopWordsIT, dataframeIT, [0, 0, 0, 1, 0, 0]],
             "Índia": [966, stopWordsIN, dataframeIN, [0, 0, 0, 0, 1, 0]],
             "EUA": [12167, stopWordsEUA, dataframeEUA, [0, 0, 0, 0, 0, 1]]}

for country in countries:
    grafo = nx.Graph()
    ingredientsDictionary = []
    dicFinal = dict(ingredientsDictionary)
    for i in range(0, countries[country][0]):
        if calculaScore(countries[country][2], i) >= 0.0:
            ingredients = countries[country][2].loc[i, "ingredients"]
            newIngredientsList = []
            for item in ingredients:
                newitem = item.replace("'", "").lower()
                newIngredientsList.append(newitem)
            criaListaIngredientes(filtraIngredientes(newIngredientsList, countries[country][1]), dicFinal,
                                  countries[country][2].loc[i, "_id"])

    graphSize = criaNos(grafo, dict(dicFinal), countries[country][3])
    criaLinks(grafo, graphSize, dicFinal)
    defineTops(calculaCentralidade(grafo), country + "TOTAL.txt")
    salvaGrafo(grafo, country + ".dot")
    grafo.clear()

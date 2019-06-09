import networkx as nx
import pandas as pd
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import math

def filtraIngredientes(ingredients,stopWordsUSA):
    wordsFiltered = []
    for sent in sent_tokenize(str(ingredients)):
        words = word_tokenize(sent)
        filtered_sentence = [w for w in words if not w in stopWordsUSA]

        for i in range(len(filtered_sentence)):
            if len(filtered_sentence[i]) > 3 or filtered_sentence[i] == "rum" or filtered_sentence[i] == "sal":
                filtered_sentence[i].replace(filtered_sentence[i], "").replace("\'", "")
                wordsFiltered.append(filtered_sentence[i])
    return wordsFiltered

def criaNos(arquivoBR, arquivoUSA, arquivoFR, grafo, listaTotalBR_USA_FR):
    br = 0
    listaTotal =[]

    with open(arquivoBR) as file:
        for line in file:
            listaTotalBR_USA_FR.write(str(line.split(":")[1]))
            grafo.add_node(br, ingredientePT=line.split(":")[0], ingredienteEN=line.split(":")[1].replace("\n", ""),
                           qtdadeReceitas=0, brasil=1, eua=0, franca=0,receitas=[])
            print("criou no: " + line.split(":")[0] + " ou " + line.split(":")[1])
            listaTotal.append(line.split(":")[1].replace("\n", ""))
            br = br + 1

    us = br
    with open(arquivoUSA) as fileUSA:
        for lineUSA in fileUSA:
            flag = 1
            for item in listaTotal:
                if(lineUSA.split(":")[0] == item):
                    for i in range(0, len(grafo)):
                        if(grafo.nodes[i]['ingredienteEN'] == item):
                            grafo.nodes[i]['eua'] = 1
                            print("BRASIL E USA")
                            flag = 0
                            break
                    break

            if(flag):
                grafo.add_node(us, ingredientePT="", ingredienteEN=lineUSA.split(":")[0].replace("\n", ""),
                               qtdadeReceitas=0, brasil=0, eua=1, franca=0, receitas=[])
                us = us + 1
                listaTotalBR_USA_FR.write(str(lineUSA.split(":")[0]))
                listaTotal.append(lineUSA.split(":")[0].replace("\n", ""))
                print("criou no USA: " + lineUSA.split(":")[0])

    fr = us
    with open(arquivoFR) as fileFR:
        for lineFR in fileFR:
            outraFlag = 2
            for k in listaTotal:
                if(lineFR.split(":")[1].replace("\n", "") == k):              # se este ingrediente já estiver adicionado
                    for m in range(0, len(grafo)):
                        if(grafo.nodes[m]['ingredienteEN'] == k):
                            grafo.nodes[m]['franca'] = 1
                            print("BRASIL, USA E FRANCA")
                            outraFlag = 0
                            break
                    break

            if(outraFlag):
                grafo.add_node(fr, ingredientePT="", ingredienteEN=lineFR.split(":")[1].replace("\n", ""),
                               qtdadeReceitas=0, brasil=0, eua=0, franca=1, receitas=[])
                fr = fr + 1
                listaTotalBR_USA_FR.write(str(lineFR.split(":")[1]))
                listaTotal.append(lineFR.split(":")[1].replace("\n", ""))
                print("criou na Franca: " + lineFR.split(":")[1])

def insereIDreceitas(dataframeBR, dataframeUSA):

    # primeiro analisa as receitas brasileiras
    for i in range(0,7794):                                                                     # controla o dataframe                                                                # controla o grafo
        listIngredient = filtraIngredientes(dataframeBR.loc[i, "ingredients"], stopWordsBR)     # pega os ingredientes de uma receita
        for item in listIngredient:                                                             # controla a lista de ingredientes
            for j in range(0, len(grafo)):
                if(grafo.nodes[j]['ingredientePT'] == item):                                    # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    recipeList.append(dataframeBR.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                     # guarda o id desta receita dentro do nó
                    grafo.nodes[j]['qtdadeReceitas'] = len(recipeList)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas'] ))
                    print("achou ingrediente BR!")

    # analisa as receitas estadunidenses
    for i in range(0, 12167):                                                                             # controla o dataframe
        for j in range(0, len(grafo)):  # controla o grafo
            listIngredient = filtraIngredientes(dataframeUSA.loc[i, "ingredients"], stopWordsUSA)         # pega os ingredientes de uma receita
            for item in listIngredient:                                                                   # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteEN'] == item):                                             # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    recipeList.append(dataframeUSA.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                               # guarda o id desta receita dentro do nó
                    grafo.nodes[j]['qtdadeReceitas'] = len(recipeList)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente USA")

    # analisando as receitas francesas
    for i in range(0, 5568):                                                                             # controla o dataframe
        for j in range(0, len(grafo)):  # controla o grafo
            listIngredient = filtraIngredientes(dataframeFR.loc[i, "ingredients"], stopWordsUSA)         # pega os ingredientes de uma receita
            for item in listIngredient:                                                                   # controla a lista de ingredientes
                if (grafo.nodes[j]['ingredienteEN'] == item):                                             # se o ingrediente procurado estiver dentro da receita
                    recipeList = grafo.nodes[j]['receitas']
                    recipeList.append(dataframeFR.loc[i, "_id"])
                    grafo.nodes[j]['receitas'] = recipeList                                               # guarda o id desta receita dentro do nó
                    grafo.nodes[j]['qtdadeReceitas'] = len(recipeList)
                    print("qtdade  " + str(grafo.nodes[j]['qtdadeReceitas']))
                    print("achou ingrediente FR")


# Calcula a quantidade, não é qualitativo!
def calculaReceitasComuns(listIngre1, listIngre2):
    qtdade = 0
    for m in listIngre1:
        for n in listIngre2:
            if m == n:
                qtdade = qtdade + 1
    return qtdade

# Com base no PMI
def criaLinks(grafo, tam):
    count = 0
    for m in range(0, tam):
        for j in range(0, tam):
            if(grafo.nodes[m]['ingredienteEN'] != grafo.nodes[j]['ingredienteEN'] and grafo.has_edge(m,j) == False):
                pA = int(grafo.nodes[m]['qtdadeReceitas'])/19961
                pB = int(grafo.nodes[j]['qtdadeReceitas'])/19961
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
    nx.drawing.nx_pydot.write_dot(grafo, "grafoBR-USA-FR-ALTO.dot")

client = MongoClient()
db = client['AllrecipesDB']
dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))          # pega dados do Brasil
dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))         # pega dados dos EUA
dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"})))         # pega dados da França
grafo = nx.Graph()

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
                  "cored", "whole"])

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

listaTotalBR_USA_FR = open("listaTotalBR_USA_FR.txt", "a")
criaNos("BR-pt-en-alto.txt", "top50-USA-alto.txt", "FR-fr-en-alto.txt", grafo, listaTotalBR_USA_FR)
insereIDreceitas(dataframeBR, dataframeUSA)
criaLinks(grafo, len(grafo))
salvaGrafo(grafo)

#for i in range(0, len(grafo)):
 #   print(grafo.nodes[i])













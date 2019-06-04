from pymongo import MongoClient
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
from wordcloud import WordCloud

nltk.download('stopwords')
nltk.download('punkt')

client = MongoClient()
db = client['AllrecipesDB']
data = db.recipesFormated.find()        #pega todos os valores do banco

# dataframeBR = pd.DataFrame(list(db.recipesFormated.find({"id": "1"})))
# dataframeBR.insert(10, "Score", 0)

abacaxiBR = 0
abacaxiFR = 0
abacaxiGR = 0
abacaxiIT = 0
abacaxiIN = 0
abacaxiUSA = 0
wordsFiltered = []

# for i in range(0,7794):
#     score1 = math.log(float(dataframeBR.loc[i,"numberOfEvaluations"]) + 1.0, 10)
#
#     if(type(dataframeBR.loc[i, "peopleWhoMade"]) != int):
#         score2 = (math.log(1.0, 10))
#     else:
#         score2 = (math.log(float(dataframeBR.loc[i, "peopleWhoMade"]) + 1.0, 10))
#
#     score3 = ((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeBR.loc[i, "numberOfStars"])) + 1.0)
#     score = (score3 + (score2 + score1))
#     dataframeBR.loc[i,"Score"] = score

#     if(score < 5.0):
#         #if(score < 35.0):
#         #print(str(dataframeBR.loc[i, "ingredients"]))
#         data = (str(dataframeBR.loc[i, "ingredients"]))
#         stopWords = set(stopwords.words('portuguese'))
#         stopWords.update(["colheres","pitada", "suco","molho", "picado","2'", "2 '" "picada'","pó", "colher", "xícara", "xícaras", "\'", "sopa", "lata", "caixinha", "caixa", "chá", "dentes", "gosto", ",", "1", "2", "2 '", "3", "4", "5", "6", "creme", "reino", "branco", "ml", "kg", "g", "dente"])
#         words = word_tokenize(data)
#
#         for w in words:
#             if w not in stopWords:
#                 w.replace("d'", "").replace("\'", "")
#                 wordsFiltered.append(w)
#
# # Create a list of word
# text = str(wordsFiltered)
# # Create the wordcloud object
# wordcloud = WordCloud(collocations=False, width=480, height=480, margin=0, background_color = 'white').generate(text.replace("\'", "").replace("picada", "").replace("cortada", "").replace("pedaços", ""))
#
# # Display the generated image:
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.margins(x=0, y=0)
# plt.show()

#plt.hist(dataframeBR["Score"], bins=50, normed=True, cumulative=True, label='CDF DATA',
          #histtype='step', alpha=0.55, color='blue')

# dataframeFR = pd.DataFrame(list(db.recipesFormated.find({"id": "2"})))
# dataframeFR.insert(10, "Score", 0)
#
# for i in range(0,5568):
#     score1 = math.log(float(dataframeFR.loc[i,"numberOfEvaluations"]) + 1.0, 10)
#
#     if(type(dataframeFR.loc[i, "peopleWhoMade"]) != int):
#         score2 = (math.log(1.0, 10))
#     else:
#         score2 = (math.log(float(dataframeFR.loc[i, "peopleWhoMade"]) + 1.0, 10))
#
#     score3 = ((float(dataframeFR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeFR.loc[i, "numberOfStars"])) + 1.0)
#     score = (score3 + (score2 + score1))
#     if (score > 28):
#         abacaxiFR = abacaxiFR + 1
#     dataframeFR.loc[i,"Score"] = score
#
# dataframeGR = pd.DataFrame(list(db.recipesFormated.find({"id": "3"})))
# dataframeGR.insert(10, "Score", 0)
#
# for i in range(0,6984):
#     score1 = math.log(float(dataframeGR.loc[i,"numberOfEvaluations"]) + 1.0, 10)
#
#     if(type(dataframeGR.loc[i, "peopleWhoMade"]) != int):
#         score2 = (math.log(1.0, 10))
#     else:
#         score2 = (math.log(float(dataframeGR.loc[i, "peopleWhoMade"]) + 1.0, 10))
#
#     score3 = ((float(dataframeGR.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeGR.loc[i, "numberOfStars"])) + 1.0)
#     score = (score3 + (score2 + score1))
#     if (score > 28):
#         abacaxiGR = abacaxiGR + 1
#     dataframeGR.loc[i,"Score"] = score
#
# dataframeIT = pd.DataFrame(list(db.recipesFormated.find({"id": "4"})))
# dataframeIT.insert(10, "Score", 0)
#
# for i in range(0,4005):
#     score1 = math.log(float(dataframeIT.loc[i,"numberOfEvaluations"]) + 1.0, 10)
#
#     if(type(dataframeIT.loc[i, "peopleWhoMade"]) != int):
#         score2 = (math.log(1.0, 10))
#     else:
#         score2 = (math.log(float(dataframeIT.loc[i, "peopleWhoMade"]) + 1.0, 10))
#
#     score3 = ((float(dataframeIT.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeIT.loc[i, "numberOfStars"])) + 1.0)
#     score = (score3 + (score2 + score1))
#     if (score > 28):
#         abacaxiIT = abacaxiIT + 1
#     dataframeIT.loc[i,"Score"] = score
#
dataframeIN = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))
dataframeIN.insert(10, "Score", 0)

for i in range(0,12166):
    score1 = math.log(float(dataframeIN.loc[i,"numberOfEvaluations"]) + 1.0, 10)

    if(type(dataframeIN.loc[i, "peopleWhoMade"]) != int):
        score2 = (math.log(1.0, 10))
    else:
        score2 = (math.log(float(dataframeIN.loc[i, "peopleWhoMade"]) + 1.0, 10))

    score3 = ((float(dataframeIN.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeIN.loc[i, "numberOfStars"])) + 1.0)
    score = (score3 + (score2 + score1))
    if(score > 28):
        abacaxiIN = abacaxiIN + 1
    dataframeIN.loc[i,"Score"] = score

    if (dataframeIN.loc[i, "numberOfStars"] < 2.0):
        data = (str(dataframeIN.loc[i, "ingredients"]))
        stopWords = set(stopwords.words('english'))
        stopWords.update(
               ["cup", "teaspoon", "teaspoons", "tablespoon", "tablespoons", "ounce", "chopped", "sliced", "cups",
                 "taste", "diced", "white", "pound", "ground", "caster", "100g", "fresh", "finely", "175g", "leaves", "red", "xc2xbd"
                "paste", "needed", "green", "tsp", "water", "grated", "xc2xbd", "powder", "tbsp", "e", "a", "i", "'", " "], "1/2", "1/4", "black")
        words = word_tokenize(data)

        for w in words:
           if w not in stopWords:
               if len(w) > 2 and w != "1/2" and w != "1/4" and w != "paste" and w != "large" and w != "'275g" and w != "black" and w != "crushed" and w != "mashed":
                   w.replace("d'", "").replace("\'", "").replace("xc2xbd", "").replace(",", "")
                   wordsFiltered.append(w)

counts = dict(Counter(wordsFiltered).most_common(5))

for i in counts:
    if len(i) > 2:
        print (i + ":" + str(counts[i]))


letter_counts = Counter(counts)
df = pd.DataFrame.from_dict(letter_counts, orient='index')
df.plot(kind='bar')

#for i in range(len(wordsFiltered)):
 #   print(wordsFiltered[i])

#pd.Series(dict(Counter(counts))).value_counts().plot('hist')

'''
letter_counts = Counter(wordsFiltered)
df = pd.DataFrame.from_dict(letter_counts, orient='index')
df.plot(kind='bar')
'''

plt.show()

'''
# Create the wordcloud object
wordcloud = WordCloud(collocations=False, width=480, height=480, margin=0, background_color='white').generate(
    text.replace("\'", ""))

# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()

# #
# dataframeUSA = pd.DataFrame(list(db.recipesFormated.find({"id": "6"})))
# dataframeUSA.insert(10, "Score", 0)
#
# for i in range(0,12166):
#     score1 = math.log(float(dataframeUSA.loc[i,"numberOfEvaluations"]) + 1.0, 10)
#
#     if(type(dataframeUSA.loc[i, "peopleWhoMade"]) != int):
#         score2 = (math.log(1.0, 10))
#     else:
#         score2 = (math.log(float(dataframeUSA.loc[i, "peopleWhoMade"]) + 1.0, 10))
#
#     score3 = ((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)*((float(dataframeUSA.loc[i, "numberOfStars"])) + 1.0)
#     score = (score3 + (score2 + score1))
#     if (score > 28):
#         abacaxiUSA = abacaxiUSA + 1
#     dataframeUSA.loc[i,"Score"] = score
#'''







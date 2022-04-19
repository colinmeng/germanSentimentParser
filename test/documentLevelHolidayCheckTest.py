import json
from statistics import median
from statistics import mean
from statistics import stdev
from sentimentParser import lexicon
from sentimentParser import calculateSentiment as sa
import spacy


SAMPLE_SIZE = 0
LEXICON_MODE = "no neutral"
LEXICON_PATH = "sentimentLexicon.json"
SPACY_MODEL = "de_core_news_lg"

TEST_DATASET= "balancedHolidayCheck200.tsv"

#decides if the sentiment is per aspect or per sentence
PER_SENTENCE = False


nlp = spacy.load(SPACY_MODEL)
lex = lexicon.Lexicon(LEXICON_PATH,LEXICON_MODE)

holidayCheckFile = open(f"balancedDataSets//{TEST_DATASET}","r",encoding="UTF-8")
lines = holidayCheckFile.readlines()

# error log
errorLog = open("holidayCheckErrorLog.txt","w",encoding="UTF-8")
# create result container
sentiments = []

for i in range(0,6):
    sentiments.append([])

totalLineCount = len(lines)

if SAMPLE_SIZE > 0:
    if SAMPLE_SIZE < totalLineCount:
        totalLineCount = SAMPLE_SIZE

lineCount = 0
invalidLinesCount = 0
errorLinesCount = 0

print(f"{totalLineCount} lines to analyze.")

for line in lines:

    #progressBar
    if lineCount:
        percentageBefore = "{:.0f}".format(float(lineCount+invalidLinesCount+errorLinesCount) * 100 / totalLineCount) 
    else:
        percentageBefore = 0.0

    parts = line.split("\t")

    stars = parts[1]
    message = parts[2]

    if stars == "null":
        invalidLinesCount += 1
        continue
        
    else:
        stars = int(stars) - 1 #1-6 --> 0-5
        

    

    docSentiment = sa.getDocumentSentiment(message,lex,nlp,PER_SENTENCE)
    lineCount += 1

    sentiments[stars].append(docSentiment)
    
    #progress Bar
    percentageDone = "{:.0f}".format(float((lineCount+invalidLinesCount+errorLinesCount) * 100) / totalLineCount)

    if percentageBefore != percentageDone:
        print(percentageDone)

    # stop if sample size reached

    if(lineCount + invalidLinesCount + errorLinesCount) >= totalLineCount:
        break

data = dict()

data["sentiments"] = sentiments
data["lineCount"] = lineCount
data["invalidLinesCount"] = invalidLinesCount
data["errorLinesCount"] = errorLinesCount

#logFileName = TEST_DATASET.split(".")[0]
logFileName = f"{totalLineCount}_{LEXICON_MODE}_result.json"

file = open(logFileName,"w",encoding="UTF-8")
json.dump(data,file)

file.close()
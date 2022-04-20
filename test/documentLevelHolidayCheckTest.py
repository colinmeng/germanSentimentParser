# This script takes a subset of the holidayCheck dataset by Oliver Guhr
# and runs a document level sentiment analysis

import json
from statistics import median
from statistics import mean
from statistics import stdev
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon
import spacy


SAMPLE_SIZE = 0
LEXICON_MODE = "no neutral"
LEXICON_PATH = "lexicon//sentimentLexicon.json"
SPACY_MODEL = "de_core_news_lg"

TEST_DATA_PATH = "test//testData//hcTunesia//balancedDataSets"
TEST_DATASET= "balancedHolidayCheck200.tsv"
LOGS_PATH = "test//logs//documentLevel"

#decides if the sentiment is per aspect or per sentence
PER_SENTENCE = False


nlp = spacy.load(SPACY_MODEL)
lex = lexicon.Lexicon(LEXICON_PATH,LEXICON_MODE)

holidayCheckFile = open(f"{TEST_DATA_PATH}//{TEST_DATASET}","r",encoding="UTF-8")
lines = holidayCheckFile.readlines()

# error log
errorLogName = TEST_DATASET.split(".")[0]

errorLog = open(f"{LOGS_PATH}//{errorLogName}.txt","w",encoding="UTF-8")
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
        

    
    # do the sentiment analysis
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

fullLogFilePath = f"{LOGS_PATH}//{logFileName}"

file = open(fullLogFilePath,"w",encoding="UTF-8")
json.dump(data,file)

file.close()
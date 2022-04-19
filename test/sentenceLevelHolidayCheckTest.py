
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon
import spacy

# settings
SAMPLE_SIZE = 250
STARS_RATING = 1 # 1 to 6
MIN_LETTERS_PER_SENTENCE = 15
LEXICON_MODE = "no neutral"

# paths
LEXICON_PATH = "lexicon//sentimentLexicon.json"
DATASET_PATH = "test//testData//hcTunesia//balancedDataSets"
TEST_DATASET = "balancedHolidayCheck2k.tsv"
LOG_PATH = "test//logs//sentenceLevel"



fileName = f"{STARS_RATING-1}Star_{SAMPLE_SIZE}"

lex = lexicon.Lexicon(LEXICON_PATH,LEXICON_MODE)
nlp = spacy.load("de_core_news_lg")

path = "balancedHolidayCheck2k.tsv"
holidayCheckFile = open(f"{DATASET_PATH}//{TEST_DATASET}","r",encoding="UTF-8")

lines = holidayCheckFile.readlines()
linesCount = len(lines)

posLog = open(f"{LOG_PATH}//{fileName}_POS.csv","w",encoding="UTF-8")
negLog = open(f"{LOG_PATH}//{fileName}_NEG.csv","w",encoding="UTF-8")
neutralLog = open(f"{LOG_PATH}//{fileName}_NEU.txt","w",encoding="UTF-8")

statsLog = open(f"{LOG_PATH}//{fileName}_STATS.txt","w",encoding="UTF-8")

posLog.write("sentiment,sentence,missingWords,polarity\n")
negLog.write("sentiment,sentence,missingWords,polarity\n")

dataPointsCollected = 0
negCount = 0
posCount = 0
neuCount = 0
meanPos = 0
meanNeg = 0

for i in range(0,linesCount):
    line = lines[i]

    parts = line.split("\t")

    stars = parts[1]
    if stars == "null":
        stars = - 1

    stars = float(stars)

    if stars != STARS_RATING:
        continue

    message = parts[2]
    message = message.replace(","," ").strip()



    doc = nlp(message)
    sentences = []

    for sentence in doc.sents:
        sentences.append(sentence.text)


    for k in range (0, len(sentences)):
        sentence = sentences[k]

        if len(sentence.strip()) <= MIN_LETTERS_PER_SENTENCE:
            continue

        sentenceSentiment = sa.getDocumentSentiment(sentences[k],lex,nlp)
        missingWords = sa.getMissingWords(sentences[k],lex,nlp)
        mwString = ""
        for mw in missingWords:
            mwString += f" {mw}"

        dataPointsCollected += 1

        if sentenceSentiment == 0:
            neutralLog.write(f"{sentence}\n")
            neuCount += 1
            continue

        if sentenceSentiment > 0:
            posLog.write(f"{'{:.2f}'.format(sentenceSentiment)},{sentence},{mwString},0\n")
            posCount += 1
            meanPos += sentenceSentiment
        else:
            negLog.write(f"{'{:.2f}'.format(sentenceSentiment)},{sentence},{mwString},0\n")
            negCount += 1
            meanNeg += sentenceSentiment
        

    if dataPointsCollected >= SAMPLE_SIZE:
        break

statsLog.write(f"files: {fileName}_(POS.csv|NEG.csv|NEU.txt)\n")
statsLog.write(f"POS\t{posCount}({'{:.0f}'.format(posCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(meanPos/posCount)}\n")
statsLog.write(f"NEG\t{negCount}({'{:.0f}'.format(negCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(meanNeg/negCount)}\n")
statsLog.write(f"NEU\t{posCount}({'{:.0f}'.format(neuCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(0)}\n")

posLog.close()
neutralLog.close()
negLog.close()
statsLog.close()


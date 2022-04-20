# this script splits documents of a defined Star rating into sentences
# and calculates sentence level results
# keep in mind that this is not working great, because the grammar and spelling is horrible in this dataset
# furthermore it is impossible for my program to identify one important class of sentiment phrases: desireable facts

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon
import spacy

# Change this
SAMPLE_SIZE = 250
STARS_RATING = 1 # 1 to 6
# exclude Sentences that are obviosly to short
MIN_LETTERS_PER_SENTENCE = 15
LEXICON_MODE = "no neutral"
SPACY_MODEL = "de_core_news_lg"

# paths
LEXICON_PATH = "lexicon//sentimentLexicon.json"
DATASET_PATH = "test//testData//hcTunesia//balancedDataSets"
# does not really matter which one you load, as long as your SAMPLE SIZE is not to big
TEST_DATASET = "balancedHolidayCheck2k.tsv"
LOG_PATH = "test//logs//sentenceLevel"


# naming for the logs
# there will be 3 logs: one for positive sentence, one for negative sentences and one for unknown sentiments
fileName = f"{STARS_RATING-1}Star_{SAMPLE_SIZE}"


lex = lexicon.Lexicon(LEXICON_PATH,LEXICON_MODE)
nlp = spacy.load(SPACY_MODEL)

holidayCheckFile = open(f"{DATASET_PATH}//{TEST_DATASET}","r",encoding="UTF-8")

lines = holidayCheckFile.readlines()
linesCount = len(lines)

posLog = open(f"{LOG_PATH}//{fileName}_POS.csv","w",encoding="UTF-8")
negLog = open(f"{LOG_PATH}//{fileName}_NEG.csv","w",encoding="UTF-8")
neutralLog = open(f"{LOG_PATH}//{fileName}_NEU.txt","w",encoding="UTF-8")

statsLog = open(f"{LOG_PATH}//{fileName}_STATS.txt","w",encoding="UTF-8")

posLog.write("sentiment,sentence,missingWords,polarity\n")
negLog.write("sentiment,sentence,missingWords,polarity\n")

# keep track of some values
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

    # no stars rating -> set to invalid value
    if stars == "null":
        stars = - 1

    stars = float(stars)

    # take the next review if it is not the rating group we want
    if stars != STARS_RATING:
        continue

    message = parts[2]
    message = message.replace(","," ").strip()


    # sentence splitting with spacy
    doc = nlp(message)
    sentences = []

    for sentence in doc.sents:
        sentences.append(sentence.text)


    for k in range (0, len(sentences)):
        sentence = sentences[k]

        # skip to short sentences
        if len(sentence.strip()) <= MIN_LETTERS_PER_SENTENCE:
            continue

        # get sentence sentiment
        sentenceSentiment = sa.getDocumentSentiment(sentences[k],lex,nlp)
        missingWords = sa.getMissingWords(sentences[k],lex,nlp)
        mwString = ""
        for mw in missingWords:
            mwString += f" {mw}"

        dataPointsCollected += 1

        # logging to the write log
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

# statsLog gives an overview over thre results
statsLog.write(f"files: {fileName}_(POS.csv|NEG.csv|NEU.txt)\n")
statsLog.write(f"POS\t{posCount}({'{:.0f}'.format(posCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(meanPos/posCount)}\n")
statsLog.write(f"NEG\t{negCount}({'{:.0f}'.format(negCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(meanNeg/negCount)}\n")
statsLog.write(f"NEU\t{posCount}({'{:.0f}'.format(neuCount/dataPointsCollected*100)}%)\tmean\t{'{:.2f}'.format(0)}\n")

posLog.close()
neutralLog.close()
negLog.close()
statsLog.close()


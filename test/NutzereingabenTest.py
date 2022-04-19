import os
import sys



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon
import spacy

#paths

LEXICON_PATH = "lexicon//sentimentLexicon.json"
LEXICON_MODE = "no neutral"

nlp = spacy.load("de_core_news_lg")
lex = lexicon.Lexicon(LEXICON_PATH,LEXICON_MODE)

nutzerEingaben = open("test//testData//Nutzereingaben.txt","r",encoding="UTF-8")
resultLog = open("test//logs//documentLevel//Nutzereingaben_result.txt","w",encoding="UTF-8")

lines = nutzerEingaben.readlines()

for line in lines:

    msg = line.strip()

    docSent = sa.getDocumentSentiment(msg,lex,nlp)
    missingWords = sa.getMissingWords(msg,lex,nlp)

    resultLog.write(f"{docSent}\t{missingWords} \n")
    resultLog.write(msg+"\n\n")




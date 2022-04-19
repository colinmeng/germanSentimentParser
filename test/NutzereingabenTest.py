from sentimentParser import lexicon
from sentimentParser import calculateSentiment as sa
import spacy

nlp = spacy.load("de_core_news_lg")
lex = lexicon.Lexicon("sentimentLexicon.json","no neutral")

nutzerEingaben = open("Nutzereingaben.txt","r",encoding="UTF-8")
resultLog = open("Nutzereingaben_result.txt","w",encoding="UTF-8")

lines = nutzerEingaben.readlines()

for line in lines:

    msg = line.strip()

    docSent = sa.getDocumentSentiment(msg,lex,nlp)
    missingWords = sa.getMissingWords(msg,lex,nlp)

    resultLog.write(f"{docSent}\t{missingWords} \n")
    resultLog.write(msg+"\n\n")




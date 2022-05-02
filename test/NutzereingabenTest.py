# Let's have a look how my sentiment analyser analyses some phrases that could be in a conversion with a chatbot

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon
import spacy

#paths
LEXICON_PATH = "lexicon//sentimentLexicon.json"
LEXICON_MODES = ["min","max","mean","no neutral","polarity"]

nlp = spacy.load("de_core_news_lg")

nutzerEingaben = open("test//testData//Nutzereingaben.txt","r",encoding="UTF-8")
resultLog = open("test//logs//documentLevel//Nutzereingaben_result.txt","w",encoding="UTF-8")

lines = nutzerEingaben.readlines()

for lexiconMode in LEXICON_MODES:
    lex = lexicon.Lexicon(LEXICON_PATH,lexiconMode)
    resultLog.write(f"Ergebnisse für Lexikon-Modus: {lexiconMode}\n\n")
    resultLog.write(f"pol\tactual\t\tcorrect\tmissingWords\tmessage\n")

    correctClassifiedCount = 0
    FP, TP, FN, TN = 0,0,0,0
    totalCount = len(lines)

    for line in lines:

        msg = line.split("\t")[0].strip()
        polarity = int(line.split("\t")[1].strip())

        docPolarity = sa.getDocumentPolarity(msg,lex,nlp)
        missingWords = sa.getMissingWords(msg,lex,nlp)

        if polarity == docPolarity:
            correctClassifiedCount += 1

        # for confusion matrix
        if polarity == -1:  
            if docPolarity == -1:
                TN += 1
            else:
                FP += 1
        
        elif polarity == 1:
            if docPolarity == 1:
                TP += 1
            else:
                FN += 1
            
        resultLog.write(f"{docPolarity}\t{polarity}\t{docPolarity == polarity}\t{missingWords}\t{msg}\n")

    resultLog.write(f"{correctClassifiedCount} von {totalCount} korrekt klassifiziert.\n\n")
        
    accuracy = (TN + TP) / (TN + FP + TP + FN)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2* ((precision * recall)/(precision + recall))

    resultLog.write("Confusion Matrix\n_______________________________________________________\n")
    resultLog.write(f"FP\t{FP}\tFN\t{FN}\tTP\t{TP}\tTN\t{TN}\taccuracy\t{accuracy}\tprecision\t{precision}\trecall\t{recall}\tf1\t{f1}") 
    resultLog.write("\n\n")




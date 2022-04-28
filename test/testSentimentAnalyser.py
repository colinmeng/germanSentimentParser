# this script can be used to quickly try out the sentiment analyser
# it will call sentiment analysis an all levels and you will get some information about the dependency parsing

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import sentimentParser.sentimentAnalysis as sa
import sentimentParser.lexicon as lexicon

import spacy
import time

nlp = spacy.load("de_core_news_lg", exclude=["attribute_ruler","ner"])
print(nlp.pipe_names)

lex = lexicon.Lexicon("lexicon//sentimentLexicon.json","no neutral")

running = True
while(running):
    print("type 'q' to quit.\n\n")

    msg = input()
    if(msg == "q"):
        running = False
        continue
    

    
    aP = sa.getAspectPolarities(msg,lex,nlp)
    aS = sa.getAspectSentiments(msg,lex,nlp)
    sP = sa.getSentencePolarities(msg,lex,nlp)
    sS = sa.getSentenceSentiments(msg,lex,nlp)
    dP = sa.getDocumentPolarity(msg,lex,nlp)

    #measures time for document level SA
    start = time.time()
    dS = sa.getDocumentSentiment(msg,lex,nlp)
    mW = sa.getMissingWords(msg,lex,nlp)
    end = time.time()

    if not mW:
        mW = " "

    print("aspect Polarity:     ", aP)
    print("aspect Sentiment:    ", aS)
    print("sentence Polarity:   ", sP)
    print("sentence Sentiment:  ", sS)
    print("document Polarity:   ", dP,)
    print("document Sentiment:  ", dS,)
    print("missing Words:       ", mW,)
    print(end - start,"s elapsed\n")

    doc = nlp(msg)

    # some information about the token
    for token in doc:
        print(f"{token.text}\t{token.pos_}\t{token.lemma_}\t{token.dep_}\t{token.head}")

    print(sa.getAspectSentimentDetails(msg,lex,nlp))


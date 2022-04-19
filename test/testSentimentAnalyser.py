from sentimentParser import calculateSentiment as sa
from sentimentParser import lexicon
import spacy
import time

nlp = spacy.load("de_core_news_lg")
lex = lexicon.Lexicon("sentimentLexicon.json","no neutral")

running = True
while(running):

    msg = input()
    if(msg == "q"):
        running = False
        continue
    

    
    aP = sa.getAspectPolarities(msg,lex,nlp)
    aS = sa.getAspectSentiments(msg,lex,nlp)
    sP = sa.getSentencePolarities(msg,lex,nlp)
    sS = sa.getSentenceSentiments(msg,lex,nlp)
    dP = sa.getDocumentPolarity(msg,lex,nlp)

    #measure time
    start = time.time()
    dS = sa.getDocumentSentiment(msg,lex,nlp)
    mW = sa.getMissingWords(msg,lex,nlp)
    end = time.time()

    print("aP: ", aP,"\n")
    print("aS: ", aS,"\n")
    print("sP: ", sP,"\n")
    print("sS: ", sS,"\n")
    print("dP: ", dP,"\n")
    print("dS: ", dS,"\n")
    print("mWs: ", mW, "\n")

    doc = nlp(msg)

    for token in doc:
        print(token.text,token.pos_,token.lemma_, token.dep_, token.head)

    print(sa.getAspectSentimentDetails(msg,lex,nlp))

    print(end - start,"s elapsed")
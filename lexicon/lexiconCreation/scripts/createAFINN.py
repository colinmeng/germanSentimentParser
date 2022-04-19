import spacy

afinn = open("lexicon//lexiconCreation//data//raw//AFINN-deutsch-deepl.txt","r",encoding="UTF-8")
nlp = spacy.load("de_core_news_lg")
lines = afinn.readlines()

afinnLex = open("lexicon//lexiconCreation//data//processed//afinn_ger_deepl_auto.csv","w",encoding="UTF-8")
afinnLex.write("wordStem,wordFunction,value,pos\n")

resultDict = {}
for line in lines:

    parts = line.split(" ")
    # exclude words that are non atomic (eg. "in Verlegenheit bringen")
    if len(parts) > 2:
        continue

    value = float(parts[1].strip())
    normalizedValue = value / 5
    normalizedValue = float("{:.4f}".format(normalizedValue))



    doc = nlp(parts[0].strip())
    for token in doc:
        if token.lemma_  not in resultDict:
            resultDict[token.lemma_] = {"value": normalizedValue,"pos":token.pos_}
        
lemmata = resultDict.keys()

for lemma in lemmata:
    afinnLex.write(f"{lemma},VAL,{resultDict[lemma]['value']},{resultDict[lemma]['pos']}\n")

    
afinn.close()
afinnLex.close()
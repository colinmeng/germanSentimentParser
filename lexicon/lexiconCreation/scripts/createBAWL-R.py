bawlr = open("lexicon//lexiconCreation//data//raw//bawl-r.csv","r",encoding="UTF-8")
lines = bawlr.readlines()

bawlrLexicon = open("lexicon//lexiconCreation//data//processed//bawlr.csv","w",encoding="UTF-8")
bawlrLexicon.write("wordStem,wordFunction,value,pos\n")

for line in lines:
    parts = line.split(",")
    wordStem = parts[0].strip()

    #skip first line
    if wordStem == "wordStem":
        continue
    pos = parts[1].strip()
    originalValue = float(parts[2].strip())
    normalizedValue = originalValue / 3
    normalizedValue = float("{:.4f}".format(normalizedValue))

    # POS-Token parsed to spacy default
    if pos == "N":
        pos = "NOUN"
    elif pos == "A":
        pos = "ADJ"
    elif pos == "V":
        pos = "VERB"

    bawlrLexicon.write(f"{wordStem},VAL,{normalizedValue},{pos}\n")

bawlrLexicon.close()
bawlr.close()
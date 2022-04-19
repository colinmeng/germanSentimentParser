sentiWS = open("lexicon//lexiconCreation//data//raw//SentiWS.csv","r",encoding="UTF-8")
lines = sentiWS.readlines()

sentiLex = open("lexicon//lexiconCreation//data//processed//senti.csv","w",encoding="UTF-8")
sentiLex.write("wordStem,wordFunction,value,pos\n")

for line in lines:
    parts = line.split(",")
    wordStem = parts[0].strip()

    #skip first line
    if wordStem == "wordStem":
        continue

    pos = parts[1].strip()
    value = float(parts[2].strip())

    value = float("{:.4f}".format(value))
    sentiLex.write(f"{wordStem},VAL,{value},{pos}\n")

sentiLex.close()
sentiWS.close()
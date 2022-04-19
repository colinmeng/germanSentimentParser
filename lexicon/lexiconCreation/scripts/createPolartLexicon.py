polArtLexicon = open("rawLexika//polart.csv","w",encoding="UTF-8")
polArtFile = open("rawLexika//polartlexicon.txt","r",encoding="UTF-8")
lines = polArtFile.readlines()

polArtLexicon.write("wordStem,wordFunction,value,pos\n")

# for stats
countVerb, countNoun, countAdj, countINT, countSHI = 0, 0, 0, 0, 0
minINT = 1
maxINT = 0

minVAL = 0
maxVAL = 0
sumVal = 0
countVal = 0

for line in lines:

    # skip comments
    if line.startswith("%"):
        continue

    parts = line.split(" ")

    wordStem = parts[0]
    wordFunctionAndValue = parts[1].split("=")
    wordFunction = wordFunctionAndValue[0]
    value = float(wordFunctionAndValue[1])
    pos = parts[2].strip("\n")

    if pos == "verben":
        pos = "VERB"
        countVerb += 1
    elif pos == "adj":
        pos = "ADJ"
        countAdj += 1
    elif pos == "nomen":
        pos = "NOUN"
        countNoun += 1
    elif pos == "neg":
        pos = "ADV"
        wordFunction = "SHI"
    else:
        raise ValueError(f"pos: {pos} does not exist!")

    #wordFunction cleaning
    # positive -> no change
    # negative -> invert value
    # neutral -> set value 0
    if wordFunction == "POS":
        wordFunction = "VAL"
        if value > maxVAL:
            maxVAL = value
            print(f"{maxVAL} bei {wordStem}")

    elif wordFunction == "NEU":
        wordFunction = "VAL"
        value = 0

    elif wordFunction == "NEG":
        wordFunction = "VAL"
        #turns values negative
        value *= -1
        if value < minVAL:
            minVAL = value
            #debug print(f"{minVAL} bei {wordStem}")
    
    elif wordFunction == "INT":
        countINT += 1
        if value > maxINT:
            maxINT = value
        elif value < minINT:
            minINT = value

    elif wordFunction == "SHI":
        value = 0
        countSHI += 1
        


    #make pos tags spaCy conform



    if wordFunction == "VAL":
        sumVal += value
        countVal += 1

    polArtLexicon.write(f"{wordStem},{wordFunction},{value},{pos}\n")

print(f"Verben: {countVerb}, Adjektive: {countAdj}, Nomen: {countNoun}, Adverben: {countSHI}\n")
print(f"Intensifier: {countINT} von {minINT} bis {maxINT}\n")
print(f"{countVal} Sentimentwörter von {minVAL} bis {maxVAL}, Mittelwert: {sumVal/countVal}")
polArtLexicon.close()
polArtFile.close()
    
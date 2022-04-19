# creates a sentiment dictionary
# numerical valence values from -1.0 to 1.0
# for every lemma only one entry, but multiple pos tags and values possible (will be stored as a list)
# sentiment dictionary will be stored as as a python dictionary with lemma as key

import json

sentimentDictionary = {}

#loading lexica

polart = open("lexicon//lexiconCreation//data//processed//polart.csv","r", encoding="UTF-8")
afinn = open("lexicon//lexiconCreation//data//processed//afinn_ger_deepl_man.csv","r", encoding="UTF-8")
bawlr = open("lexicon//lexiconCreation//data//processed//bawlr.csv","r",encoding="UTF-8")
sentiws = open("lexicon//lexiconCreation//data//processed//senti.csv","r",encoding="UTF-8")
shifters = open("lexicon//lexiconCreation//data//processed//shifters.csv","r",encoding="UTF-8")

lexica = [polart,afinn,bawlr,sentiws,shifters]

countEntrys = 0

for lexicon in lexica:
    rows = lexicon.readlines()

    for row in rows:

        #skip first line because there is no data
        if row.startswith("wordStem"):
            continue
    
        data = row.split(",")

        lemma = data[0].lower().strip()
        wordFunction = data[1].strip()
        value = float(data[2].strip())
        pos = data[3].strip()

        if lemma not in sentimentDictionary:
            sentimentDictionary[lemma] = {"wordFunction" : wordFunction, "values":[value], "pos":[pos]}
        else:
            entry = sentimentDictionary[lemma]
            
            # shifter always stay shifter
            if entry["wordFunction"] == "SHI":
                continue

            #INT overwrite VAL, but not SHI
            elif entry["wordFunction"] == "INT":
                if wordFunction == "INT":
                    entry["values"].append(value)

                elif wordFunction == "SHI":
                    entry["values"] = [value]
                    entry["wordFunction"] = "SHI"


            elif wordFunction in ["SHI","INT"]:
                entry["values"] = [value]
                entry["wordFunction"] = wordFunction

            else:
                entry["values"].append(value)

            # add pos to entry if not exist
            if pos not in entry["pos"]:
                entry["pos"].append(pos)
                print(lemma,entry)

        countEntrys += 1

    # add ordinalWörter as INT
    oW = open("lexicon//lexiconCreation//data//raw//ordinalWörter.txt","r",encoding="UTF-8")
    lines = oW.readlines()

    for line in lines:
        parts = line.split("=")
        value = float(parts[0])
        words = parts[1].split(",")

        # overwrite entrys if exists, so no check neccessary
        for word in words:
            sentimentDictionary[word] = {"wordFunction" : "INT", "values":[value], "pos": ["ADJ"]}
            countEntrys += 1
            


with open('lexicon//sentimentLexicon.json', "w", encoding="UTF-8") as file:
    json.dump(sentimentDictionary,file,ensure_ascii=False)        

print(f"{countEntrys} entrys created!") 


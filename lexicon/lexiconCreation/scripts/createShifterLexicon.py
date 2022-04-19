shifterList = open("lexicon//lexiconCreation//data//raw//verbal_shifters.gold_standard.txt","r",encoding="UTF-8")

lines = shifterList.readlines()

shifterLexicon = open("lexicon//lexiconCreation//data//processed//shifters.csv","w",encoding="UTF-8")
shifterLexicon.write("wordStem,wordFunction,value,pos\n")

for line in lines:
    parts = line.split(" ")
    if parts[1].strip() == "SHIFTER":
        shifterLexicon.write(f"{parts[0].strip()},SHI,0,VERB\n")
    

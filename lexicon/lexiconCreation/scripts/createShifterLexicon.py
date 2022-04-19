shifterList = open("vrawLexika//erbal_shifters.gold_standard.txt","r",encoding="UTF-8")

lines = shifterList.readlines()

shifterLexicon = open("rawLexika//shifters.csv","w",encoding="UTF-8")
shifterLexicon.write("wordStem,wordFunction,value,pos\n")

for line in lines:
    parts = line.split(" ")
    if parts[1].strip() == "SHIFTER":
        shifterLexicon.write(f"{parts[0].strip()},SHI,0,VERB\n")
    

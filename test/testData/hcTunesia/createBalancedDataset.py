# source data set at: https://github.com/oliverguhr/german-sentiment
path = "path to your dataset"
holidayCheckFile = open(path,"r",encoding="UTF-8")
lines = holidayCheckFile.readlines()
DATASET_SIZE = 20000 #for each rating

balancedDataSet = open("balancedHolidayCheck100k.tsv","w",encoding="UTF-8")

count = [0,0,0,0,0,0]

for line in lines:
    parts = line.split("\t")

    if parts[1] == "null":
        continue

    try:
        stars = int(parts[1]) -1
    except:
        continue

    if count[stars] < DATASET_SIZE:
        count[stars] += 1
        balancedDataSet.write(line)

print(count)

balancedDataSet.close()

    


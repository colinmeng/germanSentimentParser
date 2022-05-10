# this script is checking the results previosly calculated by documentLevelHolidayCheckTest.py
# Takes the result and calculates a confusion matrix

import json
from statistics import mean
from statistics import median
from statistics import stdev

# the script calculates the confusion matrix based on a threshold
# the more far away the best Threshold is from the intended Threshold of 0.0,
# the less accurate is the dataset.

STEP_SIZE = 0.01    # smaller step sizes, will make computation time longer
START_THRESHOLD = -0.2  # the first threshold used (always keep it below 0)

# if ZERO_STAR_WEIGHT is bigger, makes it more important to classify negative results.
# Weight are only active if ENABLE_WEIGHTS is set to "True"
ZERO_STAR_WEIGHT = 2
TWO_STAR_WEIGHT = 1
FIVE_STAR_WEIGHT = 2
# enable Neutral is some kind of experimental -> no good results for non binary classifcation yet
# if enabled: take 2 star-(or 3 Suns)reviews as neutral (hint: they are not neutral at all....)
ENABLE_NEUTRAL = False
ENABLE_WEIGHTS = False

# the best Threshold is shown at the end, and it is where this value (OPTIMIZE) has its maximum
# in scientific research we always want to maximum f1
OPTIMIZE = "accuracy" #f1, precision, accuracy, recall
RESULTS_PATH = "test//analysisResults//"

#        CHANGE THIS
############################################
RESULT_JSON = "12000_max_result.json"#
############################################

# non binary classification is always using weights
# if no weights should be use, just set them to 1 (equal weights)
if ENABLE_NEUTRAL:
    if not ENABLE_WEIGHTS:
        ZERO_STAR_WEIGHT = 1
        TWO_STAR_WEIGHT = 1
        FIVE_STAR_WEIGHT = 1
        ENABLE_WEIGHTS = True
    
    # make it so the weights sum = 1
    else:
        sumWeights = ZERO_STAR_WEIGHT + TWO_STAR_WEIGHT + FIVE_STAR_WEIGHT
        TWO_STAR_WEIGHT = TWO_STAR_WEIGHT / sumWeights
        ZERO_STAR_WEIGHT = ZERO_STAR_WEIGHT / sumWeights
        FIVE_STAR_WEIGHT = FIVE_STAR_WEIGHT / sumWeights
else:
    # change weights:  exclude neutral case
    sumWeights = ZERO_STAR_WEIGHT + FIVE_STAR_WEIGHT

    ZERO_STAR_WEIGHT = ZERO_STAR_WEIGHT / sumWeights
    FIVE_STAR_WEIGHT = FIVE_STAR_WEIGHT / sumWeights
    TWO_STAR_WEIGHT = 0



def classify(sentiments,negativeThreshold,positiveThreshold):
    """classifies a list of sentiments from the result.json, depending on negative- and positive Threshold"""
    data = dict()

    result = []

    for i in range(0,len(sentiments)):
        entry = dict()

        entry["positiv"] = 0
        entry["negativ"] = 0
        entry["neutral"] = 0

        for value in sentiments[i]:

            if value == 0.0:
                entry["neutral"] += 1

            elif value <= negativeThreshold:
                entry["negativ"] += 1

            else:
                entry["positiv"] += 1

        result.append(entry)
    
    data["classification"] = result
    data["positiveThreshold"] = positiveThreshold
    data["negativeThreshold"] = negativeThreshold

    return data


def logResult(classificationResult,log):
    """logs the classificationResult"""
    log.write(f"Einträge werden ab: {'{:6.3f}'.format(classificationResult['positiveThreshold'])} als positiv und ab {'{:6.3f}'.format(classificationResult['negativeThreshold'])} als negativ klassifiziert.\n\n")

    for i in range(0,len(classificationResult["classification"])):
        pos = classificationResult["classification"][i]['positiv']
        neg = classificationResult["classification"][i]['negativ']
        neu = classificationResult["classification"][i]['neutral']

        ges = pos + neg + neu

        # check if results with this polarity exist and format
        if pos:
            posPer = "{:.1f}".format(pos/ges*100)
        else:
            pos = 0.0
            posPer = 0.0
        
        if neg:
            negPer = "{:.1f}".format(neg/ges*100)
        else: 
            neg = 0.0
            negPer = 0.0

        if neu:
            neuPer = "{:.1f}".format(neu/ges*100)
        else:
            neu = 0.0
            neuPer = 0.0

        log.write(f"{i} Sterne: {ges} Einträge \n\t{pos} positiv({posPer}%) \n\t{neg} negativ({negPer}%) \n\t{neu} neutral({neuPer}%)\n\n")


path = f"{RESULTS_PATH}{RESULT_JSON}"
resultFile = open(path,"r",encoding="UTF-8")
resultData =  json.load(resultFile)

sentiments = resultData["sentiments"]
invalidLinesCount = resultData["invalidLinesCount"]
errorLinesCount = resultData["errorLinesCount"]
lineCount = resultData["lineCount"]

logName = RESULT_JSON.split(".")[0]
if ENABLE_NEUTRAL:
    logName += "_tri"
else:
    logName += "_bin"

    if OPTIMIZE:
        logName += f"_optimize_{OPTIMIZE.lower()}"
    
if ENABLE_WEIGHTS:
    logName += "_weighted"
    formatted0Weight = "{:.0f}".format(ZERO_STAR_WEIGHT*100)
    formatted2Weight = "{:.0f}".format(TWO_STAR_WEIGHT*100)
    formatted5Weight = "{:.0f}".format(FIVE_STAR_WEIGHT*100)

    logName += f"_NEG{formatted0Weight}_NEU{formatted2Weight}_POS{formatted5Weight}"

else:
    logName += "_unweighted"



logPath = f"test//logs//documentLevel//{logName}.txt"

resultLog = open(logPath,"w",encoding="UTF-8")
resultLog.write(f"Analysiertes Dokument: {path}\n")
resultLog.write(f"{lineCount} Einträge wurden analysiert, davon sind {invalidLinesCount} ungültig und bei {errorLinesCount} Einträgen kam es zu Fehlern.\n")
resultLog.write(f"Ergebnisse nach Sternen sortiert: \n\n")

for i in range(0,len(sentiments)):
    meanSen = "{:.3f}".format(mean(sentiments[i]))
    medianSen = "{:.3f}".format(median(sentiments[i]))
    stdSen = "{:.3f}".format(stdev(sentiments[i]))

    resultLog.write(f"{i} Sterne: {len(sentiments[i])} Einträge \n\tmean:\t{meanSen}\n\tmedian:\t{medianSen}\n\tstd: {stdSen}\n\n")

# log weights and stepsize

if ENABLE_WEIGHTS:
    resultLog.write("Gewichtung:\n")
    resultLog.write(f"\tkorrekt negativ: {ZERO_STAR_WEIGHT*100}%\n")
    resultLog.write(f"\tkorrekt positiv: {FIVE_STAR_WEIGHT*100}%\n")
    resultLog.write(f"\tkorrekt neutral: {TWO_STAR_WEIGHT*100}%\n\n")

elif OPTIMIZE.lower() in ["f1","f1score","accuracy","precision","reca´ll"]:
    resultLog.write(f"Optimierung nach: {OPTIMIZE.lower()}\n\n")

resultLog.write(f"Schrittgröße: {STEP_SIZE}\n\n")

minNegativeThreshold = START_THRESHOLD
maxPositiveThreshold = float("{:.2f}".format(mean(sentiments[5])))

negativeThreshold = maxPositiveThreshold
positiveThreshold = negativeThreshold

minError = 999
optimizingValue = None
minErrorNegThresh = START_THRESHOLD
minErrorPosTresh = START_THRESHOLD
comparisonValue = None

# if neutral ENABLED: change min and max Threshold iterative, so we can find the best Thresholds
# no further explanation here because it is not giving acceptable results anyway...
while negativeThreshold >= minNegativeThreshold and ENABLE_NEUTRAL:
    negativeThreshold -= STEP_SIZE
    positiveThreshold = negativeThreshold

    while positiveThreshold <= maxPositiveThreshold :
        positiveThreshold += STEP_SIZE

        classificationResult = classify(sentiments,negativeThreshold,positiveThreshold)

        fiveStarPositiveCount = classificationResult["classification"][5]["positiv"]
        fiveStarTotalCount = classificationResult["classification"][5]["positiv"] + classificationResult["classification"][5]["negativ"] + classificationResult["classification"][5]["neutral"]
        fiveStarRatio = fiveStarPositiveCount / fiveStarTotalCount

        fiveStarError = 1 - fiveStarRatio

        zeroStarPositiveCount = classificationResult["classification"][0]["positiv"]
        zeroStarTotalCount = classificationResult["classification"][0]["positiv"] + classificationResult["classification"][0]["negativ"] + classificationResult["classification"][0]["neutral"]
        zeroStarRatio = zeroStarPositiveCount / fiveStarTotalCount

        zeroStarError = zeroStarRatio

        twoStarNeutralRatio = classificationResult["classification"][2]["neutral"]/(classificationResult["classification"][2]["positiv"]+classificationResult["classification"][2]["negativ"]+classificationResult["classification"][2]["neutral"])

        twoStarError = 1 - twoStarNeutralRatio

        
        weightedError = zeroStarError *  ZERO_STAR_WEIGHT + twoStarError * TWO_STAR_WEIGHT + fiveStarError * FIVE_STAR_WEIGHT

        if minError > weightedError:
            minError = weightedError
            minErrorNegThresh = negativeThreshold
            minErrorPosTresh = positiveThreshold

            formattedZeroStarError = "{:.3f}".format(zeroStarError)
            formattedTwoStarError = "{:.3f}".format(twoStarError)
            formattedFiveStarError = "{:.3f}".format(fiveStarError)
            formattedWeightedError = "{:.3f}".format(weightedError)
            formattedError = "{:.3f}".format((zeroStarError+fiveStarError+twoStarError)/3)

            formattedNegativeThreshold = "{:.2f}".format(negativeThreshold)
            formattedPositiveThreshold = "{:.2f}".format(positiveThreshold)

            resultLog.write(f"FP\t{formattedZeroStarError}\FN\t{formattedTwoStarError}\t5Error\t{formattedFiveStarError}\tError\t{formattedError}\tweightedError\t{formattedWeightedError}\tnegThresh\t{formattedNegativeThreshold}\tposThresh\t{formattedPositiveThreshold}\n")            

# this is for binary classification
if not ENABLE_NEUTRAL:
    positiveThreshold = START_THRESHOLD

    # every iteration positiveThreshold grows by STEP_SIZE until it reached the maximum positive Threshold
    # the maxPositiveThreshold is the mean sentiment of the 5-Star review 
    while positiveThreshold <= maxPositiveThreshold:

        # classify the sentiments according to threshold
        classificationResult = classify(sentiments,positiveThreshold,positiveThreshold)

        # if we use weights.... but we don't usually
        # this is also not so scientific and i don't want to dig to deep into unneccessary stuff
        if ENABLE_WEIGHTS:
            fiveStarPositiveCount = classificationResult["classification"][5]["positiv"]
            fiveStarTotalCount = classificationResult["classification"][5]["positiv"] + classificationResult["classification"][5]["negativ"]
            fiveStarRatio = fiveStarPositiveCount / fiveStarTotalCount

            fiveStarError = 1 - fiveStarRatio

            zeroStarPositiveCount = classificationResult["classification"][0]["positiv"]
            zeroStarTotalCount = classificationResult["classification"][0]["positiv"] + classificationResult["classification"][0]["negativ"] + classificationResult["classification"][0]["neutral"]
            zeroStarRatio = zeroStarPositiveCount / fiveStarTotalCount

            zeroStarError = zeroStarRatio



            weightedError = zeroStarError *  ZERO_STAR_WEIGHT + fiveStarError * FIVE_STAR_WEIGHT

            if minError > weightedError:
                minError = weightedError
                minErrorNegThresh = positiveThreshold
                minErrorPosTresh = positiveThreshold

                formattedZeroStarError = "{:6.3f}".format(zeroStarError)
                formattedFiveStarError = "{:6.3f}".format(fiveStarError)
                formattedWeightedError = "{:6.3f}".format(weightedError)
                formattedError = "{:6.3f}".format((zeroStarError+fiveStarError)/2)

                formattedThreshold = "{:.3f}".format(positiveThreshold)

                resultLog.write(f"FP\t{formattedZeroStarError}\tFN\t{formattedFiveStarError}\tError\t{formattedError}\tweightedError\t{formattedWeightedError}\tTresh\t{formattedThreshold}\n")    
        
        # here we calculate the confusion matrix
        else:
            # calculate statistic values
            comparisonValue = None

            # define the groups
            FP = classificationResult["classification"][0]["positiv"]
            TN = classificationResult["classification"][0]["negativ"]

            TP = classificationResult["classification"][5]["positiv"]
            FN = classificationResult["classification"][5]["negativ"]

            # calculations 
            accuracy = (TN + TP) / (TN + FP + TP + FN)
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            f1 = 2* ((precision * recall)/(precision + recall))

            # decide what to optimize
            if OPTIMIZE.lower() == "accuracy":
                if not optimizingValue:
                    optimizingValue = accuracy
                elif optimizingValue <= accuracy:
                    comparisonValue = accuracy

            elif OPTIMIZE.lower() == "precision":
                if not optimizingValue:
                    optimizingValue = precision
                elif optimizingValue <= precision:
                    comparisonValue = precision


            elif OPTIMIZE.lower() == "recall":
                if not optimizingValue:
                    optimizingValue = recall
                elif optimizingValue <= recall:
                    comparisonValue = recall

            elif OPTIMIZE.lower() in ["f1","f1score"]:
                if not optimizingValue:
                    optimizingValue = f1
                elif optimizingValue <= f1:
                    comparisonValue = f1

            else:
                raise Exception(f"can not optimize unknown value: {OPTIMIZE.lower()}")

            # the comparisonValue is higher than the value in the best iteration before
            # log the result
            if comparisonValue:
                optimizingValue = comparisonValue
                formattedThreshold = "{:.2f}".format(positiveThreshold)
                minErrorNegThresh = positiveThreshold
                minErrorPosTresh = positiveThreshold

                #formatting makes it pretty
                accuracy = "{:6.3f}".format(accuracy)
                precision = "{:6.3f}".format(precision)
                recall = "{:6.3f}".format(recall)
                f1 = "{:6.3f}".format(f1)


                resultLog.write(f"FP\t{FP}\tFN\t{FN}\tTP\t{TP}\tTN\t{TN}\taccuracy\t{accuracy}\tprecision\t{precision}\trecall\t{recall}\tf1\t{f1}\tTresh\t{formattedThreshold}\n") 


        positiveThreshold += STEP_SIZE


minErrorResult = classify(sentiments,minErrorNegThresh,minErrorPosTresh) 


logResult(minErrorResult,resultLog)
resultLog.close()
print(minError)

print("done")
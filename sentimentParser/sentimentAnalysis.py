from statistics import mean

#   the threshold determines, when the verbs/nouns sentiment will be included in the overall sentiment
# set this to a value greater 1, to exclude verbs/nouns completely from sentiment calculation
NeutralVerbThreshold = 0.0
NeutralNounThreshold = 0.0

# if a word could not be found in the lexicon and has one of these POS-Tags, add it to the missing words list
listOfPosToIncludeInMissingWordList = ["PART","VERB","ADV","ADJ","NOUN","AUX"]

def lookUpWordAndLemmaInLexicon(token,lexicon):
    """looks up the text and the lemma of a given token and returns a result dictionary"""
    result = dict()
    missingWords = []
    success = False

    # firstly we look up the original text of the token
    tokenLookUpResult = lexicon.lookUp(token.text)

    # if this is unsuccessfull, look up the lemma of the word
    if not tokenLookUpResult:
        tokenLookUpResult = lexicon.lookUp(token.lemma_)

    # if this is also unsuccessfull, add word and it's lemma to missing words list ()
    # the "data" will be the lexicon result if "success" is set to true, else it is the missing words list
    if not tokenLookUpResult:
        if token.pos_ in listOfPosToIncludeInMissingWordList:
            missingWords.append(token.text)
            missingWords.append(token.lemma_)
        result["data"] = missingWords
        
    else:
        success = True
        result["data"] = tokenLookUpResult

    result["success"] = success

    return result
    
def analyseAdjective(token, lexicon):
    """
    analyses a token and its child tokens and returns a result as dict

    Parameters
        ----------
        token : token
            a spacy token, should be a adjective

        Returns
        -------
        dict
            "type" - the type of the adjective
                 VAL -> word is a regular sentiment word 
                 INT -> word is an intensifier 
                 UNC -> the word itself is not in lexicon
            "value"
                float, can be positive or negative for VAL, positive for INT
            "missingWords"
                list of words, that are uncovered by lexicon
            
    """

    adjType = "UNC" #UNC VAL or INT
    adjValue = 0
    adjIsShifted = False
    missingWords = []

    adjLookUpResult = lookUpWordAndLemmaInLexicon(token,lexicon)

    if adjLookUpResult["success"]:
        adjType = adjLookUpResult["data"]["wordFunction"]
        adjValue = adjLookUpResult["data"]["value"]

    # uncovered -> further investigations unneccesary
    else:
        result = dict()
        result["type"] = adjType
        result["value"] = adjValue
        result["missingWords"] = adjLookUpResult["data"]

        return result
    
    
    # inspect the direct children of the adjective and the second grade children
    adjChilds = token.children
    
    if adjChilds:
        
        for adjChild in adjChilds:
            adjChildLookUp = lookUpWordAndLemmaInLexicon(adjChild,lexicon)

            # if child look up unsuccessfull, move to the next child
            if not adjChildLookUp["success"]:
                for missingWord in adjChildLookUp["data"]:
                    missingWords.append(missingWord)

                continue    


            adjChildType = adjChildLookUp["data"]["wordFunction"]
            adjChildValue = adjChildLookUp["data"]["value"]

            # childs of Intensifier are either intensifier (INT) themselfes, or negations (SHI)
            # look through the Intensifiers childs and modify the adjectives value
            if adjChildType == "INT":

                adjChildChildren = adjChild.children

                # the child has no more childs, nothing to do here
                if not adjChildChildren:
                    continue
                
                for child in adjChildChildren:
                    childLookUp = lookUpWordAndLemmaInLexicon(child,lexicon)

                    if not childLookUp["success"]:
                        for missingWord in childLookUp["data"]:
                            missingWords.append(missingWord)
                            continue
                            
                    # child is found
                    else: 
                        childType = childLookUp["data"]["wordFunction"]
                        
                        # INTs multiply each other
                        if childLookUp["data"]["wordFunction"] == "INT":
                            adjValue *= childLookUp["data"]["value"]
                            continue
                        
                        # Negations (SHI), that belong to INTs make it "less intense" 
                        # sehr(3) -> nicht sehr (1/3)
                        if childType == "SHI":
                            adjChildValue = 1 / adjChildValue
                
                # first grad child is INT -> intensify the underlaying adjectives value (no matter if it is VAL- or INT-type)
                adjValue *= adjChildValue

            # SHI negate (* -1) VAL, and weaken (1/Value) INTs
            if adjChildType == "SHI":
                if adjType == "INT":
                    adjValue = 1 / adjValue
                else:
                    adjValue *= -1

            # if first level child of an adjective is VAL, it is probably a comma conjucted one (enumeration)
            # well written german sentences use enumeration (as attributes or adverbs) in the following way
            # "..."((adj),(adj))^n "und" (adj) -> e. g. "Das Essen ist schmackhaft, warm und gesund."
            if adjChildType == "VAL":

                # indirect recursion: getNextConjuctedAdjectiveResult calls this function itself on the next adjective that is following a conjuction
                conjAdjResult = getNextConjuctedAdjectiveResult(adjChild,lexicon)
                if conjAdjResult != -1:

                    if conjAdjResult["result"]["type"] == "VAL":
                        
                        # we add up conjucted VAL adjectives 
                        adjValue += conjAdjResult["result"]["value"]

                # to get even to the deepest level, call the function again
                analysisResult = analyseAdjective(adjChild,lexicon)

                 # add up sentiment of comma conjuncted adjectives
                if analysisResult["type"] == "VAL":
                    adjValue += analysisResult["value"] 
                    
    

    # negations are on the same level as the adjective in the parse tree and belong to the verb (that's why pos-tag = ADV)
    # so it is neccessary to look up the verbs child and identify them as a Shifter
    if token.pos_ == "ADV":
        verbToken = token.head

        for child in verbToken.children:
            childLookUp = lookUpWordAndLemmaInLexicon(child,lexicon)

            # if it is a negation change the shifter flag
            if childLookUp["success"]:
                if childLookUp["data"]["wordFunction"] == "SHI":
                    adjIsShifted = not adjIsShifted

            else:
                for missingWord in childLookUp["data"]:
                    missingWords.append(missingWord)

    result = dict()
    result["type"] = adjType

    # as before: shifted INTs are weakened
    if adjType == "INT" and adjIsShifted:
        result["value"] = 1 / adjValue

    # normal use of shifter
    elif adjType == "VAL" and adjIsShifted:
        result["value"] = -1 * adjValue

    else:
        result["value"] = adjValue

    # cleanUp missing words
    cleanedUpMissingWords = []

    for word in missingWords:
        if word not in cleanedUpMissingWords:
            cleanedUpMissingWords.append(word)

    result["missingWords"] = cleanedUpMissingWords

    return result          


def getNextConjuctedAdjectiveResult(token,lex):
    """
    takes childrens, looks through them, if they are a conjuction and return result of the underlaying adjective.

    Parameters
        ----------
        token : token
            

        Returns
        -------
        -1, if no childrens found or no conjucted adjectives found

        dict
            "result" : dict
                "type" - the type of the adjective
                    VAL -> word is a regular sentiment word 
                    INT -> word is an intensifier 
                    UNC -> the word itself is not in lexicon
                "value"
                    float, can be positive or negative for VAL, positive for INT
                "missingWords"
                    list of words, that are uncovered by lexicon
            "token" : token
                the child, that is an adjective and is conjuncted
    """
    childrens = token.children

    if not childrens:
        return -1

    for possibleConjToken in childrens:
        if possibleConjToken.pos_ == "CCONJ" or possibleConjToken.text in [",",";","/","|"]:
            possibleConjTokenChildren = possibleConjToken.children

            if possibleConjTokenChildren:
                for child in possibleConjTokenChildren:
                    if child.pos_ in ["ADJ","ADV"]:
                        result = dict()
                        result["result"] = analyseAdjective(child, lex)
                        result["token"] = child
                        
                        return result
    
    return -1

#we assume this function  only gets sentences (could also be very large one), so it's computing sentence sentiment
def getAspectSentimentDetails(msg,lex,nlp):
    noVerbRoot = False

    doc = nlp(msg)
    rootToken = None
    #get the root of the sentence

    for token in doc:
        if token.dep_ == "ROOT":
            rootToken = token
            break


    if not rootToken:
        return 0

    # filter out some cases, that make no sense
    if rootToken.pos_ not in ["VERB","AUX","NOUN"]:
        return 0
        
    rootChildren = rootToken.children

    # not a sentencegr
    if not rootChildren:
        return 0
        
    rootConjTokens = []

    for rootChild in rootChildren:
        if rootChild.pos_ == "CCONJ":
            rootConjTokens.append(rootChild)

    #get the root of each part of the sentence to begin parsing from there

    subSentenceRootTokens = []

    # first part always exist
    subSentenceRootTokens.append(rootToken)

    if rootConjTokens:
        for token in rootConjTokens:
            possibleRootTokens = token.children

            if possibleRootTokens:
                for possibleRootToken in possibleRootTokens:
                    if possibleRootToken.pos_ in ["VERB","AUX",]:
                        subSentenceRootTokens.append(possibleRootToken)
    
    aspectSentimentDetails = dict()

    for rootToken in subSentenceRootTokens:
        missingWords = []
        subSentenceAspectToken = None

        # get aspect word of subsentence (direct children)

        rootChildren = rootToken.children

        #gives back empty dict as result for the sentencePart -> no information can be extracted
        if not rootChildren:
            break
        
        for rootChild in rootChildren:
            if rootChild.pos_ == "NOUN":
                subSentenceAspectToken = rootChild
                break

        if not subSentenceAspectToken:
            for rootChild in rootToken.children:
                if rootChild.pos_ == "PRON":
                    subSentenceAspectToken = rootChild
                    break
        
        # sentence with NOUN as root ist not a sentence but can still contain a sentiment
        if rootToken.pos_ == "NOUN":
            subSentenceAspectToken = rootToken

        # no aspect found --> empty result for subsentence
        if not subSentenceAspectToken:
            break
                
        ###############################################################################################################

        #get aspect word sentiment

        aspectWordSentiment = 0

        lookUpResult = lookUpWordAndLemmaInLexicon(subSentenceAspectToken, lex)

        if lookUpResult["success"]:
            
            #check if pos-tag is right:
            if "NOUN" in lookUpResult["data"]["pos"] and lookUpResult["data"]["wordFunction"] == "VAL":
                aspectWordSentiment = lookUpResult["data"]["value"]

        else:
            for missingWord in lookUpResult["data"]:
                missingWords.append(missingWord)

        ###############################################################################################################

        # get the attributes that belong to the aspect word
        attributes = []
        aspectWordIntensifier = 1

        aspectWordChilds = subSentenceAspectToken.children

        if aspectWordChilds:

            for awChild in aspectWordChilds:
                
                #INT can be "ADV"
                if awChild.pos_ in ["ADJ","ADV"]:
                    attributeAnalyseResult = analyseAdjective(awChild, lex)

                    if attributeAnalyseResult["type"] == "INT":
                        aspectWordIntensifier *= attributeAnalyseResult["value"]

                    if attributeAnalyseResult["type"] == "VAL":
                        attributes.append(attributeAnalyseResult["value"])

                    for missingWord in attributeAnalyseResult["missingWords"]:
                        missingWords.append(missingWord)

                # check for conjunctions and Commas (","), that chains multiple attributes

                conjChilds = awChild.children

                if conjChilds:

                    result = 0

                    while result != -1:
                        result = getNextConjuctedAdjectiveResult(awChild,lex)
                        
                        if result == -1:
                            break

                        if result["result"]["type"] == "INT":
                            aspectWordIntensifier *= result["result"]["value"]

                        if result["result"]["type"] == "VAL":
                            attributes.append(result["result"]["value"])

                        if result["result"]["type"] == "UNC":
                            missingWords.append(result["token"].text)
                            missingWords.append(result["token"].lemma_)
                        
                        conjChilds = result["token"].children

                        if not conjChilds:
                            result = -1
                            break

                    #has it conjuncted parts?

                # direct aspect word negation detection
                elif awChild.pos_ in ["PART","DET"]:

                    negLookUp = lookUpWordAndLemmaInLexicon(awChild,lex)

                    if negLookUp["success"]:
                        if negLookUp["data"]["wordFunction"] == "SHI":
                            aspectWordIntensifier *= -1
                    else:
                        for missingWord in negLookUp["data"]:
                            missingWords.append(missingWord)
        
        ###############################################################################################################

        # get adverbials sentiments

        adverbials = []
        potentialAdverbs = None 

        # case a NOUN is root -> no adverbials without verb
        if rootToken != subSentenceAspectToken:
            potentialAdverbs = rootToken.children

        if potentialAdverbs:
            for child in potentialAdverbs:
                if child.pos_ == "ADV":

                    adverbialAnalysisResult = analyseAdjective(child,lex)

                    if adverbialAnalysisResult["type"] == "VAL":
                        adverbials.append(adverbialAnalysisResult["value"])

                    for missingWord in adverbialAnalysisResult["missingWords"]:
                        missingWords.append(missingWord)

                # check for conjunctions and Commas (","), that chains multiple attributes

                conjChilds = child.children

                if conjChilds:

                    result = 0

                    while result != -1:
                        result = getNextConjuctedAdjectiveResult(child,lex)
                        
                        if result == -1:
                            break

                        if result["result"]["type"] == "VAL":
                            adverbials.append(result["result"]["value"])

                        if result["result"]["type"] == "UNC":
                            missingWords.append(result["token"].text)
                            missingWords.append(result["token"].lemma_)
                        
                        conjChilds = result["token"].children

                        if not conjChilds:
                            result = -1
                            break 

        ###############################################################################################################

        # get verbs sentiment
        verbSentiment = 0

        if rootToken.pos_ == "VERB":
            verbLookUpResult = lookUpWordAndLemmaInLexicon(rootToken,lex)

            if verbLookUpResult["success"]:
                verbType = verbLookUpResult["data"]["wordFunction"]

                if verbType == "SHI":
                    verbSentiment = -1
                
                elif verbType == "VAL":
                    verbSentiment = verbLookUpResult["data"]["value"]

                else:
                    verbSentiment = 0

            verbChildren = rootToken.children

            # direct negation of the verb 
            # e. G. "ich verstehe diese Aufgabe nicht"
            if verbChildren:
                for child in verbChildren:
                    if child.dep_ == "ng":
                        verbSentiment *= -1
                    
                    # "ich glaube(0.5) ich verzweifle(-0.5)..." --> -0.25
                    if child.pos_ == "VERB":
                        verbLookUpResult = lookUpWordAndLemmaInLexicon(child,lex)

                        if verbLookUpResult["success"]:
                            verbType = verbLookUpResult["data"]["wordFunction"]

                            if verbType == "SHI":
                                verbSentiment *= -1
                
                            elif verbType == "VAL":
                                verbSentiment *= verbLookUpResult["data"]["value"]

        aspectDetails = dict()
        aspectDetails["aspectWord"] = aspectWordSentiment
        aspectDetails["attr"] = attributes
        aspectDetails["adv"] = adverbials
        aspectDetails["verb"] = verbSentiment
        aspectDetails["int"] = aspectWordIntensifier
        
        aspectSentimentDetails[subSentenceAspectToken.text] = aspectDetails
        
    result = dict()
    result["sentimentDetails"] = aspectSentimentDetails

        # cleanUp missing words
    cleanedUpMissingWords = []
    for word in missingWords:
        if word not in cleanedUpMissingWords:
            cleanedUpMissingWords.append(word)

    result["missingWords"] = cleanedUpMissingWords
    

    return result


def calculateAspectSentiments(aspectSentimentDetails):

    if not aspectSentimentDetails:
        return {}

    aspectSentiments = dict()
    # we don't care for missing words here
    aspectSentimentDetails = aspectSentimentDetails["sentimentDetails"]


    for aspect in aspectSentimentDetails:    
        details = aspectSentimentDetails[aspect]

        attr = details["attr"]
        adv = details["adv"]
        aw = details["aspectWord"]
        verb = details["verb"]
        awInt = details["int"]

        if abs(aw) < NeutralNounThreshold:
            aw = 0

        if abs(verb) < NeutralVerbThreshold:
            verb = 0
            
        # the sentiment of an aspect is calculated by  3 individual components: 
        #   1. aspect Word and the product of its Intensifier
        #   2. the mean value of the attributes
        #   3. the verbs sentiment multiplied by the mean value of the adverbs
        #
        #   the not neutral components will be counted (min 1, max 3) and the sentiment is divided by the number of used components
        #   under following conditions are components neutral:
        #
        #   1. aspect Word * aspectWordIntensifier (aw * awInt):
        #       - aspectWord is neutral (sentiment == 0)
        #
        #   2. attributes (attr):
        #       - no attributes exist (likely)
        #       - mean of attributes == 0 (less likely)
        #
        #   3. verb * mean of adverbials (verb * adv)
        #       - no verb(0) and no adverbials exist(0)
        #       - neutral verb(0) and no adverbials(0)
        #       - neutral verb(0) and neutral mean of adverbials(0)
        #   
        #   to make sure the sentiment for adverbials or verb is included, even if one of these 2 factors equals zero,
        #   there will be a change in value after neutral case is checked
        #   if verb(0) and attr(!=0) -> verb(1)
        #   if attr(0) and verb(!=0) -> attr(1)
        #   
        #   in this case we ignore the non existant parameter

        # calculate means and check if empty
        meanAttr = 0
        meanAdv = 0
        
        if attr:
            meanAttr = mean(attr)
        
        if adv:
            meanAdv = mean(adv)

        if not aw:
            aw = 0

        component1 = aw * awInt
        component2 = meanAttr

        component3 = 0
        #special rules for third component

        if verb and meanAdv:
            component3 = verb * meanAdv
        
        elif verb and not meanAdv:
            component3 = verb

        elif not verb and meanAdv:
            component3 = meanAdv

        # shifter is applied to aspectword
        # e.g. "Krieg beenden"
        if component3 == -1:
            component1 *= -1

            component3 = 0

        
        # put the 3 components together for aspect sentiment calculation

        sentiment = 0
        countComponents = 0

        if component1:
            sentiment += component1
            countComponents += 1

        if component2:
            sentiment += component2
            countComponents += 1
  
        if component3:
            sentiment += component3
            countComponents += 1 

        if countComponents:
            sentiment /= countComponents

                   
        aspectSentiments[aspect] = sentiment

    return aspectSentiments

def getMissingWords(msg,lex,nlp):
    missingWords = []
    doc = nlp(msg)

    for sen in doc.sents:
        sen = nlp(sen.text)
        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)

        missingWordsInAspect = None
        if aspectSentimentDetails:
            missingWordsInAspect = aspectSentimentDetails["missingWords"]

        
            for missingWord in missingWordsInAspect:
                if str.lower(missingWord) not in missingWords:
                    missingWords.append(str.lower(missingWord))

    return missingWords


def calcSenSentiment(aspectSentiments):
    countAspects = 0
    aspectSum = 0
    for aspect in aspectSentiments:
        aspectSum += aspectSentiments[aspect]
        countAspects += 1

    if countAspects:
        aspectSum /= countAspects

    return aspectSum


def getAspectSentiments(msg,lex,nlp):
    doc = nlp(msg)
    
    aspectSents = []

    for sen in doc.sents:
        sen = nlp(sen.text)
        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)

        if aspectSentiments:
            for aspect in aspectSentiments:
                aspectSents.append((aspect,aspectSentiments[aspect]))

    return aspectSents


def getAspectPolarities(msg,lex,nlp):
    doc = nlp(msg)
    
    aspectPolarities = []

    for sen in doc.sents:
        sen = nlp(sen.text)

        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)

        if aspectSentiments:
            for aspect in aspectSentiments:
                pol = 0

                if aspectSentiments[aspect] > 0:
                    pol = 1

                elif aspectSentiments[aspect] < 0:
                    pol = -1
                
                aspectPolarities.append((aspect,pol))

    return aspectPolarities


def getSentenceSentiments(msg,lex,nlp):
    doc = nlp(msg)
    sentenceSentiments = []

    for sen in doc.sents:
        sen = nlp(sen.text)

        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)
        sentenceSentiments.append(calcSenSentiment(aspectSentiments))
    
    return sentenceSentiments


def getSentencePolarities(msg,lex,nlp):
    doc = nlp(msg)
    sentencePolarities = []

    for sen in doc.sents:
        sen = nlp(sen.text)

        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)
        sentenceSentiment = calcSenSentiment(aspectSentiments)

        if sentenceSentiment > 0:
            sentencePolarities.append(1)

        elif sentenceSentiment < 0:
            sentencePolarities.append(-1)

        else:
            sentencePolarities.append(0)
    
    return sentencePolarities


def getDocumentSentiment(msg,lex,nlp, perSentence = False):
    doc = nlp(msg)
    countParts = 0
    sentimentSum = 0

    for sen in doc.sents:
        sen = nlp(sen.text)
        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)
        
        if perSentence:
            countParts += 1
            sentimentSum += calcSenSentiment(aspectSentiments)

        else:
            for aspect in aspectSentiments:
                sentimentSum += aspectSentiments[aspect]
                countParts += 1

    if countParts:
        return sentimentSum / countParts
        
    else:
        return 0


def getDocumentPolarity(msg,lex,nlp, perSentence = False):
    docSentiment = getDocumentSentiment(msg,lex,nlp, perSentence) 

    if docSentiment > 0:
        return 1

    elif docSentiment < 0:
        return -1

    else:
        return 0



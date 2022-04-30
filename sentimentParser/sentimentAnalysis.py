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
    uncoveredWords = []
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
            uncoveredWords.append(token.text)
            uncoveredWords.append(token.lemma_)
        result["data"] = uncoveredWords
        
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
            
            # look if the conjuction has a child with pos "ADV" or "ADJ" and get the analysis result of it
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
    """
    Analyses a message, with the help of a sentiment lexicon and a spacy language model.

    Parameters
        ----------
        msg : string
            the message to analyse. (Should be a phrase or one)
        lex : Lexicon
            an instance of lexicon class
        nlp : spacy.Language
            an instance of a Language object

        Returns
        -------
    
        dict[aspect] -> dict(missingWords, sentimentDetails)
            missingWords : list(string)
                list of words, that are uncovered by lexicon

            sentimentDetails : list of dict()
                sentimentDetails["aspectWord"]  : float
                    the sentiment of the aspect word itself, included direct negations of it
                sentimentDetails["attr"]        : list(float)
                    a list of all the attributes sentiment, that belong to the aspect word (conjuncted attributes form one value)
                sentimentDetails["adv"]         : list(float)
                    a list of all the adverbials sentiment, that belong to the root Verb (conjuncted adverbials form one value)
                sentimentDetails["verb"]        : float
                    product of the root verbs and its direct childrens sentiment, excluding adverbials
                sentimentDetails["int"]         : float
                    a factor that states, how much the aspect words sentiment is intensified
    """
    # creates the doc -> executes nlp pipeline
    doc = nlp(msg)
    
    subSentenceRootTokens = []
    cleanedUpMissingWords = []
    missingWords = []

    #get the tokens, that are a root of a sentence part
    for token in doc:
        if token.dep_ == "ROOT":
            subSentenceRootTokens.append(token)

        elif token.dep_ == "cj" and token.pos_ in ["AUX","VERB"]:
            subSentenceRootTokens.append(token)
    
    # no root -> no message -> nothing to analyse
    if not subSentenceRootTokens:
        return 0
    
    # will be filled with aspect sentiment information for one aspect
    aspectSentimentDetails = dict()

    # start parsing from each verb -> 1 sentence can have multiple aspects and different verbs
    for rootToken in subSentenceRootTokens:
        
        subSentenceAspectToken = None

        # get aspect word of subsentence (direct children)
        rootChildren = rootToken.children

        #gives back empty dict as result for the sentencePart -> no information can be extracted
        if not rootChildren:
            break
        
        # obvious aspect word candidates are always nouns
        for rootChild in rootChildren:
            if rootChild.pos_ == "NOUN":
                subSentenceAspectToken = rootChild
                break
        
        # only if there are no nouns in first grade childrens of root verb, look if there is a pronome, that can be the aspect token 
        if not subSentenceAspectToken:
            for rootChild in rootToken.children:
                if rootChild.pos_ == "PRON":
                    subSentenceAspectToken = rootChild
                    break
        
        # sentence with NOUN as root is not a sentence but can still contain a sentiment
        if rootToken.pos_ == "NOUN":
            subSentenceAspectToken = rootToken

        # no aspect found --> empty result for subsentence
        if not subSentenceAspectToken:
            break
            
        ###############################################################################################################

        #get aspect words sentiment

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

        # get the attributes that belong to the aspect word and negations
        attributes = []
        aspectWordIntensifier = 1
        aspectWordChilds = subSentenceAspectToken.children

        if aspectWordChilds:

            for awChild in aspectWordChilds:
                
                #INT can be "ADV", if it is a "real" adverb
                if awChild.pos_ in ["ADJ","ADV"]:
                    attributeAnalyseResult = analyseAdjective(awChild, lex)

                    if attributeAnalyseResult["type"] == "INT":
                        aspectWordIntensifier *= attributeAnalyseResult["value"]

                    if attributeAnalyseResult["type"] == "VAL":
                        attributes.append(attributeAnalyseResult["value"])

                    for missingWord in attributeAnalyseResult["missingWords"]:
                        missingWords.append(missingWord)

                # direct aspect word negation detection
                elif awChild.pos_ in ["PART","DET"]:

                    negLookUp = lookUpWordAndLemmaInLexicon(awChild,lex)

                    if negLookUp["success"]:
                        if negLookUp["data"]["wordFunction"] == "SHI":
                            aspectWordIntensifier *= -1

                        if negLookUp["data"]["wordFunction"] == "INT":
                            aspectWordIntensifier *= negLookUp["data"]["value"]

                    else:
                        for missingWord in negLookUp["data"]:
                            missingWords.append(missingWord)

                # check for conjunctions and Commas (","), that chains multiple attributes
                conjChilds = awChild.children

                if conjChilds:

                    result = 0

                    # traverse the parse tree, until you found every conjuncted adjective and calculate the base adjectives value
                    while result != -1:
                        result = getNextConjuctedAdjectiveResult(awChild,lex)
                        
                        #no result
                        if result == -1:
                            break
                        
                        if result["result"]["type"] == "INT":
                            aspectWordIntensifier *= result["result"]["value"]

                        if result["result"]["type"] == "VAL":
                            attributes.append(result["result"]["value"])

                        if result["result"]["type"] == "UNC":
                            missingWords.append(result["token"].text)
                            missingWords.append(result["token"].lemma_)
                        
                        awChild = result["token"]

                        if not conjChilds:
                            result = -1
                            break
 
        ###############################################################################################################

        # get adverbials sentiments

        adverbials = []
        potentialAdverbs = None 

        # case the root token equals aspect token -> no adverbials without a verb
        if rootToken != subSentenceAspectToken:
            potentialAdverbs = rootToken.children

        # in case of above: this variable is not set, nothing to do then, else we look through the adverbs
        if potentialAdverbs:
            for child in potentialAdverbs:
                if child.pos_ == "ADV":

                    adverbialAnalysisResult = analyseAdjective(child,lex)

                    if adverbialAnalysisResult["type"] == "VAL":
                        adverbials.append(adverbialAnalysisResult["value"])

                    for missingWord in adverbialAnalysisResult["missingWords"]:
                        missingWords.append(missingWord)

                # check for conjunctions and Commas (","), that chains multiple adverbs 
                # similar to attributes chaining
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
                        
                        child = result["token"]


                        if not conjChilds:
                            result = -1
                            break 

        ###############################################################################################################

        # get verbs sentiment including direct negations
        verbSentiment = 0

        if rootToken.pos_ == "VERB":
            verbLookUpResult = lookUpWordAndLemmaInLexicon(rootToken,lex)

            if verbLookUpResult["success"]:
                verbType = verbLookUpResult["data"]["wordFunction"]

                # Shifters have value of 0 in lexicon -> set it to -1, so it is inverting the sentiment
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

        # fill the dict, that holds information for one aspect 
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

    for word in missingWords:
        print(word)
        if word not in cleanedUpMissingWords:
            cleanedUpMissingWords.append(word)

    result["missingWords"] = cleanedUpMissingWords
    

    return result


def calculateAspectSentiments(aspectSentimentDetails):
    """
    Takes an aspectSentimentDetails object and calculate each aspects sentiment.

    Parameters
        ----------
        aspectSentimentDetails : dict
            the result of getAspectSentimentDetails()

        Returns
        -------
    
        dict[aspect] -> aspects sentiment
        or empty dict, if no aspects found
    """

    # nothing to do here
    if not aspectSentimentDetails:
        return {}

    aspectSentiments = dict()
    # we don't care for missing words here
    aspectSentimentDetails = aspectSentimentDetails["sentimentDetails"]

    # go through each aspect and calculate its sentiment
    for aspect in aspectSentimentDetails:    
        details = aspectSentimentDetails[aspect]

        attr = details["attr"]
        adv = details["adv"]
        aw = details["aspectWord"]
        verb = details["verb"]
        awInt = details["int"]

        # sometimes we do not want to include the nouns or verbs Threshold, especially when they have only a low sentiment
        # and the nouns sentiment is generally determined by the attribute and the verbs sentiment is multiplied by the adverbs mean sentiment
        # even if the adverbs mean sentiment is high, when the verbs sentiment is low, the general sentiment value is low, because we use multiplication (you will see later)
        if abs(aw) < NeutralNounThreshold:
            aw = 0

        if abs(verb) < NeutralVerbThreshold:
            verb = 0
            
        # the sentiment of an aspect is calculated by  3 individual components: 
        #   1. aspect Word and the product of its Intensifier
        #   2. the summed up value of the attributes
        #   3. the verbs sentiment multiplied by the sum of of the adverbs valences
        #
        #   the not neutral components will be counted (min 1, max 3) and the sentiment is divided by the number of used components
        #   under following conditions are components neutral:
        #
        #   1. aspect Word * aspectWordIntensifier (aw * awInt):
        #       - aspectWord is neutral (sentiment == 0)
        #
        #   2. attributes (attr):
        #       - no attributes exist (likely)
        #       - sum of attributes == 0 (less likely)
        #
        #   3. verb * mean of adverbials (verb * adv)
        #       - no verb(0) and no adverbials exist(0)
        #       - neutral verb(0) and no adverbials(0)
        #       - neutral verb(0) and neutral sum of adverbials(0)
        #   
        #   to make sure the sentiment for adverbials or verb is included, even if one of these 2 factors equals zero,
        #   there will be a change in value after neutral case is checked
        #   if verb(0) and attr(!=0) -> verb(1)
        #   if attr(0) and verb(!=0) -> attr(1)
        #   
        #   in this case we ignore the non existant parameter

        # calculate means and check if empty
        sumAttr = 0
        sumAdv = 0
        
        if attr:
            sumAttr = sum(attr)
        
        if adv:
            sumAdv = sum(adv)

        if not aw:
            aw = 0

        component1 = aw * awInt
        component2 = sumAttr
        component3 = 0

        #special rules for third component, we don't want the product to be 0, just because one part is zero (not existent)
        if verb and sumAdv:
            component3 = verb * sumAdv
        
        elif verb and not sumAdv:
            component3 = verb

        elif not verb and sumAdv:
            component3 = sumAdv

        # put the 3 components together for aspect sentiment calculation
        sentiment = 0
        countComponents = 0

        # if there are no attributes or adverbials to further describe the aspect, than the aspect word itself has a valence
        if component1 and not component2 and not component3:
            sentiment += component1
            countComponents += 1

        if component2:
            sentiment += component2
            countComponents += 1
  
        if component3:
            if verb == -1:
                sentiment *= -1
            else: 
                sentiment += component3
                countComponents += 1 
         
        aspectSentiments[aspect] = sentiment

    return aspectSentiments

def getMissingWords(msg,lex,nlp):
    """returns a list of no in the lexicon covered words for a given message"""
    missingWords = []
    doc = nlp(msg)

    for sen in doc.sents:
        sen = nlp(sen.text)
        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)

        missingWordsInAspect = None
        if aspectSentimentDetails:
            missingWordsInAspect = aspectSentimentDetails["missingWords"]

            # to prevent duplicates        
            for missingWord in missingWordsInAspect:
                if str.lower(missingWord) not in missingWords:
                    missingWords.append(str.lower(missingWord))

    return missingWords


def calcSenSentiment(aspectSentiments):
    """Takes aspect Sentiments and calculate the sentence sentiment as the mean of aspect sentiments."""
    countAspects = 0
    aspectSum = 0
    for aspect in aspectSentiments:
        aspectSum += aspectSentiments[aspect]
        countAspects += 1

    if countAspects:
        aspectSum /= countAspects

    return aspectSum


def getAspectSentiments(msg,lex,nlp):
    """Returns a list of aspect sentiments, as a float, for a given message, that can be any length."""
    doc = nlp(msg)
    
    aspectSents = []

    # getAspectSentimentDetails can only take on sentence, so we use sentence splitting
    for sen in doc.sents:
        sen = nlp(sen.text)
        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)

        if aspectSentiments:
            for aspect in aspectSentiments:
                aspectSents.append((aspect,aspectSentiments[aspect]))

    return aspectSents


def getAspectPolarities(msg,lex,nlp):
    """returns a list of integers, -1 = negative, 0 = no sentiment, 1 = positive, representing the aspects polarities, for a given message."""
    doc = nlp(msg)
    
    aspectPolarities = []

    # getAspectSentimentDetails can only take on sentence, so we use sentence splitting 
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
    """Returns a list of sentence sentiments, as a float, for a given message, that can be any length."""
    doc = nlp(msg)
    doc = nlp(msg)
    sentenceSentiments = []

    for sen in doc.sents:
        sen = nlp(sen.text)

        aspectSentimentDetails = getAspectSentimentDetails(sen,lex,nlp)
        aspectSentiments = calculateAspectSentiments(aspectSentimentDetails)
        sentenceSentiments.append(calcSenSentiment(aspectSentiments))
    
    return sentenceSentiments


def getSentencePolarities(msg,lex,nlp):
    """returns a list of integers, -1 = negative, 0 = no sentiment, 1 = positive, representing the sentences polarities, for a given message."""
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
    """
    Returns a float value, that is the documents sentiment.

    Parameters
        ----------
        msg : string
            the message to analyse

        lex : Lexicon
            the lexicon to use

        nlp : spacy.Language
            the language model to use

        perSentence (optional): bool
            calculate documents sentiment sentence-wise (if not the aspect-wise)
    """
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
    """
    Returns a int value, that is the documents sentiment polarity (-1 = negative, 0 = no sentiment, 1 = positive).

    Parameters
        ----------
        msg : string
            the message to analyse

        lex : Lexicon
            the lexicon to use

        nlp : spacy.Language
            the language model to use

        perSentence (optional): bool
            calculate documents sentiment sentence-wise (if not the aspect-wise)
    """
    docSentiment = getDocumentSentiment(msg,lex,nlp, perSentence) 

    if docSentiment > 0:
        return 1

    elif docSentiment < 0:
        return -1

    else:
        return 0
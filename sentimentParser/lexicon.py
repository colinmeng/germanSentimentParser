import json
import statistics

# because the sentimentLexicon.json can contain multiple sentiment values per entry
# look up modes exist to determine, which values matter
# min -> takes ONLY the lowest value
# max -> takes ONLY the highest value
# mean -> takes the mean of ALL values
# no neutral (suggested option) -> takes the mean of all values BUT neutral ones (neutral values contain no Information about the sentiment = bad for SA)
lookUpModes = ["min","max","mean","no neutral","polarity"]

class Lexicon:
    """
    A class to represent a sentiment lexicon.


    Attributes
    ----------
    data : dict
        container that holds information [wordFunction, values[], pos[]] for the key(the words lemma)
    mode : str
        determines the calculation of the entrys sentiment value

    Methods
    -------
    changemode(mode):
        changes the mode used for calculation of sentiment value

    lookUp(word)
        looks up a word in lexicon and return a result as dict
    """
    def __init__(self,path,mode):
        with open(path,encoding="UTF-8") as jsonData:
            self.data = json.load(jsonData)
        
        if mode in lookUpModes:
            self.mode = mode
        else:
            raise ValueError(f"{mode} is not a valid mode. Use one of following modes instead: {lookUpModes}")

    def changeMode(self, mode):
        """ changes the mode of the lexicon """
        if mode in lookUpModes:
            self.mode = mode
            print(f"mode has been changed to {mode}")

        else:
            raise ValueError(f"{mode} is not a valid mode. Use one of following modes instead: {lookUpModes}")



    
    def lookUp(self, word):
        """
        looks up the given word in the lexicon and returns a result(dict)

        Parameters
        ----------
        word : str
            a word, preferably a words lemma

        Returns
        -------
        dict
            "wordFunction" - the function that this word has in a sentence
                 VAL -> word is a regular sentiment word (from -1 (negative) to 1 (positive), 0 = no sentiment)
                 INT -> word is an intensifier (INT > 1 = intensifying |INT > 0 && INT < 1 = weakening)
                 SHI -> word is a negation or a shifter (has no value)
            "values"
                list of values for this word
            "pos"
                list of possible POS-Tokens for this word
            
        """
        # we don't want to deal with upper and lower case, so make it lower
        wordIsLower = str.islower(word) 

        word = str.lower(word)
        result = dict()
        
        # look up the word in data
        if word in self.data:
            entry = self.data[word]

            result["wordFunction"] = entry["wordFunction"]

            # get the polarity
            if statistics.mean(result["values"]) > 0:
                resultPolarity = 1

            elif statistics.mean(result["values"]) < 0:
                resultPolarity = -1

            else:
                resultPolarity = 0
            
            if self.mode == "polarity":
                result["value"] = resultPolarity

            elif self.mode == "min":
                if resultPolarity == 1:
                    result["value"] = min(entry["values"])
                
                elif resultPolarity == -1:
                    result["value"] = max(entry["values"])
                
                else:
                    result["value"] = 0


            elif self.mode == "max":
                if resultPolarity == 1:
                    result["value"] = max(entry["values"])
                
                elif resultPolarity == -1:
                    result["value"] = min(entry["values"])
                
                else:
                    result["value"] = 0

            elif self.mode == "mean":
                result["value"] = statistics.mean(entry["values"])
                
            elif self.mode == "no neutral":
                values = []

                for value in entry["values"]:
                    if value:
                        values.append(value)
                
                # if no values found, set result value to 0
                if values == []:
                    result["value"] = 0.0
                else:
                    result["value"] = statistics.mean(values)
            
            else:
                raise Exception("Wrong Mode")

            # pos identification only NOUNS identifiable

            if "NOUN" in entry["pos"] and not wordIsLower:
                result["pos"] = "NOUN"
            else:
                result["pos"] = entry["pos"]

        # if no result, returns empty dict
        return result



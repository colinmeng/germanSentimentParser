import json
import statistics

lookUpModes = ["min","max","mean","no neutral"]

class Lexicon:

    def __init__(self,path,mode):
        with open(path,encoding="UTF-8") as jsonData:
            self.data = json.load(jsonData)
        
        if mode in lookUpModes:
            self.mode = mode
        else:
            raise ValueError(f"{mode} is not a valid mode. Use one of following modes instead: {lookUpModes}")

    def changeMode(self, mode):
        if mode in lookUpModes:
            self.mode = mode
            print(f"mode has been changed to {mode}")

        else:
            raise ValueError(f"{mode} is not a valid mode. Use one of following modes instead: {lookUpModes}")



    def lookUp(self, word):
        wordIsLower = str.islower(word)

        word = str.lower(word)
        result = dict()
        
        if word in self.data:
            entry = self.data[word]



            result["wordFunction"] = entry["wordFunction"]
            
            if self.mode == "min":
                result["value"] = min(entry["values"])

            elif self.mode == "max":
                result["value"] = max(entry["values"])

            elif self.mode == "mean":
                result["value"] = statistics.mean(entry["values"])
                
            elif self.mode == "no neutral":
                values = []

                for value in entry["values"]:
                    if value:
                        values.append(value)
                
                if values == []:
                    result["value"] = 0.0
                else:
                    result["value"] = statistics.mean(values)
            
            else:
                raise Exception("should not happen!")

            # pos identification only NOUNS identifiable

            if "NOUN" in entry["pos"] and not wordIsLower:
                result["pos"] = "NOUN"
            else:
                result["pos"] = entry["pos"]

        return result



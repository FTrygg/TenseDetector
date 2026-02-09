import nltk
import re
import spacy

class TenseDetector:
    class _CustomToken:
        CustomTokens = []
        def __init__(self, tokenTag, textPattern, requiredTag):
            self._tokenTag = tokenTag
            self._textPattern = textPattern 
            self._requiredTag = requiredTag
            TenseDetector._CustomToken.CustomTokens.append(self)

    class _Tense:
        def __init__(self, name, tenseStructure, examples = [""]):
            self._tenseName = name
            self._tenseStructure = tenseStructure #list
            self._examples = examples
        
        def getTenseStructure(self):
            tenseStructureString = "{"
            for element in self._tenseStructure:
                if type(element) == list:
                    subElements = []
                    for tag in element:
                        subElements.append(tag)
                        subElements.extend([specialTag._tokenTag for specialTag in TenseDetector._CustomToken.CustomTokens if (tag in specialTag._requiredTag)])

                    tenseStructureString = tenseStructureString + f"<{"|".join(subElements)}>"
                    
                else:
                    subElements = []
                    subElements.append(element)
                    subElements.extend([specialTag._tokenTag for specialTag in TenseDetector._CustomToken.CustomTokens if (element in specialTag._requiredTag)])
                    tenseStructureString = tenseStructureString + f"<{"|".join(subElements)}>"
            
            tenseStructureString = tenseStructureString + "+}"
            return tenseStructureString

    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")
        self._ruler = self._nlp.get_pipe("attribute_ruler")
        self._tagFilters = ["VBG","VBN","VB","TO","VBP","VBZ","VBD","NNS"]
        self._setCustomTags()
        self._tenses = []
        self._tenseNames = []
        self._tensesGrammar = ""
        self._setTenseGrammar()
        

    def _setCustomTags(self):
        TenseDetector._CustomToken("HAD",       ["had"],            ["VBD"])
        TenseDetector._CustomToken("BEEN",      ["been"],           ["VBN"])
        TenseDetector._CustomToken("GOING",     ["going"],          ["VBG"])
        TenseDetector._CustomToken("BEING",     ["being"],          ["VBG"])
        TenseDetector._CustomToken("WILL",      ["will","'ll"],     ["MD"])
        TenseDetector._CustomToken("IS",        ["is","'s"],        ["VBZ"])
        TenseDetector._CustomToken("ARE",       ["are"],            ["VBP"])
        TenseDetector._CustomToken("AM",        ["am","'m"],        ["VBP"])
        TenseDetector._CustomToken("BE",        ["be"],             ["VB"])
        TenseDetector._CustomToken("HAS",       ["has"],            ["VBZ"])
        TenseDetector._CustomToken("WAS",       ["was"],            ["VBD"])
        TenseDetector._CustomToken("WERE",      ["were"],           ["VBD"])
        TenseDetector._CustomToken("HAVE",      ["have","'ve"],     ["VBP","VB"])
        TenseDetector._CustomToken("WOULD",     ["would","'d"],     ["MD"])
        TenseDetector._CustomToken("MAY",       ["may"],            ["MD"])
        TenseDetector._CustomToken("MIGHT",     ["might"],          ["MD"])
        TenseDetector._CustomToken("CAN",       ["can"],            ["MD"])
        TenseDetector._CustomToken("COULD",     ["could"],          ["MD"])
        TenseDetector._CustomToken("SHALL",     ["shall"],          ["MD"])
        TenseDetector._CustomToken("SHOULD",    ["should"],         ["MD"])
        TenseDetector._CustomToken("MUST",      ["must"],           ["MD"])
        TenseDetector._CustomToken("OUGHT",     ["ought"],          ["MD"])

        for customTag in TenseDetector._CustomToken.CustomTokens:
            pattern = [
                {
                    "LOWER" : {"IN": customTag._textPattern}, 
                    "TAG": {"IN": customTag._requiredTag}
                }
            ]
            attrs = {"TAG": customTag._tokenTag}
            self._ruler.add(patterns=[pattern], attrs=attrs)
            self._tagFilters.append(customTag._tokenTag)

    def _setTenseGrammar(self):
        self._tenses.append(TenseDetector._Tense("conditional_perfect_continuous",          ["WOULD", "HAVE", "BEEN", "VBG"],                   ["I would have been watching the movie."]))
        self._tenses.append(TenseDetector._Tense("conditional_perfect",                     ["WOULD", "HAVE", "VBN"],                           ["I would have watched the movie."]))
        self._tenses.append(TenseDetector._Tense("conditional_continuous",                  ["WOULD", "BE", "VBG"],                             ["I would be watching the movie."]))
        self._tenses.append(TenseDetector._Tense("conditional_simple",                      ["WOULD", "VB"],                                    ["I would watch the movie."]))
        self._tenses.append(TenseDetector._Tense("future_continuous_passive",               ["WILL", "BE", "BEING", "VBN"],                     ["The movie will be being watched."]))
        self._tenses.append(TenseDetector._Tense("future_perfect_continuous",               ["WILL", "HAVE", "BEEN", "VBG"],                    ["I will have been watching the movie (all day)."]))
        self._tenses.append(TenseDetector._Tense("future_perfect_simple",                   ["WILL", "HAVE", "VBN"],                            ["I will have watched the movie (by tonight)."]))#check
        self._tenses.append(TenseDetector._Tense("future_continuous",                       ["WILL", "BE", "VBG"],                              ["I will be watching the movie."]))
        self._tenses.append(TenseDetector._Tense("will_future",                             ["WILL", "VB"],                                     ["I will watch the movie."]))
        self._tenses.append(TenseDetector._Tense("going_to_future",                         [["AM", "IS", "ARE"], "GOING", "TO", "VB"],         ["I am going to watch the movie.", "She is going to watch the movie.", "They are going to watch the movie."]))
        self._tenses.append(TenseDetector._Tense("present_continuous_passive",              [["AM", "IS", "ARE"], "BEING", "VBN"],              ["The movie is being watched.", "The movies are being watched.", "I am being watched."]))
        self._tenses.append(TenseDetector._Tense("present_continuous",                      [["AM", "IS", "ARE"], "VBG"],                       ["I am watching the movie.", "She is watching the movie.", "They are watching the movie."]))
        self._tenses.append(TenseDetector._Tense("can_present_passive",                     ["CAN", "BE", "VBN"],                               ["The movie can be watched."]))
        self._tenses.append(TenseDetector._Tense("can_present",                             ["CAN", "VB"],                                      ["I can watch the movie."]))
        self._tenses.append(TenseDetector._Tense("could_past_passive",                      ["COULD", "BE", "VBN"],                             ["The movie could be watched."]))
        self._tenses.append(TenseDetector._Tense("could_past",                              ["COULD", "VB"],                                    ["I could watch the movie."]))
        self._tenses.append(TenseDetector._Tense("Might_passive",                           [["MAY, MIGHT"], "BE", "VBN"],                      ["The movie may be watched.", "The movie might be watched."]))
        self._tenses.append(TenseDetector._Tense("Might",                                   [["MAY, MIGHT"],"VB"],                              ["I may watch the movie.", "I might watch the movie."]))
        self._tenses.append(TenseDetector._Tense("Should_passive",                          [["SHALL", "SHOULD"], "BE", "VBN"],                 ["The movie should be watched."]))
        self._tenses.append(TenseDetector._Tense("Should",                                  [["SHALL", "SHOULD"],"VB"],                         ["I should watch the movie.", "I shall watch the movie."]))
        self._tenses.append(TenseDetector._Tense("past_continuous_passive",                 [["WAS", "WERE"], "BEING", "VBN"],                  ["The movie was being watched.", "The movies were being watched"]))
        self._tenses.append(TenseDetector._Tense("past_continuous",                         [["WAS", "WERE"],"VBG"],                            ["I was watching the movie.", "They were watching the movie."]))
        self._tenses.append(TenseDetector._Tense("present_perfect_continuous_passive",      [["HAS", "HAVE"], "BEEN", "BEING", "VBN"],          ["The movie has been being watched.", "The movies have been being watched."]))
        self._tenses.append(TenseDetector._Tense("present_perfect_continuous",              [["HAS", "HAVE"], "BEEN", "VBG"],                   ["I have been watching the movie.", "She has been watching the movie."]))
        self._tenses.append(TenseDetector._Tense("present_perfect_passive",                 [["HAS", "HAVE"], "BEEN", "VBN"],                   ["The movie has been watched.", "The movies have been watched."]))
        self._tenses.append(TenseDetector._Tense("present_perfect",                         [["HAS", "HAVE"], "VBN"],                           ["I have watched the movie.", "She has watched the movie."]))
        self._tenses.append(TenseDetector._Tense("past_perfect_continuous_passive",         ["HAD", "BEEN", "BEING", "VBN"],                    ["The movie had been being watched."]))
        self._tenses.append(TenseDetector._Tense("past_perfect_continuous",                 ["HAD", "BEEN", "VBG"],                             ["I had been watching the movie (for an hour)."]))
        self._tenses.append(TenseDetector._Tense("past_perfect_passive",                    ["HAD", "BEEN", "VBN"],                             ["The movie had been watched."]))
        self._tenses.append(TenseDetector._Tense("past_perfect",                            ["HAD", "VBN"],                                     ["I had watched the movie (before you arrived)."]))
        self._tenses.append(TenseDetector._Tense("past_simple_passive",                     [["WAS", "WERE"], "VBN"],                           ["The movie was watched.", "The movies were watched."]))
        self._tenses.append(TenseDetector._Tense("present_simple_passive",                  [["AM", "IS", "ARE"], "VBN"],                       ["The movie is watched.", "The movies are watched.", "I am watched."]))                        
        self._tenses.append(TenseDetector._Tense("past_simple",                             ["VBD"],                                            ["I watched the movie."]))
        self._tenses.append(TenseDetector._Tense("present_simple",                          [["VBP", "VBZ"]],                                   ["I watch the movie."]))
        self._tenses.append(TenseDetector._Tense("infinitive",                              ["TO", "VB"],                                       ["I (like) to watch the movie"]))

        
        for tense in self._tenses:
            self._tensesGrammar = self._tensesGrammar + f"{tense._tenseName}: {tense.getTenseStructure()}\n"
            self._tenseNames.append(tense._tenseName)

    def listTenses(self, text, splitSentences=False): 
        if type(text) == list:
            return self._determineTenses(text)

        if type(text) == str:
            #if its supposed to be split
            if splitSentences == True:
                sentences = self._splitSentences(text)
                return self._determineTenses(sentences)
            else:
                return self._determineTense(text)
        
    def _checkTenseGrammar(self): #check whether the example sentences are all detected
        for tense in self._tenses:
            for sentence in tense._examples:
                print(f"{tense._tenseName}:{self._determineTense(sentence)}")

    def _splitSentences(self, text : str) -> list[str]:
        return re.split(r"[.!?]\s+(?=[A-Z])", text)

    def _determineTense(self, sentence : str):
        doc = self._nlp(sentence)
        filteredTaggedSentence = [(token.text, token.tag_) for token in doc if token.tag_ in self._tagFilters]
        if len(filteredTaggedSentence) == 0: #if there is nothing left in the sentence
            return "", []
        cp = nltk.RegexpParser(self._tensesGrammar)
        result = cp.parse(filteredTaggedSentence,trace=0)

        tenses = []
        for subtree in result.subtrees():
            if subtree.label() in self._tenseNames:
                tenses.append(subtree.label())

        return sentence, tenses

    def _determineTenses(self, sentences : list[str]):
        results = []
        for sentence in sentences:
            results.append(self._determineTense(sentence))
        
        return results


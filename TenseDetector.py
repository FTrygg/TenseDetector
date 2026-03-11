import re
import nltk
import spacy

class TenseDetector:
    class CustomToken:
        CustomTokens = []
        def __init__(self, token_tag, text_pattern, required_tag):
            self.token_tag = token_tag
            self.text_pattern = text_pattern
            self.required_tag = required_tag
            TenseDetector.CustomToken.CustomTokens.append(self)

    class _Tense:
        def __init__(self, name, tense_structure, examples = [""]):
            self.tense_name = name
            self.tense_structure = tense_structure
            self.examples = examples

        def get_tense_structure(self) -> str:
            """
            Creates a lookup string for the tense, taking into account that special tags might have multiple roles.

            Returns
            -------
            str
                Returns
                String of tense structure.
            """
            tense_structure_string = "{"
            for element in self.tense_structure:
                if isinstance(element, list):
                    sub_elements = []
                    for tag in element:
                        sub_elements.append(tag)
                        sub_elements.extend([specialTag.token_tag for specialTag in TenseDetector.CustomToken.CustomTokens if tag in specialTag.required_tag])

                    tense_structure_string = tense_structure_string + f"<{"|".join(sub_elements)}>"

                else:
                    sub_elements = []
                    sub_elements.append(element)
                    sub_elements.extend([specialTag.token_tag for specialTag in TenseDetector.CustomToken.CustomTokens if element in specialTag.required_tag])
                    tense_structure_string = tense_structure_string + f"<{"|".join(sub_elements)}>"

            tense_structure_string = tense_structure_string + "+}"
            return tense_structure_string

    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")
        self._ruler = self._nlp.get_pipe("attribute_ruler")
        self._tag_filters = ["VBG","VBN","VB","TO","VBP","VBZ","VBD","NNS"]
        self._setcustom_tags()
        self._tenses = []
        self.tense_names = []
        self._tenses_grammar = ""
        self._set_tense_grammar()


    def _setcustom_tags(self) -> None:
        TenseDetector.CustomToken("HAD",       ["had"],            ["VBD"])
        TenseDetector.CustomToken("BEEN",      ["been"],           ["VBN"])
        TenseDetector.CustomToken("GOING",     ["going"],          ["VBG"])
        TenseDetector.CustomToken("BEING",     ["being"],          ["VBG"])
        TenseDetector.CustomToken("WILL",      ["will","'ll"],     ["MD"])
        TenseDetector.CustomToken("IS",        ["is","'s"],        ["VBZ"])
        TenseDetector.CustomToken("ARE",       ["are"],            ["VBP"])
        TenseDetector.CustomToken("AM",        ["am","'m"],        ["VBP"])
        TenseDetector.CustomToken("BE",        ["be"],             ["VB"])
        TenseDetector.CustomToken("HAS",       ["has"],            ["VBZ"])
        TenseDetector.CustomToken("WAS",       ["was"],            ["VBD"])
        TenseDetector.CustomToken("WERE",      ["were"],           ["VBD"])
        TenseDetector.CustomToken("HAVE",      ["have","'ve"],     ["VBP","VB"])
        TenseDetector.CustomToken("WOULD",     ["would","'d"],     ["MD"])
        TenseDetector.CustomToken("MAY",       ["may"],            ["MD"])
        TenseDetector.CustomToken("MIGHT",     ["might"],          ["MD"])
        TenseDetector.CustomToken("CAN",       ["can"],            ["MD"])
        TenseDetector.CustomToken("COULD",     ["could"],          ["MD"])
        TenseDetector.CustomToken("SHALL",     ["shall"],          ["MD"])
        TenseDetector.CustomToken("SHOULD",    ["should"],         ["MD"])
        TenseDetector.CustomToken("MUST",      ["must"],           ["MD"])
        TenseDetector.CustomToken("OUGHT",     ["ought"],          ["MD"])

        for custom_tag in TenseDetector.CustomToken.CustomTokens:
            pattern = [
                {
                    "LOWER" : {"IN": custom_tag.text_pattern}, 
                    "TAG": {"IN": custom_tag.required_tag}
                }
            ]
            attrs = {"TAG": custom_tag.token_tag}
            self._ruler.add(patterns=[pattern], attrs=attrs)
            self._tag_filters.append(custom_tag.token_tag)

    def _set_tense_grammar(self) -> None:
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
        self._tenses.append(TenseDetector._Tense("Might_passive",                           [["MAY", "MIGHT"], "BE", "VBN"],                    ["The movie may be watched.", "The movie might be watched."]))
        self._tenses.append(TenseDetector._Tense("Might",                                   [["MAY", "MIGHT"],"VB"],                            ["I may watch the movie.", "I might watch the movie."]))
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
            self._tenses_grammar = self._tenses_grammar + f"{tense.tense_name}: {tense.get_tense_structure()}\n"
            self.tense_names.append(tense.tense_name)

    def list_tenses(self, text : (str|list[str]), split_sentences=False) -> (tuple[str, list[str]] | tuple[list[str], list[list[str]]]):
        """
        Lists the tenses of a text or list of texts.

        Parameters
        ----------
        text : (str/list[str])
            Text or list of texts to analyze.
        split_sentences : bool
            When passing single string, option to split into sentences.

        Returns
        -------
        tuple[str, list[str]]/tuple[list[str], list[list[str]]]
            If a single, text is passed with ``split_sentences = false`` returns the text and the list of tenses in that text.
            If a list of texts is passed or a text with ``split_sentences = true`` returns the list of sentences and a list of their corresponding tenses.

        Examples
        --------
        >>> list_tenses(["The movie has been watched. The movies have been watched."])
        ('The movie has been watched. The movies have been watched.', ['present_perfect_passive', 'present_perfect_passive'])]
        >>> list_tenses(["The movie has been watched. The movies have been watched."],split_sentences = True)
        [('The movie has been watched. The movies have been watched.', ['present_perfect_passive', 'present_perfect_passive'])]
        >>> list_tenses(["The movie has been watched.", "The movies have been watched."])
        [('The movie has been watched.', ['present_perfect_passive']), ('The movies have been watched.', ['present_perfect_passive'])]
        """

        if isinstance(text, list):
            return self._determine_tenses(text)

        if isinstance(text, str):
            #if its supposed to be split
            if split_sentences:
                sentences = self._split_sentences(text)
                return self._determine_tenses(sentences)
            else:
                return self._determine_tense(text)

    def _check_tense_grammar(self): #check whether the example sentences are all detected
        for tense in self._tenses:
            for sentence in tense.examples:
                print(f"{tense.tense_name}:{self._determine_tense(sentence)}")

    def _split_sentences(self, text : str) -> list[str]:
        return re.split(r"[.!?]\s+(?=[A-Z])", text)

    def _determine_tense(self, sentence : str):
        doc = self._nlp(sentence)
        filtered_tagged_sentence = [(token.text, token.tag_) for token in doc if token.tag_ in self._tag_filters]
        if len(filtered_tagged_sentence) == 0: #if there is nothing left in the sentence
            return "", []
        cp = nltk.RegexpParser(self._tenses_grammar)
        result = cp.parse(filtered_tagged_sentence,trace=0)

        tenses = []
        for subtree in result.subtrees():
            if subtree.label() in self.tense_names:
                tenses.append(subtree.label())

        return sentence, tenses

    def _determine_tenses(self, sentences : list[str]):
        results = []
        for sentence in sentences:
            results.append(self._determine_tense(sentence))

        return results

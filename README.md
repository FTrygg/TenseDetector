# TenseDetector
Simple Python Class to determine tenses in english sentences


# How to use
Create an instance of the class and feed it text. The text can either be a block of text (then you should use splitSentences=True), or a list of sentences.

## Code:
```
t = TenseDetector()   
t.listTenses(["This is a great test.", "I would like to get the tenses back.", "Wouldnt this be great?"], splitSentences=True)
```
## Results:
```
[('This is a great test.', ['present_simple']),
 ('I would like to get the tenses back.',
  ['conditional_simple', 'infinitive']),
 ('Wouldnt this be great?', ['conditional_simple'])]
```

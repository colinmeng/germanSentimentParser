# German Sentiment Parser

A dictionary-based approach to Aspect-Level-Sentiment Analysis of german text on the basis of [SpaCy's](https://spacy.io) dependency parsing. 

## Getting Started

### Dependencies
- Python Version 3.x.x
- Spacy Version 3.x.x 
- Spacy Language Model "de_core_news_lg"

### How to install
Find out [here](https://spacy.io/usage) how to install SpaCy on your system. Make sure to download the right Language Model.

### How to use
For a demonstration execute the script ./test/testSentimentAnalyser.py

To use the sentiment analyser in your own script you only need to create a sentiment lexicon and initalize the language model.

#### Create a sentiment lexicon
1. import the lexicon  module from sentimentParser
2. decide which look up mode you want to choose
    1. "min"        : always takes the lowest value
    2. "max"        : always takes the highest value
    3. "mean"       : takes the mean of all values
    4. "no neutral" : takes the mean of all values, that are not 0

- the most accurate results are brought by "no neutral" or "mean"
- for further information about the data used to create the sentiment lexicon see lexicon/README.md 

##### create a Lexicon object
    
    lexicon = lexicon.Lexicon(pathToSentimentLexicon.json, mode)
e. g.: 

    lexicon = lexicon.Lexicon("lexicon//sentimentLexicon.json, "no neutral")

#### Initalize a language model

    nlp = spacy.load("de_core_news_lg")
- you can also use different models, but make sure you installed them before
- the language model brings with it a complete NLP-Pipeline
- we use dependency parsing as well as POS-tagging

#### Do the magic

firstly you need to import the sentimentAnalysis (sa) module from sentimentParser
Now you have can do sentiment analysis on different levels on your message

1. aspect level
    -  Returns a list of tupels('aspect', sentiment)

            aspectSentiments = sa.geAspectSentiments(message,lexicon,nlp)
    
    - Returns a list of tupels('aspect', polarity) polarity is one of these: [1,0,-1]

            aspectPolarities = sa.getAspectPolarities(message,lexicon.nlp)
  
2. sentence level

    - Returns a list of sentiments (float) with index = sentence number (starting with 0)

            sentenceSentiments = sa.geSentenceSentiments(message,lexicon,nlp)
    
    - Returns a list of polarities (int) with index = sentence number (starting with 0)

            sentencePolarities = sa.getSentencePolarities(message,lexicon,nlp)

3. document level
    for document level sentiment analysis there is one extra (optional) parameter "perSentence" (default: False)
    If you set this to True, then the document sentiment is calculated as mean of all sentence sentiments. Else it is the mean of all aspects sentiments.

    - Returns the documents sentiment (float), calculated per Sentence

            documentSentiment = sa.getDocumentPolarities(message,lexicon,nlp,True)
    
    - Returns the documents polarity (int), calculated per Aspect

            documentSentiment = sa.getDocumentPolarities(message,lexicon,nlp,False)

#### Nice to know
1. if you want to get the words, that are uncovered by the sentiment lexicon

        missingWords = sa.getMissingWords(message,lexicon,nlp)

2. You can set a threshold from which value nouns and verbs are considered in sentiment calculation. Sometimes the calculation gets messed up because of low sentiment verbs. Change the NeutralVerbThreshold in sentimentParser/sentimentAnalysis.py to a value of 1, to completely exclude the verbs sentiment, except for verbial shifter(they have a value of -1), which are **essential**.

### More Questions?
Contact me  via [email](mailto:colin.meng.business@gmail.com) or 
+49 174 201 66 91 on SMS/ WhatsApp/ Signal /Telegram or
add me on Discord: Colin#8916




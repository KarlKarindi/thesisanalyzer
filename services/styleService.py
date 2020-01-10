import estnltk
from estnltk import Text
from .utils import *
import simplejson as json
import nltk
from .. import vabamorf

def analyze_style(content):
    text = json_to_text(request)
    sentences = Text(text).sentence_texts

    for sent in sentences:
        analyze_sentence_length_by_verb_count(sent)
    
    return "TODO: make style"


def analyze_sentence_length_by_verb_count(sentence):
    """ Analyzes the sentence by verb count.
        If there are too many verbs in a sentence,
        it can be considered to be too long.
    """ 
    
    def tag_words(analysis):
        """ Tag all the words in a sentence using vabamorf.
            
            Parameters:
                analysis (list): one analysed sentence 

            Returns:
                list of tags
                list of tuplets (word, tag)
        """

        tags = []
        words = []
        tags_with_words = []

        for analyzed_sent in analysis:
            tag = analyzed_sent["analysis"][0]["partofspeech"]
            word = analyzed_sent["text"]
            tags.append(tag)
            tags_with_words.append((word, tag))
        
        return tags, tags_with_words

    analysis = vabamorf.analyze(sentence)
    tags, tags_with_words = tag_words(analysis)

    verb_count = 0 
    for i in range(len(tags)):
        if tags[i] == "V":
            verb_count += 1
            print(analysis[i]["text"])
    
    return True
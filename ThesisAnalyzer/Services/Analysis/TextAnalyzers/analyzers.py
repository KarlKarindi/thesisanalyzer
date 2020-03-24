# This module contains different analyzers for text processing.

from ThesisAnalyzer.Constants import constants

from estnltk import Text

import re


class QuoteAnalyzer(object):
    """ QuoteAnalyzer checks whether a certain word in a sentence is in quotes or not.

        Usage:
            1. Initialize a new instance of QuoteAnalyzer
            2. Take one sentence for inspection.
            3. Iterate over all of the words.
            4. For every word, call out the is_word_in_quotes(word) function with
            the word's text (string) as its argument.
    """

    def __init__(self):
        self.in_quotes = False
        self.previous_word = None

    def is_word_in_quotes(self, word):
        """ Checks whether word is in quotes or not.
            Uses self.previous_word and self.in_quotes to make a decision whether word is in quotes or not.
            Parameters:
                word (String) - Examples: "," ; "hi", "'"
            Returns:
                in_quotes (boolean) - whether the word is in quotes or not
        """
        # First, assume that this word won't be skipped
        quotes_just_started = False

        # Ending the quote
        if self.previous_word is not None and self.in_quotes:
            # Check if the last letter is an ending quotation mark.
            # The last letter is necessary, as sometimes words are marked as !",
            # so just checking previous_word isn't enough.
            if self.previous_word[-1] in constants.QUOTE_MARKS_ENDING:
                self.in_quotes = False

            # Sometimes an ending quote word is 2 symbols together.
            # for example: ". or “.
            # This condition checks for these cases.
            # First, check if word is longer than 1 to avoid out of bounds exception.
            elif len(self.previous_word) > 1:
                # If second to last letter is an ending quotation mark, set in_quotes to false
                if self.previous_word[-2] in constants.QUOTE_MARKS_ENDING:
                    self.in_quotes = False

        # Starting the quote
        if not self.in_quotes and word in constants.QUOTE_MARKS_STARTING:
            # Set quotes_just_started_to_true
            self.in_quotes, quotes_just_started = True, True

        # If quotes just started, skip setting the previous word as current word so that on the next word,
        # the same quotes won't be marked as ending the quote
        if not quotes_just_started:
            self.previous_word = word

        return self.in_quotes


class CitationAnalyzer(object):
    """ Analyzer for citations in text.
        Usage:
            1. Initalize a new instance of CitationAnalyzer.
            2. Take one sentence for inspection.
            3. Call out the get_sentence_without_citations function
    """

    # Initializes the regex to find citations by
    def __init__(self):
        between_parentheses_with_first_char_uppercase = r"\([A-Z][^\)]*,[^\)]*\)"
        between_brackets = r"\[[0-9]+]"
        ibid = r"\(ibid.+\)"
        self.regex = re.compile(
            between_parentheses_with_first_char_uppercase + "|" + between_brackets + "|" + ibid)

    def find_citation_indexes_in_sentence(self, sentence):
        """ Finds the indexes of citations in a sentence.
            Indexes are on a char level.
            Parameters:
                sentence (string) - sentence text
            Returns:
                indexes (list) - list of char indexes that are part of citations
        """

        indexes = []
        for m in self.regex.finditer(sentence):
            start = m.start()
            end = m.end()

            # Remove whitespace around citation
            if (start - 1 >= 0) and sentence[start - 1] == " ":
                start -= 1
            if (end + 1 < len(sentence) - 1) and sentence[end + 1] == " ":
                end += 1

            indexes.extend(list(range(start, end)))
        return indexes

    def get_sentence_without_citations(self, sentence):
        """ Returns a Text object of a sentence without citations in the text
            Parameters:
                sentence (string) - sentence text
            Returns:
                Text object of a sentence with tagged layers.
        """

        ref_indexes = self.find_citation_indexes_in_sentence(sentence)

        return Text("".join([char for i, char in enumerate(
            sentence) if i not in ref_indexes])).tag_layer()

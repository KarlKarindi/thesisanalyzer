from ThesisAnalyzer.Services.Analysis import sentences_analyzer
from ThesisAnalyzer.Models.Analysis import SentenceWithMissingCommas, MissingCommas
from copy import copy
from pprint import pprint


def get_sentence_with_missing_comma(i, mc_clause_segmenter, vc_detector,
                                    sentence_copy, clause_and_verb_chain_index,
                                    preprocessed_text):
    """ Analyzes a single sentence. Is called out in the sentences_analyzer module
        when iterating over all the sentences.

        Parameters:
            i (int) - the index of the current sentence under observation
            mc_clause_segmenter (ClauseSegmenter) - missing commas clause segmenter.
                                                    an instance of the clause segmenter that
                                                    has ignore_missing_commas setting set to True
            vc_detector (VerbChainDetector) - an instance of the VerbChainDetector
            sentence_copy (Text) - a copy of the cleaned (!) sentence
            clause_and_verb_chain_index (dict) - an index of values: clauses and corresponding verb chains
            preprocessed_text (PreprocessedText) - output of utils.preprocess_text()

        Returns:
            None if the sentence doesn't have a missing comma.
            Instance of SentenceWithMissingCommas if there is a missing comma in the sentence
    """

    # Tag the sentence copy using mc_clause_segmenter
    mc_clause_segmenter.tag(sentence_copy)

    clauses_using_mc_segmenter = sentence_copy.clauses

    mc_clause_and_verb_chain_index = sentences_analyzer.create_clause_and_verb_chain_index(
        clauses_using_mc_segmenter, vc_detector)

    clause_positions_with_mc_segmenter = clauses_using_mc_segmenter[["start", "end"]]

    # Find the missing commas in a sentence. missing_commas is of type MissingCommas
    missing_commas = find_missing_commas_in_sentence(
        mc_clause_and_verb_chain_index, clause_and_verb_chain_index,
        preprocessed_text.sentences[i], preprocessed_text.sentence_words[i],
        clause_positions_with_mc_segmenter, sentence_copy)

    if missing_commas is not None:
        # Add the sentence dictionary from the preprocessed_text.sentences, contains position info and text.
        return SentenceWithMissingCommas(preprocessed_text.sentences[i],
                                         missing_commas, clause_positions_with_mc_segmenter)

    return None


def find_missing_commas_in_sentence(mc_clause_and_verb_chain_index, clause_and_verb_chain_index,
                                    preprocessed_text_sentence, preprocessed_text_sentence_words,
                                    clause_positions, cleaned_sentence_copy):
    """ Finds the missing commas in a sentence if there are any.
        Compares the original clause segmenter's result with the one that ignores missing commas.
        Parameters:
            mc_clause_and_verb_chain_index (dict) - the clause to verb chain dictionary using missing commas segmenter
            clause_and_verb_chain_index (dict) - the original clause to verb chain dictionary
            preprocessed_text_sentence (dict) - dictionary value from preprocessed_text.sentences[i]
            preprocessed_text_sentence_words (dict) - dictionary value from preprocessed_text.sentence_words[i]
            clause_positions (list) - list of clause positions in the cleaned_sentence (!)
            cleaned_sentence_copy (string) - Copy of the original cleaned sentence
        Returns:
            clause_positions and an instance of MissingCommas or None, if there isn't one.
    """
    # Initialize the missing_commas as an empty list, in case there aren't any missing commas
    missing_commas = None
    if len(mc_clause_and_verb_chain_index) > len(clause_and_verb_chain_index):
        # There is a potentially missing comma in the sentence.
        # We make dict (!) copies so as to not add an empty row into the original clause_and_verb_chain index.
        # defaultdict adds a key if the key isn't found, and we don't want that to happen to the original index.
        original = dict(copy(clause_and_verb_chain_index))
        fixed = dict(copy(mc_clause_and_verb_chain_index))

        # Find the indexes of the clauses needing a comma in front of them
        indexes_of_clauses_needing_comma = find_indexes_of_clauses_needing_comma(original, fixed)

        # Find the indexes of the commas that are missing
        if len(indexes_of_clauses_needing_comma) > 0:
            indexes_of_missing_commas = []
            for i in indexes_of_clauses_needing_comma:
                indexes_of_missing_commas.append(clause_positions[i][0])

            clauses_that_need_comma = []
            for i in indexes_of_clauses_needing_comma:
                clauses_that_need_comma.append(cleaned_sentence_copy.text[
                    clause_positions[i][0]:clause_positions[i][1]])

            missing_commas = MissingCommas(indexes_of_missing_commas, clauses_that_need_comma)

    return missing_commas


def find_indexes_of_clauses_needing_comma(original, fixed):
    """ Finds the indexes of the clauses that a comma should be put in front of.

        Iterate over the original_clause dictionary.
        If the original and fixed don't match, it should be 2 clauses.
        Set a counter that, when looking at the original clause, will iterate over
        all the subclauses that belong to the original clause.
        Once the subclauses are all found, increment i to take the next original clause.

        Parameters:
            original (dict) - the original clause_to_verb_chain_index
            fixed (dict) - the clause_to_verb_chain_index_with_missing_commas
        Returns:
            indexes of the clauses needing a comma
    """
    indexes = []

    counter = 0
    for i, v in original.items():
    
        original_clause = original[i]["clause"]
        fixed_clause = fixed[counter]["clause"]

        clauses_are_the_same = all(word in fixed_clause for word in original_clause)
        if not clauses_are_the_same:
            prev = fixed_clause
            can_add_comma = False  # A comma can be added if it's not the first clause in fixed.
            # Start to iterate over the following fixed clauses.
            # If they are a sublist of the original clause, they need a comma.
            while counter < len(fixed) and is_sublist(fixed_clause, original_clause):
                last_clause_ended_with_comma = prev[-1][-1] == ","
                if can_add_comma and not last_clause_ended_with_comma:
                    indexes.append(counter)

                counter += 1

                if counter >= len(fixed):
                    break

                prev = fixed_clause
                fixed_clause = fixed[counter]["clause"]
                can_add_comma = True  # It's not the first clause anymore, so start adding comas
        else:
            counter += 1

    return indexes


def is_sublist(pattern, bigger_list):
    """ Checks if a pattern is a sublist of a bigger list
        Taken from here: https://stackoverflow.com/questions/10106901/elegant-find-sub-list-in-list
    """

    matches = []
    for i in range(len(bigger_list)):
        if bigger_list[i] == pattern[0] and bigger_list[i:i + len(pattern)] == pattern:
            matches.append(pattern)
    return matches

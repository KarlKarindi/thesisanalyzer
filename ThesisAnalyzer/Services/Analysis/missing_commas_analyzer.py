from ThesisAnalyzer.Services.Analysis import sentences_analyzer
from ThesisAnalyzer.Models.Analysis import SentenceWithMissingCommas, MissingCommas
from copy import copy


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
        Parameters:
            original (dict) - the original clause_to_verb_chain_index
            fixed (dict) - the clause_to_verb_chain_index_with_missing_commas
        Returns:
            index of the clause
    """
    indexes = []

    skip = False
    for k, v in fixed.items():
        if skip:
            skip = False
            continue

        fixed_clause = fixed[k]["clause"]
        try:
            original_clause = original[k]["clause"]
            clauses_are_the_same = all(word in fixed_clause for word in original_clause)
            if not clauses_are_the_same:
                # In the original_clause there is a clause A that should be divided to clauses M and N.
                # This means that a comma should be put in front of clause N.
                if k + 1 < len(fixed):
                    indexes.append(k + 1)
                    # Skip the next one
                    skip = True
                    # FIXME: Continue cycle
                    return indexes

        except KeyError:
            print("keyerror", k, v)
            # This clause didn't exist in the original index.
            # It should not get to this exception, but it's added for extra safety.
            # indexes.append(k)

    return indexes

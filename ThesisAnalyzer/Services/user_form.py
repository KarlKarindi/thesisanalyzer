from ThesisAnalyzer.Config import analysis as config
from copy import deepcopy
from pprint import pprint


class FormData(object):
    def __init__(self,
                 elapsed_time,
                 sentence_count,
                 word_count,
                 sentences_with_pv,
                 pv_in_sentences,
                 long_sentences,
                 overused_words,
                 highlighted_sentences,
                 highlighted_clusters,
                 poolt_tarind_sentences,
                 olema_kesksona_sentences,
                 maarus_saavas_sentences,
                 nominalisatsioon_mine_vormis_sentences,
                 missing_comma_sentences
                 ):

        self.elapsed_time = elapsed_time
        self.sentence_count = sentence_count
        self.word_count = word_count
        self.sentences_with_pv = sentences_with_pv
        self.pv_in_sentences = pv_in_sentences
        self.long_sentences = long_sentences
        self.overused_words = overused_words
        self.highlighted_sentences = highlighted_sentences
        self.highlighted_clusters = highlighted_clusters
        self.poolt_tarind_sentences = poolt_tarind_sentences
        self.olema_kesksona_sentences = olema_kesksona_sentences
        self.maarus_saavas_sentences = maarus_saavas_sentences
        self.nominalisatsioon_mine_vormis_sentences = nominalisatsioon_mine_vormis_sentences
        self.missing_comma_sentences = missing_comma_sentences


def format_data(text, result):
    """ Format the data received from the user form.
        ONLY CALLED OUT WHEN A REQUEST FROM THE USER FORM IS MADE
        Parameters:
            text (string) the original, full text
            result (Summary) - analysis result in decoded form
    """

    # Initalize in case some analyses are turned off, avoids errors.
    # if a new list is added, it must be initialized here first.
    sentence_count, word_count, sentences_with_pv, pv_in_sentences, long_sentences, \
        overused_words, all_WS_sentences, all_WS_clusters, all_poolt_tarind_sentences, \
        all_olema_kesksona_sentences, all_maarus_saavas_sentences, all_nominalisatsioon_mine_vormis_sentences, \
        missing_comma_sentences \
        = 1, 1, [], [], [], [], [], [], [], [], [], [], []

    elapsed_time = result["elapsed_time"]
    if config.ANALYZE_OVERUSED_WORDS:
        sentence_count = result["text_summary"]["sentence_count"]
        word_count = result["text_summary"]["word_count"]

    # Impersonality
    if config.ANALYZE_IMPERSONALITY:
        is_impersonal = result["impersonality_summary"]["is_impersonal"]
        sentences_with_pv = result["impersonality_summary"]["sentences_with_pv"]

        pv_in_sentences = []
        if not is_impersonal:
            for value in sentences_with_pv.values():
                words = ", ".join(value)
                pv_in_sentences.append(words)

    # Long sentences
    if config.ANALYZE_SENTENCES:
        long_sentence_object_list = result["sentences_summary"]["long_sentences"]
        long_sentences = [s["text"] for s in long_sentence_object_list]

        missing_comma_sentence_object_list = result["sentences_summary"]["sentences_with_missing_commas"]
        missing_comma_sentences = [[s["text"], " ; ".join(s["clauses_after_missing_comma"])]
                                   for s in missing_comma_sentence_object_list]

    # Overused words
    if config.ANALYZE_OVERUSED_WORDS:
        overused_words = result["text_summary"]["overused_word_summary"]
        # Create a list of sentences. Word summary is shortened here to WS.
        # Each highlighted sentence index corresponds to one word's summary. Has all the sentences of that word summary
        all_WS_sentences = []
        all_WS_clusters = []
        for word_summary in overused_words:
            # Add all the sentences of one word summary to highlighted_sentences list.
            one_WS_sentences = handle_sentences_for_one_OWS(text, word_summary)
            all_WS_sentences.append(one_WS_sentences)

            # Clusters
            one_WS_clusters = []
            words = word_summary["words"]
            for cluster in word_summary["clusters"]:
                sentence = []
                cluster_text = cluster["text"]
                word_indexes = cluster["word_indexes"]
                last_word_pos = 0
                for i in word_indexes:
                    positions = words[i]["position_in_cluster"]
                    before = cluster_text[last_word_pos:positions[0]]
                    bold = cluster_text[positions[0]:positions[1]]
                    sentence.append(before)
                    sentence.append(bold)
                    # Update the position of the last word's end.
                    last_word_pos = positions[1]
                # Add the remainder of the sentence.
                sentence.append(cluster_text[last_word_pos:])

                one_WS_clusters.append(sentence)

            # Add all the clusters of one word summary to all_WS_clusters list.
            all_WS_clusters.append(one_WS_clusters)

    if config.ANALYZE_OFFICIALESE:
        poolt_tarind_list = result["officialese_summary"]["poolt_tarind_summary"]
        all_poolt_tarind_sentences = handle_olema_kesksona_and_poolt_tarind_list(
            poolt_tarind_list, text)

        olema_kesksona_list = result["officialese_summary"]["olema_kesksona_summary"]
        all_olema_kesksona_sentences = handle_olema_kesksona_and_poolt_tarind_list(
            olema_kesksona_list, text)

        maarus_saavas_list = result["officialese_summary"]["maarus_saavas_summary"]
        all_maarus_saavas_sentences = handle_parent_child_list(
            maarus_saavas_list, text)

        nominalisatsioon_mine_vormis_list = result["officialese_summary"]["nominalisatsioon_mine_vormis_summary"]
        all_nominalisatsioon_mine_vormis_sentences = handle_parent_child_list(
            nominalisatsioon_mine_vormis_list, text)

    return FormData(elapsed_time,
                    sentence_count,
                    word_count,
                    sentences_with_pv,
                    pv_in_sentences,
                    long_sentences,
                    overused_words,
                    all_WS_sentences,
                    all_WS_clusters,
                    all_poolt_tarind_sentences,
                    all_olema_kesksona_sentences,
                    all_maarus_saavas_sentences,
                    all_nominalisatsioon_mine_vormis_sentences,
                    missing_comma_sentences
                    )


def handle_sentences_for_one_OWS(text, word_summary):
    """ Iterate over all the words for an overused word. """

    one_WS_sentences = []

    # Create a copy of the words list, as we don't want to modify the original one
    words = deepcopy(word_summary["words"])

    # Every element with an even-numbered index is the word to be marked in bold.
    # For example, if we are looking for the word "verb", our final singular sentence would be
    # ["See siin on mitme ", "verbiga", " lause, sest siin sisaldub mitu ", "verbi", ", kuna see on mu lemmiks??na."]
    # Further on, the comments will explain building this sentence.
    sentence = []
    a_pos = None
    last_sentence_pos = None
    last_sentence_index = None
    is_first_elem = True

    while len(words) > 0:
        # Comments will play through the example found further up.
        word = words.pop(0)
        sentence_index = word["sentence_index"]
        sentence_pos = word["sentence_position"]
        word_pos = word["position"]

        # If it's the first element, set a_pos as the start of the sentence
        if is_first_elem:
            a_pos = sentence_pos[0]

        if not is_first_elem:
            if last_sentence_index != sentence_index:
                # A new sentence has started.
                # Add the remainder of the sentence: ", kuna see on mu lemmiks??na."
                sentence.append(text[a_pos:last_sentence_pos[1]])
                one_WS_sentences.append(sentence)  # Add sentence to this WS sentences
                # Initialize a new sentence list and set a_pos to the start of the new sentence
                a_pos = sentence_pos[0]
                sentence = []

        sentence.append(text[a_pos:word_pos[0]])  # Add "See siin on mitme ", then " lause, sest siin sisaldub mitu "
        sentence.append(text[word_pos[0]:word_pos[1]])  # Add "verbiga", then "verbi"

        a_pos = word_pos[1]  # Set a_pos to the end of the word "verbiga", then "verbi"
        last_sentence_pos = sentence_pos
        last_sentence_index = sentence_index
        is_first_elem = False

    return one_WS_sentences


def handle_olema_kesksona_and_poolt_tarind_list(analysis_list, text):
    """ Handles objects that have the following attributes:
            position,
            sentence_position,
            sentence_text,
            text
    """
    # Contains lists, where
    # The first element is the sentence before bold, the second is the bold text, third is after bold.
    all_analysis_sentences = []

    for offender in analysis_list:
        sentence_position = offender["sentence_position"]
        position = offender["position"]

        sentence_before_bold = text[sentence_position[0]:position[0]]
        text_in_bold = text[position[0]:position[1]]
        sentence_after_bold = text[position[1]:sentence_position[1]]
        all_analysis_sentences.append(
            [sentence_before_bold, text_in_bold, sentence_after_bold])

    return all_analysis_sentences


def handle_parent_child_list(analysis_list, text):
    """ Used for m????rus saavas and nominalisatsiooni mine vorm analysis results.
        Used to mark words in bold that might not be connected.
        See class ParentChildContainer
    """
    # Contains lists, where:
    # The first element is in before bold, second is bold, third is after the first bold,
    # fourth is bold and the fifth is after bold.
    all_parent_child_sentences = []

    for offender in analysis_list:
        sentence_position = offender["sentence_position"]
        first_position, second_position = find_first_and_second_position(offender)

        sentence_before_first_bold = text[sentence_position[0]:first_position[0]]
        text_in_first_bold = text[first_position[0]:first_position[1]]
        sentence_after_first_bold = text[first_position[1]:second_position[0]]
        text_in_second_bold = text[second_position[0]:second_position[1]]
        sentence_after_second_bold = text[second_position[1]:sentence_position[1]]

        all_parent_child_sentences.append(
            [sentence_before_first_bold, text_in_first_bold, sentence_after_first_bold,
             text_in_second_bold, sentence_after_second_bold])

    return all_parent_child_sentences


def find_first_and_second_position(maarus_saavas_container):
    if child_is_first_in_text(maarus_saavas_container):
        return maarus_saavas_container["child_position"], maarus_saavas_container["parent_position"]
    else:
        return maarus_saavas_container["parent_position"], maarus_saavas_container["child_position"]


def child_is_first_in_text(maarus_saavas_container):
    if maarus_saavas_container["child_position"][0] < maarus_saavas_container["parent_position"][0]:
        return True
    return False

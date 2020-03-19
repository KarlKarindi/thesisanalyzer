class FormData(object):
    def __init__(self, sentences_with_pv, pv_in_sentences, long_sentences,
                 overused_words, highlighted_sentences, highlighted_clusters):
        self.sentences_with_pv = sentences_with_pv
        self.pv_in_sentences = pv_in_sentences
        self.long_sentences = long_sentences
        self.overused_words = overused_words
        self.highlighted_sentences = highlighted_sentences
        self.highlighted_clusters = highlighted_clusters


def format_data(text, result):
    """ Format the data received from the user form.
        Parameters:
            text (string) the original, full text
            result (Summary) - analysis result in decoded form
    """

    # Impersonality
    is_impersonal = result["impersonality_summary"]["is_impersonal"]
    sentences_with_pv = result["impersonality_summary"]["sentences_with_pv"]
    pv_in_sentences = []
    if not is_impersonal:
        for value in sentences_with_pv.values():
            words = ", ".join(value)
            pv_in_sentences.append(words)

    # Long sentences
    long_sentences = result["sentences_length_summary"]["long_sentences"]

    # Overused words
    overused_words = result["text_summary"]["overused_word_summary"]
    # Create a list of sentences. Word summary is shortened here to WS.
    # Each highlighted sentence index corresponds to one word's summary. Has all the sentences of that word summary
    all_WS_sentences = []
    all_WS_clusters = []
    for word_summary in overused_words:
        one_WS_sentences = []  # Contains all the sentences of one word summary

        # Iterate over all the words for an overused word. Find the sentences the word is contained in.
        for word in word_summary["words"]:
            sentence_pos = word["sentence_position"]
            word_pos = word["position"]

            # Creates a list with 3 elements. Adds them to sentences list.
            sentence_before_word = text[sentence_pos[0]:word_pos[0]]
            word_in_bold = text[word_pos[0]:word_pos[1]]
            sentence_after_word = text[word_pos[1]:sentence_pos[1]]
            one_WS_sentences.append(
                [sentence_before_word, word_in_bold, sentence_after_word])

        # Add all the sentences of one word summary to highlighted_sentences list.
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

    return FormData(sentences_with_pv, pv_in_sentences, long_sentences,
                    overused_words, all_WS_sentences, all_WS_clusters)

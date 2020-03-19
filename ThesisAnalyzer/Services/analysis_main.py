# Import analyzers
from ThesisAnalyzer.Services.Analysis import \
    overused_word_analyzer, tag_analyzer, \
    sentences_length_analyzer, impersonality_analyzer

from ThesisAnalyzer.Config import style as config
from ThesisAnalyzer.Services.Analysis.tag_analyzer import TagSummary
from ThesisAnalyzer.Models.Summary import Summary
from ThesisAnalyzer.Services import utils
from ThesisAnalyzer.Services import profiler
from ThesisAnalyzer.Models.Lemma import Lemma
from ThesisAnalyzer.Models.LemmaStopword import LemmaStopword
from ThesisAnalyzer.Models.Analysis import SentencesLengthSummary, ImpersonalitySummary, TextSummmary

from flask import jsonify
import jsonpickle
from timeit import default_timer as timer
from threading import Thread
import queue
import os


def analyze(text):
    """ The main function that starts all analyses """
    start = timer()

    que = queue.Queue()
    threads = []
    # Set jsonpickle settings
    jsonpickle.set_preferred_backend("json")
    jsonpickle.set_encoder_options("json", ensure_ascii=False)

    # The main summary to be returned from the API
    summary = Summary()

    # Since finding the sentences layer takes time, do it once and pass it as an argument for the analyzers
    if config.ANALYZE_OVERUSED_WORDS or config.ANALYZE_SENTENCE_LENGTH or config.ANALYZE_IMPERSONALITY:
        sentences_layer = utils.get_sentences_layer(text)

        # Impersonality analyzer
        if config.ANALYZE_IMPERSONALITY:
            t1 = Thread(target=lambda q, arg1, arg2: q.put(
                impersonality_analyzer.analyze(arg1, arg2)), args=(que, text, sentences_layer))
            t1.start()
            threads.append(t1)

            #summary.impersonality_summary = th.join()

        # Overused words analysis
        if config.ANALYZE_OVERUSED_WORDS:
            Lemma_list = Lemma.query.all()
            Lemma_stopword_list = LemmaStopword.query.all()
            t2 = Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(
                overused_word_analyzer.analyze(arg1, arg2, arg3, arg4)),
                args=(que, text, sentences_layer, Lemma_list, Lemma_stopword_list))
            t2.start()
            threads.append(t2)

        # Clause analysis
        if config.ANALYZE_SENTENCE_LENGTH:
            t3 = Thread(target=lambda q, arg1, arg2: q.put(
                sentences_length_analyzer.analyze(arg1, arg2)), args=(que, text, sentences_layer))
            t3.start()
            threads.append(t3)

    # Tag analysis
    if config.ANALYZE_TAGS:
        summary.tag_summary = tag_analyzer.analyze(text)

    for t in threads:
        t.join()

    while not que.empty():
        result = que.get()
        if type(result) is ImpersonalitySummary:
            summary.impersonality_summary = result
        elif type(result) is SentencesLengthSummary:
            summary.sentences_length_summary = result
        elif type(result) is TextSummmary:
            summary.text_summary = result

    end = timer()

    print("TIME ELAPSED", end - start)

    return utils.encode(summary)

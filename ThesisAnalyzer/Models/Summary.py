from ThesisAnalyzer import db


class Summary(object):
    """ Container class for style analysis classes """

    def __init__(self):
        self.elapsed_time = None
        self.impersonality_summary = None
        self.tag_summary = None
        self.sentences_length_summary = None
        self.text_summary = None

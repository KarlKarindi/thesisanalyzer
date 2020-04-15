from ThesisAnalyzer import db


class Summary(object):
    """ Container class for analysis results. """

    def __init__(self):
        # Initialize the id as None, as it is only set when it's added to the database.
        self.id = None
        self.elapsed_time = None
        self.impersonality_summary = None
        self.tag_summary = None
        self.sentences_summary = None
        self.text_summary = None
        self.officialese_summary = None

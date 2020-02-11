from ThesisAnalyzer import db
from ThesisAnalyzer.Services.Analysis.Style.overused_word_analyzer import OverusedWordSummary, TextSummmary
from ThesisAnalyzer.Services.Analysis.Style.tag_analyzer import TagSummary


class StyleSummary(object):
    """ Container class for style analysis classes """

    def __init__(self):
        self.tagSummary = None
        self.clauseSummary = None
        self.textSummary = None

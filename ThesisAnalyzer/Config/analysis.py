# Config file for analysis
import env

LOG_TO_DATABASE = env.LOG_TO_DATABASE

ANALYSIS_MAX_CHAR_COUNT = 150000

# Options for analysis
ANALYZE_IMPERSONALITY = True
ANALYZE_OVERUSED_WORDS = True
ANALYZE_SENTENCES = True
ANALYZE_TAGS = True
ANALYZE_OFFICIALESE = True


# Clause analyzer
MAX_CLAUSE_AMOUNT = 4  # Max clause amount for the sentence to not even be considered long

# Overused word analyzer
OUW_NUM_WORDS_TO_ANALYZE = 8  # Number of overused words to return
OVERUSED_MULTIPLIER = 5
MIN_COUNT_OF_LEMMA = 7  # Minimum count of lemma in text
MAX_CLUSTER_SIZE = 3  # If the cluster size is larger than this, show it
CLUSTER_DISTANCE = 300  # Max distance of words in a cluster

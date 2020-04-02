import sys
sys.path.insert(0, "/var/www/thesis-api")

from ThesisAnalyzer import create_app
application = create_app()

import sys
sys.path.insert(0, "/var/www/thesis-api")
print("executable:", sys.executable)
print("prefix:", sys.prefix)
print(sys.version)
#help('modules')

from ThesisAnalyzer import create_app
application = create_app()

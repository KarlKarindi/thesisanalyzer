import os
import platform
import pathlib


def get_vislcg3_path():
    """ Returns the path of the vislcg3 binaries depending on OS """

    if platform.system() == "Windows":
        return os.getcwd() + "\\ThesisAnalyzer\\lib\\vislcg_windows\\vislcg3.exe"
    else:
        # Assume the OS is Ubuntu, use Ubuntu binaries
        return str(pathlib.Path(__file__).parent) + "/ThesisAnalyzer/lib/vislcg_ubuntu/cg3"


INDEX_PAGE = "/"
LOG_TO_DATABASE = False

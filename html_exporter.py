from bs4 import BeautifulSoup
from html.parser import HTMLParser

# Helper module to create html files for easier results analysis.

# IMPORT_PATH is the file created from an exported database set.
# EXPORT_PATH is the folder to save the results to.
# Run this file separately from the rest of the application, and change paths accordingly.
IMPORT_PATH = "C:\\users\\Karl\\PythonProjects\\Database_export\\2020_04_16.html"
EXPORT_PATH = "C:\\users\\Karl\\PythonProjects\\Database_results\\"


def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


with open(IMPORT_PATH, encoding="utf-8") as file:
    data = file.read().replace("&amp;lt;", "<").replace("&amp;gt;", ">")
    soup = BeautifulSoup(data, "html.parser")

    i = 0
    results = soup.find_all("td")

    while i < len(results):
        result = results[i]
        td_removed = str(result).strip("<td>").strip("</td>")
        if is_int(td_removed):
            id = td_removed
            # timestamp = str(results[i + 1])
            # timestamp = timestamp.strip("<td>").strip(
            #    "</td>").replace(" ", "_").replace(":", ".")[2:len(timestamp) - 6]
            content = str(results[i + 3])
            content = content[4:len(content) - 5]  # Remove the unnecessary td tags
            filename = str("result_" + id + ".html")
            with open(EXPORT_PATH + filename, "w", encoding="utf-8") as new_file:
                new_file.write(content)
                print("Created file", filename)
        i += 1

import csv


def create_csv_file_for_lemmas(file_loc):
    # Read in the file
    csv_rows = []
    with open(file_loc, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split()
            count, lemma = line[0], line[1]
            row = []
            row.append(lemma)
            row.append(count)
            csv_rows.append(row)

    # Write info into a csv file
    with open("lemmad_kahanevas.csv", mode="w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",",
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["lemma", "count"])
        for row in csv_rows:
            writer.writerow(row)

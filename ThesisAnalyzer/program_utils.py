import csv


def create_csv_file_for_lemma_frequency(file_path):
    # Read in the file
    csv_rows = []
    uid = 1
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip().split()
            count, lemma = line[0], line[1]
            row = []
            row.append(uid)
            row.append(lemma)
            row.append(count)
            csv_rows.append(row)
            uid += 1

    # Write info into a csv file
    with open("lemmad_kahanevas.csv", mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=",",
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id", "lemma", "count"])
        writer.writerows(csv_rows)

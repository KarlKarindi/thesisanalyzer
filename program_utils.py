import csv


def create_csv_file_for_lemmas(file_loc):
    # Read in the file
    csv_rows = []
    u_id = 1
    with open(file_loc, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip().split()
            count, lemma = line[0], line[1]
            row = []
            row.append(u_id)
            row.append(lemma)
            row.append(count)
            csv_rows.append(row)
            u_id += 1

    # Write info into a csv file
    with open("lemmad_kahanevas.csv", mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=",",
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id", "lemma", "count"])

        writer.writerows(csv_rows)

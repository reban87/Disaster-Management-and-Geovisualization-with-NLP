import csv

csv_file = "/home/rebanaryal/Disaster-Management-and-Geovisualization-with-NLP/datasets/ner_dataset.csv"
output_folder = "/home/rebanaryal/Disaster-Management-and-Geovisualization-with-NLP/datasets/ner_dataset"

with open(csv_file, "r") as my_input_file:
    csv_reader = csv.reader(my_input_file)
    for i, row in enumerate(csv_reader):
        txt_file = f"{output_folder}/row_{i+1}.txt"
        with open(txt_file, "w") as my_output_file:
            my_output_file.write(" ".join(row))

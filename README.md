# Disaster-Management-and-Geovisualization-with-NLP
ME Thesis - Rebanta Aryal Geo Informatics

# To run the script:
python3 main.py

# To download the model 
[bert-base-uncased](https://drive.google.com/drive/folders/176tJxO4A9pdraXwaVjFW74efZcPN7uIh)

[classification_roberta_v3.h5](https://drive.google.com/drive/folders/15nf9vXyF6ZsnpU3k6XZQr5FaDqH2KxKj)

[classification_roberta_v3.tokenizer](https://drive.google.com/drive/folders/15nf9vXyF6ZsnpU3k6XZQr5FaDqH2KxKj)

# Request Payload
For entity extraction:
```bash 
curl --location 'http://localhost:5000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "text": "a huge landslide occurs in bajura nepal. It happened in 1st march 2024. stay safe everyone"
}'

```
For classification
```bash
curl --location 'http://localhost:5000/predict' \
--header 'Content-Type: application/json' \
--data '{
    "text": "a huge landslide occurs in bajura nepal. It happened in 1st march 2024. stay safe everyone"
}'
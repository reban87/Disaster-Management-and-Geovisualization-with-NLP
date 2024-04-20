from transformers import (
    RobertaForSequenceClassification,
    AutoModelForTokenClassification,
    RobertaTokenizer,
    AutoTokenizer,
    pipeline,
)


import torch
from torch.utils.data import Dataset, DataLoader

from utils.preprocessing import preprocess_text

# Load RoBERTa classifier
from transformers import RobertaForSequenceClassification, RobertaTokenizer

# Load the saved model and tokenizer
roberta_model = RobertaForSequenceClassification.from_pretrained(
    "../models/classfication_roberta_v3.h5"
)
roberta_tokenizer = RobertaTokenizer.from_pretrained(
    "../models/classfication_roberta_v3.tokenizer"
)


# Load DistilBERT entity extractor
distilbert_model = AutoModelForTokenClassification.from_pretrained(
    "../models/bert-base-uncased-finetuned-v2/checkpoint-500"
)
distilbert_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


# Create custom dataset class
class TextDataset(Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.encodings["input_ids"])

    def __getitem__(self, index):
        item = {key: torch.tensor(val[index]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[index])
        return item


def classify_text(text):
    # Use the global model
    global roberta_model

    # Preprocess and classify text
    preprocessed_texts = preprocess_text(text)
    input_encodings = roberta_tokenizer(
        preprocessed_texts, truncation=True, padding=True, return_tensors="pt"
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Move the model to the device
    roberta_model = roberta_model.to(device)
    roberta_model.eval()

    input_ids = input_encodings["input_ids"].to(device)
    attention_mask = input_encodings["attention_mask"].to(device)

    with torch.no_grad():
        outputs = roberta_model(input_ids, attention_mask=attention_mask)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        prediction_label = "Disaster" if prediction == 1 else "Not Disaster"

    return prediction_label


def extract_entities(text):
    # Create a pipeline for 'ner'
    nlp = pipeline(
        "ner",
        model=distilbert_model,
        tokenizer=distilbert_tokenizer,
        aggregation_strategy="average",
    )

    # Run the pipeline on the input text
    ner_results = nlp(text)

    # Process the results
    entities = {"location": [], "date": [], "hazard_type": []}
    for entity in ner_results:
        if entity["entity_group"] == "LOC":
            entities["location"].append(entity["word"])
        elif entity["entity_group"] == "DATE":
            entities["date"].append(entity["word"])
        elif entity["entity_group"] == "HAZ":
            entities["hazard_type"].append(entity["word"])

    return {"entities": entities}

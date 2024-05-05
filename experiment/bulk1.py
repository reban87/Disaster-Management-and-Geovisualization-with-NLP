import streamlit as st
import pandas as pd
import requests
import moment
from io import StringIO
from visualise import generate_disaster_map
from streamlit_folium import folium_static

# Set up the page layout and title
st.set_page_config(page_title="Enhanced Text Analysis Tool", layout="wide")
st.title("Text Analysis and Visualization App")

# Initialize session state variables for results and map generation
if "classification_result" not in st.session_state:
    st.session_state["classification_result"] = ""
if "location" not in st.session_state:
    st.session_state["location"] = ""
if "raw_date" not in st.session_state:
    st.session_state["raw_date"] = ""
if "normalised_date" not in st.session_state:
    st.session_state["normalised_date"] = ""
if "hazard_type" not in st.session_state:
    st.session_state["hazard_type"] = ""
if "map_generated" not in st.session_state:
    st.session_state["map_generated"] = False

# Sidebar for input and controls
with st.sidebar:
    st.subheader("Input Text")
    user_input = st.text_area("Enter your text here:", height=200)
    classify_button = st.button("Classify Text")
    ner_button = st.button("Extract Entities")
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        if "text" in data.columns:
            process_button = st.button("Process Uploaded Texts")
        else:
            st.error("CSV must have a column named 'text'.")


# Function to call API endpoints
def process_text(api_url, input_text):
    response = requests.post(api_url, json={"text": input_text})
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Display classification result
st.subheader("Classification Results")
if classify_button:
    response = process_text("http://0.0.0.0:5000/predict", user_input)
    if response:
        st.session_state["classification_result"] = response.get("result", "")
    else:
        st.session_state["classification_result"] = (
            "Failed to get response from classification API."
        )
st.text_input(
    "Disaster vs Non Disaster",
    value=st.session_state["classification_result"],
    placeholder="Classification",
)

# Display NER results
st.subheader("NER Results")
if ner_button:
    response = process_text("http://0.0.0.0:5000/extract", user_input)
    if response:
        data = response
        location_set = set(
            filter(
                lambda x: x != "nan", data["results"]["entities"].get("location", [])
            )
        )
        st.session_state["location"] = ", ".join(location_set)

        raw_dates = data["results"]["entities"].get("date", [])
        st.session_state["raw_date"] = ", ".join(raw_dates)
        formatted_dates = [moment.date(d).format("YYYY-MM-DD") for d in raw_dates]
        st.session_state["normalised_date"] = ", ".join(set(formatted_dates))

        hazard_type_set = set(data["results"]["entities"].get("hazard_type", []))
        st.session_state["hazard_type"] = ", ".join(hazard_type_set)

    else:
        st.error("Failed to get response from NER extraction API.")

# Text input fields for displaying NER results
st.text_input(
    "Location",
    value=st.session_state["location"],
    placeholder="Location will appear here.",
)
st.text_input(
    "Date", value=st.session_state["raw_date"], placeholder="Date will appear here."
)
st.text_input(
    "Normalised Date",
    value=st.session_state["normalised_date"],
    placeholder="Normalised date will appear here.",
)
st.text_input(
    "Disaster Type",
    value=st.session_state["hazard_type"],
    placeholder="Disaster type will appear here.",
)

# Generate and display map
if ner_button and location_set and hazard_type_set:
    visualization_data = {
        "location": st.session_state["location"],
        "date": st.session_state["normalised_date"],
        "hazard_type": st.session_state["hazard_type"],
    }
    result_map = generate_disaster_map(
        visualization_data, "Disaster Layer", "Disaster Data"
    )
    if result_map:
        st.session_state["map_generated"] = True
        folium_static(result_map)
        st.success("Map has been successfully generated")

# Process uploaded CSV if available and button pressed
if "process_button" in locals() and process_button:
    results = []
    for text in data["text"]:
        classification_result = process_text("http://0.0.0.0:5000/predict", text)
        ner_result = process_text("http://0.0.0.0:5000/extract", text)
        result_entry = {
            "text": text,
            "classification": (
                classification_result.get("result")
                if classification_result
                else "Error"
            ),
            "location": (
                ", ".join(
                    set(
                        filter(
                            lambda x: x != "nan",
                            ner_result["results"]["entities"].get("location", []),
                        )
                    )
                )
                if ner_result
                else "Error"
            ),
            "date": (
                ", ".join(
                    set(
                        [
                            moment.date(d).format("YYYY-MM-DD")
                            for d in ner_result["results"]["entities"].get("date", [])
                        ]
                    )
                )
                if ner_result
                else "Error"
            ),
            "hazard_type": (
                ", ".join(set(ner_result["results"]["entities"].get("hazard_type", [])))
                if ner_result
                else "Error"
            ),
        }
        results.append(result_entry)
    results_df = pd.DataFrame(results)
    st.download_button(
        label="Download Results as CSV",
        data=results_df.to_csv(index=False),
        file_name="processed_results.csv",
        mime="text/csv",
    )

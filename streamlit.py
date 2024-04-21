import streamlit as st
import requests
import moment
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

# Display classification result
st.subheader("Classification Results")
if classify_button:
    response = requests.post("http://0.0.0.0:5000/predict", json={"text": user_input})
    if response.status_code == 200:
        st.session_state["classification_result"] = response.json().get("result", "")
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
    response = requests.post("http://0.0.0.0:5000/extract", json={"text": user_input})
    if response.status_code == 200:
        data = response.json()
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
    "Hazard Type",
    value=st.session_state["hazard_type"],
    placeholder="Hazard type will appear here.",
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

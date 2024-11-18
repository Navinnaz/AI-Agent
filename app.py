import io
import pandas as pd
import streamlit as st
import google_sheets  # Import your google_sheets.py file
from serpapi import GoogleSearch
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import time
import re
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
serpapi_key = os.getenv('SERPAPI_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

st.title('AI Data Extraction Dashboard')

# Reset session state on fresh run
if "reset" not in st.session_state:
    st.session_state.reset = True
    st.session_state.column = ""
    st.session_state.information_type = ""
    st.session_state.query_template = ""

# Sample UI element for file upload
uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

# Dynamically generate a dataset description
def generate_dataset_description(df):
    """Generate a textual description of the dataset."""
    try:
        description = "The dataset contains the following columns:\n"
        for col in df.columns:
            example_value = df[col].iloc[0] if not df[col].isna().all() else "N/A"
            description += f"- {col}: example value '{example_value}'\n"
        return description.strip()
    except Exception as e:
        return f"Error generating dataset description: {str(e)}"

# Load the CSV file into a DataFrame
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
        st.session_state.df = df
        st.success("CSV loaded successfully!")
        st.write(df.head())
    except Exception as e:
        st.error("Error loading CSV file. Please check the file format.")
        st.write(str(e))
else:
    df = st.session_state.get('df', None)

# Google Sheets Data Fetcher
sheet_id = st.text_input("Enter Google Sheet ID:")
range_name = st.text_input("Enter range name (e.g., 'Sheet1!A1:Z100'): ")

if sheet_id and range_name:
    try:
        data = google_sheets.get_google_sheet_data(sheet_id, range_name)
        if data is not None and not data.empty:
            st.success("Data fetched successfully from Google Sheets!")
            st.write(data)
            df = data
            st.session_state.df = df
        else:
            st.warning("No data found in the specified range.")
            df = None
    except Exception as e:
        st.error("Error fetching data from Google Sheets.")
        st.write(f"Details: {e}")
else:
    df = st.session_state.get('df', None)

# Main logic for column selection and processing
if df is not None and not df.empty:
    dataset_description = generate_dataset_description(df)  # Generate dynamic dataset description
    st.write("Dataset Description:")
    st.text(dataset_description)

    column = st.selectbox("Select the column for entities", df.columns, key="column")
    information_type = st.text_input("Enter the type of information you want (e.g., email, phone, etc.)", key="information_type")
    query_template = st.text_input(
        "Enter query template",
        placeholder="For example: Get the {information} of {entity}.",
        key="query_template"
    )

    if column and information_type and query_template:
        st.write(f"Selected Column: {column}")
        st.write(f"Information Type: {information_type}")
        st.write(f"Query Template: {query_template}")

        # Generate dynamic query
        def generate_dynamic_query(entity, information, query_template, dataset_description):
            return f"{dataset_description}\n\n{query_template.format(entity=entity, information=information)}"

        # Search query function
        def search_query(query):
            try:
                params = {"q": query, "api_key": serpapi_key, "num": 10}
                search = GoogleSearch(params)
                results = search.get_dict()

                if 'organic_results' in results:
                    return results['organic_results']
                else:
                    return f"No organic results found. Response: {results}"
            except Exception as e:
                return f"Error occurred: {str(e)}"

        # Parallel search processing
        search_results = {}
        progress_bar = st.progress(0)
        num_entities = len(df[column])

        def process_entity(entity):
            query = generate_dynamic_query(entity, information_type, query_template, dataset_description)
            results = search_query(query)
            return entity, results

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_entity = {executor.submit(process_entity, entity): entity for entity in df[column]}
            for idx, future in enumerate(as_completed(future_to_entity)):
                entity = future_to_entity[future]
                try:
                    entity, results = future.result()
                    search_results[entity] = results
                    progress_bar.progress((idx + 1) / num_entities)
                except Exception as e:
                    st.write(f"Error processing entity {entity}: {str(e)}")

        # Groq API integration for extracting information
        def process_with_retry(data, api_url, headers):
            try:
                response = requests.post(api_url, json=data, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if "Rate limit exceeded" in str(e):
                    wait_time = 60
                    time.sleep(wait_time)
                    return process_with_retry(data, api_url, headers)
                else:
                    raise

        def extract_information_with_groq(entity, search_results, query_template, groq_api_key):
            try:
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {groq_api_key}"}
                data = {
                    "model": "llama-3.2-1b-preview",
                    "messages": [{"role": "user", "content": generate_dynamic_query(entity, information_type, query_template, dataset_description) + f"\n\nWeb Results:\n{search_results}"}],
                    "max_tokens": 500,
                    "temperature": 0.5
                }
                response_data = process_with_retry(data, api_url, headers)

                if "choices" not in response_data or not response_data["choices"]:
                    return f"Error: 'choices' key is missing or empty in the response: {response_data}"
                
                choice = response_data["choices"][0]
                return choice.get("text", "Error: 'text' field is missing in the first choice.").strip()
            except Exception as e:
                return f"Error extracting information: {str(e)}"

       
        # Parallel extraction processing
        extracted_data = {}

        def process_extraction(entity, results, groq_api_key):
            """Process extraction of information for an entity."""
            try:
                result_text = "\n".join([str(r) for r in results])
                extracted_info = extract_information_with_groq(entity, result_text, query_template, groq_api_key)
                return entity, extracted_info  # Ensure exactly two values are returned
            except Exception as e:
                return entity, f"Error: {str(e)}"  # Return the error as the second value for debugging

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit tasks for parallel execution
            future_to_entity = {
                executor.submit(process_extraction, entity, results, groq_api_key): entity
                for entity, results in search_results.items()
            }
            for idx, future in enumerate(as_completed(future_to_entity)):
                entity = future_to_entity[future]  # Retrieve the entity associated with the future
                try:
                    entity, extracted_info = future.result()  # Unpack exactly two values
                    extracted_data[entity] = extracted_info  # Store the result in the dictionary
                    progress_bar.progress((idx + 1) / len(search_results))
                except Exception as e:
                    st.error(f"Error extracting data for {entity}: {str(e)}")


        # Display the extracted data
        st.write("Extracted Data:")
        st.write(extracted_data)

        # Download extracted data as CSV
        def download_extracted_data_as_csv(extracted_data):
            data_for_download = pd.DataFrame(extracted_data.items(), columns=["Entity", "Extracted Information"])
            return data_for_download.to_csv(index=False)

        st.download_button(
            label="Download Extracted Data",
            data=download_extracted_data_as_csv(extracted_data),
            file_name="extracted_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("Please fill out all required fields before processing.")
else:
    st.warning("Please upload a CSV file or connect to Google Sheets first.")

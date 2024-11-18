# AI-Agent
Here’s a sample README file based on the provided code:

---

# AI Data Extraction Dashboard

## Project Summary

The **AI Data Extraction Dashboard** is a web-based tool that allows users to upload a CSV file or connect to their Google Sheets account, select specific columns, and extract information from web search results using AI. The tool uses **Google Sheets API** to retrieve data from Google Sheets, integrates with **SerpApi** for web search, and leverages **Groq API** for extracting specific information from the results. The extracted data can be downloaded in CSV format for further analysis.

## Features
- Upload CSV files or connect to Google Sheets dynamically.
- Select a column for processing and enter query templates to fetch specific information from web search results.
- Use AI (Groq API) to process search results and extract structured data.
- Download the extracted data as a CSV file.

## Setup Instructions

To get started with the project, follow the steps below.

### 1. Prerequisites
- Python 3.7 or higher
- Install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```

The `requirements.txt` should include the following libraries:

- `streamlit`
- `pandas`
- `serpapi`
- `requests`
- `python-dotenv`
- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`

### 2. Environment Variables
Ensure you have the following environment variables set up:

- `SERPAPI_KEY`: Your SerpApi key for performing web searches.
- `GROQ_API_KEY`: Your Groq API key for extracting information from the web search results.

To set these variables, you can create a `.env` file in the project root and add your keys:

```plaintext
SERPAPI_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Google Sheets API Setup
- Create a project in the [Google Developer Console](https://console.developers.google.com/).
- Enable the Google Sheets API.
- Download the `credentials.json` file and place it in the project root.
- When running the project for the first time, it will prompt you to authenticate using your Google account.

### 4. Running the Application
Once everything is set up, you can run the application using Streamlit:

```bash
streamlit run app.py
```

This will launch the dashboard in your browser, where you can interact with the tool.

---

## Usage Guide

### 1. Uploading Data
- **CSV Upload**: Click on the "Upload CSV file" button to upload your file. The dashboard will display the first few rows of the CSV for review.
- **Google Sheets**: Enter the Google Sheets ID and the range (e.g., `Sheet1!A1:Z100`) to fetch data directly from your Google Sheets.

### 2. Processing Data
- **Column Selection**: Select the column from your dataset that contains the entities you want to search for (e.g., names or keywords).
- **Information Type**: Enter the type of information you're looking for (e.g., emails, phone numbers).
- **Query Template**: Define the template for the query you want to generate. For example: "Get the {information} of {entity}".

### 3. Extracting Information
The tool will perform web searches using **SerpApi** to retrieve organic search results, then use **Groq API** to extract the specified information from those results. The extraction will be done in parallel for each entity.

### 4. Downloading Extracted Data
After processing, the extracted data will be displayed on the dashboard. You can download the results in CSV format by clicking the "Download Extracted Data" button.

---

## Third-Party APIs and Tools

### 1. **Google Sheets API**
Used for retrieving data from Google Sheets, allowing users to dynamically fetch data based on the Google Sheets ID and range. The project uses the **Google API Client** to authenticate and interact with Google Sheets.

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)

### 2. **SerpApi**
SerpApi is used for retrieving organic search results from Google. It allows us to perform web searches programmatically, which can then be used for further processing.

- [SerpApi Documentation](https://serpapi.com/)

### 3. **Groq API**
The Groq API is used for extracting information from web search results. It processes the search result data using a language model to extract structured information based on the user-defined query template.

- [Groq API Documentation](https://www.groq.com/)

---

## Additional features
While the core features align with the outlined requirements, several additional functionalities have been incorporated into the project to enhance user experience and flexibility:

### 1. Dynamic Dataset Description
Feature: A dynamic description of the dataset is generated based on the columns of the uploaded CSV or Google Sheet.
Purpose: This feature helps users understand the structure and content of the dataset before proceeding with further actions, enhancing usability.
### 2. Parallel Web Search and Data Extraction
Feature: The web search and LLM processing are handled in parallel for multiple entities to speed up the data retrieval and extraction process.
Purpose: This enables quicker processing of large datasets, ensuring a smooth user experience even with many entities.
### 3. Retry Mechanism for API Calls
Feature: A retry mechanism is implemented for both web searches and LLM processing to handle issues like rate limits or temporary failures in API calls.
Purpose: Ensures reliability and robustness of the system, reducing the chances of failures due to external service interruptions or rate-limiting issues.
### 4. User-friendly and Robust Error Handling
Feature: Detailed error messages and status updates are provided to users throughout the process.
Purpose: Users are kept informed in case of errors, which helps them understand and correct any issues with their input or the system.
### 5. Progress Bar
Feature: Tracking the progress of the API, search results processes using a Progress Bar.
Purpose: Users can be able to track the output processings progress with the help of a visual and dynamic Progress Bar in the Application.

---
## Loom Video Guide

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides an overview of how to set up, use, and understand the dependencies of the AI Data Extraction Dashboard project.

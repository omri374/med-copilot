import os
import json
import io
from typing import Dict, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

import llm_calls
from llm_calls import validate_llm_response

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """
You are a medical assistant specialized in modifying structured medical data.
You will receive JSON input representing a dataset of medications for Retinitis Pigmentosa (RP).

Your task is to:
- Answer user requests about the provided medication data
- Either Add new columns or rows if requested, or modify existing ones
- Provide references, explanations and additional remarks
Always return only a JSON object with:
- "dataset": updated dataset
- "explanation": explanation of changes and additional information related to the findings. Specify the change made for each medication
- "references": References for findings, i.e. links to scientific papers or websites. Specify which reference relates to which finding on each medication.

Additional guidelines:
1. Please respond in valid JSON format only.
2. Make sure the JSON is valid, e.g. has no unterminated strings or missing commas.
3. Ensure the response starts with `{` and ends with `}` without any trailing text.
"""


def update_dataframe(records: List[Dict] | pd.DataFrame):
    """Update the DataFrame with new records. """
    print(f"UPDATING DATAFRAME: {records}")
    if isinstance(records, pd.DataFrame):
        new_data = records
    else:
        new_data = pd.DataFrame(records)

    st.session_state.df = new_data  # Assign the updated DataFrame
    #st.rerun()  # Trigger a rerun


# Page config
st.set_page_config(layout="wide", page_title="RP Medication Analyzer")
col1, col2 = st.columns([2, 18])
col1.image("rp_logo.jpg", use_container_width=True)
col2.title("Analyze RP Related Medications")

# Sidebar for API Key settings
with st.sidebar:
    st.subheader("Select AI service")
    llm_provider = st.radio(options=["Perplexity.ai", "OpenAI"], index=0, label="API")

    api_key = None  # Initialize API key

    if llm_provider == "OpenAI":
        st.subheader("OpenAI API key")
        api_base_input = st.text_input(
            "Enter API Base (Leave empty to use env variable)",
            value=os.environ.get("OPENAI_API_BASE", ""),
        )
        api_key_input = st.text_input(
            "Enter API Key",
            type="password",
            value=os.environ.get("OPENAI_API_KEY", ""),
        )

        openai_api_base = api_base_input if api_base_input else os.environ.get("OPENAI_API_BASE")
        api_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY")

        # Validate API key presence
        if not api_key:
            st.error("🚨 OpenAI API key is required!")

        openai_client = OpenAI(api_key=api_key)
        openai_client.api_base = openai_api_base

    elif llm_provider == "Perplexity.ai":
        st.subheader("Perplexity.ai API key")
        api_key_input = st.text_input(
            "Enter API Key",
            type="password",
            value=os.environ.get("PERPLEXITY_API_KEY", ""),
        )
        api_key = api_key_input if api_key_input else os.environ.get("PERPLEXITY_API_KEY")

        # Validate API key presence
        if not api_key:
            st.error("🚨 Perplexity.ai API key is required!")


# Ensure session persistence
if "df" not in st.session_state:
    st.session_state.df = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "explanation" not in st.session_state:
    st.session_state.explanation = "No modifications yet."
if "references" not in st.session_state:
    st.session_state.references = "No additional references."
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = {}
if "history" not in st.session_state:
    st.session_state.history = []  # Stores all past interactions

# File uploader
file = st.file_uploader("Upload an Excel file", type=["xlsx"])

print(f"FILE: {file}")
if file and file != st.session_state.uploaded_file:
    try:
        with pd.ExcelFile(file) as xls:
            if "Metadata" in xls.sheet_names:
                st.session_state.history = pd.read_excel(xls, sheet_name="Metadata").to_dict(orient="records")
            if "Data" in xls.sheet_names:
                data_df = pd.read_excel(xls, sheet_name="Data")
                update_dataframe(data_df)
            else:
                st.error("🚨 No 'Data' sheet found in the uploaded file. Make sure the file has it")

        st.session_state.uploaded_file = file
        print("File uploaded successfully!")
        st.success("✅ File uploaded successfully!")
    except Exception as e:
        print(f"Error reading file: {e}")
        st.error(f"🚨 Error reading file: {e}")


if st.session_state.df is not None:
    st.write("### Updated Dataset")
    st.dataframe(st.session_state.df, use_container_width=True)
else:
    st.warning("⚠️ Upload a file to proceed.")

# Explanation & remarks
if st.session_state.explanation:
    with st.expander("Explanation and remarks"):
        st.info(st.session_state.explanation)
if st.session_state.references:
    with st.expander("References"):
        st.warning(st.session_state.references)
if st.session_state.last_prompt:
    with st.expander("📜 Sent Prompt"):
        st.code(st.session_state.last_prompt, language="plaintext")

# if st.session_state.last_response:
#     with st.expander("🧠 LLM Response (Raw)"):
#         st.json(st.session_state.last_response)

# User query input
input_text = st.chat_input("Type your prompt here")

# 🚨 Validate: Ensure both API key and dataset are present before making an API call
if input_text:
    if not api_key:
        st.error("🚨 API key is missing! Please provide a valid key before proceeding.")
    elif st.session_state.df is None:
        st.error("🚨 No dataset uploaded! Please upload an Excel file.")
    else:
        # Convert dataframe to JSON for LLM processing
        json_data = st.session_state.df.to_json(orient="records")
        print(json_data)
        with st.spinner(f"Processing request: *{input_text}*..."):
            response = None  # Ensure response is defined before use

            # Call the appropriate LLM provider
            if llm_provider == "OpenAI":
                response = llm_calls.query_openai(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=input_text,
                    json_data=json_data,
                    openai_client=openai_client,
                )
            elif llm_provider == "Perplexity.ai":
                response = llm_calls.query_perplexity(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=input_text,
                    json_data=json_data,
                    api_key=api_key,
                )

            print(f"Response:{response}")

        # Ensure response exists before processing
        if response:
            st.session_state.df = None
            try:
                parsed_response = validate_llm_response(response)
                print(f"Parsed response: {parsed_response}")

                st.session_state.last_prompt = input_text
                st.session_state.last_response = response  # Keep full JSON response

                # Display structured output
                if "error" in parsed_response:
                    st.error(parsed_response["error"])
                else:
                    print(f"Parsed data: {parsed_response['dataset']}")
                    update_dataframe(parsed_response["dataset"])
                    st.session_state.explanation = parsed_response["explanation"]
                    st.session_state.references = parsed_response["references"]
                    st.session_state.history.append({
                        "Prompt": input_text,
                        "Explanation": parsed_response["explanation"],
                        "References": parsed_response["references"]
                    })
            except json.JSONDecodeError:
                st.error("🚨 Error parsing response: Invalid JSON format.")
            except Exception as e:
                st.error(f"🚨 Unexpected error: {e}")

            st.rerun()


# 📥 Download Updated Excel
if st.session_state.df is not None:
    st.sidebar.subheader("Download Updated Dataset")

    def generate_excel(dataframe, history):
        output_stream = io.BytesIO()
        with pd.ExcelWriter(output_stream, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Data")
            # Convert history to DataFrame and save in a new sheet
            if history:
                history_df = pd.DataFrame(history)
                history_df.to_excel(writer, index=False, sheet_name="Metadata")

            workbook = writer.book

            # Apply word wrapping
            for sheet_name in ["Data", "Metadata"]:
                if sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    wrap_format = workbook.add_format({"text_wrap": True, "align": "top", "valign": "top"})

                    # Apply word wrap to all columns
                    df_to_format = dataframe if sheet_name == "Data" else history_df
                    for col_num, col_name in enumerate(df_to_format.columns):
                        worksheet.set_column(col_num, col_num, 30, wrap_format)  # Adjust width if needed

        output_stream.seek(0)
        return output_stream


    st.sidebar.download_button(
        "📥 Download Excel File",
        data=generate_excel(st.session_state.df, st.session_state.history),
        file_name="updated_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

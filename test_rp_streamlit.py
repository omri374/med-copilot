import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

import llm_calls
from rp_streamlit import SYSTEM_PROMPT



def test_openai_rp_streamlit():
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")

    openai_client = OpenAI(api_key=api_key)


    file = "data/sample.xlsx"
    df = pd.read_excel(file)
    json_data = df.to_json(orient="records")
    response = llm_calls.query_openai(
        system_prompt=SYSTEM_PROMPT,
        user_prompt="Add an index column",
        json_data=json_data,
        openai_client=openai_client,
    )

    parsed_response = llm_calls.validate_llm_response(response)

    print(parsed_response)




def test_perplexity_rp_streamlit():
    load_dotenv()
    api_key = os.environ.get("PERPLEXITY_API_KEY")

    file = "data/sample.xlsx"
    df = pd.read_excel(file)
    json_data = df.to_json(orient="records")


    response = llm_calls.query_perplexity(
        system_prompt=SYSTEM_PROMPT,
        user_prompt="Add a column specifying if the medication passes the Retinal Blood Barrier (RBB)",
        json_data=json_data,
        api_key=api_key)

    parsed_response = llm_calls.validate_llm_response(response)

    print(parsed_response)





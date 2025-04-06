import json
import os
from typing import Generator, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def query_llm(
    messages,
    history: List,
    df: Optional[pd.DataFrame],
    llm_type: str,
    api_key: str,
    system_prompt: str,
) -> Generator[str, None, None]:
    """Chat function that streams responses using an LLM API.

    Args:
        messages (str or list): User input message(s).
        history (list): Conversation history.
        df (pd.DataFrame): a representation of the data already obtained
        system_prompt (str): The syste prompt
        api_key (str): The OpenAI api key
    Returns:
        str: The assistant's response.
    """

    if not api_key:
        if llm_type == "OpenAI":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif llm_type == "Perplexity":
            api_key = os.environ.get("PERPLEXITY_API_KEY")
        else:
            yield "No API key provided for the selected LLM type."

    print(f"LLM Type: {llm_type}, API Key len: {len(api_key)}")  # Debugging

    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    # Extract last 2 messages from history (if available)
    history = history[-2:] if history else []

    # Build message history (prepend system prompt)
    full_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Past interactions: {history}"},
        {
            "role": "assistant",
            "content": f"Dataset: {df.to_json() if df is not None else {}}",
        },
    ] + messages

    if llm_type == "Perplexity":
        yield from query_perplexity(full_messages, api_key=api_key)
    elif llm_type == "OpenAI":
        yield from query_openai(full_messages, api_key=api_key)
    else:
        yield "Unsupported LLM type. Please choose either 'OpenAI' or 'Perplexity'."


def query_perplexity(
    full_messages,
    api_key: str,
    url="https://api.perplexity.ai/chat/completions",
    model="sonar-pro",
):
    """Query Perplexity AI API for a response.

    Args:
        full_messages (list): List of messages in the conversation.
        api_key (str): Perplexity API key.
        url (str): API endpoint URL.
        model (str): Model to use for the query.

    Returns:
        str: Parsed JSON response from Perplexity AI API.
    """

    payload = {
        "model": model,
        "messages": full_messages,
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with requests.post(url, json=payload, headers=headers, stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data: "):
                            line = line[len("data: ") :]  # Remove "data: " prefix

                        data = json.loads(line)
                        if "choices" in data and len(data["choices"]) > 0:
                            yield data["choices"][0]["message"]["content"]
                    except json.JSONDecodeError:
                        yield f"Error decoding JSON: {line}"
        else:
            yield f"API request failed with status code {response.status_code}, details: {response.text}"


def query_openai(full_messages, api_key: str) -> Generator[str, None, None]:
    """Chat function that streams responses using OpenAI API.

    Args:
        full_messages (list): List of messages in the conversation.
        api_key (str): OpenAI API key.
    """
    openai_client = OpenAI(api_key=api_key)

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=full_messages,
        stream=True,  # Enable streaming
    )

    llm_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            llm_response += chunk.choices[0].delta.content
            yield llm_response


def llm_extract_table(chat_output, llm_type, api_key) -> str:
    system_prompt = """
    You are a pharmacology assistant specialized in analyzing and structuring medical data.
    Your role is to extract information in either markdown, JSON or text, and turn it structured information.
    You will be given output from a conversation with an LLM. This conversation should have a dataset formatted
    as either json or markdown. Extract the dataset and return a JSON object.
    The dataset should be a JSON object with a dict per medication, with the following format:
    ```json
    {
        "Medications": [
            {"Name": "Medication Name", "key1": "value1", "key2": "value2",..},
            {"Name": "Medication Name", "key1": "value1", "key2": "value2",..}
        ]
    }
    
    Guidelines:
    - Make sure the response contains only a valid JSON
    - Avoid adding text before or after
    """

    response = query_llm(
        messages=chat_output,
        history=None,
        df=None,
        llm_type=llm_type,
        api_key=api_key,
        system_prompt=system_prompt,
    )
    json_str = "".join(response).strip()
    return json_str

import re
import json
from typing import Optional
import pandas as pd
import simplejson


def json_to_dict(response: str) -> dict:
    """Convert a JSON string to a Python dictionary.
    Args:
        response (str): JSON string to convert.
    Returns:
        dict: Parsed JSON as a dictionary.
    Raises:
        ValueError: If the JSON string is invalid.
    """

    # extract dict from json
    try:
        match = re.search(r"\{.*}", response, re.DOTALL)
        if match is None:
            raise ValueError("No valid JSON found in the response.")
        match_response = match.group()
        match_response = json.loads(match_response)
    except json.JSONDecodeError:
        try:
            match_response = simplejson.loads(response)  # More forgiving JSON parser
        except simplejson.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

    return match_response  # Return as a structured dictionary


def json_to_pandas(json_data: str, key: Optional[str] = None) -> pd.DataFrame:
    """Convert JSON data to a pandas DataFrame."""
    try:
        dic = json_to_dict(json_data)
        if key:
            dic = dic[key]
        df = pd.DataFrame(dic)
        return df
    except ValueError as e:
        raise ValueError(f"Invalid JSON data: {e}")


def extract_and_return_data_table(chat_output, key="Medications"):
    """Extract a pandas data frame out of the chat.
    Try rule-based first and use LLM if it fails."""

    if chat_output:
        if "content" in chat_output[-1]:
            chat_output = chat_output[-1]["content"]

    print(f"chat output: {chat_output}type: {type(chat_output)}")

    try:
        df = json_to_pandas(chat_output, key=key)
    except ValueError as e:
        raise ValueError(e)

    return df

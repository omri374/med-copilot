import json

import random
from typing import List, Optional

import pandas as pd


def get_current_df(dfs: List[pd.DataFrame], current: int) -> pd.DataFrame:
    if len(dfs) == 0:
        return pd.DataFrame()
    else:
        return dfs[current]


def query_llm_mock(
    messages,
    history: List,
    df: pd.DataFrame,
    llm_type: str,
    api_key: str,
    system_prompt: str,
):
    """Chat function that streams responses using mock llm.

    Args:
        messages (str or list): User input message(s).
        history (list): Conversation history.
        dfs (List[pd.DataFrame): a representation of the data already obtained
        system_prompt (str): The syste prompt
        openai_client (OpenAI): The OpenAI client
    Returns:
        str: The assistant's response.

    """

    mock_json = json.dumps(
        {
            "Medications": [
                {
                    "Medication name": "Tamsulosin",
                    "Passes_RBB": "Yes",
                    "Random": random.random(),
                },
                {
                    "Medication name": "Metoprolol",
                    "Passes_RBB": "Yes",
                    "Random": random.random(),
                },
                {
                    "Medication name": "Bromocriptine",
                    "Passes_RBB": "Yes",
                    "Random": random.random(),
                },
                {
                    "Medication name": "Reserpine",
                    "Passes_RBB": "Yes",
                    "Random": random.random(),
                },
                {
                    "Medication name": "Rasagiline",
                    "Passes_RBB": "Yes",
                    "Random": random.random(),
                },
            ]
        }
    )
    yield (
        f"Good question!\n"
        f"Here's the data frame in JSON format:\n"
        f"```json\n"
        f"{mock_json if random.random() > 0.5 else ''}\n"
        f"```\n\n"
        f"Hope this is useful."
    )


def llm_extract_table_mock(chat_output, llm_type, api_key) -> str:
    dic = {
        "Medications": [
            {
                "Name": "Medication Name",
                "key1": "value1",
                "key2": "value2",
                "Random": random.random(),
            },
            {
                "Name": "Medication Name",
                "key1": "value1",
                "key2": "value2",
                "Random": random.random(),
            },
        ]
    }

    return json.dumps(dic)

from typing import Dict, List

from openai import OpenAI

import requests
import json
import simplejson

from pydantic import BaseModel

class AnswerFormat(BaseModel):
    dataset: List[Dict]
    explanations: str
    references: str


def query_perplexity(
        system_prompt: str,
        user_prompt: str,
        json_data: str,
        api_key: str,
        url="https://api.perplexity.ai/chat/completions",
        model="sonar-pro",
):
    """Query Perplexity AI API for a response.

    Args:
        system_prompt (str): System message providing AI context.
        user_prompt (str): User's query.
        json_data (str): JSON data representing the current dataset.
        api_key (str): Perplexity AI API key.
        url (str): API endpoint.
        model (str): Perplexity AI model to use.
        max_tokens (int): Maximum number of tokens in the response.
        temperature (float): Sampling temperature for randomness.
        top_p (float): Nucleus sampling parameter.
        top_k (int): Top-k filtering.
        presence_penalty (float): Encourages new token diversity.
        frequency_penalty (float): Penalizes frequent tokens.
        return_images (bool): Whether to include images in response.
        return_related_questions (bool): Whether to include related questions.
        search_domain_filter (str or None): Domain filter for web search.
        search_recency_filter (str or None): Recency filter for web search.
        stream (bool): Whether to stream response.

    Returns:
        str: Parsed JSON response from Perplexity AI API.
    """

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"{system_prompt}\n"
                                          f"Make sure you add the citations found to the references key"},
            {"role": "user", "content": f"Here is the dataset: {json_data}\n\n"
                                        f"User query:\n"
                                        f"{user_prompt}"},
        ],
        "response_format": {
		    "type": "json_schema",
        "json_schema": {"schema": AnswerFormat.model_json_schema()},
    },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]
    else:
        return f"API request failed with status code {response.status_code}, details: {response.text}"



def query_openai(system_prompt: str, user_prompt: str, json_data: str, openai_client: OpenAI) -> str:
    """Query OpenAI API for a response.

    Args:
        system_prompt (str): System prompt providing context to the AI.
        user_prompt (str): User's query.
        json_data (str): JSON data representing the current dataset.
        openai_client (OpenAI): OpenAI client instance with API key set.

    Returns:
        str: JSON response from the API.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the dataset: {json_data}"},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    if len(response.choices) > 0:
        content = response.choices[0].message.content
        return content
    else:
        return "Bad response from OpenAI"


def validate_llm_response(response: str) -> dict:

    # extract dict from json
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            return simplejson.loads(response)  # More forgiving JSON parser
        except simplejson.JSONDecodeError:
            return None  # JSON is too broken to fix

    # Validate expected keys
    required_keys = {"dataset", "explanation", "references"}
    if not required_keys.issubset(response.keys()):
        raise ValueError(f"Missing required keys: {required_keys - response.keys()}")

    return response  # Return as a structured dictionary



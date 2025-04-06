---
title: Medication Research CoPilot
sdk: gradio
sdk_version: 5.20.1
app_file: medication_copilot.py
pinned: false
---

# Medication research CoPilot

## Introduction
This project is a web application that allows users to perform an AI based analysis of medications. 
Users start with either a list of medications, or a dataset from a previous interaction with the tool, 
can ask questions, modify, delete or add columns and rows, and download the updated dataset.

## Installation
To install the project, clone the repository and run the following command:
```bash
conda create --name med-copilot python=3.10
conda activate med-copilot
pip install -r requirements.txt
```

## Running the application
To run the application, run the following command:
```bash
python medication_copilot.py
```

### Using the application
1. Upload a dataset with a list of medications. The dataset should be in an Excel file with a sheet called "Data". If you are continuing the work from a previous session, upload the data that was downloaded on the last interaction.
2. Define the AI service to use- Perplexity or OpenAI.
3. Input the API key for the service. For Perplexity, see [here](https://docs.perplexity.ai/guides/getting-started). For OpenAI, see [here](https://platform.openai.com/api-keys).
4. Input the prompt for the AI service. See below for more details.
5. Inspect the dataset, explanations and references to make sure the responses are correct.
6. Download the updated dataset by clicking on the "Download" button.

## Prompt
Note that the default system prompt can be found [here](medication_copilot.py). 
Consider modifying the prompt to better suit your needs, for example for a specific disease or condition.


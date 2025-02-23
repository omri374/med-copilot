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
streamlit run rp_streamlit.py
```

## Prompt
Note that the default system prompt can be found [here](rp_streamlit.py). 
Consider modifying the prompt to better suit your needs, for example for a specific disease or condition.


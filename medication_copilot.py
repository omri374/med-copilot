from functools import partial
import gradio as gr

from src.gradio_utils import (
    extract_table_from_chat,
    upload_file,
    redo,
    undo,
    edit_or_save_changes,
    update_llm_selection,
)
from src.llm_calls import query_llm
from src.data_handler import generate_excel_base64

SYSTEM_PROMPT = """You are a pharmacology assistant specialized in analyzing and structuring medical data.

Inputs You Receive:
A JSON dataset representing medications for Retinitis Pigmentosa

A user query requesting additional details to be added to the dataset

Your Task:
Analyze the dataset and determine what new information is needed

Research and generate new details based on the user’s request

Enhance the dataset by adding the requested information

Ensure completeness: The updated dataset must always include all medications

Your Output:
A succinct response explaining your findings and how the dataset was extended

A fully updated JSON dataset, strictly following this format:

json
Copy
Edit
{
  "Medications": [
    {"Name": "Medication Name", "key1": "value1", "key2": "value2", ...},
    {"Name": "Medication Name", "key1": "value1", "key2": "value2", ...}
  ]
}
Key Requirements:
- JSON output is mandatory in every response
- All medications must be present in the JSON, even if unchanged
- Extend the dataset with newly generated information—do not just retrieve existing data
- No repetition of the example JSON—only return the updated data
- Verify the JSON before responding to ensure it is well-formed and complete

Always structure your response clearly:

- Text Summary: Explanation of findings and dataset extensions

- Updated JSON Dataset: Full dataset with all medications, including new information

- References & Sources (if applicable)
"""


with gr.Blocks(theme=gr.themes.Glass()) as app:
    df_before = gr.State([])  # Undo history
    df_state = gr.State(None)  # Current DataFrame
    df_after = gr.State([])  # Redo history
    last_response = gr.State("")  # Store last LLM response
    edit_mode = gr.State("Edit")  # Track edit mode
    base64data = gr.State(None)

    with gr.Sidebar():
        gr.Markdown("### Configuration")
        llm_type = gr.Radio(
            choices=["Perplexity", "OpenAI"], label="LLM Type", value="Perplexity"
        )

        api_key = gr.Textbox(
            label="OpenAI API Key",
            placeholder=f"Enter {llm_type.value} Key",
            interactive=True,
            type="password"
        )

        gr.Markdown("### Upload existing data")
        file_upload = gr.File(label="Upload Excel File", file_types=[".xlsx"])
        gr.Markdown("### Download table to Excel")
        excel_output = gr.State(None)

        excel_data = gr.Textbox(visible=False)
        download_button = gr.DownloadButton(label="Download dataset")

        download_button.click(
            generate_excel_base64, inputs=[df_state], outputs=[excel_data]
        )

        excel_data.change(
            None,
            [excel_data],
            None,
            js="""
        (base64Data) => {
            const binaryString = atob(base64Data);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            const blob = new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });

            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "dataset.xlsx";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        """,
        )

        llm_type.change(update_llm_selection, inputs=[llm_type], outputs=[api_key])
        with gr.Accordion("System Prompt", open=False):
            system_prompt_box = gr.Textbox(
                value=SYSTEM_PROMPT, interactive=True, lines=10, label="System Prompt"
            )

    gr.Markdown("## Medications Data CoPilot")
    # Chat Interface
    chat = gr.ChatInterface(
        fn=query_llm,
        type="messages",
        description="Chat with an LLM to create a data representation of medications.",
        stop_btn=False,
        save_history=False,
        additional_inputs=[df_state, llm_type, api_key, system_prompt_box],
        examples=[
            [
                "List 10 medications that are known to be effective for Retinitis Pigmentosa"
            ],
            [
                "Add a column specifying if the medication passes the Retinal Blood Barrier"
            ],
            ["Add the safety profile for each medication"],
            ["Create four columns, each specifying each of the ADME profile factors"],
            [
                "Categorize each column into up to five categories, for simple classification."
            ],
        ],
    )
    with gr.Row():
        gr.Markdown("### Medications Table")
    with gr.Row():
        update_button = gr.Button(
            "Update table using the chat information", scale=8, interactive=True
        )
    with gr.Row():
        dataframe_display = gr.DataFrame(interactive=False)
    with gr.Row():
        prev_button = gr.Button("<-", interactive=False, scale=1)
        edit_save_button = gr.Button("Edit", interactive=True, scale=2)
        next_button = gr.Button("->", interactive=False, scale=1)

    # Save user changes
    edit_save_button.click(
        edit_or_save_changes,
        inputs=[dataframe_display, df_before, df_state, df_after, edit_mode],
        outputs=[
            dataframe_display,  # Updated DataFrame
            df_before,  # Undo history
            df_state,  # Current state
            df_after,  # Redo history
            prev_button,  # Update prev button
            next_button,  # Update next button
            dataframe_display,  # Update DataFrame interactivity
            edit_save_button,  # Update button label
            edit_mode,  # Update edit mode
        ],
    )
    # Undo button
    prev_button.click(
        undo,
        inputs=[df_before, df_state, df_after],
        outputs=[
            dataframe_display,
            df_before,
            df_state,
            df_after,
            prev_button,
            next_button,
        ],
    )
    # Redo button
    next_button.click(
        redo,
        inputs=[df_before, df_state, df_after],
        outputs=[
            dataframe_display,
            df_before,
            df_state,
            df_after,
            prev_button,
            next_button,
        ],
    )
    # File upload event
    file_upload.change(
        upload_file,
        inputs=[file_upload, df_before, df_state, df_after],
        outputs=[
            dataframe_display,
            df_before,
            df_state,
            df_after,
            prev_button,
            next_button,
        ],
    )
    # Update button copies chat history to text box
    update_button.click(
        partial(extract_table_from_chat, key="Medications"),
        inputs=[chat.chatbot, df_before, df_state, df_after, llm_type, api_key],
        outputs=[
            dataframe_display,
            df_before,
            df_state,
            df_after,
            prev_button,
            next_button,
        ],
    )

# Launch App
app.launch()

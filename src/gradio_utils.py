import pandas as pd

from src.llm_calls import llm_extract_table
from src.parse_response import extract_and_return_data_table
import gradio as gr


def __update_df_state(df_before, df_state, updated_df):
    new_df = pd.DataFrame(updated_df)

    if df_before is not None:
        new_df_before = df_before + [df_state]
    else:
        new_df_before = [df_state]

    new_df_after = []  # Clear redo history
    new_df_state = new_df.copy()

    return new_df_before, new_df_state, new_df_after


def extract_table_from_chat(
    chat_output, df_before, df_state, df_after, llm_type, api_key, key="Medications"
):
    try:
        updated_df = extract_and_return_data_table(chat_output=chat_output, key=key)
    except ValueError:
        try:
            json_str = llm_extract_table(chat_output, llm_type, api_key)
            updated_df = extract_and_return_data_table(chat_output=json_str, key=key)
        except KeyError:
            gr.Error(
                "Cannot extract table information from chat. "
                "Please ask the LLM to provide the dataset in JSON format.",
                duration=None,
            )
            updated_df = df_before
        except ValueError:
            gr.Error(
                "Cannot extract table information from chat. "
                "Please ask the LLM to provide the dataset in JSON format.",
                duration=None,
            )
            updated_df = df_before

    new_df_before, new_df_state, new_df_after = __update_df_state(
        df_before, df_state, updated_df
    )
    return (
        new_df_state,
        new_df_before,
        new_df_state,
        new_df_after,
        gr.update(interactive=True),
        gr.update(interactive=False),
    )


def update_llm_selection(selected_llm):
    if selected_llm == "OpenAI":
        return gr.update(label="OpenAI API Key", placeholder="Enter OpenAI API Key")
    elif selected_llm == "Perplexity":
        return gr.update(
            label="Perplexity API Key", placeholder="Enter Perplexity API Key"
        )
    else:
        raise ValueError("Invalid LLM type selected.")


def edit_or_save_changes(updated_df, df_before, df_state, df_after, current_edit_mode):
    """Save user changes, update undo history."""

    new_df = pd.DataFrame(updated_df)
    new_df_before = df_before + [df_state.copy()]
    new_df_after = []  # Clear redo history
    new_df_state = new_df.copy()

    if current_edit_mode == "Save":
        # User wants to move from save to edit
        return (
            new_df,
            new_df_before,
            new_df_state,
            new_df_after,
            gr.update(
                interactive=True
            ),  # prev button is now enabled as there was a change
            gr.update(interactive=False),  # next button
            gr.update(interactive=True),  # df display
            gr.update(value="Edit"),  # edit button
            "Edit",
        )
    elif current_edit_mode == "Edit":
        return (
            new_df_state,
            new_df_before,
            new_df_state,
            new_df_after,
            gr.update(interactive=False),  # prev button
            gr.update(interactive=False),  # next button
            gr.update(interactive=True),  # df display
            gr.update(value="Save"),  # edit button
            "Save",
        )

    else:
        raise ValueError(f"Wrong edit mode selected: {current_edit_mode}. ")


def undo(df_before, df_state, df_after):
    """Undo user change without enabling Save button."""
    if not df_before:
        return (
            df_state,
            df_before,
            df_state,
            df_after,
            gr.update(interactive=False),
            gr.update(interactive=(len(df_after) > 0)),
        )

    new_df_after = df_after + [df_state.copy()]
    new_df_state = df_before[-1]
    new_df_before = df_before[:-1]

    return (
        new_df_state,
        new_df_before,
        new_df_state,
        new_df_after,
        gr.update(interactive=(len(new_df_before) > 0)),  # prev button
        gr.update(interactive=(len(new_df_after) > 0)),  # next button
    )


def redo(df_before, df_state, df_after):
    """Redo user change without enabling Save button."""
    if not df_after:
        return (
            df_state,
            df_before,
            df_state,
            df_after,
            gr.update(interactive=(len(df_before) > 0)),
            gr.update(interactive=False),
        )

    if df_state is None:
        df_state = df_after

    new_df_before = df_before + [df_state.copy()]
    new_df_state = df_after[-1]
    new_df_after = df_after[:-1]

    return (
        new_df_state,
        new_df_before,
        new_df_state,
        new_df_after,
        gr.update(interactive=(len(new_df_before) > 0)),
        gr.update(interactive=(len(new_df_after) > 0)),
    )


# def toggle_save_edit(button_state, dataframe_display):
#     if button_state == "Edit":
#         return "Save", gr.update(interactive=True), gr.update(interactive=True)  # Enable DataFrame editing
#     else:
#         return "Edit", gr.update(interactive=True), gr.update(interactive=False)  # Disable DataFrame editing
#


def upload_file(file, df_before, df_state, df_after):
    if file is None:
        return gr.update()

    df = pd.read_excel(file.name, engine="openpyxl")

    new_df_before, new_df_state, new_df_after = __update_df_state(
        df_before, df_state, df
    )

    # print("Uploaded DataFrame:\n", df)  # Print DataFrame to console
    return (
        df,
        new_df_before,
        df,
        new_df_after,
        gr.update(interactive=False),
        gr.update(interactive=False),
    )

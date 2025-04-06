import tempfile
import io
from typing import List

import pandas as pd
import base64


def generate_excel_base64(dataframe: pd.DataFrame) -> str:
    """Generates an Excel file from the provided data frame and returns it as a base64 string."""
    output_stream = io.BytesIO()  # Create in-memory buffer

    # Ensure `xlsxwriter` writes to the buffer
    with pd.ExcelWriter(output_stream, engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Data")

    output_stream.seek(0)  # Move to the beginning for reading
    base64_data = base64.b64encode(output_stream.getvalue()).decode(
        "utf-8"
    )  # Encode to base64

    return base64_data  # Return base64 string directly


def generate_excel(dataframe: pd.DataFrame) -> str:
    """Generates an Excel file from the provided data frame."""
    output_stream = io.BytesIO()  # Create in-memory buffer

    # Ensure `xlsxwriter` writes to the buffer
    with pd.ExcelWriter(output_stream, engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Data")

    output_stream.seek(0)  # Move to the beginning for reading

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        tmp_file.write(output_stream.getvalue())  # Write bytes to temp file
        tmp_path = tmp_file.name  # Get temp file path

    return tmp_path  # ✅ Return file path directly

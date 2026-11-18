"""
SocialPulse AI - CSV Loader
Handles CSV file reading with encoding detection and basic parsing.
"""
import pandas as pd
import io
from typing import Tuple, Optional
from utils.constants import SUPPORTED_ENCODINGS, MAX_FILE_SIZE_MB, MAX_ROWS


def load_csv(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load a CSV file from Streamlit's UploadedFile object.
    
    Returns:
        Tuple of (DataFrame or None, error_message or None)
    """
    if uploaded_file is None:
        return None, "No file provided."

    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return None, f"File too large ({file_size_mb:.1f} MB). Maximum allowed: {MAX_FILE_SIZE_MB} MB."

    # Try different encodings
    content = uploaded_file.getvalue()
    df = None
    used_encoding = None

    for encoding in SUPPORTED_ENCODINGS:
        try:
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            used_encoding = encoding
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    if df is None:
        return None, "Could not parse the CSV file. Please ensure it's a valid CSV with supported encoding (UTF-8, Latin-1, or ISO-8859-1)."

    # Check if empty
    if df.empty:
        return None, "The uploaded CSV file is empty (no data rows found)."

    if len(df.columns) < 2:
        return None, "The CSV file has fewer than 2 columns. Please check the file format."

    # Check row count
    if len(df) > MAX_ROWS:
        return None, f"File contains {len(df):,} rows, exceeding the maximum of {MAX_ROWS:,}. Please reduce the dataset."

    # Clean column names (strip whitespace)
    df.columns = [str(col).strip() for col in df.columns]

    return df, None


def load_csv_from_path(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Load a CSV file from a file path (for sample data)."""
    try:
        for encoding in SUPPORTED_ENCODINGS:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                df.columns = [str(col).strip() for col in df.columns]
                return df, None
            except UnicodeDecodeError:
                continue
        return None, f"Could not read file with any supported encoding."
    except FileNotFoundError:
        return None, f"File not found: {file_path}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def get_file_info(uploaded_file) -> dict:
    """Get basic information about an uploaded file."""
    return {
        "name": uploaded_file.name if hasattr(uploaded_file, 'name') else "Unknown",
        "size_bytes": uploaded_file.size if hasattr(uploaded_file, 'size') else 0,
        "size_mb": round(uploaded_file.size / (1024 * 1024), 2) if hasattr(uploaded_file, 'size') else 0,
        "type": uploaded_file.type if hasattr(uploaded_file, 'type') else "Unknown",
    }

import streamlit as st
import pandas as pd
import json
import glob
import os

def flatten_json(nested_json, parent_key='', sep='.'): 
    """Recursively flattens a nested JSON object into a list of dictionaries, handling arrays as multiple rows."""
    flattened_rows = []

    def recursive_flatten(obj, parent, row):
        if isinstance(obj, dict):
            for k, v in obj.items():
                recursive_flatten(v, parent + [(k, None)], row)
        elif isinstance(obj, list):
            if all(isinstance(item, (str, int, float)) for item in obj):
                key = sep.join(k for k, _ in parent)
                row[key] = ', '.join(map(str, obj))
            else:
                for item in obj:
                    new_row = row.copy()
                    recursive_flatten(item, parent, new_row)
                    flattened_rows.append(new_row)
        else:
            key = sep.join(k for k, _ in parent)
            row[key] = obj

    recursive_flatten(nested_json, [], {})
    return flattened_rows if flattened_rows else [{}]

def json_to_csv(json_files):
    """Converts multiple nested JSON files to a CSV format with hierarchical column names and multiple rows for arrays."""
    all_rows = []

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            for entry in data:
                all_rows.extend(flatten_json(entry))

    df = pd.DataFrame(all_rows)
    return df

st.title("JSON to CSV Converter")
st.write("Upload multiple JSON files to flatten and convert them into a single CSV file.")

uploaded_files = st.file_uploader("Choose JSON files", type=["json"], accept_multiple_files=True)

if uploaded_files:
    json_files = []
    for file in uploaded_files:
        file_path = os.path.join("temp", file.name)
        os.makedirs("temp", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.read())
        json_files.append(file_path)

    df = json_to_csv(json_files)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="output_combined.csv", mime='text/csv')

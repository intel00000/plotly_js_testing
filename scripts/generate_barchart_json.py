import os
import json
import base64
import pandas as pd


def generate_bar_chart_json(
    output_json_path: str,
    properties_pkl: str,
    data_dir: str,
    image_dir: str,
    page_title: str,
):
    """
    Generates a JSON file containing bar chart data for visualization.

    Args:
        output_json_path (str): Path to save the generated JSON file.
        properties_pkl (str): Properties data file (pickle).
        data_dir (str): Path to the folder containing data pickle files.
        image_dir (str): Directory containing molecular images, named by compound IDs.
        page_title (str): Title for the bar chart page.

    Returns:
        None
    """
    # Validate required files and directories
    required_files = [
        os.path.join(data_dir, properties_pkl),
        os.path.join(data_dir, "mol_image_paths_captioned.json"),
        os.path.join(data_dir, "yields.pkl"),
        os.path.join(data_dir, "yield_data_df.pkl"),
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    df = pd.read_pickle(required_files[0])  # Load dataset
    with open(required_files[1], "r") as f:
        mol_image_paths = json.load(f)  # Load image JSON file
    yields_df = pd.read_pickle(required_files[2])

    # Convert image paths to base64 encoded strings
    mol_image_base64 = {}
    for compound_id, img_path in mol_image_paths.items():
        base_filename = os.path.basename(img_path)
        img_full_path = os.path.join(image_dir, base_filename)
        if os.path.exists(img_full_path):
            with open(img_full_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                mol_image_base64[compound_id] = encoded_string
        else:
            print(f"Warning: Image file not found for {compound_id} at {img_full_path}")

    print("Generating JSON file...")
    bar_chart_data = {
        "page_title": page_title,
        "data": {},
        "images": mol_image_base64,
    }

    # Generate data for each numeric column
    for column in df.select_dtypes(include="number").columns:
        sorted_df = df.sort_values(column)
        x_values = sorted_df["Compound_Name"].tolist()
        y_values = sorted_df[column].tolist()

        # Reorder yields_df to match the order of x_values
        yields_df_reordered = yields_df.set_index("id").reindex(x_values)

        # Prepare yield traces
        yield_traces = []
        for method in yields_df.select_dtypes(include="number").columns:
            yield_values = yields_df_reordered[method].tolist()
            yield_traces.append(
                {
                    "x": x_values,
                    "y": yield_values,
                    "type": "scatter",
                    "mode": "lines",
                    "name": method,
                    "line": {"dash": "dash"},
                }
            )

        # Store data in JSON format
        bar_chart_data["data"][column] = {
            "x_values": x_values,
            "y_values": y_values,
            "yield_data": yield_traces,
        }

    # Save JSON output
    with open(output_json_path, "w") as json_file:
        json.dump(bar_chart_data, json_file, indent=4)

    print(f"Bar chart JSON data file generated: {output_json_path}")


if __name__ == "__main__":
    page_title = "Bar Chart of 35 Compound with DFT Properties"
    output_json_path = "docs/data/barchart/bar_chart_data.json"
    properties_pkl = "Select_properties.pkl"
    data_dir = "data"  # Path to the folder containing data pickle files
    image_dir = "images"

    generate_bar_chart_json(
        output_json_path, properties_pkl, data_dir, image_dir, page_title
    )

import os
import json
import pandas as pd


def generate_bar_chart_and_yield_json(
    output_bar_chart_json: str,
    output_yield_json: str,
    properties_pkl: str,
    data_dir: str,
    image_dir: str,
    page_title: str,
):
    """
    Generates two JSON files:
    - Bar chart data containing DFT properties.
    - Yield data for compounds to be queried dynamically.

    Args:
        output_bar_chart_json (str): Path to save the bar chart JSON file.
        output_yield_json (str): Path to save the yield JSON file.
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
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    df = pd.read_pickle(required_files[0])  # Load properties dataset
    with open(required_files[1], "r") as f:
        mol_image_paths = json.load(f)  # Load image JSON file
    yields_df = pd.read_pickle(required_files[2])  # Load yield dataset

    # Convert image paths to base64 encoded strings
    mol_image_base64 = {}
    for compound_id, img_path in mol_image_paths.items():
        base_filename = os.path.basename(img_path)
        img_full_path = os.path.join(image_dir, base_filename)
        if os.path.exists(img_full_path):
            mol_image_base64[compound_id] = img_path
        else:
            mol_image_base64[compound_id] = None
            print(f"Warning: Image file not found for {compound_id} at {img_full_path}")

    print("Generating JSON files...")

    # Generate Bar Chart Data
    bar_chart_data = {
        "page_title": page_title,
        "data": {},
        "images": mol_image_base64,
        "yield_data_path": output_yield_json,
    }

    # Store Yield Data Separately
    yield_data = {
        "compounds": yields_df["id"].tolist(),
        "methods": list(yields_df.select_dtypes(include="number").columns),
        "yields": yields_df.set_index("id")
        .select_dtypes(include="number")
        .to_dict("index"),
    }

    # Generate data for each numeric property
    for column in df.select_dtypes(include="number").columns:
        sorted_df = df.sort_values(column)
        x_values = sorted_df["Compound_Name"].tolist()
        y_values = sorted_df[column].tolist()

        # Store data in JSON format
        bar_chart_data["data"][column] = {
            "x_values": x_values,
            "y_values": y_values,
        }

    # Save JSON output
    with open(output_bar_chart_json, "w") as json_file:
        json.dump(bar_chart_data, json_file, indent=2, allow_nan=False)

    with open(output_yield_json, "w") as json_file:
        json.dump(yield_data, json_file, indent=2, allow_nan=False)

    print(f"Bar chart JSON data file generated: {output_bar_chart_json}")
    print(f"Yield JSON data file generated: {output_yield_json}")


if __name__ == "__main__":
    page_title = "Bar Chart of 252 Compounds with DFT Properties"
    output_bar_chart_json = "docs/data/barchart/252_compounds.json"
    output_yield_json = "docs/data/yields/252_yields.json"
    properties_pkl = "Select_properties.pkl"
    data_dir = "data_252"  # Path to the folder containing data pickle files
    image_dir = os.path.join("docs", "images")

    generate_bar_chart_and_yield_json(
        output_bar_chart_json,
        output_yield_json,
        properties_pkl,
        data_dir,
        image_dir,
        page_title,
    )

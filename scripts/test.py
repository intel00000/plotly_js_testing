import os
import json
import base64
import pandas as pd


def generate_heatmap_json(output_json_path, data_dir, image_dir):
    """
    Generates a JSON file containing heatmap data for visualization.

    Args:
        output_json_path (str): Path to save the generated JSON file.
        data_dir (str): Path to the folder containing data pickle files.
        image_dir (str): Directory containing molecular images, named by compound IDs.

    Returns:
        None
    """
    # Validate required files
    required_files = [
        os.path.join(data_dir, "yields.pkl"),
        os.path.join(data_dir, "yield_data_df.pkl"),
        os.path.join(data_dir, "mol_image_paths_captioned.json"),
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    # Load data
    yields_df = pd.read_pickle(required_files[0])
    yield_data_df = pd.read_pickle(required_files[1])
    with open(required_files[2], "r") as f:
        mol_image_paths = json.load(f)

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

    # Prepare heatmap data
    heatmap_data = {
        "z_values": yield_data_df.T.to_numpy().tolist(),
        "x_values": yields_df["id"].tolist(),
        "y_values": yield_data_df.columns.tolist(),
        "images": mol_image_base64,
    }

    # Save JSON output
    with open(output_json_path, "w") as json_file:
        json.dump(heatmap_data, json_file, indent=4)

    print(f"Heatmap JSON data file generated: {output_json_path}")


if __name__ == "__main__":
    output_json_path = "docs/data/heatmap_data.json"
    data_dir = "data"  # Path to the folder containing data pickle files
    image_dir = "images"  # Path to the folder containing images

    generate_heatmap_json(output_json_path, data_dir, image_dir)

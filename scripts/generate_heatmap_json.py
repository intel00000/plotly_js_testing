import os
import json
import pandas as pd


def generate_heatmap_json(
    output_json_path: str,
    yield_json_path: str,
    data_dir: str,
    image_dir: str,
    page_title: str,
    graph_name: str,
):
    """
    Generates a JSON file containing heatmap data for visualization.

    Args:
        output_json_path (str): Path to save the generated JSON file.
        yield_json_path (str): Path to the separate yield data JSON file.
        data_dir (str): Path to the folder containing data pickle files.
        image_dir (str): Directory containing molecular images, named by compound IDs.
        page_title (str): Title for the heatmap page.
        graph_name (str): Name of the graph to be included in the JSON data.

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

    # Generate image paths (instead of base64 encoding)
    mol_image_urls = {}
    for compound_id, img_path in mol_image_paths.items():
        base_filename = os.path.basename(img_path)
        img_full_path = os.path.join(image_dir, base_filename)
        if os.path.exists(img_full_path):
            mol_image_urls[compound_id] = img_path
        else:
            print(f"Warning: Image file not found for {compound_id} at {img_full_path}")

    # Generate heatmap JSON
    heatmap_data = {
        "page_title": page_title,
        "graph_name": graph_name,
        "compounds": yields_df["id"].tolist(),
        "methods": yield_data_df.columns.tolist(),
        "yield_data_path": yield_json_path,  # Path to external yield data JSON
        "images": mol_image_urls,  # Store only hosted image URLs
    }

    # Save JSON output
    with open(output_json_path, "w") as json_file:
        json.dump(heatmap_data, json_file, indent=2, allow_nan=False)

    print(f"Heatmap JSON data file generated: {output_json_path}")


def generate_yield_json(yield_json_path: str, data_dir: str):
    """
    Generates a separate JSON file for yield values.

    Args:
        yield_json_path (str): Path to save the yield data JSON file.
        data_dir (str): Path to the folder containing data pickle files.

    Returns:
        None
    """
    # Validate required files
    required_files = [
        os.path.join(data_dir, "yields.pkl"),
        os.path.join(data_dir, "yield_data_df.pkl"),
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")

    # Load data
    yields_df = pd.read_pickle(required_files[0])
    yield_data_df = pd.read_pickle(required_files[1])

    # Create structured yield data
    yield_data = {
        "compounds": yields_df["id"].tolist(),
        "methods": yield_data_df.select_dtypes(include="number").columns.tolist(),
        "yields": yields_df.set_index("id")
        .select_dtypes(include="number")
        .to_dict(orient="index"),
    }

    # Save JSON output
    with open(os.path.join("docs", yield_json_path), "w") as json_file:
        json.dump(yield_data, json_file, indent=2, allow_nan=False)

    print(f"Yield JSON data file generated: {yield_json_path}")


if __name__ == "__main__":
    title = "Yields Map of 252 Compounds"
    graph_name = "Yields Map"
    output_json_path = "docs/data/heatmap/252_compounds.json"
    yield_json_path = "data/yields/252_yields.json"
    data_dir = "data_252"  # Path to the folder containing data pickle files
    image_dir = os.path.join("docs", "images")  # Path to the folder containing images

    print("Generating JSON files...")
    # Generate separate yield JSON
    generate_yield_json(yield_json_path, data_dir)
    # Generate heatmap JSON with reference to yield data JSON
    generate_heatmap_json(
        output_json_path, yield_json_path, data_dir, image_dir, title, graph_name
    )

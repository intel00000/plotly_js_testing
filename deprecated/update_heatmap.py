import os, json, base64
import pandas as pd


def update_heatmap_html_template(
    html_template_path, output_html_path, title, data_dir, image_dir
):
    """
    Updates the HTML file with data from a dataset and image paths from a directory.

    Args:
        html_template_path (str): Path to the template HTML file.
        output_html_path (str): Path to save the updated HTML file.
        title (str): Title for the HTML page.
        data_dir (str): Path to the data file (pickle containing yields_df and yield_data_df).
        image_dir (str): Directory containing images, named by compound IDs.

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

    # Load data from pickle files
    yields_df = pd.read_pickle(required_files[0])
    yield_data_df = pd.read_pickle(required_files[1])
    # Load the image JSON file
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

    # Prepare the data for the heatmap
    z_values = yield_data_df.T.to_numpy().tolist()
    x_values = yields_df["id"].tolist()
    y_values = yield_data_df.columns.tolist()

    # Load the HTML template
    if not os.path.exists(html_template_path):
        raise FileNotFoundError(f"HTML template not found: {html_template_path}")
    with open(html_template_path, "r") as file:
        html_template = file.read()

    # Update placeholders in the HTML template
    updated_html = html_template.replace("__TITLE__", title)
    updated_html = updated_html.replace("__Z_VALUES__", json.dumps(z_values))
    updated_html = updated_html.replace("__X_VALUES__", json.dumps(x_values))
    updated_html = updated_html.replace("__Y_VALUES__", json.dumps(y_values))
    updated_html = updated_html.replace("__IMAGE_DATA__", json.dumps(mol_image_base64))

    # Write the updated HTML to a new file
    with open(output_html_path, "w") as file:
        file.write(updated_html)

    print(f"HTML file updated and saved to: {output_html_path}")


if __name__ == "__main__":
    html_template_path = os.path.join("templates", "heapmap_template.html")
    output_html_path = os.path.join("docs", "Yield Heatmap.html")
    title = "Yield interactive heatmap"  # Title for the HTML page
    data_dir = "data"  # Path to the folder containing data pickle files
    image_dir = "images"  # Path to the folder containing images

    update_heatmap_html_template(
        html_template_path, output_html_path, title, data_dir, image_dir
    )

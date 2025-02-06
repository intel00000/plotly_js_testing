import os, json, base64
import pandas as pd


def update_html_with_bar_charts(
    html_template, output_dir, properties_pkl, data_dir, image_dir
):
    """
    Generates individual HTML files for bar charts of each numeric column in a dataset,
    with molecular images and tooltips.

    Args:
        html_template (str): Path to the template HTML file.
        output_dir (str): Directory to save the generated HTML files.
        properties_pkl (str): Properties data file (pickle).
        data_dir (str): Path to the folder containing data pickle files.
        image_dir (str): Directory containing molecular images, named by compound IDs.

    Returns:
        None
    """
    # Validate required files and directories
    required_files = [
        os.path.join(data_dir, properties_pkl),
        os.path.join(data_dir, "mol_image_paths_captioned.json"),
        os.path.join(data_dir, "yields.pkl"),
        os.path.join(data_dir, "yield_data_df.pkl"),
        html_template,
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df = pd.read_pickle(required_files[0])  # Load dataset
    with open(required_files[1], "r") as f:
        mol_image_paths = json.load(f)  # Load image JSON file
    yields_df = pd.read_pickle(required_files[2])
    with open(required_files[4], "r") as file:  # Load HTML template
        html_template = file.read()

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

    print("Generating HTML files...")
    # Generate one HTML file for each numeric column
    for column in df.select_dtypes(include="number").columns:
        sorted_df = df.sort_values(column)
        x_values = sorted_df["Compound_Name"].tolist()
        y_values = sorted_df[column].tolist()
        # reorder the mol_image_base64 dictionary to match the order of x_values
        mol_image_base64_reordered = {k: mol_image_base64[k] for k in x_values}
        # reorder the yields_df to match the order of x_values
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

        # Update the HTML template
        updated_html = html_template.replace("__TITLE__", f"{column} by Compound")
        updated_html = updated_html.replace("__X_VALUES__", json.dumps(x_values))
        updated_html = updated_html.replace("__Y_VALUES__", json.dumps(y_values))
        updated_html = updated_html.replace(
            "__IMAGE_DATA__", json.dumps(mol_image_base64_reordered)
        )
        updated_html = updated_html.replace("__YIELD_DATA__", json.dumps(yield_traces))

        # Save the updated HTML to a new file
        # sanitize the column name
        sanitized_column = "".join(
            c if c.isalnum() or c in (" ", "-") else "_" for c in column
        )
        filename = f"{sanitized_column}_by_compounds.html"
        output_file_path = os.path.join(output_dir, filename)
        with open(output_file_path, "w") as file:
            file.write(updated_html)

        print(f"HTML file generated: {output_file_path}")


if __name__ == "__main__":
    html_template = os.path.join("templates", "bar_chart_template.html")
    output_dir = "docs"
    properties_pkl = "Select_properties.pkl"
    data_dir = "data"  # Path to the folder containing data pickle files
    image_dir = "images"

    update_html_with_bar_charts(
        html_template, output_dir, properties_pkl, data_dir, image_dir
    )

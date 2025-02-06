import os
import glob
import time
from datetime import datetime, timezone
import pytz

folder = "docs"
tz = pytz.timezone("America/Chicago")  # CST/CDT timezone
timestamp = int(time.time())  # Get a timestamp for cache busting

# List all HTML files in the current directory excluding index.html
html_files = [f for f in glob.glob("*.html", root_dir=folder) if f != "index.html"]

# get the root directory name
repo_name = os.path.basename(os.getcwd())

# Start writing the index.html file
with open(os.path.join(folder, "index.html"), "w") as index_file:
    index_file.write(
        f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Available Pages for {repo_name} repo</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
</head>
<body>
<div class="container mt-5">
  <h1 class="mb-4">Available Pages for {repo_name} repo</h1>
  <div class="list-group">
"""
    )

    # Add a list item for each HTML file with its creation date
    for filename in sorted(html_files):
        created_utc = datetime.fromtimestamp(
            os.path.getmtime(os.path.join(folder, filename)), tz=timezone.utc
        )
        created_est = created_utc.astimezone(tz)  # Convert to EST/EDT dynamically
        created_time = created_est.strftime("%Y-%m-%d %H:%M")  # Removed UTC offset
        path = os.path.join(folder, filename)
        display_name = filename.replace("_", " ").replace(".html", "")
        index_file.write(
            f'<a href="{filename}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">'
            f'{display_name}<small class="text-muted">{created_time}</small></a>\n'
        )

    # Finish writing the index.html file
    index_file.write(
        """  </div>
</div>
</body>
</html>
"""
    )

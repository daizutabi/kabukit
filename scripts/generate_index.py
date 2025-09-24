import os
import glob

def generate_index_html(notebooks_dir="notebooks", public_dir="public"):
    """
    Generates an index.html file in the public_dir with links to all
    marimo notebooks found in the notebooks_dir.
    """
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)

    index_path = os.path.join(public_dir, "index.html")

    html_content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head><title>Notebooks</title></head>",
        "<body>",
        "<h1>Notebooks</h1>",
        "<ul>"
    ]

    # Find all .py files in the notebooks directory and its subdirectories
    notebook_files = sorted(glob.glob(os.path.join(notebooks_dir, "**", "*.py"), recursive=True))

    for file_path in notebook_files:
        # Get the base name without extension (e.g., "01_J-Quants_認証")
        base_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        
        # The exported HTML file will be in public/ and named after the original .py file
        html_file_name = f"{file_name_without_ext}.html"
        
        # Add a list item with a link
        html_content.append(
            f"<li><a href='{html_file_name}'>{base_name}</a></li>"
        )

    html_content.append("</ul>")
    html_content.append("</body>")
    html_content.append("</html>")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print(f"Generated {index_path}")

if __name__ == "__main__":
    generate_index_html()


from bs4 import BeautifulSoup
import os

# --- Configuration ---
html_file_path = r"C:\Users\savel\Documents\machine-learning-engineering\machine_learning_engineering\tasks\pond-2564617\Pond - Build and Own The Future of AI.html"
output_file_path = r"C:\Users\savel\Documents\machine-learning-engineering\machine_learning_engineering\tasks\pond-2564617\task_description.txt"
image_files_dir = r"C:\Users\savel\Documents\machine-learning-engineering\machine_learning_engineering\tasks\pond-2564617\Pond - Build and Own The Future of AI_files"

# --- HTML Parsing ---
def parse_html_to_text(html_path, img_dir):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        return "Error: HTML file not found."

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Find all images and replace them with placeholders
    for img in soup.find_all('img'):
        img_src = img.get('src')
        if img_src:
            # Create a placeholder text
            img_filename = os.path.basename(img_src)
            placeholder = f"\n[ИЗОБРАЖЕНИЕ: См. файл '{img_filename}' в папке {os.path.basename(img_dir)}]\n"
            # Replace the img tag with the placeholder text
            img.replace_with(placeholder)

    # Get text, preserving some structure
    text = soup.get_text(separator='\n', strip=True)

    # Clean up excessive blank lines
    lines = [line for line in text.split('\n') if line.strip()]
    cleaned_text = "\n".join(lines)

    return cleaned_text

# --- Main Execution ---
if __name__ == "__main__":
    description_text = parse_html_to_text(html_file_path, image_files_dir)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(description_text)
        print(f"Successfully created task description at: {output_file_path}")
    except IOError as e:
        print(f"Error writing to file: {e}")

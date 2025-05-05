import os
from flask import Flask, render_template, request, send_file, abort
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

BASE_DIR = app.root_path
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploaded_folder')

def save_folder_structure(root_folder, output_file, include_files=True):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for root, dirs, files in os.walk(root_folder):
                level = root.replace(root_folder, '').count(os.sep)
                indent = ' ' * 4 * level
                f.write(f"{indent}{os.path.basename(root)}/\n")
                if include_files:
                    for file in files:
                        file_indent = ' ' * 4 * (level + 1)
                        f.write(f"{file_indent}{file}\n")
    except Exception as e:
        print(f"Error saving folder structure: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('folder')
    custom_filename = request.form.get('output_filename', '').strip()

    if not files:
        return 'No files received', 400

    if not custom_filename:
        custom_filename = 'folder_structure'

    if not custom_filename.endswith('.txt'):
        custom_filename += '.txt'

    output_path = os.path.join(BASE_DIR, secure_filename(custom_filename))

    # Clean previous uploads
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR)

    for file in files:
        relative_path = file.filename
        full_path = os.path.join(UPLOAD_DIR, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        file.save(full_path)

    try:
        save_folder_structure(UPLOAD_DIR, output_path)
    except Exception:
        return 'Failed to save folder structure', 500

    if not os.path.exists(output_path):
        return 'Output file not found', 500

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

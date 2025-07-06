import os
from flask import Flask, request, jsonify, send_file, abort
import subprocess

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is required")

def check_auth():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        abort(403, description="Forbidden: Invalid API Key")

def clean_latex_aux_files(build_path):
    extensions = [".aux", ".bbl", ".bcf", ".blg", ".log", ".out", ".run.xml",
                  ".synctex.gz", ".fdb_latexmk", ".fls", ".toc"]
    for f in os.listdir(build_path):
        if any(f.endswith(ext) for ext in extensions):
            try:
                os.remove(os.path.join(build_path, f))
            except Exception as e:
                print(f"Warning: Could not delete {f} — {e}")

def build_latex_and_respond(content, tex_filename):
    latex_path = os.path.join(os.getcwd(), "latex")
    os.makedirs(latex_path, exist_ok=True)
    os.chdir(latex_path)

    with open("content.tex", "w", encoding="utf-8") as f:
        f.write(content)

    clean_latex_aux_files(latex_path)

    result = subprocess.run(
        ["tectonic", tex_filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30
    )

    os.chdir("..")  # ✅ Reset working dir

    if result.returncode == 0:
        pdf_path = os.path.join(latex_path, tex_filename.replace(".tex", ".pdf"))
        return send_file(pdf_path, mimetype="application/pdf")
    else:
        return jsonify({"error": "Compilation failed", "log": result.stdout}), 500
    
@app.route("/buildcv", methods=["POST"])
def build_cv():
    check_auth()
    content = request.get_json().get("content_tex")
    if not content:
        return jsonify({"error": "Missing content_tex in request"}), 400
    return build_latex_and_respond(content, "cv.tex")

@app.route("/buildcvreferences", methods=["POST"])
def build_cv_with_references():
    check_auth()
    content = request.get_json().get("content_tex")
    if not content:
        return jsonify({"error": "Missing content_tex in request"}), 400
    return build_latex_and_respond(content, "cvReferences.tex")



if __name__ == "__main__":
    # Default Fly.io port is 8080 — already fine!
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

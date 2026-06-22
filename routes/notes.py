import os
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db, Note
from services.openai_service import generate_notes
from services.pdf_service import extract_text

notes_bp = Blueprint("notes", __name__)
ALLOWED_EXTENSIONS = {"pdf", "txt", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@notes_bp.route("/notes")
@login_required
def notes():
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("notes.html", notes=user_notes)

@notes_bp.route("/notes/generate", methods=["POST"])
@login_required
def generate():
    title = request.form.get("title", "Untitled")
    note_type = request.form.get("note_type", "all")
    text = request.form.get("text", "").strip()

    if "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            text = extract_text(filepath)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = generate_notes(text[:4000], note_type)  # limit tokens

    note = Note(
        user_id=current_user.id,
        title=title,
        original_text=text[:2000],
        summary=result if note_type in ["summary", "all"] else "",
        bullet_points=result if note_type == "bullets" else "",
        key_highlights=result if note_type == "highlights" else ""
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({"result": result, "note_id": note.id})

@notes_bp.route("/notes/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "deleted"})

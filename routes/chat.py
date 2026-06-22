from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.database import db, ChatHistory
from services.openai_service import chat_with_ai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat")
@login_required
def chat():
    history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at).limit(50).all()
    return render_template("chat.html", history=history)

@chat_bp.route("/chat/send", methods=["POST"])
@login_required
def send_message():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Build conversation context
    recent = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).limit(10).all()
    messages = [{"role": "system", "content": "You are a helpful AI study tutor. Explain concepts clearly, provide examples, and encourage students. Be concise but thorough."}]
    for h in reversed(recent):
        messages.append({"role": h.role, "content": h.message})
    messages.append({"role": "user", "content": user_message})

    ai_response = chat_with_ai(messages)

    # Save to DB
    db.session.add(ChatHistory(user_id=current_user.id, role="user", message=user_message))
    db.session.add(ChatHistory(user_id=current_user.id, role="assistant", message=ai_response))
    db.session.commit()

    return jsonify({"response": ai_response})

@chat_bp.route("/chat/clear", methods=["POST"])
@login_required
def clear_chat():
    ChatHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"status": "cleared"})

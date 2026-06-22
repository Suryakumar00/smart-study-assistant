from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

def _generate(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content

def chat_with_ai(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content

def generate_study_plan(subject, syllabus, deadline, hours_per_day):
    prompt = f"""Create a detailed personalized study plan for:
Subject: {subject}
Syllabus/Topics: {syllabus}
Deadline: {deadline}
Available hours per day: {hours_per_day}

Format the plan as a day-by-day schedule with:
- Topics to cover each day
- Time allocation
- Study tips
- Revision slots
Keep it practical and achievable."""
    return _generate(prompt)

def generate_notes(text, note_type="all"):
    prompts = {
        "summary": f"Summarize the following text in 3-5 clear paragraphs:\n\n{text}",
        "bullets": f"Convert the following text into concise bullet points (key points only):\n\n{text}",
        "highlights": f"Extract the most important key highlights, definitions, and concepts from:\n\n{text}",
        "all": f"""Analyze the following text and provide:
1. SUMMARY: A 3-5 paragraph summary
2. BULLET POINTS: Key points as bullet list
3. KEY HIGHLIGHTS: Important terms, definitions, and concepts

Text: {text}"""
    }
    return _generate(prompts.get(note_type, prompts["all"]))

def generate_quiz(topic, difficulty, num_questions, quiz_type):
    prompt = f"""Generate {num_questions} {quiz_type} questions on "{topic}" at {difficulty} difficulty.

Format STRICTLY as JSON:
{{
  "questions": [
    {{
      "question": "question text",
      "type": "{quiz_type}",
      "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
      "answer": "correct answer",
      "explanation": "brief explanation"
    }}
  ]
}}
Only return valid JSON, no extra text, no markdown code blocks."""
    return _generate(prompt)

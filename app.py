from flask import Flask, render_template, request, send_file
import PyPDF2
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ⭐ Skills list
ALL_SKILLS = [
    "python", "java", "c", "c++", "sql",
    "html", "css", "javascript",
    "machine learning", "ai", "flask",
    "django", "git", "github", "react"
]

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- ANALYZE ----------------
@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['pdf_file']
    job_desc = request.form['job_desc'].lower()

    pdf_reader = PyPDF2.PdfReader(file)

    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    text_lower = text.lower()

    # ---------------- SKILLS ----------------
    found_skills = []
    for skill in ALL_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)

    # ---------------- SCORE ----------------
    score = len(found_skills) * 10
    if score > 100:
        score = 100

    # ---------------- MISSING ----------------
    missing_skills = []
    for skill in ALL_SKILLS:
        if skill not in found_skills:
            missing_skills.append(skill)

    # ---------------- SUGGESTIONS ----------------
    suggestions = []

    if "python" not in found_skills:
        suggestions.append("Python nerchuko")

    if "sql" not in found_skills:
        suggestions.append("SQL practice cheyyi")

    if score < 50:
        suggestions.append("More technical skills add cheyyi")

    suggestions.append("Real projects add cheyyi")

    # ---------------- AI FEEDBACK ----------------
    if score >= 80:
        ai_feedback = "Excellent resume! Focus on advanced projects."
    elif score >= 50:
        ai_feedback = "Good resume, improve some skills."
    else:
        ai_feedback = "Improve core skills and projects."

    # ---------------- JOB MATCH ----------------
    jd_skills = []
    for skill in ALL_SKILLS:
        if skill in job_desc:
            jd_skills.append(skill)

    if len(jd_skills) > 0:
        match_percent = int((len(found_skills) / len(jd_skills)) * 100)
    else:
        match_percent = 0

    if match_percent > 100:
        match_percent = 100

    # ---------------- STORE GLOBALS ----------------
    global DATA
    DATA = {
        "text": text,
        "found_skills": found_skills,
        "score": score,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "ai_feedback": ai_feedback,
        "match_percent": match_percent
    }

    # ---------------- OUTPUT ----------------
    return f"""
    <div class="container mt-5">

        <div class="card p-4 shadow">

            <h3>📄 Extracted Text</h3>
            <pre style="max-height:250px; overflow:auto;">{text}</pre>

            <h3>🧠 Skills</h3>
            <ul>
            {''.join(f'<li>{s}</li>' for s in found_skills)}
            </ul>

            <h3>📊 Score</h3>
            <h2>{score}/100</h2>

            <h3>🎯 Job Match</h3>
            <h2>{match_percent}%</h2>

            <h3>🤖 AI Feedback</h3>
            <p>{ai_feedback}</p>

            <a href="/download" class="btn btn-success mt-3">
                Download PDF Report
            </a>

        </div>

    </div>
    """


# ---------------- PDF GENERATION ----------------
def generate_pdf(data):

    file_path = "/tmp/resume_report.pdf"  # deployment safe path
    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("AI Resume Analysis Report", styles['Title']))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Score: {data['score']}/100", styles['Normal']))
    content.append(Paragraph(f"Job Match: {data['match_percent']}%", styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Skills:", styles['Heading2']))
    content.append(Paragraph(", ".join(data['found_skills']), styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Suggestions:", styles['Heading2']))
    content.append(Paragraph(", ".join(data['suggestions']), styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("AI Feedback:", styles['Heading2']))
    content.append(Paragraph(data['ai_feedback'], styles['Normal']))

    doc.build(content)

    return file_path


# ---------------- DOWNLOAD FIXED ----------------
@app.route('/download')
def download():

    file_path = generate_pdf(DATA)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="AI_Resume_Report.pdf"
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# Pursuit

A job application tracker with AI-powered resume-to-job match scoring.

## What it does

Pursuit lets you log job applications, track their status through a pipeline (Applied, Interview, Offer, Rejected), and get an AI-generated match score between your resume and a job's description before or after applying.

## Features

- **Authentication** — signup and login with hashed passwords and session-based access control
- **Dashboard** — real-time analytics: response rate, applications this week, average days to interview, and a status pipeline breakdown
- **Applications list** — searchable and filterable by company, role, and status
- **Application detail view** — full record per application, including notes and uploaded resume
- **AI match scoring** — extracts text from an uploaded resume PDF, compares it against the job description using the Claude API, and returns a 1-5 score with reasoning and a list of missing keywords

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **AI:** Anthropic Claude API
- **PDF parsing:** pypdf
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 templating

## Running it locally

```bash
git clone <repo-url>
cd pursuit
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-api-key-here
```

Initialize the database:

```bash
python database.py
```

Run the app:

```bash
python app.py
```

Visit `http://127.0.0.1:5001`.

## Notes

- Resume uploads are stored locally in `/uploads` and are not committed to the repository.
- `applications.db` is excluded from version control since it contains real user data once the app is in use.

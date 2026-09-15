import os
from dotenv import load_dotenv
from anthropic import Anthropic
import re
from pypdf import PdfReader
import json
#We are testing the Claude API in this file, by passing through static data for the Claude API to assess
#The Claude console has been loaded up with credits

load_dotenv()


client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


reader = PdfReader("Dutton-Voshana.pdf")

full_text = ""
for page in reader.pages:
    full_text += page.extract_text()
resume_text = re.sub(r'\s+', ' ', full_text)

job_description = f"""Role: Software Developer, Australian BioCommons
Salary: $125,191 - $135,504 p.a. plus 17% super

You will develop, maintain and operate a PostgreSQL database 
with a FastAPI backend and several Python data management 
tools, and be responsible for engineering the data flows and 
automation, monitoring the system and presenting data and 
status back to end users in meaningful ways.

Key Responsibilities:
- Work in a highly collaborative, interdisciplinary team as 
  the core software developer
- Work independently and deliver tasks with minimal daily 
  supervision
- Develop and deploy secure services and infrastructure, 
  preventing vulnerabilities, managing dependencies, and 
  ensuring secure access and communication protocols
- Design and develop relational databases with standardised 
  APIs using frameworks and specifications such as FastAPI 
  and OpenAPI
- Develop and analyse user stories in collaboration with the 
  product owner and business analyst
- Ensure all code is automatically tested using a standard 
  testing framework
- Write technical documentation
- Effectively work and collaborate with a nationally-
  distributed team
- Understand and apply UX best practices and a modern design 
  language when developing front end systems

Essential Requirements:
- A degree in software engineering, computer science, or 
  bioinformatics, or extensive equivalent industry experience
- At least two years of experience as a software developer
- Experience building and maintaining relational databases 
  and API backends
- Experience with CI/CD practices, GitHub workflows, and 
  deployment on Linux systems
- In depth experience with at least one backend language, 
  preferably Python
- Demonstrated ability to work in unfamiliar environments 
  and code bases
- Excellent verbal and written communication skills"""
prompt = f"""You are an experienced technical recruiter evaluating how well a candidate's resume matches a specific job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Evaluate the match between this resume and this job description. Consider:
- Required skills and technologies explicitly mentioned in the job description
- Years of experience and seniority level expected versus what the resume demonstrates
- Relevant project or work experience that maps directly to the role's responsibilities
- Domain or industry alignment, if the job description specifies one

Score the match on a scale of 1 to 5, where:
1 = Poor match, missing most core requirements
2 = Weak match, missing several important requirements
3 = Moderate match, meets some core requirements but has notable gaps
4 = Strong match, meets most core requirements with minor gaps
5 = Excellent match, meets or exceeds nearly all requirements

Respond with ONLY valid JSON in exactly this structure, and nothing else. Do not include any explanation, preamble, or text outside the JSON object:

{{
  "score": <integer from 1 to 5>,
  "reasoning": "<2-3 sentence explanation for the score, referencing specific evidence from the resume>",
  "missing_keywords": ["<skill or requirement from the job description not clearly evidenced in the resume>", "..."]
}}

If there are no missing keywords, return an empty array for missing_keywords."""
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=300,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(message.content[0].text)

response_text = message.content[0].text
print("RAW RESPONSE:")
print(response_text)
print("---END---")

response_text = message.content[0].text.strip()

if response_text.startswith("```"):
    response_text = response_text.split("\n", 1)[1]
if response_text.endswith("```"):
    response_text = response_text.rsplit("\n", 1)[0]

try:
    result = json.loads(response_text)
    print(result['score'])
    print(result['reasoning'])
    print(result['missing_keywords'])
except json.JSONDecodeError:
    print("Couldn't parse the response as JSON")

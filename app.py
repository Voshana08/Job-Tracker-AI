from flask import Flask,render_template,request,redirect,url_for,flash,session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
#This below import can create a random set of strings with Python.
import uuid
import sqlite3
#The packages imported below are for reading a pdf and parsing it to Claude
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import re
from pypdf import PdfReader
import json
load_dotenv()
#Creating the flask app
app = Flask(__name__)
#These secret keys should not be hardcoded but for this project its fine.
app.secret_key = 'voshana-dev-secret-2026'
#Creating the routes to the different pages
#base route

#This is a context processor, its job is to make a variable available to every template.
@app.context_processor
def inject_user():
    return dict(logged_in='username' in session)


@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('landing.html')

#Contact route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # If not logged in, show the login prompt version of the page.
    if 'username' not in session:
        return render_template('dashboard.html')

    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Counting the total number of applications
    cursor.execute("SELECT COUNT(*) FROM applications")
    total_rows = cursor.fetchone()[0]

    # Number of applications that have moved past "Applied"
    applied = "Applied"
    query = "SELECT COUNT(*) FROM applications WHERE status != ?"
    cursor.execute(query, (applied,))
    responded = cursor.fetchone()[0]

    # Response rate calculation, with divide-by-zero guard
    if total_rows > 0:
        response_rate = round((responded / total_rows) * 100)
    else:
        response_rate = 0

    # Applications submitted in the last 7 days
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    query2 = "SELECT COUNT(*) FROM applications WHERE date_applied >= ?"
    cursor.execute(query2, (one_week_ago_str,))
    applications_this_week = cursor.fetchone()[0]

    # Calculating the average days between applied and interview
    interview1 = "Interview"
    query3 = "SELECT date_applied, status_updated_at FROM applications WHERE status = ?"
    cursor.execute(query3, (interview1,))
    data_date = cursor.fetchall()

    day_gaps = []
    for row in data_date:
        applied_date = datetime.strptime(row['date_applied'], '%Y-%m-%d')
        interview_date = datetime.strptime(row['status_updated_at'], '%Y-%m-%d')
        gap = (interview_date - applied_date).days
        day_gaps.append(gap)

    if len(day_gaps) > 0:
        avg_days_to_interview = sum(day_gaps) / len(day_gaps)
    else:
        avg_days_to_interview = 0

    # Pipeline counts, one per status
    cursor.execute("SELECT status, COUNT(*) AS count FROM applications GROUP BY status")
    pipeline_data = cursor.fetchall()
    status_count_dict = {}
    for row in pipeline_data:
        status_count_dict[row["status"]] = row['count']

    applied_count = status_count_dict.get('Applied', 0)
    interview_count = status_count_dict.get('Interview', 0)
    offer_count = status_count_dict.get('Offer', 0)
    rejected_count = status_count_dict.get('Rejected', 0)

    # Most recent 5 applications, for the dashboard list
    query5 = "SELECT id, company, role, status, date_applied FROM applications ORDER BY date_applied DESC LIMIT 5"
    cursor.execute(query5)
    recent_applications = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html',
                        total_rows=total_rows,
                        response_rate=response_rate,
                        applications_this_week=applications_this_week,
                        avg_days_to_interview=round(avg_days_to_interview),
                        applied_count=applied_count,
                        interview_count=interview_count,
                        rejected_count=rejected_count,
                        recent_applications=recent_applications,
                        offer_count=offer_count)



# full view of applications that have been submitted
@app.route('/applications',methods = ['GET','POST'])
def applications():
    #This check if the user is logged in.
    if 'username' not in session:
        return render_template('applications.html')
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #Reading the search box and status filter out of the query string
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'All')

    cursor.execute("SELECT COUNT(*) FROM applications")
    total_rows = cursor.fetchone()[0]

    query = "SELECT id,company, role, status, date_applied FROM applications WHERE 1=1"
    params = []

    if status_filter != 'All':
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (company LIKE ? OR role LIKE ?)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term])

    query += " ORDER BY date_applied DESC"
    cursor.execute(query, params)
    filtered_applications = cursor.fetchall()

    conn.close()
    return render_template('applications.html',
                        total_rows=total_rows,
                        filtered_applications=filtered_applications,
                        search_query=search_query,
                        status_filter=status_filter,
                        status_options=['All', 'Applied', 'Interview', 'Offer', 'Rejected'])

#Form to add a new job application
@app.route('/applications/add', methods = ['GET','POST'])
def add_application():
    status_options = ['Applied', 'Interview', 'Offer', 'Rejected']
    if 'username' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('auth', mode='login'))
    if request.method == 'POST':
        #This 4 lines of code are for the resume pdf when the user uploads
        #It will change the name of the filename
        resume_file = request.files.get('resume')
        resume_filename = None
        
        if resume_file and resume_file.filename:
                #uuid can create a random string in Python, and that string is attached to the front of the resume name.
                resume_filename = f"{uuid.uuid4()}_{resume_file.filename}"
                resume_file.save(f"uploads/{resume_filename}")
            
        company = request.form.get('company', '').strip()
        role = request.form.get('role', '').strip()
        job_description = request.form.get('job_description', '').strip()
        status = request.form.get('status', 'Applied')
        date_applied = request.form.get('date_applied') or datetime.now().strftime('%Y-%m-%d')
        notes = request.form.get('notes', '').strip()
        now = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect("applications.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications
                (company, role, job_description, status, date_applied, notes, status_updated_at, created_at,resume_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
        """, (company, role, job_description, status, date_applied, notes, now, now,resume_filename))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_application.html', status_options=status_options)


#Creating a route to view each application individually
@app.route('/applications/<int:id>')
def application_detail(id):
    #Connecting to the DB
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    #Finding the application with its id
    cursor.execute("SELECT * FROM applications WHERE id = ?", (id,))
    application = cursor.fetchone()
    conn.close()

    if application is None:
       flash("This application doesnt exist") 
       return redirect(url_for('applications'))
   
    application = dict(application)  # convert to a plain dict so we can modify it

    if application['missing_keywords']:
        #This convert the string format missing keywords to a actual array
        #The missing keywords now are stored in a format of "['json','java','html']"
        # #But with json.loads(application['missing_keywords']) it will get converted to a actual python.
        #This list can then be manupilated.
        application['missing_keywords'] = json.loads(application['missing_keywords'])
    else:
        application['missing_keywords'] = []

    return render_template('application_detail.html', application=application)


#Scoring the resume 
@app.route('/applications/<int:id>/score', methods=['POST'])
def score_application(id):
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications WHERE id = ?", (id,))
    application = cursor.fetchone()
    if 'username' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('auth', mode='login'))
    if application is None:
        conn.close()
        flash("Application not found.")
        return redirect(url_for('applications'))

    if application['resume_filename'] is None:
        conn.close()
        flash("Upload a resume before scoring this application.")
        return redirect(url_for('application_detail', id=id))

    # STEP 4 — open the PDF and extract text
    reader = PdfReader(f"uploads/{application['resume_filename']}")
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()
    resume_text = re.sub(r'\s+', ' ', resume_text)

    # STEP 5 — build the prompt
    job_description = application['job_description']
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
  "match_score": <integer from 1 to 5>,
  "reasoning": "<2-3 points explanation for the score, referencing specific evidence from the resume>",
  "missing_keywords": ["<skill or requirement from the job description not clearly evidenced in the resume>", "..."]
}}

If there are no missing keywords, return an empty array for missing_keywords."""

    #This is where the Anthropic key gets read from.
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    # STEP 6 — call Claude
    message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=300,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

    # STEP 7 — clean and parse
    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("\n", 1)[0]

    try:
        #json.loads(response_text), converts the cleaned-up JSON string into an actual Python dictionary,
        #for me to access result['score'], result['reasoning']
        result = json.loads(response_text)
        #Handling the JSON error if it occurs
    except json.JSONDecodeError:
        conn.close()
        flash("Couldn't get a match score right now. Try again.")
        return redirect(url_for('application_detail', id=id))

    # STEP 8 — UPDATE the database (new SQL keyword for you)
    cursor.execute("""
    UPDATE applications
    SET match_score = ?, reasoning = ?, missing_keywords = ?
    WHERE id = ?
""", (result['match_score'], result['reasoning'], json.dumps(result['missing_keywords']), id))
    #print(result['match_score'])
    conn.commit()

    conn.close()
    return redirect(url_for('application_detail', id=id))
#Auth page (layout only - login/signup logic to be built separately)
@app.route('/auth',methods = ['GET','POST'])
def auth():
    mode = request.args.get('mode', 'login')
    
    if request.method == 'POST':
        conn = sqlite3.connect("applications.db")
        conn.row_factory =sqlite3.Row
        cursor = conn.cursor()
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)  # hash it
        if mode == 'signup':
            print("Signup") 
            try :
                cursor.execute(
                "INSERT INTO users (username,password) VALUES (?, ?)",
                ( username, hashed_password)
                )   
                conn.commit()
                conn.close()
                flash("Account created! Please log in.")
                 
                conn.close()
                return redirect(url_for('auth', mode='login'))
                
            
            except sqlite3.IntegrityError:
                conn.close()
                flash("That username is already taken.")
                return redirect(url_for('auth'))
            
        elif mode == 'login':
            print("login logic")
            
            query6 = "SELECT * FROM users WHERE username = ?"
            cursor.execute(query6,(username,))
            user = cursor.fetchone()
            
            if user :
                print("Username exists")
                print("Stored value:", user['password'])
                print("Submitted password:", password)
                if check_password_hash(user['password'],password):
                    print("Password is correct")
                    session['username'] = username
                    flash("Logged in successfully!")
                    conn.commit()  
                    conn.close()
                    return redirect(url_for('dashboard'))
                else:
                # username exists, but wrong password
                    flash("Incorrect password.")
                    return redirect(url_for('auth', mode='login'))   
            else:
                flash("No account found with that username.")
                return redirect(url_for('auth', mode='signup'))
        
    # cursor.execute("SELECT COUNT(*) FROM users")
    # total_users = cursor.fetchone()[0]
    # print("Total user logins : ",total_users)  
        conn.commit()  
        conn.close()
    return render_template('auth.html',mode=mode)


#Detailed view of the job applications
@app.route('/view')
def view():
    return render_template('view.html')

#logout for users
@app.route('/logout')
def logout():
    #This removes the username from session, if the username doesnt exist, it will do nothing.
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('home')) 

if __name__ == '__main__':
    
    app.run(debug=True,port=5001) 
#End of file
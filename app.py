from flask import Flask,render_template,request,redirect,url_for,flash,session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
#Creating the flask app
app = Flask(__name__)
#These secret keys should not be hardcoded but for this project its fine.
app.secret_key = 'voshana-dev-secret-2026'
#Creating the routes to the different pages
#base route

@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('landing.html')

#Contact route
@app.route('/dashboard',methods = ['GET','POST'])
def dashboard():
    #Connecting to the database
    conn = sqlite3.connect("applications.db")
    conn.row_factory =sqlite3.Row
    cursor = conn.cursor()
    
    #The logic to read the database and calculate the response rate
    cursor.execute("SELECT COUNT(*) FROM applications")
    total_rows = cursor.fetchone()[0]
    #print("Total rows :" , total_rows)
    
    #Counting the number of responded. 
    #Using a ? placeholder prevents SQL injection
    applied = "Applied"
    query = "SELECT COUNT(*) FROM applications WHERE status != ?"
    #If its a single placeholder, it needs a tuple
    cursor.execute(query,(applied,))
    #fetchone method gives us sort of an array,even though its one number to be returned back. So use indexing.
    responded = cursor.fetchone()[0]
    #print("Responded to ", responded)
   
    
    #Now lets calculate the response rate
    if total_rows > 0 :
        response_rate = round((responded/total_rows)*100)
        print(response_rate)
    else:
        response_rate =0
        print("No job applications yet")
    
    #Calculating how many appliations, was put through this week (last 7 days)
    #This may look complex, but all its doing is string manupulation. And changing the date format.
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    #one_week_ago comes back as a Python datetime object
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')
    
    query2 = "SELECT COUNT(*) FROM applications WHERE date_applied >= ?"
    cursor.execute(query2,(one_week_ago_str,))
    applications_this_week = cursor.fetchone()[0]
    print("Applications this week : ", applications_this_week)
    
    #Average days to interview is the next calculation
    #This is calculated by checking when the application was submited - the date the status changed.
    interview1 = "Interview"
    query3 = "SELECT date_applied,status_updated_at FROM applications WHERE status = ?"
    cursor.execute(query3,(interview1,))
    data_date = cursor.fetchall()
    for row in data_date:
        print(row['date_applied'], row['status_updated_at'])
    
    day_gaps = []   # empty container, created BEFORE the loop

    for row in data_date:
        applied_date = datetime.strptime(row['date_applied'], '%Y-%m-%d')
        interview_date = datetime.strptime(row['status_updated_at'], '%Y-%m-%d')
        # the .days gives you just the days as an int. Its part of the timedelta package.
        
        gap =(interview_date-applied_date).days
        
        day_gaps.append(gap)  # add gap into your container
    if len(day_gaps) > 0 :
        
        avg_days_to_interview = sum(day_gaps) / len(day_gaps)
        print("Average between application and Interview : ", round(avg_days_to_interview))
    else :
        print("No applications yet, apply for a job !")
        avg_days_to_interview = 0
    
    # Grouping all of the status to one row now, to count how many instances of the status I got 
    cursor.execute("SELECT status, COUNT(*) AS count FROM applications GROUP BY status")
    pipeline_data = cursor.fetchall()
    status_count_dict = {}
    for row in pipeline_data:
        print(row['status'], row['count'])
        status_count_dict[row["status"]] = row['count']
    print(status_count_dict)
    #Now its time to get the count for the 4 status variables.
    #This is how you get values out of a dict, the 0 is if its null and the value doesnt exist.
    applied_count = status_count_dict.get('Applied',0)
    interview_count = status_count_dict.get('Interview',0)
    offer_count = status_count_dict.get('Offer',0)
    rejected_count = status_count_dict.get('Rejected',0)
    
    # Now we need to get the recently applied applications (top 5 most recent ) to be shown on the dashboard
    query5 = "SELECT company, role, status, date_applied FROM applications ORDER BY date_applied DESC LIMIT 5"
    cursor.execute(query5)
    recent_applications = cursor.fetchall()
    for recent in recent_applications:
        print(recent['date_applied'], "Date applied")
    

    

    
    conn.close()
    return render_template('dashboard.html',
                        total_rows=total_rows,
                        response_rate=response_rate,
                        applications_this_week=applications_this_week,
                        avg_days_to_interview=round(avg_days_to_interview),
                        applied_count = applied_count,
                        interview_count = interview_count,
                        rejected_count = rejected_count,
                        recent_applications = recent_applications,
                        offer_count = offer_count)




# full view of applications that have been submitted
@app.route('/applications',methods = ['GET','POST'])
def applications():
    conn = sqlite3.connect("applications.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #Reading the search box and status filter out of the query string
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'All')

    cursor.execute("SELECT COUNT(*) FROM applications")
    total_rows = cursor.fetchone()[0]

    query = "SELECT company, role, status, date_applied FROM applications WHERE 1=1"
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

    if request.method == 'POST':
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
                (company, role, job_description, status, date_applied, notes, status_updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company, role, job_description, status, date_applied, notes, now, now))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_application.html', status_options=status_options)

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


if __name__ == '__main__':
    
    app.run(debug=True,port=5001) 

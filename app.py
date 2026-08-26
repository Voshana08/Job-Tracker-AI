from flask import Flask,render_template,request
from datetime import datetime, timedelta
import sqlite3
#Creating the flask app
app = Flask(__name__)
#Creating the routes to the different pages
#base route

@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('base.html')

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
    avg_days_to_interview = sum(day_gaps) / len(day_gaps)
    print("Average between application and Interview : ", round(avg_days_to_interview))
    # Grouping all of the status to one row now, to count how many instances of the status I got 
  
  
    
    conn.close()
    return render_template('dashboard.html',
                        total_rows=total_rows,
                        response_rate=response_rate,
                        applications_this_week=applications_this_week,
                        avg_days_to_interview=round(avg_days_to_interview))




# full view of applications that have been submitted 
@app.route('/applications',methods = ['GET','POST'])
def applications():
    return render_template('applications.html')

#Detailed view of the job applications
@app.route('/view')
def view():
    return render_template('view.html')


if __name__ == '__main__':
    
    app.run(debug=True,port=5001) 

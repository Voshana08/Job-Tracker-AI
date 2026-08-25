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
@app.route('/Dashboard',methods = ['GET','POST'])
def contact():
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
    interview = "Interview"
    query3 = "SELECT date_applied,status_updated_at FROM applications WHERE status = ?"
    cursor.execute(query3,(interview,))
    data_date = cursor.fetchall()
    for row in data_date:
        print(row['date_applied'], row['status_updated_at'])
  
  
  
  
  
    
    conn.close()
    return render_template('dashboard.html')




# full view of applications that have been submitted 
@app.route('/applications',methods = ['GET','POST'])
def learning():
    return render_template('applications.html')

#Detailed view of the job applications
@app.route('/view')
def projects():
    return render_template('view.html')


if __name__ == '__main__':
    
    app.run(debug=True,port=5001) 

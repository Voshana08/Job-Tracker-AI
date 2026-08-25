from flask import Flask,render_template,request
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

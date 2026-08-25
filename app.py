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
    print(total_rows)
    
    #Counting the number of responded. 
    #Using a ? placeholder prevents SQL injection
    applied = "Applied"
    query = "SELECT COUNT(*) FROM applications WHERE status != ?"
    #If its a single placeholder, it needs a tuple
    cursor.execute(query,(applied,))
    
    
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

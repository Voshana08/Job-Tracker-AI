from flask import Flask,render_template,request
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

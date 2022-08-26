from flask import Flask, render_template


app = Flask(__name__)



#----------practice start------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def index2():
    return render_template("about.html")

@app.route('/model')
def index3():
    return render_template("model.html")    

@app.route('/analysis')
def index4():
    return render_template("analysis.html")


#----------practice end-------------- 


if __name__=="__main__":
    app.run(debug=True)

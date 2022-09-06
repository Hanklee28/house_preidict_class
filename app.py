from flask import Flask, render_template, request



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
#----------post-------------- 
@app.route('/model', methods=['GET', 'POST'])
def get_form():
    if request.method == "GET":
        return render_template('model.html', page_header="Form")
    elif request.method == "POST":# 以post的形式傳出去
        print(f'method:{request.values["parking"]}')
        return render_template('model.html', page_header="Form")
# @app.route('/form_result', methods=['POST']) # default methods is "GET"
# def form_result():
#     data = [["method:", request.method],
#             ["base_url:", request.base_url],
#             ["form data:", request.form]]
#     print(request.parking)
#     return render_template('model.html', page_header="Form data", data=data)


#----------post-------------- 


if __name__=="__main__":
    app.run(debug=True)

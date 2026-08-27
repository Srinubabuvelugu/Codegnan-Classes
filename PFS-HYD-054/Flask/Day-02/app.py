from flask import Flask,render_template

app=Flask(__name__)

# routes create
@app.route('/')
def home():
    return 'PFS-HYD-054 was brilliant'

@app.route('/batchno')
def batchno():
    return str(54)

@app.route('/index')
def indexPage():
    return render_template('index.html')

@app.route('/about')
def aboutPage():
    return render_template('about.html')

if (__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )


from flask import Flask,render_template

app=Flask(__name__)

@app.route('/')
def index():
    a=[
        {'id':1,'name':'Madhu'},
        {'id':2,'name':'sai'}
    ]

    return render_template('index.html',a=a)

@app.route('/about')
def about():
    return render_template('about.html')

if (__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
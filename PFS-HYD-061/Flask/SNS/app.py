from flask import Flask, render_template, request, redirect


from database import createTables


# flask instance
app = Flask(__name__)

# ======================================================================
#                              Authentication Routes
# ======================================================================
@app.route('/')
def home():
    return render_template('home.html')



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port = 5001)

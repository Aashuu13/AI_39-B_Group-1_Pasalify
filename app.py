from flask import Flask

app = Flask(__name__)

@app.route("/")
def about():
    return "Pasalify Welcomes You! Happy to have you here 😍"


if __name__ == "__main__":
    app.run(debug=True)
     
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}".format(name)

if __name__ == "__main__":
    print("Hello World")
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))



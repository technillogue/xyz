from flask import Flask, request


app = Flask(__name__)


@app.route("/")
def foo():
    if request.args:
        resp = ", ".join(f"{k} is {v}" for k, v in request.args.items())
        return f"you said {resp}. good for you!"
    return """
    <html><body>welcome to my webbed sight.<br/><br/>my content is currently at <a href="https://technillogue.github.io">technillogue.github.io</a></body></html>
    """

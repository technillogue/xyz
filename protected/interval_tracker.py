import json
import csv
from itertools import groupby
from datetime import datetime as dt
from json2html import json2html
from flask import Flask, request, render_template, Markup


class Counts:
    def __init__(self):
        try:
            self.log = [dt.fromisoformat(row[0]) for row in csv.reader(open("counts.csv"))]
        except FileNotFoundError:
            self.log = []
        self.day_counts = self.count_days()
        self.logfile = open("counts.csv", "a")
        self.writer = csv.writer(self.logfile)

    def count_days(self):
        return  [len(list(group)) for key, group in groupby(self.log, key=lambda ts:ts.day)]

    def click(self):
        now = dt.now()
        self.writer.writerow([now.isoformat()])
        self.logfile.flush()
        if self.log[-1].day == now.day:
            self.day_counts[-1] += 1
        else:
            self.day_counts.append(1)
        self.log.append(now)

    def asdict(self):
        if self.log:
            return {
                "elapsed": str(dt.now() - self.log[-1]),
                "today": day_counts[-1],
                "last 7 day average": sum(day_counts[-7:])/len(day_counts[-7:]),
            }
        else:
            return {}


app = Flask(__name__)
counts = Counts()

@app.route("/")
def foo():
    if request.args:
        resp = ", ".join(f"{k} is {v}" for k, v in request.args.items())
        return f"you said {resp}. good for you!"
    return """
    <!DOCTYPE html>welcome to my webbed sight.<br/><br/>my content is currently at <a href="https://technillogue.github.io">technillogue.github.io</a>
    """

@app.route("/counter", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        counts.click()
    return render_template(
        "main.html", stats=Markup(json2html.convert(counts.asdict()))
    )


@app.route("/counter/api")
def api():
    return json.dumps(counts.asdict())

if __name__=="__main__":
    app.run()

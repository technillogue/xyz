import json
import csv
from collections.abc import Iterator
from itertools import groupby, islice
from datetime import timedelta, datetime as dt
from json2html import json2html
from flask import Flask, request, render_template, Markup


class Counts:
    def __init__(self) -> None:
        try:
            self.log = [
                dt.fromisoformat(row[0])
                for row in csv.reader(open("counts.csv"))
            ]
        except FileNotFoundError:
            self.log = []
        self.day_counts = self.count_days()
        self.logfile = open("counts.csv", "a")
        self.writer = csv.writer(self.logfile)

    def count_days(self, reverse: bool = True) -> Iterator[int]:
        if not self.log:
            return
        prev_date = (self.log[-1] if reverse else self.log[0]).date()
        groups = groupby(reversed(self.log) if reverse else self.log, dt.date)
        for date, events in groups:
            for missing_day in range(abs(date - prev_date).days - 1):
                yield 0
            prev_date = date
            yield len(list(events))
        return

    def click(self) -> None:
        now = dt.now()
        self.writer.writerow([now.isoformat()])
        self.logfile.flush()
        self.log.append(now)
        # self.stats = self.asdict()

    def asdict(self) -> dict[str, str]:
        if not self.log:
            return {}
        recent_counts = list(islice(self.count_days(), 7))
        elapsed = dt.now() - self.log[-1]
        return {
            "elapsed": str(
                elapsed - timedelta(microseconds=elapsed.microseconds)
            ),
            "today": str(recent_counts[0]),
            "last 7 day average": str(
                round(sum(recent_counts[:7]) / len(recent_counts[:7]), 3)
            ),
        }


app = Flask(__name__)
counts = Counts()


@app.route("/")
def index() -> str:
    if request.args:
        resp = ", ".join(f"{k} is {v}" for k, v in request.args.items())
        return f"you said {resp}. good for you!"
    return render_template("index.html")


@app.route("/counter", methods=["GET", "POST"])
def counter() -> str:
    if request.method == "POST":
        counts.click()
    return render_template(
        "main.html", stats=Markup(json2html.convert(counts.asdict()))
    )


@app.route("/counter/api")
def api() -> str:
    return json.dumps(counts.asdict())


if __name__ == "__main__":
    app.run()

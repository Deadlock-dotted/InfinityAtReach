from Models.GlobalConstants import Create_New_Policy, Policy_Suggestion, Basic_Insurance_Details
from chatbot import chatbot
from flask import Flask, render_template, request, redirect, url_for

import pypyodbc

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    usertext = request.args.get('msg')
    if usertext == Create_New_Policy:
        return redirect(url_for('database'))
    if usertext == Policy_Suggestion:
        return redirect(url_for('getuserinformation'))
    if usertext == Basic_Insurance_Details:
        return redirect(url_for('needtodo'))
    return str(chatbot.get_response(usertext))


@app.route("/database")
def database():
    connection = pypyodbc.connect('Driver={SQL Server};Server=REM-HMB0GG3;Database=DEMO;')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM demotable")
    print(cursor)
    print(cursor.rowcount)

    for row in cursor:
        print(row)

    return str(row)


@app.route("database")
def getuserinformation():
    return str('hi')


if __name__ == "__main__":
    app.run(debug=True)

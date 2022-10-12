import io

from numpy.compat import basestring

from Models.GlobalConstants import Create_New_Policy, Policy_Suggestion, Basic_Insurance_Details, Descriptive_Statistics
from chatbot import chatbot
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from flask_cors import CORS, cross_origin
import pypyodbc

app = Flask(__name__)
# app.static_folder = 'static'

connection = pypyodbc.connect('Driver={SQL Server};Server=REM-HMB0GG3;Database=DEMO;')
CustomerStatus = 'House Owner'
Salaried = 1
CoverType = 'Structure & Content'
Tenure = 10
OutParam = ''
country = 'India'
data = pd.read_excel('C:/Users/suhil.roshan/Downloads/ExportExcel (1).xlsx')


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """

        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
@crossdomain(origin='*')
def get_bot_response():
    usertext = request.args.get('msg')
    if usertext == Create_New_Policy:
        return redirect(url_for('database'))
    if usertext == Policy_Suggestion:
        return redirect(url_for('FindSimilarCustomers', CustomerStatus=CustomerStatus,
                                Salaried=Salaried,
                                CoverType=CoverType,
                                Tenure=Tenure))
    if usertext == Descriptive_Statistics:
        return redirect(url_for('DescriptiveStatistics'))
    if usertext == Basic_Insurance_Details:
        return redirect(url_for('needtodo'))
    if usertext == Basic_Insurance_Details:
        return redirect(url_for('needtodo'))
    return str(chatbot.get_response(usertext))


@app.route("/database")
def database():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM demotable")
    print(cursor)
    print(cursor.rowcount)

    for row in cursor:
        print(row)

    return str(row)


@app.route("/database")
def getuserinformation():
    return str('hi')


@app.route("/FindSimilarCustomers")
def FindSimilarCustomers():
    cursor = connection.cursor()
    storedProcedure = ("EXEC FindSimilarCustomersFromHistoryData "
                       "@CustomerStatus=?,"
                       "@Salaried=?,"
                       "@CoverType=?,"
                       "@Tenure=?,"
                       "@RecommendationStrength=?")
    params = (CustomerStatus, Salaried, CoverType, Tenure, OutParam)

    cursor.execute(storedProcedure, params)

    print(OutParam)

    for row in cursor:
        print(row)

    if len(row) > 0:
        return redirect(url_for('PolicyRating'))
    else:
        return str('Not a valid input')


@app.route("/PolicyRating")
def PolicyRating():
    cursor = connection.cursor()
    storedProcedure = ("EXEC PolicyRating "
                       "@CustomerStatus=?,"
                       "@Salaried=?,"
                       "@CoverType=?,"
                       "@Tenure=?")

    params = (CustomerStatus, Salaried, CoverType, Tenure)

    cursor.execute(storedProcedure, params)

    for row in cursor:
        print(row)

    if len(row) > 0:
        return row


@app.route("/HousePricePrediction")
def HousePricePrediction():
    return str('')


@app.route("/DescriptiveStatistics")
def DescriptiveStatistics():
    dataframe = pd.DataFrame(data)
    dataframe2 = dataframe[dataframe['Country'] == country]

    plt.figure(figsize=(10, 8))
    plt.xticks(rotation='vertical')

    visualisation = sns.barplot(x=dataframe2['City'], y=dataframe2['BeenCustomer'])

    # plt.show(), plt.savefig was not working, getting the typeerror
    # returning visualisation is 200 status but preview is not seen in UI

    # Converting to bytes -- Working perfectly
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return send_file(bytes_image, mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
    CORS(app)

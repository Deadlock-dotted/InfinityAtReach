import io
import json
from random import random

from numpy.compat import basestring

from Models import HomeInsuranceSuggestion
from Models.GlobalConstants import Create_New_Policy, Policy_Suggestion, Basic_Insurance_Details, Descriptive_Statistics
# from chatbot import chatbot
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from flask_cors import CORS, cross_origin
import pypyodbc

from Models.HomeInsuranceSuggestion import suggestion

app = Flask(__name__)
# app.static_folder = 'static'

connection = pypyodbc.connect('Driver={SQL Server};Server=REM-HMB0GG3;Database=DEMO;')
CustomerStatus = 'House Owner'
Salaried = 1
CoverType = 'Structure & Content'
Tenure = 10
OutParam = ''
country = 'India'
PremiumAmount = 500
Industry = 'IT'
Email = 'customer@gmail.com'
Phone = '7293423422'

Demographicaldata = pd.read_excel('C:/Users/suhil.roshan/Documents/Data_Hub/Demographical_Statistics_Data_Updated.xlsx')
Designationdata = pd.read_excel(
    'C:/Users/suhil.roshan/Documents/Data_Hub/Designation_Wise_Statistics_Data_Updated.xlsx')
CustomerRetentionStatusData = pd.read_excel(
    'C:/Users/suhil.roshan/Documents/Data_Hub/Customer_Retention_Status_Data.xlsx')


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


# @app.route("/get")
# @crossdomain(origin='*')
# def get_bot_response():
#     usertext = request.args.get('msg')
#     # botresponse = jsonify(chatbot.get_response(usertext))
#
#     # botresponse = json.dumps({'response': chatbot.get_response(usertext)})
#
#     botresponse = chatbot.get_response(usertext)
#     return str(botresponse)


@app.route("/SuggestBestPolicy")
@crossdomain(origin='*')
def SuggestBestPolicy():
    usertext = request.args.get('PremiumAmount')
    PremiumAmount = usertext[0:3]
    Tenure = usertext[6:8]
    CoverType = usertext[11:32]
    CustomerStatus = usertext[35:46]
    Salaried = 1 if usertext[49:52] == 'Yes' else 0
    country = usertext[55:60]
    Industry = usertext[63:65]

    cursor = connection.cursor()
    storedProcedure = ("EXEC SuggestPolicy "
                       "@Premium=?,"
                       "@CustomerStatus=?,"
                       "@Salaried=?,"
                       "@CoverType=?,"
                       "@Tenure=?,"
                       "@RecommendationStrength=?")
    params = (PremiumAmount, CustomerStatus, Salaried, CoverType, Tenure, OutParam)

    cursor.execute(storedProcedure, params)

    records = cursor.fetchall()

    cursor.close()

    return records


# Completed for both India and USA
@app.route("/DemoGraphicalStatistics")
@crossdomain(origin='*')
def DemoGraphicalStatistics():
    requestedCounty = request.args.get('country')
    dataframe = pd.DataFrame(Demographicaldata)
    dataframe2 = dataframe[dataframe['Country'] == requestedCounty]

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


# Completed for Designation IT alone
@app.route("/Designationstatistics")
@crossdomain(origin='*')
def Designationstatistics():
    requestedIndustry = request.args.get('industry')
    dataframe = pd.DataFrame(Designationdata)
    dataframe2 = dataframe[dataframe['Industry'] == requestedIndustry]

    plt.figure(figsize=(10, 16))
    plt.xticks(rotation='vertical')

    visualisation = sns.barplot(x=dataframe2['Designation'], y=dataframe2['BeenCustomer'])

    # Converting to bytes -- Working perfectly
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return send_file(bytes_image, mimetype='image/png')


@app.route("/GenderWiseStatistics")
@crossdomain(origin='*')
def GenderWiseStatistics():
    dataframe = pd.DataFrame(Designationdata)
    dataframe2 = dataframe[(dataframe['Industry'] == Industry) & (dataframe['Country'] == country)]

    plt.figure(figsize=(10, 8))
    plt.xticks(rotation='vertical')

    visualisation = sns.countplot(x=dataframe2['Gender'])

    # Converting to bytes -- Working perfectly
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return send_file(bytes_image, mimetype='image/png')


@app.route("/SalariedWiseStatistics")
@crossdomain(origin='*')
def SalariedWiseStatistics():
    dataframe = pd.DataFrame(Designationdata)
    dataframe2 = dataframe[(dataframe['Industry'] == Industry) & (dataframe['Country'] == country)]

    plt.figure(figsize=(10, 8))
    plt.xticks(rotation='vertical')

    visualisation = sns.countplot(x=dataframe2['Salaried'])

    # Converting to bytes -- Working perfectly
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return send_file(bytes_image, mimetype='image/png')


@app.route("/CustomerRetentionStatus")
@crossdomain(origin='*')
def CustomerRetentionStatus():
    plt.figure(figsize=(10, 8))
    plt.xticks(rotation='vertical')

    visualisation = sns.countplot(x=CustomerRetentionStatusData['Been Customer'])

    # Converting to bytes -- Working perfectly
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return send_file(bytes_image, mimetype='image/png')


@app.route("/RegisterCustomer")
@crossdomain(origin='*')
def RegisterCustomer():
    cursor = connection.cursor()
    storedProcedure = ("EXEC InsertRegisteredUser "
                       "@Name=?,"
                       "@Email=?,"
                       "@PhoneNumber=?")
    userName = request.args.get('name')
    params = (userName, Email, Phone)

    cursor.execute(storedProcedure, params)

    randomnumber = np.random.randint(200, 587)

    return str(randomnumber)


if __name__ == "__main__":
    app.run(debug=True)
    CORS(app)

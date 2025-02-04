from flask import Flask , request , jsonify , render_template
import pickle
import pandas as pd
import numpy as np


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/predict',methods=['Get','Post'])
def predict():
    #if request.method == 'GET':
        #return "I will make the predictions"
    #else:
        #return "Coming Soon"
    try:
        json_data = request.get_json()
        df = pd.DataFrame(json_data)
        cols=df.columns
        
           
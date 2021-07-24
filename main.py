from flask import Flask, render_template

import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    fields_df = pd.read_csv("testing/data/fields.csv")
    #fields    = fields_df.to_json()
    fields    = fields_df.to_json(orient="values")
    #fields    = fields_df.to_json(orient="columns")
    #fields    = fields_df.to_json(orient="index")
    #fields    = fields_df.to_json(orient="table")
    
    return render_template("index.html", fields=fields)

if __name__ == "__main__":
    app.run(debug=True)

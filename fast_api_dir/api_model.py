from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import json
from fastapi.encoders import jsonable_encoder


app = FastAPI()

# Load your pre-trained machine learning model


# Define the input data schema using Pydantic
class InputData(BaseModel):
    # Define your input data fields here, adjust accordingly to your model requirements
    car_ID: int
    CarName: str
    fueltype: str
    carlength: float
    carwidth: float
    carheight: float
    enginesize: int
    peakrpm: int


# Define the prediction route
@app.post("/predict/")
def predict(data: InputData):
    try:
        print(jsonable_encoder(data))

        df = pd.DataFrame([jsonable_encoder(data)])

        print(df)

        model = joblib.load("/home/model/Regression_model.pkl")

        print('SUCCESS LOAD MODEL')
        
        
        print('Preprocessing Data')

        carname_temp = df['CarName']

        df = df.drop(columns=['CarName','car_ID'])
        df['fueltype'] = [1 if x=='gas' else 0 for x in df['fueltype']]

        # prediction_list = model.predict_proba(X).tolist()
        # prediction = prediction_list[0][0]
        
        print('Predicting data...')
        result = model.predict(df)
        df['price_prediction'] = result[0]
        df['CarName'] = carname_temp

        print("Prediction success", result[0])

        # Return the prediction as a JSON response
        return {"prediction" : df.to_dict('list')}

    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        raise e


if __name__ == "__main__":
    # To run the API locally for testing

    uvicorn.run(app, host="0.0.0.0", port=8000)

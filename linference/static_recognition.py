import joblib
import numpy as np
from config import STATIC_MODEL,SCALER

model=joblib.load(STATIC_MODEL)
scaler=joblib.load(SCALER)

def predict_static(features):

    X=features.reshape(1,-1)

    X=scaler.transform(X)

    pred=model.predict(X)[0]

    prob=max(model.predict_proba(X)[0])

    return pred,prob
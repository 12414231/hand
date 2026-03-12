import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

X=np.load("dataset/static_X.npy")
y=np.load("dataset/static_y.npy")

scaler=StandardScaler()

X=scaler.fit_transform(X)

model=RandomForestClassifier(n_estimators=200)

model.fit(X,y)

joblib.dump(model,"models/static_model.pkl")
joblib.dump(scaler,"models/scaler.pkl")
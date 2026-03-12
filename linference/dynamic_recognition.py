import numpy as np
from tensorflow.keras.models import load_model
from config import LSTM_MODEL

model=load_model(LSTM_MODEL)

def predict_dynamic(seq):

    seq=seq.reshape(1,seq.shape[0],seq.shape[1])

    pred=model.predict(seq)

    label=np.argmax(pred)

    return label
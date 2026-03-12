import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense

X=np.load("dataset/dynamic_X.npy")
y=np.load("dataset/dynamic_y.npy")

model=Sequential()

model.add(LSTM(64,input_shape=(30,2)))

model.add(Dense(32,activation="relu"))

model.add(Dense(len(set(y)),activation="softmax"))

model.compile(
optimizer="adam",
loss="sparse_categorical_crossentropy",
metrics=["accuracy"]
)

model.fit(X,y,epochs=30)

model.save("models/lstm_model.h5")
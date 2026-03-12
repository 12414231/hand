import numpy as np

def extract_landmarks(hand):

    features=[]

    for lm in hand.landmark:

        features.append(lm.x)
        features.append(lm.y)
        features.append(lm.z)

    return np.array(features)
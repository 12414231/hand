import matplotlib.pyplot as plt

def plot_probs(labels,probs):

    plt.clf()

    plt.bar(labels,probs)

    plt.ylim(0,1)

    plt.pause(0.01)
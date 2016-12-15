from gpfit.fit import fit
from gpfit.evaluate_fit import evaluate_fit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fit_setup(name):
    rpmmax = 5800
    powermax = 98.56
    fuelburnmin = 7.0

    df = pd.read_csv("%svsrpm.csv" % name.lower())

    u = df["RPM"]/5800
    if name == "Power":
        w = df[name]/powermax
    elif name == "FuelBurn":
        w = df[name]/fuelburnmin
    x = np.log(u)
    y = np.log(w)

    return x, y

def plot_fit(name, xdata, ydata, yfit):

    RPM = np.exp(xdata)*5800
    if name == "Power":
        yd = np.exp(ydata)*98.56
        yf = np.exp(yfit)*98.56
        units = "hp"
    elif name == "FuelBurn":
        yd = np.exp(ydata)*7.0
        yf = np.exp(yfit)*7.0
        units = "L/hr"

    fig, ax = plt.subplots()
    ax.plot(RPM[::10], yd[::10], "o", mfc="none")
    ax.plot(RPM, yf)
    ax.grid()
    ax.set_ylabel("%s [%s]" % (name, units))
    ax.set_xlabel("RPM")

    return fig, ax

if __name__ == "__main__":
    X, Y = fit_setup("Power")
    cn, rm = fit(X, Y, 1, "MA")

    yfit = evaluate_fit(cn, X, "MA")
    fig, ax = plot_fit("Power", X, Y, yfit)
    fig.savefig("powervsrpmfit.pdf")

    X, Y = fit_setup("FuelBurn")
    cn, rm = fit(X, Y, 1, "SMA")

    yfit = evaluate_fit(cn, X, "SMA")
    fig, ax = plot_fit("FuelBurn", X, Y, yfit)
    fig.savefig("fuelburnvsrpmfit.pdf")

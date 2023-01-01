import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import analysis

plot_pdf = False

path_wd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
path_files = os.path.join(path_wd, 'records/hourly/')
files_raw = os.listdir(path_files)

delays = analysis.DelayData()
delays.read_data(path_files, files_raw)
delays.add_features()

delays.get_data()


def plot_timeSeries():
    fig = plt.figure()
    for i in range(delays.n):
        data_station = data[i]
        colors = delays.findColor(subset_index=i)

        ax = fig.add_subplot(2, 1, i + 1)
        ax.plot(data_station["time_plan"], np.zeros(len(data_station)), c="black", linewidth=0.5)
        ax.scatter(data_station["time_plan"], data_station["delay"], alpha=1, c=colors, s=0.1)
        if i == 0:
            ax.set_xticklabels(())
        # if i==1:
        ax.margins(x=0)
        plt.xticks(fontsize=10, rotation=45)
    fig.tight_layout()

    if plot_pdf:
        save_file = "plots/time_series_s" + delays.stations[i][0] + "_sDir" + delays.stations[i][1] + ".png"
        print("saving", save_file)
        fig.savefig(save_file, bbox_inches='tight')


def plot_histogram():
    fig = plt.figure()
    for i in range(delays.n):
        data_station = data[i]
        ax = fig.add_subplot(2, 1, i + 1)
        ax.hist(data_station["delay"], bins=20)
    plt.show()


def plot_delayVsHour(i=0, filter_mode=None):
    # fig = plt.figure()

    data_station = delays.get_data(subset_index=i)  # data[i]
    hours = delays.get_hours(i)  # np.array([j.hour for j in data_station["time_plan"]])

    boxes = [(data_station[hours == h]["delay"]) for h in np.arange(24)]
    plt.plot(range(24), np.zeros(24), c="grey", linewidth=0.5)
    # ax.scatter(hours, data_station["delay"], alpha=0.1)
    plt.boxplot(boxes, flierprops={'marker': '.', 'markersize': 5, 'alpha': 0.1, 'fillstyle': "full"})
    plt.text(1, 40, "n=" + str(len(data_station)))
    plt.grid(axis="y", color="lightgrey")
    plt.xlabel("Hour")
    plt.ylabel("Delay")
    ax = plt.gca()
    ax.set_ylim([-5, 15])
    ax.set_xlim([0.5, 24.5])

    plt.show()


def plot_eventsPerHour(i=0):
    fig = plt.figure()
    hours = delays.get_hours(subset_index=i)
    unique, counts = np.unique(hours, return_counts=True)
    plt.plot(np.append(unique, 24), np.append(counts, counts[0]), label=delays.get_name(subset_index=i))
    plt.legend()
    ax = plt.gca()
    plt.xlabel("Hour")
    plt.ylabel("# Events")
    ax.set_ylim([0, max(counts) * 1.1])
    ax.set_xlim([0, 24])


delays.set_filter(("ICE", "IC", "EC"))
#delays.set_filter(["MB"])

i = 0

# plot_timeSeries()
# plot_histogram()
plot_delayVsHour(i)  # fix error in this method! after changing analysis data handler...
plot_eventsPerHour(i)  # test this method!
plt.show()

# run_glm(i=0)
# def run_glm(i=0): #  ---------------------- create + debug function
# generalized linear model

fig = plt.figure()
from sklearn.linear_model import LinearRegression

glm = LinearRegression()
y = np.array(delays.get_data(i)["delay"]).reshape(-1, 1)
x = np.array(delays.get_hours(i)).reshape(-1, 1)
fit = glm.fit(y, x)
print("y =", fit.intercept_[0], "+", fit.coef_[0][0], "x")
plt.plot(x, y, marker="o", linestyle="")
x_plot = np.arange(0,24)
y_plot = fit.intercept_[0] + x_plot * fit.coef_[0][0]
plt.plot(x_plot, y_plot)
#plt.show()

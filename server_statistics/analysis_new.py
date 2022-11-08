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

data = delays.data


def plot_timeSeries():
    fig = plt.figure()
    for i in range(delays.n):
        data_station = data[i]
        colors = delays.findColor(subset_index= i)

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


def plot_delayVsHour():
    fig = plt.figure()
    for i in range(delays.n):
        data_station = data[i]
        hours = delays.get_hours(i)  # np.array([j.hour for j in data_station["time_plan"]])
        boxes = [(data_station[hours == h]["delay"]) for h in np.arange(24)]

        plt.subplot(2, 1, i + 1)
        plt.plot(range(24), np.zeros(24), c="black", linewidth=0.5)
        # ax.scatter(hours, data_station["delay"], alpha=0.1)
        plt.boxplot(boxes, flierprops={'marker': '.', 'markersize': 5, 'alpha': 0.5, 'fillstyle': "full"})
        plt.text(1, 40, "n=" + str(len(data_station)))
        plt.grid(axis="y", color="lightgrey")
        ax = plt.gca()
        ax.set_ylim([-5, 40])
        ax.set_xlim([0.5, 24.5])

    plt.show()


def plot_eventsPerHour():
    fig = plt.figure()
    for i in range(delays.n):
        data_station = data[i]
        # hours = stats.get_hours(i) #np.array([j.hour for j in data_station["time_plan"]])
        hours = data[i]["hour"]
        unique, counts = np.unique(hours, return_counts=True)
        hour_counts = data_station.value_counts(subset=["date", "hour"])

        # x and y are working, but sorting algo not.
        x = [n[0] for n in hour_counts.keys()]
        y = [n[1] for n in hour_counts.keys()]
        # order_x = np.argsort(hour_counts)
        x
        y

        plt.plot(x, y)
        plt.show()

        # print(counts)
        # continue here!!!
        date_unique, date_counts = np.unique(data[i]["date"], return_counts=True)
        plt.plot(date_unique, date_counts)
        plt.plot(unique, counts)
        ax = plt.gca()
        # ax.set_ylim([-5, 40])
        ax.set_xlim([0, 24])


#plot_timeSeries()
#plot_histogram()
plot_delayVsHour() # fix error in this method! after changing analysis data handler...
#plot_eventsPerHour() # test this method!

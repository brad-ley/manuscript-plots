from pathlib import Path as P
from pathlib import PurePath as PP

import PIL
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('science')

"""
filename need to be full path to file:
-- on Mac you can get this by right-clicking and then
holding option and selecting 'Copy as Pathname'
-- on Windows you can get this by holding shift before rightclicking and then
selecting 'Copy as path'
this code will assume your data is a .txt, .dat, or .csv file with the x-axis in the first column and all y-axis data in columns 2, 3, etc.
"""
FILENAME = 'C:/full/path/to/file/goes/here.dat' 
FILENAME = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/25/sample 1 (unenriched)/absorption_LightOn_sample2022125107_exp.txt' 
"""
setting axis labels, etc
"""
# legend_names = ['line 1', 'line 2'] # add as many legend names as you want to be plotted on same x axis
legend_names = ['line 1'] # add as many legend names as you want to be plotted on same x axis
# colors = ['red','black'] # as many color names as legend names
colors = ['red'] # as many color names as legend names
# styles = [':', "--"] # same number here
styles = [':'] # same number here
x_Label = 'sample x label' # x axis label
y_Label = 'sample y label' # y axis label
x_tickLabels = True # set to false to remove x axis tick labels
x_ticks = True # make False to get rid of x axis tick labels (good for arbitrary unit data)
y_tickLabels = True # set to false to remove y axis tick labels
y_ticks = True # make False to get rid of y axis tick labels (good for arbitrary unit data)
legend = True # make False if you don't want a legend to show up
savename_ext = 'sample save name' # how to name file that will be saved

def main(f):
    fig, ax = plt.subplots()
    try:
        data = np.loadtxt(f, skiprows=0)
    except:
        try:
            data = np.loadtxt(f, delimiter=', ', skiprows=0)
        except:
            data = np.loadtxt(f, delimiter='\t', skiprows=0)
    for i, n in enumerate(legend_names):
        plt.plot(data[:, 0], data[:, 1 + i], label=n, color=colors[i], linestyle=styles[i], lw=1.5)
    plt.xlabel(x_Label)
    plt.ylabel(y_Label)
    if not x_ticks:
        ax.set_xticks([])
    if not x_tickLabels:
        ax.set_xticklabels([])
    if not y_ticks:
        ax.set_yticks([])
    if not y_tickLabels:
        ax.set_yticklabels([])

    if legend:
        plt.legend()

    plt.savefig(P(f).parent.joinpath(P(f).stem + f"_{savename_ext}.tif"),dpi=300)


if __name__ == "__main__":
    main(FILENAME)
    plt.show()

from pathlib import Path as P
from pathlib import PurePath as PP

import PIL
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'
plt.style.use('science')

"""
filename need to be full path to folder:
-- on Mac you can get this by right-clicking and then
holding option and selecting 'Copy as Pathname'
-- on Windows you can get this by holding shift before rightclicking and then
selecting 'Copy as path'
this code will assume your data is a .txt, .dat, or .csv file with the x-axis in the first column and all y-axis data in columns 2, 3, etc.
"""
"""
CHANGE STUFF BELOW
"""
FOLDER = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/compare single double' 
# legend_names = ['line 1', 'line 2'] # add as many legend names as you want to be plotted on same x axis
legend_names = ['line 1'] # add as many legend names as you want to be plotted on same x axis
# colors = ['red','black'] # as many color names as legend names
colors = ['red'] # as many color names as legend names
# styles = [':', "--"] # same number here
# for light on I use color '#00A7CA' and style '--'
styles = [':'] # same number here
x_Label = 'sample x label' # x axis label
y_Label = 'sample y label' # y axis label
x_tickLabels = True # set to false to remove x axis tick labels
x_ticks = True # make False to get rid of x axis tick labels (good for arbitrary unit data)
y_tickLabels = True # set to false to remove y axis tick labels
y_ticks = True # make False to get rid of y axis tick labels (good for arbitrary unit data)
legend = True # make False if you don't want a legend to show up
savename = 'sample save name' # how to name file that will be saved
skiprows = 0
delimiter = ','
lower_limit = 0 # mT
upper_limit = 50 # mT
"""
CHANGE STUFF ABOVE
"""

def main(folder):
    fig, ax = plt.subplots()
    lw = 1.25

    if P(folder).is_file():
        folder = P(folder).parent
    data_suffixes = ['.txt', '.dat', '.asc', '.csv']
    files = [ii for ii in P(folder).iterdir() if ii.suffix in data_suffixes]
    idx = 0

    for j, f in enumerate(files):
        data = np.loadtxt(f, skiprows=skiprows, delimiter=delimiter)
        data = data[np.logical_and(data[:, 0] >= lower_limit, data[:, 0] < upper_limit)]
        cols = np.shape(data)[1]


        try:
            print(f"Plot number {j + 1} is {f.stem}, label={legend_names[idx]}, color={colors[idx]}, style={styles[idx]}")
        except:
            print(f"Plot number {j + 1} is {f.stem}, styles may be undefined")

        for i in range(1, cols):
            try:
                plt.plot(data[:, 0], data[:, i], label=legend_names[idx], color=colors[idx], linestyle=styles[idx], lw=lw)
            except IndexError:
                plt.plot(data[:, 0], data[:, i], lw=lw, label='no label')
            idx += 1

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

    plt.savefig(P(FOLDER).joinpath(f"{savename}.tif"),dpi=300)
    plt.savefig(P(FOLDER).joinpath(f"{savename}.png"),dpi=300)


if __name__ == "__main__":
    main(FOLDER)
    plt.show()

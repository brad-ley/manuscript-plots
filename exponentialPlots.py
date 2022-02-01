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
FILENAME = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/25/sample 1 (unenriched)/absorption_LightOn_sample2022125107_exp.txt' 
"""
setting axis labels, etc
"""
color = 'red' # as many color names as legend names
style = ':' # same number here
x_Label = 'sample x label' # x axis label
y_Label = 'sample y label' # y axis label
x_tickLabels = True # set to false to remove x axis tick labels
x_ticks = True # make False to get rid of x axis tick labels (good for arbitrary unit data)
y_tickLabels = True # set to false to remove y axis tick labels
y_ticks = True # make False to get rid of y axis tick labels (good for arbitrary unit data)
legend = True # make False if you don't want a legend to show up
savename_ext = 'sample save name' # how to name file that will be saved
on = 40 # how long light was on in seconds
off = 300 # how long light was off (doesn't matter unless averaging)


def exp(x, c, A, tau):
    return c + A*np.exp(-x/tau)

def main(f):
    fig, ax = plt.subplots()
    if P(f).suffix == '.csv'
        data = np.loadtxt(f, skiprows=1, delimiter=',')
    elif P(f).suffix = '.asc':
        data = np.loadtxt(f, skiprows=4, delimiter='\t')
    else:
        data = np.loadtxt(f)

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

    popt, pcov = curve_fit(
            exp, data[:,0], data[:,1], maxfev=10000000)
    # plt.plot(np.linspace(t[abovelas], t[smallen]), exponential(np.linspace(
    #     t[abovelas], t[smallen]), *popt), color="red", linestyle="--", label=r"Fit: $\tau_1$=" + f"{popt[2]:.2f}" + r" s$^{-1}$", lw=lw)

    plt.legend()
    rang = np.max(y) - np.min(y)
    plt.annotate('Laser\npulse', (on, np.min(y) - rang/6),
                 color='#0046FF', horizontalalignment='left')
    plt.ylim(np.min(y) - rang / 4, np.max(y) + rang / 4)
    plt.axvspan(0, on, facecolor='#0046FF')

    plt.ylabel('Signal (arb. u)')
    plt.xlabel('Time (s)')

    plt.savefig(P(FILENAME).parent.joinpath(P(f)+"_{savename_ext}.tif"), dpi=300)
    plt.savefig(P(FILENAME).parent.joinpath(P(f)+"_{savename_ext}.pdf"), dpi=300)



if __name__ == "__main__":
    main(FILENAME)
    plt.show()

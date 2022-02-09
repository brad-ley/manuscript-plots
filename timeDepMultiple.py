import ast
import os
import PIL
import re
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import PIL

from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

plt.style.use(['science'])
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'

"""
CHANGE STUFF BELOW (copy full path to folder by holding 'option' on Mac)
"""
FOLDER = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/compare single double'
turn_on = 0
turn_off = 5
total_experiment_time = 180 # only needs to be specific for averaging
colors = [['slategray', 'orange'], ['black', 'red']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
styles = [['-', '-.'], ['-', '--']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
savename = 'compared'
source = 'Light' # use 'Light' in Shiny's lab and 'Laser' in Brad's
delimiter = ', '
skiprows = 0
"""
CHANGE STUFF ABOVE
"""


def exp(x, c, A, tau):
    return c + A*np.exp(-x / tau)


def show(folder):
    if P(folder).is_file():
        folder = P(folder).parent
    data_suffixes = ['.txt', '.dat', '.asc', '.csv']
    files = [ii for ii in P(folder).iterdir() if ii.suffix in data_suffixes]
    fig, ax = plt.subplots()

    smoothlen = 2000
    scale = 0
    files.sort()
    try:
        for i, f in enumerate(files):
            data = np.loadtxt(f, delimiter=delimiter, skiprows=skiprows)
            data = data[np.logical_not(np.isnan(data[:, 1]))]
            expts = np.empty((smoothlen, int(np.round(data[-1, 0] / total_experiment_time))))
            loops = 0
            """
            MIGHT NEED TO CHANGE
            """
            p0 = [0, -60, 80]
            """
            MIGHT NEED TO CHANGE
            """
            while loops < int(np.round(data[-1, 0] / total_experiment_time)):
                loopdat = data[np.logical_and(data[:,0] > loops * total_experiment_time, data[:, 0] < (loops + 1) * total_experiment_time)]
                fx = interp1d(loopdat[:, 0], loopdat[:, 1]) 
                smootht = np.linspace(loopdat[0,0],loopdat[-1,0],smoothlen)
                if loops == 0:
                    plott = np.copy(smootht)
                expts[:,loops] = fx(smootht)
                loops += 1
            dat = np.mean(expts, axis=1)
            dat -= np.mean(dat[-len(dat)//100:])
            popt, pcov = curve_fit(exp, plott[plott > turn_off], dat[plott > turn_off], maxfev=100000000, p0=p0)
            perr = np.sqrt(np.diag(pcov))
            sd2 = 2*perr[2]
            if sd2 == np.inf:
                sd2 = 0
            ex = exp(plott[plott > turn_off],*popt) 
            lw = 1.25

            if popt[1] > scale:
                scale = popt[1]
            try:
                ax.plot(plott, (dat - np.mean(dat[-len(dat)//100:]))/scale, label=f.stem.replace("_"," "),
                        lw=lw, color=colors[i][0], linestyle=styles[i][0])
                ax.plot(plott[plott > turn_off], (ex - np.mean(ex[-len(ex)//100:]))/scale,
                        label=rf"$\tau={popt[2]:.1f}\pm{sd2:.1f}$ s", lw=lw, color=colors[i][1], linestyle=styles[i][1])
            except IndexError:
                ax.plot(plott, (dat - np.mean(dat[-len(dat)//100:]))/scale, label=f.stem.replace("_"," "),
                        lw=lw)
                ax.plot(plott[plott > turn_off], (ex - np.mean(ex[-len(ex)//100:]))/scale,
                        label=rf"$\tau={popt[2]:.1f}\pm{sd2:.1f}$ s", lw=lw)

        plt.axvspan(turn_on, turn_off, color='#00A7CA', label=f"{source} on")

        # handles, labels = plt.gca().get_legend_handles_labels()
        # labels.insert(0, labels.pop())
        # handles.insert(0, handles.pop())
        # plt.legend(handles, labels)
        plt.legend()
        ax.set_ylabel('Intensity (arb. u)')
        ax.set_xlabel('Time (s)')
        plt.savefig(P(folder).joinpath(f'{savename}.tif'),dpi=300)
        plt.savefig(P(folder).joinpath(f'{savename}.png'),dpi=300)
    except ValueError:
        print("You did not set the correct delimiter or skiprows.")


if __name__ == "__main__":
    show(FOLDER)
    plt.show()

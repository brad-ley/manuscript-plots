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
FOLDER = '/Users/Brad/Downloads/test'
MUTANT = 'DL T406C-E537C' # put the mutant here, it will be placed on the figure
TEMP = 294 # put as number
turn_on = -40
turn_off = 0
total_experiment_time = 614 # only needs to be specific for averaging
colors = [['purple', 'red'], ['black', 'red'], ['red', 'red']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
styles = [[':', '-.'], ['-.', '-.'], ['-','-.']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
savename = 'compared'
source = 'Light' # use 'Light' in Shiny's lab and 'Laser' in Brad's
delimiter = ','
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
    files = [ii for ii in P(folder).iterdir() if ii.suffix in data_suffixes if ii.name != 'fitdata.txt']
    fig, ax = plt.subplots()

    smoothlen = 2000
    scale = 0
    files.sort()
    files.insert(0, files.pop())
    files.insert(1, files.pop())
    lines = {}

    for i, f in enumerate(files):
        data = np.loadtxt(f, delimiter=delimiter, skiprows=skiprows)
        data = data[np.logical_not(np.isnan(data[:, 1]))]
        expts = np.empty((smoothlen, int(np.round(data[-1, 0] / total_experiment_time))))
        loops = 0
        """
        MIGHT NEED TO CHANGE
        """
        p0 = [0, 0, 80]
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
        p0[1] = dat[np.argmax(np.abs(dat))]
        popt, pcov = curve_fit(exp, plott[plott > turn_off] - turn_off, dat[plott > turn_off], maxfev=100000000, p0=p0)
        perr = np.sqrt(np.diag(pcov))
        sd2 = 2*perr[2]
        try:
            if sd2 == np.inf or sd2 == np.nan:
                sd2 = 0
            ex = exp(plott[plott > turn_off] - turn_off,*popt) 
            lw = 1.25
            
            if np.abs(popt[1]) > scale:
                scale = popt[1]

            try:
                lines[f.stem + ' data'] = dat 
                lines[f.stem + ' tau'] = popt[2]
                lines[f.stem + ' 95'] = sd2
                # ax.plot(plott, dat/scale, label=f.stem.replace("_"," "),
                #         lw=lw, color=colors[i][0], linestyle=styles[i][0])
                # ax.plot(plott[plott > turn_off], ex/scale,
                #         label=rf"$\tau={popt[2]:.1f}\pm$" + f"{sd2:.1f} s", lw=lw, color=colors[i][1], linestyle=styles[i][1])
                # ax.plot(plott[plott > turn_off], ex/scale,
                #         lw=lw, color=colors[i][1], linestyle=styles[i][1])
            except IndexError:
                ax.plot(plott, dat/scale, label=f.stem.replace("_"," "),
                        lw=lw)
                ax.plot(plott[plott > turn_off], ex/scale,
                        label=rf"$\tau={popt[2]:.1f}\pm$" + f"{sd2:.1f} s", lw=lw)
        except RuntimeError:
            print(f"{f} file did not work.")
    
    outstr = ""
    for i, f in enumerate(files):
        ax.plot(plott, lines[f.stem + ' data']/scale, label=f.stem.replace("_", " "), lw=lw, color=colors[i][0], linestyle=styles[i][0])
        outstr += f"{f.name} fit is {lines[f.stem + ' tau']:.3f} plus/minus {lines[f.stem + ' 95']:.3f} s\n"

    plt.axvspan(turn_on, turn_off, color='#00A7CA', label=f"{source} on")

    ax.text(0.45, 0.51, f'$T={TEMP}$ K\n{MUTANT}',
            horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    # handles, labels = plt.gca().get_legend_handles_labels()
    # labels.insert(0, labels.pop())
    # handles.insert(0, handles.pop())
    # plt.legend(handles, labels)
    plt.legend()
    ax.set_ylabel('cwEPR signal at $B_0$ (arb. u)')
    ax.set_xlabel('Time (s)')
    plt.savefig(P(folder).joinpath(f'{savename}.tif'),dpi=300)
    plt.savefig(P(folder).joinpath(f'{savename}.png'),dpi=300)
    P(folder).joinpath(f'fitdata.txt').write_text(outstr)


if __name__ == "__main__":
    show(FOLDER)
    plt.show()

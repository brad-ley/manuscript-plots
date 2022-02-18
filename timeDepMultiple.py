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
MUTANT = '' # put the mutant here, it will be placed on the figure
LEGEND_NAMES = ['$B_0^{(a)}$', 'test', 'testj2'] # legend name here if you want it to be fancy
TEMP = 294 # put as number
turn_on = 0
turn_off = 5
total_experiment_time = 180 # only needs to be specific for averaging
colors = [['black', 'red'], ['green', 'red'], ['blue', 'red']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
styles = [['-', '--'], ['-', '--'], ['-','--']] # make one entry for each line and it's fit [[line, fit], [line, fit]]
savename = 'compared'
source = 'Laser' # use 'Light' in Shiny's lab and 'Laser' in Brad's
delimiter = ', '
skiprows = 0
recovery = False # make True for UV-vis plots
show_fit = True
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
    files.insert(2, files.pop(1))
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

            # try:
            lines[f.stem + ' data'] = dat 
            lines[f.stem + ' tau'] = popt[2]
            lines[f.stem + ' 95'] = sd2
            lines[f.stem + ' fit'] = ex

            # except IndexError:
            #     ax.plot(plott, dat/scale, label=f.stem.replace("_"," "),
            #             lw=lw)
            #     ax.plot(plott[plott > turn_off], ex/scale,
            #             label=rf"$\tau={popt[2]:.1f}\pm$" + f"{sd2:.1f} s", lw=lw)
        except RuntimeError:
            print(f"{f} file did not work.")
    
    outstr = ""
    for i, f in enumerate(files):
        if recovery:
            d = 1 - lines[f.stem + ' data']/scale
            e = 1 - lines[f.stem + ' fit']/scale
        else:
            d = lines[f.stem + ' data']/scale
            e = lines[f.stem + ' fit']/scale
        if not LEGEND_NAMES:
            ax.plot(plott, d, label=f.stem.replace("_", " "), lw=lw, color=colors[i][0], linestyle=styles[i][0])
        else:
            ax.plot(plott, d, label=LEGEND_NAMES[i], lw=lw, color=colors[i][0], linestyle=styles[i][0])
        if show_fit:
            ax.plot(plott[plott > turn_off], e, lw=lw, color=colors[i][1], linestyle=styles[i][1])
        outstr += f"{f.name} fit is {lines[f.stem + ' tau']:.3f} plus/minus {lines[f.stem + ' 95']:.3f} s\n"

    plt.axvspan(turn_on, turn_off, color='#00A7CA', label=f"{source} on")
    
    if MUTANT:
        ax.text(0.45, 0.51, f'$T={TEMP}$ K\n{MUTANT}',
                horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    else:
        ax.text(0.45, 0.51, f'$T={TEMP}$ K',
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

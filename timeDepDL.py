import ast
import os
import re
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib import rc
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

plt.style.use(['science'])
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['xtick.major.width'] = 1
plt.rcParams['xtick.minor.size'] = 2
plt.rcParams['xtick.minor.width'] = 1
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 1
plt.rcParams['ytick.minor.size'] = 2
plt.rcParams['ytick.minor.width'] = 1

"""
CHANGE STUFF BELOW (copy full path to folder by holding 'option' on Mac)
"""
FOLDER = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/uv-vis/Q513A figure'
MUTANT = ''  # put the mutant here, it will be placed on the figure
# legend name here if you want it to be fancy
LEGEND_NAMES = []
TEMP = 294  # put as number
turn_on = -40
turn_off = 0
total_experiment_time = 2000  # only needs to be specific for averaging
# make one entry for each line and it's fit [[line, fit], [line, fit]]
colors = [['black', 'red'], ['lime', 'red'],
          ['green', 'red'], ['orange', 'red']]
# make one entry for each line and it's fit [[line, fit], [line, fit]]
styles = [['-', ':'], ['-', ':'], ['-', '--'], ['-', '--']]
savename = 'compared'
source = 'Light'  # use 'Light' in Shiny's lab and 'Laser' in Brad's
delimiter = ','
skiprows = 0
recovery = True  # make True for UV-vis plots
show_fit = True
"""
CHANGE STUFF ABOVE
"""


def exp(x, c, A, tau):
    return c + A * np.exp(-x / tau)


def show(folder):
    if P(folder).is_file():
        folder = P(folder).parent
    data_suffixes = ['.txt', '.dat', '.asc', '.csv']
    files = [ii for ii in P(folder).iterdir(
    ) if ii.suffix in data_suffixes if 'fitdata' not in ii.name]
    fig, ax = plt.subplots()

    smoothlen = 2000
    scale = 0
    offset = 0
    lines = {}

    for i, f in enumerate(files):
        data = np.loadtxt(f, delimiter=delimiter, skiprows=skiprows)
        data = data[np.logical_not(np.isnan(data[:, 1]))]
        loops = 0
        """
        MIGHT NEED TO CHANGE
        """
        p0 = [-1, 1, 300]
        """
        MIGHT NEED TO CHANGE
        """

        loopcap = int(np.round(data[-1, 0] / total_experiment_time))

        if loopcap == 0:
            loopcap += 1
        expts = np.empty((smoothlen, loopcap))

        while loops < loopcap:
            loopdat = data[np.logical_and(
                data[:, 0] > loops * total_experiment_time, data[:, 0] < (loops + 1) * total_experiment_time)]
            fx = interp1d(loopdat[:, 0], loopdat[:, 1])
            smootht = np.linspace(loopdat[0, 0], loopdat[-1, 0], smoothlen)

            if loops == 0:
                plott = np.copy(smootht)
            expts[:, loops] = fx(smootht)
            loops += 1

        dat = np.mean(expts, axis=1)
        dat -= np.mean(dat[-len(dat) // 100:])

        p0[1] = dat[np.argmax(np.abs(dat))]
        popt, pcov = curve_fit(
            exp, plott[plott > turn_off] - turn_off, dat[plott > turn_off], maxfev=100000000, p0=p0)
        perr = np.sqrt(np.diag(pcov))
        sd2 = 2 * perr[2]
        try:
            if sd2 == np.inf or sd2 == np.nan:
                sd2 = 0
            ex = exp(plott[plott > turn_off] - turn_off, *popt)
            lw = 2

            if np.abs(popt[1]) > scale:
                scale = popt[1]

            if np.abs(popt[0]) > offset:
                offset = popt[0]

            # try:
            lines[f.stem + ' data'] = dat
            lines[f.stem + ' tau'] = popt[2]
            lines[f.stem + ' 95'] = sd2
            lines[f.stem + ' fit'] = ex
            lines[f.stem + ' time'] = plott

            # except IndexError:
            #     ax.plot(plott, dat/scale, label=f.stem.replace("_"," "),
            #             lw=lw)
            #     ax.plot(plott[plott > turn_off], ex/scale,
            #             label=rf"$\tau={popt[2]:.1f}\pm$" + f"{sd2:.1f} s", lw=lw)
        except RuntimeError:
            print(f"{f} file did not work.")

    outstr = ""

    for i, f in enumerate(files):
        if not 'Q513A' in f.name:
            if recovery:
                d = 1 - (lines[f.stem + ' data'] / scale - offset)
                e = 1 - (lines[f.stem + ' fit'] / scale - offset)
            else:
                d = lines[f.stem + ' data'] / scale - offset
                e = lines[f.stem + ' fit'] / scale - offset
        
            if not LEGEND_NAMES:
                if 'Q513A' in f.stem:
                    label = 'Q513A DL'
                else:
                    label= 'DL'
                ax.plot(lines[f.stem + ' time'], d, lw=2, color=colors[i][0], linestyle=styles[i][0])
            else:
                ax.plot(lines[f.stem + ' time'], d,
                        lw=2, color=colors[i][0], linestyle=styles[i][0])

        outstr += f"{f.name} fit is {lines[f.stem + ' tau']:.3f} plus/minus {lines[f.stem + ' 95']:.3f} s\n"

    plt.axvspan(turn_on, turn_off, color='#00A7CA', label=f"{source} on")

    ax.set_ylabel('UV-Vis absorb. (a.u.)')
    ax.set_yticklabels([])
    ax.set_xlabel('Time (s)')
    ax.legend(loc=(0.475, 0.7), markerfirst=False, handletextpad=0.4, labelspacing=0.2)

    axin = ax.inset_axes([0.275, 0.175, 0.8, 0.45], transform=ax.transAxes)

    # if MUTANT:
    #     ax.text(0.65, 0.8, f'$T={TEMP}$ K\n{MUTANT}',
    #             horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    # else:
    #     axin.text(0.45, 0.8, f'$T={TEMP}$ K',
    #             horizontalalignment='left', verticalalignment='top', transform=axin.transAxes)
    ifolder = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/uv-vis/Q513A figure/inset'
    ifs = [ii for ii in P(ifolder).iterdir() if ii.suffix == '.txt']
    ifs.reverse()
    s = 0
    ics = ['#B212A3', 'lime']

    for f in ifs:
        idata = np.loadtxt(f, delimiter=',')

        idata[:, 1] = (idata[:, 1] - np.mean(idata[-len(idata) // 100:, 1]))

        if np.max(idata[:, 1]) > s:
            s = np.max(idata[:, 1])

    for i, f in enumerate(ifs):
        if not 'Q513A' in f.name:
            idata = np.loadtxt(f, delimiter=',')

            idata[:, 1] = (idata[:, 1] - np.mean(idata[-len(idata) // 100:, 1]))
            axin.plot(idata[:, 0], idata[:, 1] / s, color=ics[i], lw=lw)

    axin.axvspan(0, 5, color='#00A7CA', label='Laser on')
    axin.legend(loc=(0.3, 0.5), markerfirst=False, handletextpad=0.4, labelspacing=0.2)
    axin.set_ylabel('cwEPR', labelpad=-2)
    axin.set_yticklabels([])
    fig.tight_layout()
    fig.savefig(P(folder).joinpath(f'{savename}_DL.tif'), dpi=300)
    fig.savefig(P(folder).joinpath(f'{savename}_DL.png'), dpi=300)
    P(folder).joinpath(f'fitdata_DL.txt').write_text(outstr)


if __name__ == "__main__":
    show(FOLDER)
    plt.show()

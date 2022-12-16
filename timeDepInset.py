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
# FOLDER = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/data repository/angewandte/Q513A inset figure/uv-vis'
FOLDER = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/data repository/angewandte/Q513A inset figure/uv-vis/no normalize'
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
    ) if ii.suffix in data_suffixes if 'fitdata' not in ii.name and 'tau' not in ii.name]
    # n = 0.95
    fig, ax = plt.subplots()

    smoothlen = 2000
    scale = 0
    offset = 0
    lines = {}
    
    files.sort()
    files.reverse()
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
        # dat -= np.mean(dat[-len(dat) // 100:])

        p0[0] = dat[0]
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
            lines[f.stem + ' popt'] = popt
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

    outstr = "======UV-Vis======\n"

    for i, f in enumerate(files):
        popt = lines[f.stem + ' popt']
        if recovery:
            # d = 1 - (lines[f.stem + ' data'] / scale - offset)
            # e = 1 - (lines[f.stem + ' fit'] / scale - offset)

            # d = 1 - (lines[f.stem + ' data'] - offset)/scale
            # e = 1 - (lines[f.stem + ' fit'] - offset)/scale

            e = 1 * lines[f.stem + ' fit']
            e -= np.max(e)
            d = 1 * lines[f.stem + ' data']
            d -= np.max(d)
        else:
            d = (lines[f.stem + ' data'] - offset)/scale
            e = (lines[f.stem + ' fit'] - offset)/scale
   
        if not LEGEND_NAMES:
            if '513' in f.stem:
                label = 'Q513A DL'
                ax.plot(lines[f.stem + ' time'], d, label=label, lw=2, color='lime', linestyle=styles[i][0])
            else:
                label= 'DL'
                ax.plot(lines[f.stem + ' time'], d, label=label, lw=2, color='black', linestyle=styles[i][0])
                # ax.plot(lines[f.stem + ' time'], d, lw=2, color='black', linestyle=styles[i][0])
        else:
            ax.plot(lines[f.stem + ' time'], d, label=LEGEND_NAMES[i],
                    lw=2, color=colors[i][0], linestyle=styles[i][0])

        if show_fit:
            ax.plot(lines[f.stem + ' time'][lines[f.stem + ' time'] > turn_off],
                    e, lw=2, color=colors[i][1], linestyle=styles[i][1])
        outstr += f"{f.name} fit is {lines[f.stem + ' tau']:.3f} plus/minus {lines[f.stem + ' 95']:.3f} s\n"

    plt.axvspan(turn_on, turn_off, color='#00A7CA', label=f"{source} on")

    ax.set_ylabel('UV-Vis $\Delta_{abs}$')
    # ax.set_ylim(bottom=0)
    # ax.set_yticks([0, 1])
    ax.set_xlabel('Time (s)')
    ax.legend(loc=(0.425, 0.49), markerfirst=False,
              handlelength=1, handletextpad=0.4, labelspacing=0.2)
    # ax.legend(loc=(0.425, 0.7), markerfirst=False,
    #           handlelength=1, handletextpad=0.4, labelspacing=0.2)

    axin = ax.inset_axes([0.325, 0.125, 0.725, 0.4], transform=ax.transAxes)

    # if MUTANT:
    #     ax.text(0.65, 0.8, f'$T={TEMP}$ K\n{MUTANT}',
    #             horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    # else:
    #     axin.text(0.45, 0.8, f'$T={TEMP}$ K',
    #             horizontalalignment='left', verticalalignment='top', transform=axin.transAxes)
    ifolder = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/data repository/angewandte/Q513A inset figure/epr'
    # ifolder = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/TOC/epr'
    ifs = [ii for ii in P(ifolder).iterdir() if ii.suffix == '.txt' and 'tau' not in ii.stem]

    ifs.reverse()
    s = 0
    ics = ['black', 'lime']

    for f in ifs:
        idata = np.loadtxt(f, delimiter=',')

        idata[:, 1] = (idata[:, 1] - np.mean(idata[-len(idata) // 100:, 1]))

        if np.max(idata[:, 1]) > s:
            s = np.max(idata[:, 1])
    
    offset = 0
    scale = 0
    outstr += "======EPR======\n"
    for i, f in enumerate(ifs):
        idata = np.loadtxt(f, delimiter=',')
        # m = np.mean(idata[-len(idata) // 100:, 1])
        # s = np.max(idata[:, 1]) - m
        # d = idata[:, 1] / s 
        # d -= np.mean(d)
        d = idata[:, 1]
        t = idata[:, 0]
        in_off = 5
        in_t = np.linspace(in_off, np.max(t), 1000)

        """ 
        Don't have nice normalization yet so average the minimum and
        maximum fifty points, normalize both to the maximum and subtract
        the offset
        """
        dsort = np.sort(d[t > in_off])
        mx = np.mean(dsort[-50:])
        mn = np.mean(dsort[:50])

        d /= mx
    
        popt, pcov = curve_fit(
            exp, t[t > in_off] - in_off, d[t > in_off])

        d -= popt[0]
        perr = np.sqrt(np.diag(pcov))
        sd2 = 2 * perr[2]
        outstr += f"{f.name} fit is {popt[2]:.3f} plus/minus {sd2:.3f} s\n"
        # idata[:, 1] = (idata[:, 1] - )
        axin.plot(t, d, color=ics[i], lw=lw)
        if show_fit:
            axin.plot(in_t, (exp(in_t - in_off, *popt) - popt[0]), color='red', ls=':', lw=lw)

    # P(folder).joinpath('data_taus.txt').write_text(outstr)

    axin.axvspan(0, 5, color='#00A7CA', label='Laser on')
    axin.set_ylabel('cwEPR $\Delta$', labelpad=-2)
    axin.set_yticklabels([])
    # axin.set_ylim(top=1.25)
    axin.legend(markerfirst=False,
              handlelength=1, handletextpad=0.4, labelspacing=0.2)
    fig.tight_layout()
    fig.savefig(P(folder).joinpath(f'{savename}.tif'), dpi=300)
    fig.savefig(P(folder).joinpath(f'{savename}.png'), dpi=300)
    P(folder).joinpath(f'fitdata.txt').write_text(outstr)


if __name__ == "__main__":
    show(FOLDER)
    plt.show()

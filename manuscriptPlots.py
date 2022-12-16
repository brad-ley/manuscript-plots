from pathlib import Path as P
from pathlib import PurePath as PP

import PIL
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

plt.style.use('science')
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
FOLDER = '/Volumes/GoogleDrive/My Drive/Research/protein-dynamics/manuscripts/methods 2022/data/data repository/angewandte/UV-Vis/Mutants/UV VIS 537 406 light dark' 
MUTANT = 'T406C-E537C\nDL'
TEMP = 294
FIELDS = [447] # leave this list empty if you don't want field markers
legend_names = ['Light off', 'Light on'] # add as many legend names as you want to be plotted on same x axis
colors = ['black', '#00A7CA'] # as many color names as legend names
# for light on I use color '#00A7CA' and style '--'
styles = ['-','--'] # same number here
x_Label = 'Field (G)' # x axis label
# y_Label = 'cwEPR signal (arb. u)' # y axis label
y_Label = 'UV-Vis absorbance' # y axis label
x_tickLabels = True # set to false to remove x axis tick labels
x_ticks = True # make False to get rid of x axis tick labels (good for arbitrary unit data)
y_tickLabels = True # set to false to remove y axis tick labels
y_ticks = True # False will leave ticks but they won't be manual, they will be [-1, 0, 1]
legend = True # make False if you don't want a legend to show up
inset = False
savename = 'compare' # how to name file that will be saved
lw = 2 # linewidth in points
skiprows = 1
delimiter = ','
# lower_limit = 3445 # mT
# upper_limit = 3535 # mT
lower_limit = 325
upper_limit = 1000
Q_BAND = False
Qx = 0 # column for x axis data (python starts at 0)
Qy = 0 # column for y axis data (python starts at 0)
"""
CHANGE STUFF ABOVE
"""

def main(folder):
    fig, ax = plt.subplots()

    if inset:
        axin = ax.inset_axes([0.025, 0.65, 0.2, 0.325], transform=ax.transAxes)

    if P(folder).is_file():
        folder = P(folder).parent
    data_suffixes = ['.txt', '.dat', '.asc', '.csv']
    files = [ii for ii in P(folder).iterdir() if ii.suffix in data_suffixes]
    idx = 0
    
    if not y_ticks:
        scale = 0
        for j, f in enumerate(files):
            data = np.loadtxt(f, skiprows=skiprows, delimiter=delimiter)
            data = data[np.logical_and(data[:, 0] >= lower_limit, data[:, 0] < upper_limit)]
            if np.max(np.abs(data[:, 1])) > scale:
                scale = np.max(np.abs(data[:, 1]))
    else:
        scale = 1
    
    for j, f in enumerate(files):
        data = np.loadtxt(f, skiprows=skiprows, delimiter=delimiter)
        data = data[np.logical_and(data[:, 0] >= lower_limit, data[:, 0] < upper_limit)]
        cols = np.shape(data)[1]

        try:
            print(f"Plot number {j + 1} is {f.stem}, label={legend_names[idx]}, color={colors[idx]}, style={styles[idx]}")
        except:
            print(f"Plot number {j + 1} is {f.stem}, styles may be undefined")

        if inset:
            for i in range(1, cols):
                try:
                    axin.plot(data[:, 0], data[:, i]/scale, label=legend_names[idx], color=colors[idx], linestyle=styles[idx], lw=lw)
                except IndexError:
                    axin.plot(data[:, 0], data[:, i]/scale, lw=lw, label='no label')

        if not Q_BAND:
            for i in range(1, cols):
                try:
                    ax.plot(data[:, 0], data[:, i]/scale, label=legend_names[idx], color=colors[idx], linestyle=styles[idx], lw=lw)
                except IndexError:
                    ax.plot(data[:, 0], data[:, i]/scale, lw=lw, label='no label')
                idx += 1
        else:
            try:
                ax.plot(data[:, Qx], data[:, Qy]/scale, label=legend_names[idx], color=colors[idx], linestyle=styles[idx], lw=lw)
            except IndexError:
                ax.plot(data[:, Qx], data[:, Qy]/scale, lw=lw, label='no label')

    if inset:
        x1, x2, y1, y2 = 3474, 3478, -0.6, -0.4,
        axin.set_xlim(x1, x2)
        axin.set_ylim(y1, y2)
        axin.set_xticks([3475])
        axin.set_yticks([-0.4, -0.6])
        axin.set_xticklabels([])
        axin.set_yticklabels([])
        ax.indicate_inset_zoom(axin, edgecolor="k")
    # ax.indicate_inset_zoom(axin)

    if FIELDS:
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        alphas = np.linspace(0.25,0.75,len(FIELDS))
        FIELDS.sort()
        ticks = ax.get_ylim()
        n = 1.175
        fact = 0.99
        if np.min(ticks) < 0:
            ax.set_ylim(bottom=np.min(ticks)*n)
        else:
            ax.set_ylim(bottom=np.min(ticks)/n)
            fact = 1/fact
        t = ax.get_ylim()
        for i, f in enumerate(FIELDS):
            ax.axvline(x=f, c='gray',
                       # alpha=0.5, lw=lw, label='$B_0$') # , label=f'$B_0^{{({alphabet[i]})}}$')
                       alpha=0.5, lw=lw, label='$\lambda_{447}$') # , label=f'$B_0^{{({alphabet[i]})}}$')
            if inset:
                axin.axvline(x=f, c='gray',
                           alpha=0.5, lw=lw) # , label=f'$B_0^{{({alphabet[i]})}}$')
            # if alphabet[i] == 'a':
            #     ax.text(f, fact*np.min(t), f'$B_0^{{({alphabet[i]})}}$', horizontalalignment='right', verticalalignment='bottom')        
            # elif alphabet[i] == 'b':
            #     ax.text(f, fact*np.min(t), f'$B_0^{{({alphabet[i]})}}$', horizontalalignment='left', verticalalignment='bottom')        
            # else:
            #     ax.text(f, fact*np.min(t), f'$B_0^{{({alphabet[i]})}}$', horizontalalignment='center', verticalalignment='bottom')        

    ax.text(0.1, 0.825, f'$T=294$ K\n{MUTANT}',
            horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.set_xlabel(x_Label)
    ax.set_ylabel(y_Label)

    if not x_ticks:
        ax.set_xticks([])

    if not x_tickLabels:
        ax.set_xticklabels([])

    if not y_ticks:
        ax.set_yticks([-1, 0, 1])

    if not y_tickLabels:
        ax.set_yticklabels([])

    if legend:
        ax.legend(loc='lower left',markerfirst=False,handlelength=1,handletextpad=0.4,labelspacing=0.2,)

    plt.savefig(P(FOLDER).joinpath(f"{savename}.tif"),dpi=300,transparent=True)
    plt.savefig(P(FOLDER).joinpath(f"{savename}.png"),dpi=300,transparent=True)


if __name__ == "__main__":
    main(FOLDER)
    plt.show()

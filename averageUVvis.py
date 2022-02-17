from pathlib import Path as P
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FOLDER = '/Users/Brad/Downloads/test'

def exp(x, a, b, c):
    return a + b*np.exp(-x / c)

def average(folder):
    excel_sheets = [ii for ii in P(folder).iterdir() if ii.suffix == '.xlsx' and not ii.name.startswith('~')]
    data = {}
    for e in excel_sheets:
        d = pd.read_excel(e) 
        data[e.name] = d

    fig, ax = plt.subplots()
    
    for d in data:
        t_col = [ii for ii in list(data[d].columns.values) if 'time' in ii.lower()][0]
        others = [ii for ii in list(data[d].columns.values) if ii != t_col and 'Unnamed' not in ii]
        t = data[d][t_col]
        mat = np.zeros((len(t), len(others)))
        for i, o in enumerate(others):
            data[d][o] = data[d][o] / np.max(data[d][o])
            mat[:, i] = data[d][o]
            ax.plot(t, data[d][o], alpha=0.5, color='gray')
            popt, pcov = curve_fit(exp, t, data[d][o], p0=[1, -1, 100])
            print(popt[-1])

        avg = np.mean(mat, axis=1)
        popt, pcov = curve_fit(exp, t, avg)
        print(f"average of {popt[-1]:.1f}")
        ax.plot(t, avg)
        outstr = ''
        for i, row in enumerate(t):
            outstr += f"{row},{avg[i]}\n"
        P(FOLDER).joinpath('Averaged UV-Vis.txt').write_text(outstr)

if __name__ == "__main__":
    average(FOLDER)
    plt.savefig(P(FOLDER).joinpath('averaged.png'), dpi=300)
    # plt.show()

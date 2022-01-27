1. Install python using [Anaconda package](https://www.anaconda.com/products/individual)
1. That should automatically provide an updated version of python, numpy, matplotlib, etc. that you will need for plotting
1. Open 'Terminal' application on mac
1. Type `which conda` and press enter -- make sure that something comes up (if it doesn't, get help!)
1. Type `conda install pip` and press enter
1. Download [this repo](https://github.com/brad-ley/manuscript-plots) by pressing green code button and then 'download zip'
1. Unzip that file in your downloads
1. Right-click the folder, hold option key, and select 'Copy as Pathname'
1. Go back to terminal and type "cd" and then quotation mark, press Ctrl-V, then close the quotation -- that should move you to the folder you just downloaded in your terminal
1. Check that this worked by typing `ls` and press enter -- that should display the files that are in that folder
1. `conda install pip` -- this should install pip which is a package manager
1. `pip install -r requirements.txt` -- this should install all packages you need in order to make nice plots
1. Now you can edit the .py file however you see fit -- follow the instructions within the file
1. After editing the file, `python3 manuscriptPlots.py` in your terminal window and it will run the code you edited
1. Voila, you have a plot! And the .tif file of the plot should now be saved in whatever folder you got the datafile from
1. Ask me if you have any issues/questions

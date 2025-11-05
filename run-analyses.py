# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   10.27.2025
# -----------------------------------------------------------------------------
## @brief Load a saved Ax experiment and run
#    some analyses. 
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
import seaborn as sns

from ax.modelbridge.cross_validation import cross_validate
from ax.plot.contour import interact_contour
from ax.plot.diagnostic import interact_cross_validation
from ax.plot.scatter import interact_fitted, plot_objective_vs_constraints, tile_fitted
from ax.plot.slice import plot_slice
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.utils.measurement.synthetic_functions import hartmann6
from ax.utils.notebook.plotting import init_notebook_plotting, render

# announce start
print("\n  Starting analyses!")

# options ---------------------------------------------------------------------

# set global options
basetag = "addErrors"
datetag = "d5m11y2025"
outpath = "../out/"
outglob = "AxTrial"

# -----------------------------------------------------------------------------
# Basic analyses
# -----------------------------------------------------------------------------

# glob all trial output
filepath = pathlib.Path(outpath)
outfiles = sorted(filepath.glob(outglob + "*/*.txt"))

# announce what files are going to be processed
print(f"    Located output: {len(outfiles)} trials to analyze")
for file in outfiles:
    print(f"      -- {file.name}")

# read in data ----------------------------------------------------------------

# announce file reading starting
print("    Reading in metrics:")

# store output in a dataframe
trial     = 0
outframes = []
for file in outfiles:

    # open file, grab metric(s) and related data
    data = None
    with open(file, 'r') as f:
        data = f.readlines()
        print(f"      -- [{trial}] {data}")

    # collect data to store 
    resodata  = pd.DataFrame({'reso' : float(data[0])}, index = [0])
    eresodata = pd.DataFrame({'ereso' : float(data[1])}, index = [0])
    meandata  = pd.DataFrame({'mean' : float(data[2])}, index = [0])
    emeandata = pd.DataFrame({'emean' : float(data[3])}, index = [0])
    stavdata2 = pd.DataFrame({'stave2' : int(data[4])}, index = [0])
    stavdata3 = pd.DataFrame({'stave3' : int(data[5])}, index = [0])
    stavdata4 = pd.DataFrame({'stave4' : int(data[6])}, index = [0])
    stavdata5 = pd.DataFrame({'stave5' : int(data[7])}, index = [0])
    stavdata6 = pd.DataFrame({'stave6' : int(data[8])}, index = [0])
    filedata  = pd.DataFrame({'file' : file.stem}, index = [0])
    trialdata = pd.DataFrame({'trial' : trial}, index = [0])

    # calculate the number of staves active
    #   -- NOTE stave 1 is always active!
    nstave = 1
    for stave in data[4:]:
        active = int(stave)
        if active == 1:
            nstave += 1
    nstavdata = pd.DataFrame({'nstave' : nstave}, index = [0])

    # join data into a single frame, append
    # to big frame, and increment trial no.
    frame = pd.concat(
        [
            resodata,
            eresodata,
            meandata,
            emeandata,
            stavdata2,
            stavdata3,
            stavdata4,
            stavdata5,
            stavdata6,
            nstavdata,
            filedata,
            trialdata
        ],
        axis = 1
    )
    outframes.append(frame)
    trial += 1

# now squash frames into 1 big frame
outdata = pd.concat(outframes, ignore_index = True)
print(f"    Combined metrics and data:")
print(outdata.head())

# create matplot plots --------------------------------------------------------

# set plot style
sns.set(style = "white")

# create a figure for vars vs. trial
trialfig, trialplots = plt.subplots(
    nrows = 3,
    ncols = 1,
    figsize = (8, 12),
    sharex = True,
    sharey = False
)

# plot resolution vs. trial in top panel
trialplots[0].scatter(
    outdata["trial"],
    outdata["reso"],
    color = "midnightblue",
    alpha = 0.5
)
trialplots[0].errorbar(
    outdata["trial"],
    outdata["reso"],
    yerr = outdata["ereso"],
    ecolor = "midnightblue",
    capsize = 7,
    fmt = 'none'
)
trialplots[0].plot(
    outdata["trial"],
    outdata["reso"],
    color = "mediumblue",
    linewidth = 0.8
)
trialplots[0].set_title("Electron Resolution vs. Trial Number")
trialplots[0].set_xlabel("Trial")
trialplots[0].set_ylabel("Electron Resolution")

# plot mean vs. trial in middle panel
trialplots[1].scatter(
    outdata["trial"],
    outdata["mean"],
    color = "indigo",
    alpha = 0.5
)
trialplots[1].errorbar(
    outdata["trial"],
    outdata["mean"],
    yerr = outdata["emean"],
    ecolor = "indigo",
    capsize = 7,
    fmt = 'none'
)
trialplots[1].plot(
    outdata["trial"],
    outdata["mean"],
    color = "blueviolet",
    linewidth = 0.8
)
trialplots[1].set_title("Electron Mean %-Diff vs. Trial Number")
trialplots[1].set_xlabel("Trial")
trialplots[1].set_ylabel("Mean %-Diff")

# plot n active stave vs. trial in bottom panel
trialplots[2].scatter(
    outdata["trial"],
    outdata["nstave"],
    color = "darkred",
    alpha = 0.5
)
trialplots[2].plot(
    outdata["trial"],
    outdata["nstave"],
    color = "indianred",
    linewidth = 0.8
)
trialplots[2].set_title("N Active Staves vs. Trial Number")
trialplots[2].set_xlabel("Trial")
trialplots[2].set_ylabel("N Active Staves")

# now create vs. trial figure name and save
trialname = basetag + ".vsTrialNum." + datetag + ".png"
plt.tight_layout()
plt.savefig(trialname, dpi = 300, bbox_inches = "tight")
plt.show()

# create a figure for vars vs. nstave
stavefig, staveplots = plt.subplots(
    nrows = 2,
    ncols = 1,
    figsize = (8, 8),
    sharex = True,
    sharey = False
)

# plot resolution vs. n active stave in top panel
staveplots[0].scatter(
    outdata["nstave"],
    outdata["reso"],
    color = "midnightblue",
    alpha = 0.5
)
staveplots[0].set_title("Electron Resolution vs. N Active Staves")
staveplots[0].set_xlabel("N Active Staves")
staveplots[0].set_ylabel("Electron Resolution")

# plot mean vs. n active stave in bottom-right panel
staveplots[1].scatter(
    outdata["nstave"],
    outdata["mean"],
    color = "indigo",
    alpha = 0.5
)
staveplots[1].set_title("Electron Mean %-Diff vs. N Active Staves")
staveplots[1].set_xlabel("N Active Staves")
staveplots[1].set_ylabel("Mean %-Diff")

# now create vs. nstave figure name and save
stavename = basetag + ".vsNStave." + datetag + ".png"
plt.tight_layout()
plt.savefig(stavename, dpi = 300, bbox_inches = "tight")
plt.show()

# -----------------------------------------------------------------------------
# Ax analyses (not working yet)
# -----------------------------------------------------------------------------

# load saved experiment
#ax_client = AxClient()
#ax_client = ax_client.load_from_json_file(
#    filepath = "../out/bic_mobo_exp_out.json"
#)
#ax_client.fit_model()

# grab model
#model = ax_client.generation_strategy.model

# create contour plot
#render(
#    ax_client.get_contour_plot(
#        param_x = "enable_staves_2",
#        param_y = "enable_staves_3",
#        metric_name = "ElectronEnergyResolution"
#    )
#)

# show arm effect
#render(interact_fitted(model, rel=False))

# announce end
print("  Analyses complete!\n")

# end =========================================================================

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
datetag = "d29m10y2025"

# -----------------------------------------------------------------------------
# Basic analyses
# -----------------------------------------------------------------------------

# glob all trial output
outpath  = pathlib.Path("../out/")
outfiles = sorted(outpath.glob("AxTrial*/*.txt"))

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
    meandata  = pd.DataFrame({'mean' : float(data[1])}, index = [0])
    stavdata2 = pd.DataFrame({'stave2' : int(data[2])}, index = [0])
    stavdata3 = pd.DataFrame({'stave3' : int(data[3])}, index = [0])
    stavdata4 = pd.DataFrame({'stave4' : int(data[4])}, index = [0])
    stavdata5 = pd.DataFrame({'stave5' : int(data[5])}, index = [0])
    stavdata6 = pd.DataFrame({'stave6' : int(data[6])}, index = [0])
    filedata  = pd.DataFrame({'file' : file.stem}, index = [0])
    trialdata = pd.DataFrame({'trial' : trial}, index = [0])

    # calculate the number of staves active
    nstave = 0
    for stave in data[2:]:
        active = int(stave)
        if active == 1:
            nstave += 1
    nstavdata = pd.DataFrame({'nstave' : nstave}, index = [0])

    # join data into a single frame, append
    # to big frame, and increment trial no.
    frame = pd.concat(
        [
            resodata,
            meandata,
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
print(f"    Combined data:")
print(outdata.head())

# create plots ----------------------------------------------------------------

# set plot style
sns.set(style = "white")

# create a figure for objectives vs. data
fig, plots = plt.subplots(
    nrows = 2,
    ncols = 2,
    figsize = (12, 12),
    sharex = False,
    sharey = True
)

# plot resolution vs. trial in top-left panel
plots[0, 0].scatter(
    outdata["trial"],
    outdata["reso"],
    color = "midnightblue",
    alpha = 0.5
)
plots[0, 0].plot(
    outdata["trial"],
    outdata["reso"],
    color = "mediumblue",
    linewidth = 0.8
)
plots[0, 0].set_title("Electron Resolution vs. Trial Number")
plots[0, 0].set_xlabel("Trial")
plots[0, 0].set_ylabel("Electron Resolution")

# plot resolution vs. n active stave in top-right panel
plots[0, 1].scatter(
    outdata["nstave"],
    outdata["reso"],
    color = "midnightblue",
    alpha = 0.5
)
plots[0, 1].set_title("Electron Resolution vs. N Active Staves")
plots[0, 1].set_xlabel("N Active Staves")
plots[0, 1].set_ylabel("Electron Resolution")

# plot mean vs. trial in bottom-left panel
plots[1, 0].scatter(
    outdata["trial"],
    outdata["mean"],
    color = "darkred",
    alpha = 0.5
)
plots[1, 0].plot(
    outdata["trial"],
    outdata["mean"],
    color = "indianred",
    linewidth = 0.8
)
plots[1, 0].set_title("Electron Mean %-diff vs. Trial Number")
plots[1, 0].set_xlabel("Trial")
plots[1, 0].set_ylabel("Mean %-diff")

# plot mean vs. n active stave in bottom-right panel
plots[1, 1].scatter(
    outdata["nstave"],
    outdata["mean"],
    color = "darkorange",
    alpha = 0.5
)
plots[1, 1].set_title("Electron Mean %-diff vs. N Active Staves")
plots[1, 1].set_xlabel("N Active Staves")
plots[1, 1].set_ylabel("Electron Resolution")

# now create name
resname = "eleResoVsTrial." + datetag + ".png"

# save and show figure
plt.tight_layout()
plt.savefig(resname, dpi=300, bbox_inches = "tight")
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

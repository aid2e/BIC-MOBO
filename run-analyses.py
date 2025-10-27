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

# set global options
datetag = "d27m10y2025"

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

# announce file reading starting
print("    Reading in metrics:")

# store output in a dataframe
trial     = 0
outframes = []
for file in outfiles:

    # open file, grab metric(s)
    metric = None
    with open(file, 'r') as f:
        metric = f.readlines() 
    print(f"      -- [{trial}] {metric}")

    # collect data to store 
    resodata  = pd.DataFrame({'reso' : float(metric[0])}, index = [0])
    filedata  = pd.DataFrame({'file' : file.stem}, index = [0])
    trialdata = pd.DataFrame({'trial' : trial}, index = [0])

    # join data into a single frame, append
    # to big frame, and increment trial no.
    frame = pd.concat([resodata, filedata, trialdata], axis = 1)
    outframes.append(frame)
    trial += 1

# now squash frames into 1 big frame
outdata = pd.concat(outframes, ignore_index = True)
print(f"    Combined data:")
print(outdata.head())

# set plot style
sns.set(style = "whitegrid")

# make metrics vs. trial no. plot
plt.figure(figsize = (10, 6))
plt.scatter(
    outdata["trial"],
    outdata["reso"],
    color = "midnightblue",
    alpha = 0.5
)
plt.plot(
    outdata["trial"],
    outdata["reso"],
    color = "slateblue",
    linewidth = 0.8
)
resname = "eleResoVsTrial." + datetag + ".png"

# add title, etc. and save
plt.title("e- Resolution vs. Trial Number")
plt.xlabel("Trial")
plt.ylabel("e- energy resolution")
plt.grid(True, linestyle = ":", alpha = 0.5)
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

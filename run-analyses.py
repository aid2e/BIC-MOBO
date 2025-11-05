# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   10.27.2025
# -----------------------------------------------------------------------------
## @brief Load a saved Ax experiment and run
#    some analyses. 
# =============================================================================

from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib
import seaborn as sns

# -----------------------------------------------------------------------------
# Global Options
# -----------------------------------------------------------------------------

@dataclass
class Option:
    """Option

    Data class to
    hold global opts
    for script.

    Members:
      doAx:    turn on/off Ax-based analyses
      doRoot:  turn on/off ROOT-based analyses
      baseTag: prefix of analysis output file
      dateTag: tag indicating date/time in analysis output file
      outPath: path to output files
      outTxt:  regex pattern to glob relevant text output files
      outRoot: regex patter to glob relevant ROOT output files
      outExp:  saved Ax experiment to analyze
    """
    doRoot  : bool
    doAx    : bool
    baseTag : str
    dateTag : str
    outPath : str
    outTxt  : str
    outRoot : str
    outExp  : str

# set global options
GlobalOpts = Option(
    True,
    False,
    "addHistPlots",
    "d5m11y2025",
    "../out",
    "AxTrial*/*.txt",
    "AxTrial*/*_ana_single_electron_ElectronEnergyResolution.root",
    "../out/bic_mobo_exp_out.json",
)

# -----------------------------------------------------------------------------
# Optional dependencies
# -----------------------------------------------------------------------------

if GlobalOpts.doRoot:
    import ROOT

if GlobalOpts.doAx:
    from ax.modelbridge.cross_validation import cross_validate
    from ax.plot.contour import interact_contour
    from ax.plot.diagnostic import interact_cross_validation
    from ax.plot.scatter import interact_fitted, plot_objective_vs_constraints, tile_fitted
    from ax.plot.slice import plot_slice
    from ax.service.ax_client import AxClient, ObjectiveProperties
    from ax.utils.notebook.plotting import init_notebook_plotting, render

# -----------------------------------------------------------------------------
# Basic analyses
# -----------------------------------------------------------------------------

def DoBasicAnalyses(opts = GlobalOpts):
    """DoBasicAnalyses

    Runs a set of small analyses with
    pandas and matplotlib.

    Args:
      opts: analysis options
    """

    # announce start of basic analyses
    print("    Running basic analyses")

    # glob all trial output
    filePath = pathlib.Path(opts.outPath)
    outFiles = sorted(filePath.glob(opts.outTxt))

    # announce what files are going to be processed
    print(f"      Located text output: {len(outFiles)} trials to analyze")
    for file in outFiles:
        print(f"        -- {file.name}")

    # read in data ------------------------------------------------------------

    # announce file reading starting
    print("      Reading in metrics:")

    # store output in a dataframe
    iTrial    = 0
    outFrames = []
    for file in outFiles:

        # open file, grab metric(s) and related data
        data = None
        with open(file, 'r') as f:
            data = f.readlines()
            print(f"        -- [{iTrial}] {data}")

        # collect data to store
        reso   = pd.DataFrame({'reso' : float(data[0])}, index = [0])
        eReso  = pd.DataFrame({'eReso' : float(data[1])}, index = [0])
        mean   = pd.DataFrame({'mean' : float(data[2])}, index = [0])
        eMean  = pd.DataFrame({'eMean' : float(data[3])}, index = [0])
        stave2 = pd.DataFrame({'stave2' : int(data[4])}, index = [0])
        stave3 = pd.DataFrame({'stave3' : int(data[5])}, index = [0])
        stave4 = pd.DataFrame({'stave4' : int(data[6])}, index = [0])
        stave5 = pd.DataFrame({'stave5' : int(data[7])}, index = [0])
        stave6 = pd.DataFrame({'stave6' : int(data[8])}, index = [0])
        stem   = pd.DataFrame({'file' : file.stem}, index = [0])
        trial  = pd.DataFrame({'trial' : iTrial}, index = [0])

        # calculate the number of staves active
        #   -- NOTE stave 1 is always active!
        nActive = 1
        for stave in data[4:]:
            active = int(stave)
            if active == 1:
                nActive += 1
        nStave = pd.DataFrame({'nStave' : nActive}, index = [0])

        # join data into a single frame, append
        # to big frame, and increment trial no.
        frame = pd.concat(
            [
                reso,
                eReso,
                mean,
                eMean,
                stave2,
                stave3,
                stave4,
                stave5,
                stave6,
                nStave,
                stem,
                trial
           ],
           axis = 1
        )
        outFrames.append(frame)
        iTrial += 1

    # now squash frames into 1 big frame
    outData = pd.concat(outFrames, ignore_index = True)
    print(f"      Combined metrics and data:")
    print(outData.head())

    # create matplot plots ----------------------------------------------------

    # set plot style
    sns.set(style = "white")

    # create a figure for vars vs. trial
    trialFig, trialPlots = plt.subplots(
        nrows = 3,
        ncols = 1,
        figsize = (8, 12),
        sharex = True,
        sharey = False
    )

    # plot resolution vs. trial in top panel
    trialPlots[0].scatter(
        outData["trial"],
        outData["reso"],
        color = "midnightblue",
        alpha = 0.5
    )
    trialPlots[0].errorbar(
        outData["trial"],
        outData["reso"],
        yerr = outData["eReso"],
        ecolor = "midnightblue",
        capsize = 7,
        fmt = 'none'
    )
    trialPlots[0].plot(
        outData["trial"],
        outData["reso"],
        color = "mediumblue",
        linewidth = 0.8
    )
    trialPlots[0].set_title(r'$e^{-}$ Resolution vs. Trial Number')
    trialPlots[0].set_xlabel("Trial")
    trialPlots[0].set_ylabel(r'$e^{-}$ Resolution')

    # plot mean vs. trial in middle panel
    trialPlots[1].scatter(
        outData["trial"],
        outData["mean"],
        color = "indigo",
        alpha = 0.5
    )
    trialPlots[1].errorbar(
        outData["trial"],
        outData["mean"],
        yerr = outData["eMean"],
        ecolor = "indigo",
        capsize = 7,
        fmt = 'none'
    )
    trialPlots[1].plot(
        outData["trial"],
        outData["mean"],
        color = "blueviolet",
        linewidth = 0.8
    )
    trialPlots[1].set_title(r'$e^{-}$ Mean %-Diff vs. Trial Number')
    trialPlots[1].set_xlabel("Trial")
    trialPlots[1].set_ylabel(r'$e^{-}$ Mean %-Diff')

    # plot n active stave vs. trial in bottom panel
    trialPlots[2].scatter(
        outData["trial"],
        outData["nStave"],
        color = "darkred",
        alpha = 0.5
    )
    trialPlots[2].plot(
        outData["trial"],
        outData["nStave"],
        color = "indianred",
        linewidth = 0.8
    )
    trialPlots[2].set_title(r'$N_{\text{staves}}$ vs. Trial Number')
    trialPlots[2].set_xlabel("Trial")
    trialPlots[2].set_ylabel(r'$N_{\text{staves}}$')

    # now create vs. trial figure name and save
    trialName = opts.baseTag + ".vsTrialNum." + opts.dateTag + ".png"
    plt.tight_layout()
    plt.savefig(trialName, dpi = 300, bbox_inches = "tight")
    plt.show()
    print(f"      Created figure for variables vs. trial #: {trialName}")


    # create a figure for vars vs. nstave
    staveFig, stavePlots = plt.subplots(
        nrows = 2,
        ncols = 1,
        figsize = (8, 8),
        sharex = True,
        sharey = False
    )

    # plot resolution vs. n active stave in top panel
    stavePlots[0].scatter(
        outData["nStave"],
        outData["reso"],
        color = "midnightblue",
        alpha = 0.5
    )
    stavePlots[0].set_title(r'$e^{-}$ Resolution vs. $N_{\text{staves}}$')
    stavePlots[0].set_xlabel(r'$N_{\text{staves}}$')
    stavePlots[0].set_ylabel(r'$e^{-}$ Resolution')

    # plot mean vs. n active stave in bottom-right panel
    stavePlots[1].scatter(
        outData["nStave"],
        outData["mean"],
        color = "indigo",
        alpha = 0.5
    )
    stavePlots[1].set_title(r'$e^{-}$ Mean %-Diff vs. $N_{\text{staves}}$')
    stavePlots[1].set_xlabel(r'$N_{\text{staves}}')
    stavePlots[1].set_ylabel(r'$e^{-}$ Mean %-Diff')

    # now create vs. nstave figure name and save
    staveName = opts.baseTag + ".vsNStave." + opts.dateTag + ".png"
    plt.tight_layout()
    plt.savefig(staveName, dpi = 300, bbox_inches = "tight")
    plt.show()
    print(f"      Created figure for variables vs. N staves: {staveName}")

# -----------------------------------------------------------------------------
# ROOT analyses
# -----------------------------------------------------------------------------

def DoRootAnalyses(opts = GlobalOpts):
    """DoRootAnalyses

    Runs a set of ROOT-
    based analyses.

    Args:
      opts: analysis options
    """

    # announce start of ROOT analyses
    print("    Running ROOT analyses")

    # glob all trial output
    filePath = pathlib.Path(opts.outPath)
    outFiles = sorted(filePath.glob(opts.outRoot))

    # announce what files are going to be processed
    print(f"      Located ROOT output: {len(outFiles)} trials to analyze")
    for file in outFiles:
        print(f"        -- {file.name}")

    # create hist stacks for resolution
    hResIntVsTrialU = ROOT.THStack(
       "hResIntVsTrialU",
       "e^{-} Energy %-Difference vs. Trial Number (Unnormalized);(E_{clust} - E_{par}) / E_{par}; counts"
    )
    hResIntVsTrialN = ROOT.THStack(
       "hResIntVsTrialN",
       "e^{-} Energy %-Difference vs. Trial Number (Normalized);(E_{clust} - E_{par}) / E_{par}; a.u."
    )
    print("      Reading in files:")

    # grab relevant ROOT objects
    hists  = {}
    iTrial = 0
    for file in outFiles:

        # open input file and grab hists
        iFile   = ROOT.TFile(os.fspath(file.absolute()), "read")
        hResInt = iFile.Get("hEneRes")
        print(f"        -- [{iTrial}] hResInt: {hResInt}")

        # create updated names/titles
        trial = f"Trial {iTrial}"
        uName = hResInt.GetName() + f"NoNorm_Trial{iTrial}"
        nName = hResInt.GetName() + f"Normed_Trial{iTrial}"

        # clone histograms
        hResIntU = hResInt.Clone()
        hResIntN = hResInt.Clone()
        hResIntU.SetNameTitle(uName, trial)
        hResIntN.SetNameTitle(nName, trial)

        # normalize relevant histograms
        intResInt = hResIntN.Integral()
        if intResInt > 0.0:
            hResIntN.Scale(1.0 / intResInt)

        # add to hists to relevant stacks
        #   -- FIXME something's going on with
        #      the hist stacking here...
        hResIntVsTrialU.Add(hResIntU)
        hResIntVsTrialN.Add(hResIntN)

        # and store in output dicts
        hists[hResIntU.GetName()] = hResIntVsTrialU
        hists[hResIntN.GetName()] = hResIntVsTrialN
        iTrial += 1

    # announce end of loop
    print("      Collected relevant ROOT objects")

    # TODO
    #   - Set style of THStacks
    #   - Draw THStacks

    # save drawn output
    rootName = opts.baseTag + ".outHists." + opts.dateTag + ".root"
    with ROOT.TFile(rootName, "recreate") as f:
        for hist in hists.values():
            hist.Write()

# -----------------------------------------------------------------------------
# Ax analyses (not working yet)
# -----------------------------------------------------------------------------

def DoAxAnalyses(opts = GlobalOpts):
    """DoAxAnalyses

    Runs a set of built-in
    Ax analyses.

    Args:
      opts: analysis options
    """

    # load saved experiment
    ax_client = AxClient()
    ax_client = ax_client.load_from_json_file(
        filepath = opts.outExp
    )
    ax_client.fit_model()

    # grab model
    model = ax_client.generation_strategy.model

    # create contour plot
    render(
        ax_client.get_contour_plot(
            param_x = "enable_staves_2",
            param_y = "enable_staves_3",
            metric_name = "ElectronEnergyResolution"
        )
    )

    # show arm effect
    render(interact_fitted(model, rel=False))

# main ========================================================================

if __name__ == "__main__":

   # announce start
   print("\n  Starting analyses!")

   # set options
   opts = GlobalOpts
   print(f"    Set options:")
   print(f"      {opts}")

   # run analyses
#   DoBasicAnalyses(opts)
   if opts.doAx:
       DoAxAnalyses(opts)
   if opts.doRoot:
       DoRootAnalyses(opts)

   # announce end
   print("  Analyses complete!\n")

# end =========================================================================

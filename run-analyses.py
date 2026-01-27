# =============================================================================
## @file   run-analyses.py
#  @author Derek Anderson
#  @date   10.27.2025
# -----------------------------------------------------------------------------
## @brief Run several different analyses
#    on BIC-MOBO output.
# =============================================================================

from dataclasses import dataclass
import argparse as ap
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

    Data class to hold global opts
    for analyses.

    Members:
      doBasic:    turn on/off basic analysis
      doAx:       turn on/off Ax-based analyses
      doRoot:     turn on/off ROOT-based analyses
      doEne:      process energy resolution output
      doEta:      process eta resolution output
      doPhi:      process phi resolution output
      baseTag:    prefix of analysis output file
      dateTag:    tag indicating date/time in analysis output file
      outPath:    path to output files
      outEneTxt:  regex pattern to glob relevant energy reso text output files
      outEtaTxt:  regex pattern to glob relevant eta reso text output files
      outPhiTxt:  regex pattern to glob relevant phi reso text output files
      outEneRoot: regex pattern to glob relevant energy reso ROOT output files
      outEtaRoot: regex pattern to glob relevant eta reso ROOT output files
      outPhiRoot: regex pattern to glob relevant phi reso ROOT output files
      outExp:     saved Ax experiment to analyze
      palette:    ROOT color palette to use
    """
    doBasic    : bool
    doRoot     : bool
    doAx       : bool
    doEne      : bool
    doEta      : bool
    doPhi      : bool
    baseTag    : str
    dateTag    : str
    outPath    : str
    outEneTxt  : str
    outEtaTxt  : str
    outPhiTxt  : str
    outEneRoot : str
    outEtaRoot : str
    outPhiRoot : str
    outExp     : str
    palette    : int

# set global options
GlobalOpts = Option(
    doBasic    = True,
    doRoot     = True,
    doAx       = False,
    doEne      = True,
    doEta      = True,
    doPhi      = True,
    baseTag    = "fullBrutProduction",
    dateTag    = "d5m1y2025",
    outPath    = "./TestOutput_Step2_RunBrutProduction",
    outEneTxt  = "*EnergyReso*.txt",
    outEtaTxt  = "*EtaReso*.txt",
    outPhiTxt  = "*PhiReso*.txt",
    outEneRoot = "*EnergyReso*.root",
    outEtaRoot = "*EtaReso*.root",
    outPhiRoot = "*PhiReso*.root",
    outExp     = "../out/bic_mobo_exp_out.json",
    palette    = 60
)

# -----------------------------------------------------------------------------
# Optional dependencies
# -----------------------------------------------------------------------------

if GlobalOpts.doRoot:
    import ROOT

if GlobalOpts.doAx:
    from ax import Client
    from ax.analysis.plotly.plotly_analysis import PlotlyAnalysisCard
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

def DoBasicAnalyses(ana, glob, label, opts = GlobalOpts):
    """DoBasicAnalyses

    Runs a set of small analyses with
    pandas and matplotlib.

    Args:
      ana:   index of ana being run
      glob:  regex pattern to glob
      label: label for output files
      opts:  analysis options
    """

    # announce start of basic analyses
    print(f"    Running basic analyses:")
    print(f"        ana = {ana}, glob  = {glob}. label = {label}")

    # glob all trial output
    filePath = pathlib.Path(opts.outPath)
    outFiles = sorted(filePath.glob(glob))

    # announce what files are going to be processed
    print(f"      Located text output: {len(outFiles)} trials to analyze")
    for file in outFiles:
        print(f"        -- {file.name}")

    # exit if no files found
    if len(outFiles) == 0:
        print(f"WARNING: no files found, exiting analysis!\n")
        return

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

    # set titles/axes
    trialPlotTitles  = list()
    trialPlotTitlesX = list()
    trialPlotTitlesY = list()
    stavePlotTitles  = list()
    stavePlotTitlesX = list()
    stavePlotTitlesY = list()
    resoRange        = tuple()
    meanRange        = tuple()
    match ana:

        # energy resolution
        case 0:

            # reso vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\sigma_{E}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\sigma_{E}$')
            stavePlotTitles.append(r'Single $e^{-}$ $\sigma_{E}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\sigma_{E}$')

            # mean vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\mu_{\delta E}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\mu_{\delta E} = \langle (E_{rec} - E_{par}) / E_{par} \rangle$')
            stavePlotTitles.append(r'Single $e^{-}$ $\mu_{\delta E}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\mu_{\delta E} = \langle (E_{rec} - E_{par}) / E_{par} \rangle$')

            # set axis ranges
            resoRange = tuple([-0.007, 0.33])
            meanRange = tuple([-0.07, 0.07])

        # eta resolution
        case 1:

            # reso vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\sigma_{\eta}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\sigma_{\eta}$')
            stavePlotTitles.append(r'Single $e^{-}$ $\sigma_{\eta}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\sigma_{\eta}$')

            # mean vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\mu_{\delta\eta}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\mu_{\delta\eta} = \langle (\eta_{rec} - \eta_{par}) / \eta_{par} \rangle$')
            stavePlotTitles.append(r'Single $e^{-}$ $\mu_{\delta\eta}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\mu_{\delta\eta} = \langle (\eta_{rec} - \eta_{par}) / \eta_{par} \rangle$')

            # set axis ranges
            resoRange = tuple([-0.007, 0.13])
            meanRange = tuple([-0.07, 0.07])

        # phi resolution
        case 2:

            # reso vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\sigma_{\phi}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\sigma_{\phi}$')
            stavePlotTitles.append(r'Single $e^{-}$ $\sigma_{\phi}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\sigma_{\phi}$')

            # mean vs. trial, nstave
            trialPlotTitles.append(r'Single $e^{-}$ $\mu_{\delta\phi}$ vs. Trial Number')
            trialPlotTitlesX.append("Trial")
            trialPlotTitlesY.append(r'$\mu_{\delta\phi} = \langle (\phi_{rec} - \phi_{par}) / \phi_{par} \rangle$')
            stavePlotTitles.append(r'Single $e^{-}$ $\mu_{\delta\phi}$ vs. $N_{\text{staves}}$')
            stavePlotTitlesX.append(r'$N_{\text{staves}}$')
            stavePlotTitlesY.append(r'$\mu_{\delta\phi} = \langle (\phi_{rec} - \phi_{par}) / \phi_{par} \rangle$')

            # set axis ranges
            resoRange = tuple([-0.007, 0.13])
            meanRange = tuple([-0.07, 0.07])

    # last vs trial plot is the same regardless of objective
    trialPlotTitles.append(r'$N_{\text{staves}}$ vs. Trial Number')
    trialPlotTitlesX.append("Trial")
    trialPlotTitlesY.append(r'$N_{\text{staves}}$')

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
    trialPlots[0].set_title(trialPlotTitles[0])
    trialPlots[0].set_xlabel(trialPlotTitlesX[0])
    trialPlots[0].set_ylabel(trialPlotTitlesY[0])
    trialPlots[0].set_ylim(resoRange[0], resoRange[1])

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
    trialPlots[1].set_title(trialPlotTitles[1])
    trialPlots[1].set_xlabel(trialPlotTitlesX[1])
    trialPlots[1].set_ylabel(trialPlotTitlesY[1])
    trialPlots[1].set_ylim(meanRange[0], meanRange[1])

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
    trialPlots[2].set_title(trialPlotTitles[2])
    trialPlots[2].set_xlabel(trialPlotTitlesX[2])
    trialPlots[2].set_ylabel(trialPlotTitlesY[2])

    # now create vs. trial figure name and save
    trialName = opts.baseTag + "." + label + ".vsTrialNum." + opts.dateTag + ".png"
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
    stavePlots[0].set_title(stavePlotTitles[0])
    stavePlots[0].set_xlabel(stavePlotTitlesX[0])
    stavePlots[0].set_ylabel(stavePlotTitlesY[0])
    stavePlots[0].set_ylim(resoRange[0], resoRange[1])

    # plot mean vs. n active stave in bottom-right panel
    stavePlots[1].scatter(
        outData["nStave"],
        outData["mean"],
        color = "indigo",
        alpha = 0.5
    )
    stavePlots[1].set_title(stavePlotTitles[1])
    stavePlots[1].set_xlabel(stavePlotTitlesX[1])
    stavePlots[1].set_ylabel(stavePlotTitlesY[1])
    stavePlots[1].set_ylim(meanRange[0], meanRange[1])

    # now create vs. nstave figure name and save
    staveName = opts.baseTag + "." + label + ".vsNStave." + opts.dateTag + ".png"
    plt.tight_layout()
    plt.savefig(staveName, dpi = 300, bbox_inches = "tight")
    plt.show()
    print(f"      Created figure for variables vs. N staves: {staveName}")

# -----------------------------------------------------------------------------
# ROOT analyses
# -----------------------------------------------------------------------------

def DoRootAnalyses(ana, glob, label, opts = GlobalOpts):
    """DoRootAnalyses

    Runs a set of ROOT-
    based analyses.

    Args:
      ana:   index of ana being run
      glob:  regex pattern to glob
      label: label for output files
      opts:  analysis options
    """

    # announce start of ROOT analyses
    print("    Running ROOT analyses")

    # glob all trial output
    filePath = pathlib.Path(opts.outPath)
    outFiles = sorted(filePath.glob(glob))
    nTrials  = len(outFiles)

    # announce what files are going to be processed
    print(f"      Located ROOT output: {nTrials} trials to analyze")
    for file in outFiles:
        print(f"        -- {file.name}")

    # exit if no files found
    if len(outFiles) == 0:
        print(f"WARNING: no files found, exiting analysis!\n")
        return

    # set histogram titles
    sResIntVsTrialU  = None
    sResIntVsTrialN  = None
    sResIntVsTrial2D = None
    match ana:
        case 0:
            sResIntVsTrialU  = "Single e^{-} #deltaE vs. Trial Number (Unnormalized); #deltaE = (E_{clust} - E_{par}) / E_{par}; counts"
            sResIntVsTrialN  = "Single e^{-} #deltaE vs. Trial Number (Normalized); #deltaE = (E_{clust} - E_{par}) / E_{par}; normalized counts"
            sResIntVsTrial2D = "Single e^{-} #deltaE vs. Trial Number (Normalized); #deltaE = (E_{clust} - E_{par}) / E_{par}; trial"
        case 1:
            sResIntVsTrialU  = "Single e^{-} #delta#eta vs. Trial Number (Unnormalized); #delta#eta = (#eta_{clust} - #eta_{par}) / #eta_{par}; counts"
            sResIntVsTrialN  = "Single e^{-} #delta#eta vs. Trial Number (Normalized); #delta#eta = (#eta_{clust} - #eta_{par}) / #eta_{par}; normalized counts"
            sResIntVsTrial2D = "Single e^{-} #delta#eta vs. Trial Number (Normalized); #delta#eta = (#eta_{clust} - #eta_{par}) / #eta_{par}; trial"
        case 2:
            sResIntVsTrialU  = "Single e^{-} #delta#phi vs. Trial Number (Unnormalized); #delta#phi = (#phi_{clust} - #phi_{par}) / #phi_{par}; counts"
            sResIntVsTrialN  = "Single e^{-} #delta#phi vs. Trial Number (Normalized); #delta#phi = (#phi_{clust} - #phi_{par}) / #phi_{par}; normalized counts"
            sResIntVsTrial2D = "Single e^{-} #delta#phi vs. Trial Number (Normalized); #delta#phi = (#phi_{clust} - #phi_{par}) / #phi_{par}; trial"

    # create hists for resolution vs. trial
    hResIntVsTrialU = ROOT.THStack(
       "hResIntVsTrialU",
       sResIntVsTrialU
    )
    hResIntVsTrialN = ROOT.THStack(
       "hResIntVsTrialN",
       sResIntVsTrialN
    )
    hResIntVsTrial2D = ROOT.TH2D(
        "hResIntVsTrial2D",
        sResIntVsTrial2D,
        50,
        -2.,
        3.,
        nTrials,
        0,
        nTrials
    )
    print("      Reading in files:")

    # set which histogram we're grabbing
    iHist = None
    iFunc = None
    match ana:
        case 0:
            iHist = "hEneRes"
            iFunc = "fEneRes"
        case 1:
            iHist = "hAngRes"
            iFunc = "fAngRes"
        case 2:
            iHist = "hAngRes"
            iFunc = "fAngRes"

    # grab relevant ROOT objects
    hists  = []
    iTrial = 0
    for file in outFiles:

        # open input file and grab hists
        iFile   = ROOT.TFile(os.fspath(file.absolute()), "read")
        hResInt = iFile.Get(iHist)
        print(f"        -- [{iTrial}] hResInt: {hResInt}")

        # create updated names/titles
        sTrial = str(iTrial)
        trial  = "Trial " + sTrial
        uName = hResInt.GetName() + "NoNorm_Trial" + sTrial
        nName = hResInt.GetName() + "Normed_Trial" + sTrial

        # clone histograms
        hResIntU = hResInt.Clone()
        hResIntN = hResInt.Clone()
        hResIntU.SetNameTitle(uName, trial)
        hResIntN.SetNameTitle(nName, trial)

        # adjust 1D attributes
        hResIntU.SetMarkerStyle(24)
        hResIntU.SetFillStyle(0)
        hResIntU.GetXaxis().SetTitleOffset(1.2)
        hResIntU.GetXaxis().SetTitleOffset(1.5)
        hResIntN.SetMarkerStyle(24)
        hResIntN.SetFillStyle(0)
        hResIntN.GetXaxis().SetTitleOffset(1.2)
        hResIntN.GetYaxis().SetTitleOffset(1.5)

        # turn off fit visualization
        hResIntU.GetFunction(iFunc).SetBit(ROOT.TF1.kNotDraw)
        hResIntN.GetFunction(iFunc).SetBit(ROOT.TF1.kNotDraw)

        # make histograms available outside of input file
        hResIntU.SetDirectory(0)
        hResIntN.SetDirectory(0)

        # normalize relevant histograms
        fResIntN  = hResIntN.GetFunction(iFunc)
        intResInt = hResIntN.Integral()
        ampResInt = fResIntN.GetParameter(0)
        if intResInt > 0.0:
            hResIntN.Scale(1.0 / intResInt)
            fResIntN.SetParameter(0, ampResInt / intResInt)

        # add to hists to relevant stacks
        hResIntVsTrialU.Add(hResIntU)
        hResIntVsTrialN.Add(hResIntN)

        # fill row of 2D histogram
        for iBin in range(1, hResIntN.GetNbinsX() + 1):
            hResIntVsTrial2D.SetBinContent(
                iBin,
                iTrial + 1,
                hResIntN.GetBinContent(iBin)
            )

        # adjust 2D attributes
        hResIntU.GetXaxis().SetTitleOffset(1.2)
        hResIntU.GetYaxis().SetTitleOffset(1.5)
        hResIntN.GetXaxis().SetTitleOffset(1.2)
        hResIntN.GetYaxis().SetTitleOffset(1.5)

        # and store in output dicts
        hists.append(hResIntU)
        hists.append(hResIntN)
        iTrial += 1

    # announce end of loop
    print("      Collected relevant ROOT objects:")
    print(hists)

    # set color palette and turn off stat boxes
    ROOT.gStyle.SetPalette(opts.palette)
    ROOT.gStyle.SetOptStat(0)

    # create unnormalized energy difference vs. trial
    cResIntVsTrialU = ROOT.TCanvas("cResNoNorm", "", 950, 950)
    cResIntVsTrialU.cd()
    cResIntVsTrialU.SetRightMargin(0.02)
    cResIntVsTrialU.SetLeftMargin(0.15)
    hResIntVsTrialU.Draw("pfc plc pmc nostack")
    cResIntVsTrialU.BuildLegend(0.7, 0.7, 0.9, 0.9, "", "pf")

    canNameU = opts.baseTag + "." + label + ".resNoNormVsTrial1D." + opts.dateTag + ".png"
    cResIntVsTrialU.SaveAs(canNameU)
    print("      Created unnormalized energy integration resolution vs. trial plot")

    # create normalized energy difference vs. trial
    cResIntVsTrialN = ROOT.TCanvas("cResNormed", "", 950, 950)
    cResIntVsTrialN.cd()
    cResIntVsTrialN.SetRightMargin(0.02)
    cResIntVsTrialN.SetLeftMargin(0.15)
    hResIntVsTrialN.Draw("pfc plc pmc nostack")
    cResIntVsTrialN.BuildLegend(0.7, 0.7, 0.9, 0.9, "", "pf")

    canNameN = opts.baseTag + "." + label + ".resNormVsTrial1D." + opts.dateTag + ".png"
    cResIntVsTrialN.SaveAs(canNameN)
    print("      Created normalized energy integration resolution vs. trial plot")

    # create 2D normalized energy differnece vs. trial (color)
    cResIntVsTrial2DC = ROOT.TCanvas("cEneResNormed2DC", "", 950, 950)
    cResIntVsTrial2DC.SetLeftMargin(0.15)
    cResIntVsTrial2DC.cd()
    hResIntVsTrial2D.Draw("colz")

    canName2DC = opts.baseTag + "." + label + ".resNormed2D_col." + opts.dateTag + ".png"
    cResIntVsTrial2DC.SaveAs(canName2DC)

    # create 2D normalized energy differnece vs. trial (box)
    cResIntVsTrial2DB = ROOT.TCanvas("cEneResNormed2DB", "", 950, 950)
    cResIntVsTrial2DB.SetLeftMargin(0.15)
    cResIntVsTrial2DB.cd()
    hResIntVsTrial2D.Draw("box")

    canName2DB = opts.baseTag + "." + label + ".resNormed2D_box." + opts.dateTag + ".png"
    cResIntVsTrial2DB.SaveAs(canName2DB)
    print("    Created 2D normalized energy integration resolution vs. trial plot")

    # save drawn output
    rootName = opts.baseTag + "." + label + ".rootOutput." + opts.dateTag + ".root"
    with ROOT.TFile(rootName, "recreate") as f:
        cResIntVsTrialU.Write()
        cResIntVsTrialN.Write()
        cResIntVsTrial2DC.Write()
        cResIntVsTrial2DB.Write()
        hResIntVsTrial2D.Write()
        for hist in hists:
            hist.Write()

    # annuounce saving
    print("      Saved ROOT objects")

# -----------------------------------------------------------------------------
# Ax analyses
# -----------------------------------------------------------------------------

def DoAxAnalyses(opts = GlobalOpts):
    """DoAxAnalyses

    Runs a set of built-in
    Ax analyses.

    Args:
      opts: analysis options
    """

    # announce start of Ax analyses
    print("    Running Ax analyses")

    # load saved experiment
    client = Client()
    client = client.load_from_json_file(
        filepath = opts.outExp
    )
    print(f"      Loaded experiment from {opts.outExp}")

    # run calculations
    cards = client.compute_analyses(display = True)
    print(f"      Ran calculations:")
    print(f"        {cards}")

    # save plots for later
    for card in cards:

        # skip summary card (info is already in csv)
        if card.name == "Summary":
            continue

        # otherwise, create save html
        name  = card.name
        title = card.title
        title = title.replace(' ', '').replace('.', '').replace(',', 'vs')
        file  = opts.baseTag + ".axOutput." + name + "." + title + "." + opts.dateTag  + ".html"
        card.get_figure().write_html(file)

    # announce saving
    print("      Saved Ax cards")

# main ========================================================================

if __name__ == "__main__":

    # set up arguments
    parser = ap.ArgumentParser()
    parser.add_argument(
        "--doBasic",
        "--doBasic",
        help = "turn on/off basic analysis",
        nargs = '?',
        const = GlobalOpts.doBasic,
        default = GlobalOpts.doBasic,
        type = bool
    )
    parser.add_argument(
        "--doRoot",
        "--doRoot",
        help = "turn on/off ROOT-based analyses",
        nargs = '?',
        const = GlobalOpts.doRoot,
        default = GlobalOpts.doRoot,
        type = bool
    )
    parser.add_argument(
        "--doAx",
        "--doAx",
        help = "turn on/off Ax-based analyses",
        nargs = '?',
        const = GlobalOpts.doAx,
        default = GlobalOpts.doAx,
        type = bool
    )
    parser.add_argument(
        "--doEne",
        "--doEne",
        help = "process energy output",
        nargs = '?',
        const = GlobalOpts.doEne,
        default = GlobalOpts.doEne,
        type = bool
    )
    parser.add_argument(
        "--doEta",
        "--doEta",
        help = "process eta output",
        nargs = '?',
        const = GlobalOpts.doEta,
        default = GlobalOpts.doEta,
        type = bool
    )
    parser.add_argument(
        "--doPhi",
        "--doPhi",
        help = "process phi output",
        nargs = '?',
        const = GlobalOpts.doPhi,
        default = GlobalOpts.doPhi,
        type = bool
    )
    parser.add_argument(
        "--baseTag",
        "--baseTag",
        help = "prefix of analysis output files",
        nargs = '?',
        const = GlobalOpts.baseTag,
        default = GlobalOpts.baseTag,
        type = str
    )
    parser.add_argument(
        "--dateTag",
        "--dateTag",
        help = "tag indicating date/time in analysis output file",
        nargs = '?',
        const = GlobalOpts.dateTag,
        default = GlobalOpts.dateTag,
        type = str
    )
    parser.add_argument(
        "--outPath",
        "--outPath",
        help = "path to MOBO output files",
        nargs = '?',
        const = GlobalOpts.outPath,
        default = GlobalOpts.outPath,
        type = str
    )
    parser.add_argument(
        "--outEneTxt",
        "--outEneTxt",
        help = "regex pattern to glob relevant MOBO energy output text files",
        nargs = '?',
        const = GlobalOpts.outEneTxt,
        default = GlobalOpts.outEneTxt,
        type = str
    )
    parser.add_argument(
        "--outEtaTxt",
        "--outEtaTxt",
        help = "regex pattern to glob relevant MOBO eta output text files",
        nargs = '?',
        const = GlobalOpts.outEtaTxt,
        default = GlobalOpts.outEtaTxt,
        type = str
    )
    parser.add_argument(
        "--outPhiTxt",
        "--outPhiTxt",
        help = "regex pattern to glob relevant MOBO phi output text files",
        nargs = '?',
        const = GlobalOpts.outPhiTxt,
        default = GlobalOpts.outPhiTxt,
        type = str
    )
    parser.add_argument(
        "--outEneRoot",
        "--outEneRoot",
        help = "regex pattern to glob relevant MOBO energy output root files",
        nargs = '?',
        const = GlobalOpts.outEneRoot,
        default = GlobalOpts.outEneRoot,
        type = str
    )
    parser.add_argument(
        "--outEtaRoot",
        "--outEtaRoot",
        help = "regex pattern to glob relevant MOBO eta output root files",
        nargs = '?',
        const = GlobalOpts.outEtaRoot,
        default = GlobalOpts.outEtaRoot,
        type = str
    )
    parser.add_argument(
        "--outPhiRoot",
        "--outPhiRoot",
        help = "regex pattern to glob relevant MOBO phi output root files",
        nargs = '?',
        const = GlobalOpts.outPhiRoot,
        default = GlobalOpts.outPhiRoot,
        type = str
    )
    parser.add_argument(
        "--outExp",
        "--outExp",
        help = "saved Ax experiment to analyze",
        nargs = '?',
        const = GlobalOpts.outExp,
        default = GlobalOpts.outExp,
        type = str
    )
    parser.add_argument(
        "--palette",
        "--palette",
        help = "ROOT color palette to use",
        nargs = '?',
        const = GlobalOpts.palette,
        default = GlobalOpts.palette,
        type = int
    )
    args = parser.parse_args()

    # announce start
    print("\n  Starting analyses!")

    # set options
    opts = Option(
        doBasic    = args.doBasic,
        doRoot     = args.doRoot,
        doAx       = args.doAx,
        doEne      = args.doEne,
        doEta      = args.doEta,
        doPhi      = args.doPhi,
        baseTag    = args.baseTag,
        dateTag    = args.dateTag,
        outPath    = args.outPath,
        outEneTxt  = args.outEneTxt,
        outEtaTxt  = args.outEtaTxt,
        outPhiTxt  = args.outPhiTxt,
        outEneRoot = args.outEneRoot,
        outEtaRoot = args.outEtaRoot,
        outPhiRoot = args.outPhiRoot,
        outExp     = args.outExp,
        palette    = args.palette
    )
    print(f"    Set options:")
    print(f"      {opts}")

    # run analyses
    if opts.doBasic:
        if opts.doEne:
            DoBasicAnalyses(0, opts.outEneTxt, "ene", opts)
        if opts.doEta:
            DoBasicAnalyses(1, opts.outEtaTxt, "eta", opts)
        if opts.doPhi:
            DoBasicAnalyses(2, opts.outPhiTxt, "phi", opts)
    if opts.doRoot:
        if opts.doEne:
            DoRootAnalyses(0, opts.outEneRoot, "ene", opts)
        if opts.doEta:
            DoRootAnalyses(1, opts.outEtaRoot, "eta", opts)
        if opts.doPhi:
            DoRootAnalyses(2, opts.outPhiRoot, "phi", opts)
    if opts.doAx:
        DoAxAnalyses(opts)

    # announce end
    print("  Analyses complete!\n")

# end =========================================================================

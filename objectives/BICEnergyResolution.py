# =============================================================================
## @file   BICEnergyResolution.py
#  @author Derek Anderson
#  @date   08.28.2025
# -----------------------------------------------------------------------------
# Script to compute energy resolution for a
# specified particle species
# =============================================================================

import awkward as ak
import numpy as np
import pandas as pd
import ROOT
import uproot as ur

from podio.reading import get_reader




def CalculateReso(
    ifile = "../../input/forToyObjectiveTesting.epic25080evt1Ke5th33ele.podio.root",
    ofile = "test.root",
    pdg   = 11
):
    """CalculateReso

    A function to calculate energy resolution for a 
    specified species of particle.

    Keyword arguments:
    ifile -- input file name
    ofile -- output file name
    pdg   -- PDG code of particle species

    """

    # set up histograms, etc. -------------------------------------------------

    # create histogram from extracting resolution
    hres = ROOT.TH1D("hEneRes", ";(E_{clust} - E_{par}) / E_{par}", 50, -2., 3.)
    hres.Sumw2()

    # event loop --------------------------------------------------------------

    # loop through all events
    reader = get_reader(ifile)
    for iframe, frame in enumerate(reader.get("events")):

        # grab truth-cluster associations from frame
        assocs = frame.get("EcalBarrelTruthClusterAssociations")

        # now hunt down clusters associated with electron
        for assoc in assocs:

            # associated truth particle should be the 
            # identified species
            if assoc.getSim().getPDG() != pdg:
                continue

            # calculate energy of truth particle
            msim  = assoc.getSim().getMass()
            pxsim = assoc.getSim().getMomentum().x
            pysim = assoc.getSim().getMomentum().y
            pzsim = assoc.getSim().getMomentum().z
            psim2 = pxsim**2 + pysim**2 + pzsim**2
            esim  = np.sqrt(psim2 + msim**2)

            # and now we should be looking at a cluster
            # connected to _the_ primary
            eres = (assoc.getRec().getEnergy() - esim) / esim
            hres.Fill(eres)

    # resolution calculation --------------------------------------------------

    # fit spectrum with a gaussian to extract peak 
    fres = ROOT.TF1("fEneRes", "gaus(0)", -0.5, 0.5)
    fres.SetParameter(0, hres.Integral())
    fres.SetParameter(1, hres.GetMean())
    fres.SetParameter(2, hres.GetRMS())
    hres.Fit(fres, "r")

    # wrap up script ----------------------------------------------------------

    # save objects
    with ROOT.TFile(ofile, "recreate") as out:
        out.WriteObject(hres, "hEneRes")
        out.WriteObject(fres, "fEneRes")
        out.Close()

    # and return calculated resolution
    return fres.GetParameter(2)

# end =========================================================================

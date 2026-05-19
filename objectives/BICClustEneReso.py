#!/usr/bin/env python3
# =============================================================================
## @file   BICClustEneReso.py
#  @author Derek Anderson
#  @date   08.28.2025
# -----------------------------------------------------------------------------
## @brief Script to compute energy resolution for a
#    specified particle species from BIC clusters.
#
#  Usage if executed directly:
#    ./BICClustEneReso.py \
#        -i <input file> \
#        -o <output file> \
#        -s <pdg code: 11, 22, ...> \
#        -a <mc-cluster associations> (optional)
# =============================================================================

import argparse as ap
import json
import numpy as np
import sys
from dataclasses import dataclass, field
from typing import Any, Dict

import ROOT
from podio.reading import get_reader


# =============================================================================
# Helper classes for the calculation
# =============================================================================

@dataclass
class Options:
    """Options for calculation

    Attributes:
        ifiles: list of input files
        ofile:  output file
        pdg:    PDG code to use (optional)
        assocs: input cluster-particle associations
    """
    ifiles: list[str]
    ofile:  str
    pdg:    int = 22
    assocs: str = "EcalBarrelClusterAssociations"

    def set_opts_from_args(self, args):
        """Set optional members from CLI arguments"""
        self.pdg    = args.pdg
        self.assocs = args.assocs

# default options
DEFAULT_OPTS = Options(
    ifiles = [
        "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/26.02.0/epic_craterlake/SINGLE/gamma/5GeV/45to135deg/gamma_5GeV_45to135deg.0039.eicrecon.edm4eic.root",
    ],
    ofile    = "gam_5GeV_45to135deg.enereso.hist.root",
)


@dataclass
class Hists:
    """Histograms

    Helper class to store and manage
    output histograms

    Attributes:
        tag:   label to append to histogram names
        coord: angular coordinate (theta, eta, ...)
        hists: dictionary of histograms
        bins:  dictionary of binning schemes
    """
    tag:   str = None
    coord: str = None
    hists: Dict[str, Any] = field(default_factory = dict)
    bins:  Dict[str, Any] = field(default_factory = dict)

    def _make_hist_1D(self, name, xbin, title = ""):
        """Make a 1D histogram"""
        tag = f"_{self.tag}"
        if self.tag is None:
            tag = ""
        return ROOT.TH1D(f"{name}{tag}", title, self.bins[xbin][0], self.bins[xbin][1], self.bins[xbin][2])

    def _make_hist_2D(self, name, xbin, ybin, title = ""):
        """Make a 2D histogram"""
        tag = f"_{self.tag}"
        if self.tag is None:
            tag = ""
        return ROOT.TH2D(
            f"{name}{tag}",
            title,
            self.bins[xbin][0],
            self.bins[xbin][1],
            self.bins[xbin][2],
            self.bins[ybin][0],
            self.bins[ybin][1],
            self.bins[ybin][2]
        )

    def _define_bins(self):
        """Define dictionary of bins"""
        self.bins["ene"] = (42, -1.0, 20.0)
        self.bins["res"] = (50, -2.0, 3.0)

    def _define_hists(self):
        """Define dictionary of histograms"""
        self.hists["esim"] = self._make_hist_1D("hParEne", "ene")
        self.hists["erec"] = self._make_hist_1D("hCustEne", "ene")
        self.hists["eres"] = self._make_hist_1D("hEneRes", "res")

    def create(self):
        """Generate histograms"""
        self._define_bins()
        self._define_hists()
        for hist in self.hists.values():
            hist.Sumw2()

    def save(self, file):
        """Save histograms to provided file"""
        for hist in self.hists.values():
            file.WriteObject(hist)

    def get(self, key):
        """Get a particular histogram by key"""
        return self.hists[key]


# =============================================================================
# Energy Resolution Calculation
# =============================================================================

def CalculateClustEneReso(opts: Options = DEFAULT_OPTS) -> Dict[str, float]:
    """CalculateEneReso

    A function to calculate energy resolution for a 
    specified species of particle from BIC clusters.

    Args:
        opts: calculation options

    Returns:
        Dictionary of {key, value} where
        - key: the name of the objective associated with this script,
          in this case case the energy resolution
        - value: the value of the objective, in this case the RMS of
          the fit to the mc-reco differences
    """

    # set up histograms, etc. -------------------------------------------------

    # create histograms
    hist = Hists()
    hist.create()

    # event loops -------------------------------------------------------------

    # loop through input files
    for ifile in opts.ifiles:

        # loop through all events
        reader = get_reader(ifile)
        for iframe, frame in enumerate(reader.get("events")):

            # grab truth-cluster associations from frame
            assocs = frame.get(opts.assocs)

            # now hunt down clusters associated with electron
            for assoc in assocs:

                # associated truth particle should be the
                # identified species
                if assoc.getSim().getPDG() != opts.pdg:
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
                hist.get("esim").Fill(esim)
                hist.get("erec").Fill(assoc.getRec().getEnergy())
                hist.get("eres").Fill(eres)

    # resolution calculation --------------------------------------------------

    # fit spectrum with a gaussian to extract peak 
    fres = ROOT.TF1("fEneRes", "gaus(0)", -0.4, 0.1)
    fres.SetParameter(0, hist.get("eres").Integral())
    fres.SetParameter(1, hist.get("eres").GetMean())
    fres.SetParameter(2, hist.get("eres").GetRMS())
    hist.get("eres").Fit(fres, "r")

    # store output to dump later
    output = {
        "reso_fit_sigma"     : fres.GetParameter(2),
        "reso_fit_sigma_err" : fres.GetParError(2),
        "reso_fit_mean"      : fres.GetParameter(1),
        "reso_fit_mean_err"  : fres.GetParError(1),
    }

    # wrap up script ----------------------------------------------------------

    # save objects
    with ROOT.TFile(opts.ofile, "recreate") as out:
        hist.save(out)
        out.Close()

    # extract specific objective(s) to return
    objectives = {
        "energy_resolution" : output["reso_fit_sigma"]
    }

    ojson = opts.ofile.replace(".root", ".json")
    with open(ojson, 'w') as out:
        odata = output | objectives
        json.dump(odata, out)

    # and return calculated resolution
    return objectives


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":

    # set up argments
    parser = ap.ArgumentParser()
    parser.add_argument(
        "-i",
        "--ifiles",
        help = "Add an input file",
        nargs = '?',
        action = 'append',
        type = str
    )
    parser.add_argument(
        "-o",
        "--ofile",
        help = "Output file",
        nargs = '?',
        const = DEFAULT_OPTS.ofile,
        default = DEFAULT_OPTS.ofile,
        type = str
    )
    parser.add_argument(
        "-s",
        "--pdg",
        help = "PDG code to particle species to look for",
        nargs = '?',
        const = DEFAULT_OPTS.pdg,
        default = DEFAULT_OPTS.pdg,
        type = int
    )
    parser.add_argument(
        "-a",
        "--assocs",
        help = "Cluster-particle associations to use",
        nargs = '?',
        const = DEFAULT_OPTS.assocs,
        default = DEFAULT_OPTS.assocs,
        type = str
    )

    # grab arguments
    args = parser.parse_args()

    # if no input files provided, use default one
    inputs = list()
    if args.ifiles is None:
        inputs.append(DEFAULT_OPTS.ifiles)
    else:
        inputs.extend(args.ifiles)

    # pack options and run analysis
    opts = Options(inputs, args.ofile)
    opts.set_opts_from_args(args)
    CalculateClustEneReso(opts)

# end =========================================================================

#!/usr/bin/env python3
# =============================================================================
## @file    BICEPScan.py
#  @authors Chao Peng,
#           adapted by Derek Anderson
#  @date    04.09.2026
# -----------------------------------------------------------------------------
## @brief Scan E/p cuts for a value optimal for doing e-/pi-
#    (or otherwise) separation with the current BIC configuration,
#    and then apply this cut.
#
#  @usage Must be run inside the eic-shell. Example usage if
#    executed directly:
#      ./BICEPScan.py \
#           -i <input file 1> -i <input file 2> ... \
#           -o <output file> \
#           -a <pdg code to accept: 11, ...> (optional) \
#           -r <pdg code to reject: -211, ...> (optional) \
#           -m <imaging hit collection> (optional) \
#           -s <scfi hit collection> (optional) \
#           -p <mc particle collection> (optional)
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict
import argparse as ap
import json
import numpy as np

import ROOT
from podio.reading import get_reader

# =============================================================================
# Global Constants
# =============================================================================

MAX_NLAYERS = 14


# =============================================================================
# Helper classes for the calculation
# =============================================================================

@dataclass
class Options:
    """Options for calculation

    Attributes:
        ifiles: list of input files
        ofiles: output file
        accept: signal PDG code (eg. 11)
        reject: background PDG code (eg. -211)
        effcut: target efficienty to optimize for
        imhits: input reco imaging hit collection
        schits: imput reco scfi hit collection
        pars:   input MC particle collection
    """
    ifiles: list[str]
    ofile:  str
    accept: int   = 11
    reject: int   = -211
    effcut: float = 0.97
    imhits: str   = "EcalBarrelImagingRecHits"
    schits: str   = "EcalBarrelScFiRecHits"
    pars:   str   = "MCParticles"

    def set_opts_from_args(self, args):
        """Set optional members from CLI arguments"""
        self.accept = args.accept
        self.reject = args.reject
        self.effcut = args.effcut
        self.imhits = args.imhits
        self.schits = args.schits
        self.pars   = args.pars

# default options
DEFAULT_OPTS = Options(
    ifiles = [
        "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/26.02.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0039.eicrecon.edm4eic.root",
        "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/26.02.0/epic_craterlake/SINGLE/pi-/5GeV/45to135deg/pi-_5GeV_45to135deg.0039.eicrecon.edm4eic.root",
    ],
    ofile = "e-Xpi-_5GeV_45to135deg.epscan.hist.root",
)



@dataclass
class Info:
    """Hit and Particle Info

    Helper class to store key information
    on hits and particles

    Attributes:
        magnitude: magnitude of position/momentum of hit/particle
        energy:    energy of hit/particle
        angle:     angular coordinate (theta, eta, ...)
        perp:      radial coordinate (r/pt) of hit/particle
        layer:     layer of hit
        pdg:       PDG code of particle
        vector:    3D position/momentum of hit/particle
    """
    magnitude: float = -999.0
    energy:    float = -999.0
    angle:     float = -999.0
    perp:      float = -999.0
    layer:     int   = -999
    pdg:       int   = 0
    vector: ROOT.Math.XYZVector = ROOT.Math.XYZVector(-999.0, -999.0, -999.0)

    def _set_vector(self, edmvec):
        """Set position vector from an edm4hep::Vector3f"""
        self.vector = ROOT.Math.XYZVector(
            edmvec.x,
            edmvec.y,
            edmvec.z
        )
        self.magnitude = np.sqrt(self.vector.Mag2())
        self.perp      = self.vector.Rho()

    def set_par_info(self, cname, par):
        """Extract info from an edm4hep::MCParticle"""
        self._set_vector(par.getMomentum())
        self.energy = par.getEnergy()
        self.angle  = self.get_angle(cname)
        self.pdg    = par.getPDG()

    def set_hit_info(self, cname, hit):
        """Extract info from an edm4eic::CalorimeterHit"""
        self._set_vector(hit.getPosition())
        self.energy = hit.getEnergy()
        self.angle  = self.get_angle(cname)
        self.layer  = hit.getLayer()

    def get_angle(self, coord) -> float:
        """Get angle based on provided angular coordinate name"""
        angle = -999.0
        match coord:
            case "theta":
                angle = self.vector.Theta()
            case "eta":
                angle = self.vector.Eta()
            case "phi":
                angle = self.vector.Phi()
            case _:
                raise ValueError("Unknown coordinate specified!")
        return angle


@dataclass
class Hists:
    """Histograms

    Helper class to store and manage
    output histograms

    Attributes:
        tag:   label to append to histogram names
        hists: dictionary of histograms
        bins:  dictionary of binning schemes
    """
    tag:   str
    hists: Dict[str, Any] = field(default_factory = dict)
    bins:  Dict[str, Any] = field(default_factory = dict)

    def _make_hist_1D(self, name, xbin, title = ""):
        """Make a 1D histogram"""
        return ROOT.TH1D(f"{name}_{self.tag}", title, self.bins[xbin][0], self.bins[xbin][1], self.bins[xbin][2])

    def _make_hist_2D(self, name, xbin, ybin, title = ""):
        """Make a 2D histogram"""
        return ROOT.TH2D(
            f"{name}_{self.tag}",
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
        self.bins["eta"] = (80, -4.0, 4.0)
        self.bins["phi"] = (180, -3.15, 3.15)
        self.bins["lay"] = (16, -0.5, 15.5)
        self.bins["eop"] = (200, 0.0, 2.0)
        self.bins["eff"] = (200, 0.0, 2.0)
        self.bins["rej"] = (2000, 0.0, 1000.0)
        self.bins["lre"] = (100, 0.0, 10)

    def _define_hists(self):
        """Define dictionary of histograms"""

        # particle histograms
        self.hists["pmc"]   = self._make_hist_1D("hParMom", "ene")
        self.hists["hmc"]   = self._make_hist_1D("hParEta", "eta")
        self.hists["fmc"]   = self._make_hist_1D("hParPhi", "phi")
        self.hists["pxhmc"] = self._make_hist_2D("hParMomVsEta", "eta", "ene")
        self.hists["fxhmc"] = self._make_hist_2D("hParPhiVsEta", "eta", "phi")

        # hit histograms
        self.hists["lscfi"]   = self._make_hist_1D("hScFiLayers", "lay")
        self.hists["escfi"]   = self._make_hist_1D("hScFiEne", "ene")
        self.hists["hscfi"]   = self._make_hist_1D("hScFiEta", "eta")
        self.hists["fscfi"]   = self._make_hist_1D("hScFiPhi", "phi")
        self.hists["exlscfi"] = self._make_hist_2D("hScFiEneVsLayer", "lay", "ene")
        self.hists["exhscfi"] = self._make_hist_2D("hScFiEneVsEta", "eta", "ene")
        self.hists["fxhscfi"] = self._make_hist_2D("hScFiPhiVseta", "eta", "phi")

        # event histograms
        self.hists["minl"]  = self._make_hist_1D("hEvtMinLayer", "lay")
        self.hists["maxl"]  = self._make_hist_1D("hEvtMaxLayer", "lay")
        self.hists["sumxl"] = self._make_hist_2D("hEvtSumVsLayer", "lay", "ene")
        self.hists["sumxd"] = self._make_hist_2D("hEvtSumVsDepth", "lay", "ene")
        self.hists["epxd"]  = self._make_hist_2D("hEvtEPVsDepth", "lay", "eop")

        # per integration depth histograms
        for idepth in range(MAX_NLAYERS + 1):
            self.hists[f"sumxd{idepth}"] = self._make_hist_1D(f"hEvtSumVsDepth_Layer{idepth}", "ene")
            self.hists[f"epxd{idepth}"]  = self._make_hist_1D(f"hEvtEPVsDepth_Layer{idepth}", "eop")

        # objective histograms
        self.hists["epcut"] = self._make_hist_1D("hObjEPCutVsDepth", "lay")
        self.hists["effxl"] = self._make_hist_1D("hObjEffVsDepth", "lay")
        self.hists["rejxl"] = self._make_hist_1D("hObjRejVsDepth", "lay")
        self.hists["lrexl"] = self._make_hist_1D("hObjLogRejVsDepth", "lay")
        self.hists["effxc"] = self._make_hist_2D("hObjEffVsEPCut", "eop", "eff")
        self.hists["rejxc"] = self._make_hist_2D("hObjRejVsEPCut", "eop", "rej")
        self.hists["lrexc"] = self._make_hist_2D("hObjLogRejVsEPCut", "eop", "lre")

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
        return self.hists[key]


# =============================================================================
# E/p Scan
# =============================================================================

def DoEPScan(opts: Options = DEFAULT_OPTS) -> Dict[str, float]:
    """Scan E/p cuts

    A function to scan E/p cuts which optimize particle separation
    for efficiency of signal particles. Calculation follows this
    algorithm:

        1. For all events do:
           a. Compute E/p as a function of "integration
              depth" (N SciFi layers summed over) between
              the sum of ScFi reco hit energy and the
              primary particle momentum
        2. For each integration depth do:
           a. Find the minimum E/p threshold such that
              you retain at least X% of signal ("accepted")
              particles
           b. Apply threshold to background ("rejected")
              particles, and compute rejection power
        3. Return the largest computed rejection power

    Args:
        opts: calculation options

    Returns:
        Dictionary of {key, value} where
        - key: the name of the objective associated
          with this script, in this case 'rejection'
        - value: the value of the objective, in this
          case 1 over the efficiency of particles
          to reject SURVIVING the E/p cut
    """

    # set up histograms -------------------------------------------------------

    # create histograms for events
    hists = {
        opts.accept : Hists(str(opts.accept).replace("-", "M")),
        opts.reject : Hists(str(opts.reject).replace("-", "M")),
    }
    for hist in hists.values():
        hist.create()

    # event loops -------------------------------------------------------------

    # loop through input files
    for ifile in opts.ifiles:

        # loop through all events
        reader = get_reader(ifile)
        for iframe, frame in enumerate(reader.get("events")):

            # grab collections 
            imhits = frame.get(opts.imhits)
            schits = frame.get(opts.schits)
            mcpars = frame.get(opts.pars)

            # skip event if no imaging or scfi hits
            if len(imhits) < 1 or len(schits) < 1:
                continue

            # pick out the primary particle
            primary = None
            for par in mcpars:
                status    = par.getGeneratorStatus()
                acceptant = par.getPDG() == opts.accept and status == 1
                rejectant = par.getPDG() == opts.reject and status == 1
                if acceptant or rejectant:
                    primary = par
                    break

            # if for some reason no primary was found,
            # skip event
            if primary is None:
                print(f"Warning! Frame {iframe} has no primary in file:\n  -- {ifile}")
                continue

            # scrape particle info for analysis, histogramming 
            pinfo = Info()
            pinfo.set_par_info("eta", primary)
            hists[pinfo.pdg].get("pmc").Fill(pinfo.magnitude)
            hists[pinfo.pdg].get("hmc").Fill(pinfo.angle)
            hists[pinfo.pdg].get("fmc").Fill(pinfo.get_angle("phi"))
            hists[pinfo.pdg].get("pxhmc").Fill(pinfo.angle, pinfo.magnitude)
            hists[pinfo.pdg].get("fxhmc").Fill(pinfo.angle, pinfo.get_angle("phi"))

            # dictionary to keep track of the sum of energy
            # in each ScFi layer
            layersums = [0.0] * MAX_NLAYERS

	    # sum hits
            minlayer = 999
            maxlayer = -999
            for schit in schits:

                layer = schit.getLayer()
                if layer > maxlayer:
                    maxlayer = layer
                if layer < minlayer:
                    minlayer = layer
                layersums[schit.getLayer()] += schit.getEnergy()

                # scrape hit info for histogramming
                hinfo = Info()
                hinfo.set_hit_info("eta", schit)
                hists[pinfo.pdg].get("lscfi").Fill(layer)
                hists[pinfo.pdg].get("escfi").Fill(hinfo.energy)
                hists[pinfo.pdg].get("hscfi").Fill(hinfo.angle)
                hists[pinfo.pdg].get("fscfi").Fill(hinfo.get_angle("phi"))
                hists[pinfo.pdg].get("exlscfi").Fill(layer, hinfo.energy)
                hists[pinfo.pdg].get("exhscfi").Fill(hinfo.angle, hinfo.energy)
                hists[pinfo.pdg].get("fxhscfi").Fill(hinfo.angle, hinfo.get_angle("phi"))

            # record min/max layers
            hists[pinfo.pdg].get("minl").Fill(minlayer)
            hists[pinfo.pdg].get("maxl").Fill(maxlayer)

            # sum energy from 1st layer up to
            # maxlayer, compute E/p for each
            # integration depth
            total = 0.0
            for ilayer, sumene in enumerate(layersums):
                hists[pinfo.pdg].get("sumxl").Fill(ilayer + 1, sumene)
                if ilayer + 1 > maxlayer:
                    continue
                else:
                    total += sumene
                    pmc    = np.sqrt(pinfo.vector.Mag2())
                    ep     = total / pmc
                    hists[pinfo.pdg].get("sumxd").Fill(ilayer + 1, total)
                    hists[pinfo.pdg].get(f"sumxd{ilayer}").Fill(total)
                    hists[pinfo.pdg].get("epxd").Fill(ilayer + 1, ep)
                    hists[pinfo.pdg].get(f"epxd{ilayer}").Fill(ep)

    # e/p cut, rejection power calculation ------------------------------------

    # determine E/p cut for different integration depths
    # based on efficiency of PID to accept
    output = dict()
    maxrej = 0.0
    maxlay = MAX_NLAYERS + 1
    for ilayer in range(MAX_NLAYERS):

        ephist = hists[opts.accept].get(f"epxd{ilayer}")
        epsum  = ephist.Integral()

        # now determine where to place cut by finding
        # last bin with cumulative sum ABOVE percent
        # set by effcut
        icut  = 0
        epcut = 0.0
        epeff = 0.0
        if epsum > 0.0:
            for ibin in range(ephist.GetNbinsX() + 1, 1, -1):
                epcum = ephist.Integral(ibin, ephist.GetNbinsX())
                epeff = epcum / epsum
                if epeff >= opts.effcut:
                    epcut = ephist.GetBinLowEdge(ibin)
                    icut  = ibin
                    break

        # calculate rejection power (for completeness)
        # and log(rejection power)
        eprej = 0.0
        eplre = 0.0
        if epeff > 0.0:
            eprej = 1. / epeff
            eplre = np.log(eprej)

        # store PID to accept output to dump later
        output[f"ep_cut_layer_{ilayer + 1}"]     = epcut
        output[f"eff_accept_layer_{ilayer + 1}"] = epeff
        output[f"rej_accept_layer_{ilayer + 1}"] = eprej
        hists[opts.accept].get("epcut").SetBinContent(ilayer + 2, epcut)
        hists[opts.accept].get("effxl").SetBinContent(ilayer + 2, epeff)
        hists[opts.accept].get("rejxl").SetBinContent(ilayer + 2, eprej)
        hists[opts.accept].get("lrexl").SetBinContent(ilayer + 2, eplre)
        hists[opts.accept].get("effxc").Fill(epcut, epeff)
        hists[opts.accept].get("rejxc").Fill(epcut, eprej)
        hists[opts.accept].get("lrexc").Fill(epcut, eplre)

        # now apply E/p cut on PID to reject to determine
        # objective (rejection power)
        rehist = hists[opts.reject].get(f"epxd{ilayer}")
        resum  = rehist.Integral()
        recum  = rehist.Integral(icut, rehist.GetNbinsX() + 1)
        reeff  = recum / resum if resum > 0.0 else 0.0
        rerej  = 1. / reeff if reeff > 0.0 else 0.0
        relre  = np.log(rerej) if rerej > 0.0 else 0.0

        # store PID to reject output to dump later
        output[f"eff_reject_layer_{ilayer + 1}"] = reeff
        output[f"rej_reject_layer_{ilayer + 1}"] = rerej
        hists[opts.reject].get("epcut").SetBinContent(ilayer + 2, epcut)
        hists[opts.reject].get("effxl").SetBinContent(ilayer + 2, reeff)
        hists[opts.reject].get("rejxl").SetBinContent(ilayer + 2, rerej)
        hists[opts.reject].get("lrexl").SetBinContent(ilayer + 2, relre)
        hists[opts.reject].get("effxc").Fill(epcut, reeff)
        hists[opts.reject].get("rejxc").Fill(epcut, rerej)
        hists[opts.reject].get("lrexc").Fill(epcut, relre)

        # identify integration depth that gives largest rejection power
        if rerej > maxrej:
            maxrej = rerej
            maxlay = ilayer + 1

    # wrap up script ----------------------------------------------------------

    with ROOT.TFile(opts.ofile, "recreate") as out:
        for hist in hists.values():
            hist.save(out)

    # extract specific objective(s) to return
    objectives = {
        f"rejection_power_{opts.reject}" : output[f"rej_reject_layer_{maxlay}"]
    }

    ojson = opts.ofile.replace(".root", ".json")
    with open(ojson, 'w') as out:
        odata = output | objectives
        json.dump(odata, out)

    return objectives


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":

    # set up arguments
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
        "-a",
        "--accept",
        help = "PDG code of particle species to accept",
        nargs = '?',
        const = DEFAULT_OPTS.accept,
        default = DEFAULT_OPTS.accept,
        type = int
    )
    parser.add_argument(
        "-r",
        "--reject",
        help = "PDG code of particle species to reject",
        nargs = '?',
        const = DEFAULT_OPTS.reject,
        default = DEFAULT_OPTS.reject,
        type = int
    )
    parser.add_argument(
        "-e",
        "--effcut",
        help = "Target efficiency to optimize E/p cut for",
        nargs = '?',
        const = DEFAULT_OPTS.effcut,
        default = DEFAULT_OPTS.effcut,
        type = float
    )
    parser.add_argument(
        "-m",
        "--imhits",
        help = "Imaging reco hit collection to use",
        nargs = '?',
        const = DEFAULT_OPTS.imhits,
        default = DEFAULT_OPTS.imhits,
        type = str
    )
    parser.add_argument(
        "-s",
        "--schits",
        help = "ScFi reco hit collection to use",
        nargs = '?',
        const = DEFAULT_OPTS.schits,
        default = DEFAULT_OPTS.schits,
        type = str
    )
    parser.add_argument(
        "-p",
        "--pars",
        help = "MC particle collection to use",
        nargs = '?',
        const = DEFAULT_OPTS.pars,
        default = DEFAULT_OPTS.pars,
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

    # pack options and run analsysis
    opts = Options(inputs, args.ofile)
    opts.set_opts_from_args(args)
    DoEPScan(opts)

# end =========================================================================

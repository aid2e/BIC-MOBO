#!/usr/bin/env python3
# =============================================================================
## @file    BICHitAngReso.py
#  @authors Minho Kim,
#           adapted by Derek Anderson
#  @date    02.11.2026
# -----------------------------------------------------------------------------
## @brief Compute angular resolution of BIC AstroPix layers. This script
#    runs a simple calculation to compute the angular resolution of the
#    BIC AstroPix (imaging) layers for a specified particle species.
#
#  @usage Must be run inside the eic-shell. Example usage if executed
#    directly:
#      ./BICHitAngReso.py \
#          -i <input file 1> -i <input file 2> ... \
#          -o <output file> \
#          -c <coordinate: eta, phi, ...> \
#          -p <pdg code: 11, 22, ...> \
#          -r <reco hit collection> (optional) \
#          -m <mc particle collection> (optional) \
#          -a <mc-cluster associtions> (optional)
#          -e <layer to exclude> -e <layer to exclude> ...
# =============================================================================

import argparse as ap
import numpy as np
import sys
from dataclasses import dataclass
from typing import Dict

import ROOT
from podio.reading import get_reader


# =============================================================================
# Helper classes for the calculation
# =============================================================================

@dataclass
class Options:
    """Options for calculation

    Attributes:
        ifiles:   list of input files
        ofile:    output file
        excludes: list of layer indices to exclude
        angle:    angular coordinate to use (theta, eta, ...)
        pdg:      PDG code to use (optional)
        hits:     input reco hit collection
        pars:     input MC particle collection
        assocs:   input cluster-particle associations
    """
    ifiles:   list[str]
    ofile:    str
    excludes: list[int]
    angle:    str = "eta"
    pdg:      int = 11
    hits:     str = "EcalBarrelImagingRecHits"
    pars:     str = "MCParticles"
    assocs:   str = "EcalBarrelImagingClusterAssociations"

    def set_opts_from_args(self, args):
        """Set optional members from CLI arguments"""
        self.angle  = args.angle
        self.pdg    = args.pdg
        self.hits   = args.hits
        self.pars   = args.pars
        self.assocs = args.assocs

# default options
DEFAULT_OPTS = Options(
    ifiles = [
        "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.12.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0099.eicrecon.edm4eic.root"
    ],
    ofile    = "e-_5GeV_45to135deg.0099.angreso.hist.root",
    excludes = [],
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
        coord: angular coordinate (theta, eta, ...)
        hists: dictionary of histograms
        bins:  dictionary of binning schemes
    """
    tag:   str
    coord: str
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
        self.bins["hit"] = (100, -0.5, 4.5)
        self.bins["eta"] = (80, -4.0, 4.0)
        self.bins["phi"] = (180, -3.15, 3.15)
        self.bins["the"] = (180, -3.15, 3.15)
        self.bins["xy"]  = (1500 -1500.0, 1500.0)
        self.bins["zed"] = (3000, -3000.0, 3000.0)
        self.bins["rad"] = (775, -50.0, 1500.0
        self.bins["lay"] = (8, -0.5, 7.5)
        self.bins["eff"] = (200, 0.0, 2.0)
        self.bins["res"] = (80, -0.2, 0.2)

    def _define_hists(self):
        """Define dictionary of histograms"""

        # select relevant binning for coordinate
        angle = None
        match coord:
            case "theta":
                angle = "the"
            case "eta":
                angle = "eta"
            case "phi":
                angle = "phi"
            case _:
                raise ValueError("Unknown coordinate specified!")

        # particle histograms
        self.hists["emc"]   = self._make_hist_1D("hParEne", "ene")
        self.hists["hmc"]   = self._make_hist_1D("hParEta", "eta")
        self.hists["amc"]   = self._make_hist_1D("hParAng", angle)
        self.hists["exhmc"] = self._make_hist_1D("hParEneVsEta", "eta", "ene")
        self.hists["examc"] = self._make_hist_1D("hParEneVsAng", angle, "ene")

        # cluster histograms
        self.hists["eclu"] = self._make_hist_1D("hClustEne", "ene")

        # all hit histograms
        self.hists["eima"]   = self._make_hist_1D("hAllImageEne", "hit")
        self.hists["hima"]   = self._make_hist_1D("hAllImageEta", "eta")
        self.hists["rima"]   = self._make_hist_1D("hAllImageR", "rad")
        self.hists["zima"]   = self._make_hist_1D("hAllImageZ", "zed")
        self.hists["aima"]   = self._make_hist_1D("hAllImageAng", angle)
        self.hists["lima"]   = self._make_hist_1D("hAllImageLayer", "lay")
        self.hists["exhima"] = self._make_hist_1D("hAllImageEneVsEta", "eta", "hit")
        self.hists["exrima"] = self._make_hist_1D("hAllImageEneVsRad", "rad", "hit")
        self.hists["exlima"] = self._make_hist_1D("hAllImageEneVsLayer", "lay", "hit")
        self.hists["exaima"] = self._make_hist_1D("hAllImageEneVsAng",angle, "hit")
        self.hists["yxxima"] = self._make_hist_1D("hAllImageYVsX", "xy", "xy")
        self.hists["rxzima"] = self._make_hist_1D("hAllImageRVsZ", "zed", "rad")
        self.hists["axlima"] = self._make_hist_1D("hAllImageAngVsLayer", "lay", angle)

        # max hit histograms
        self.hists["emax"]   = self._make_hist_1D("hMaxImageEne", "hit")
        self.hists["hmax"]   = self._make_hist_1D("hMaxImageEta", "eta")
        self.hists["rmax"]   = self._make_hist_1D("hMaxImageR", "rad")
        self.hists["zmax"]   = self._make_hist_1D("hMaxImageZ", "zed")
        self.hists["amax"]   = self._make_hist_1D("hMaxImageAng", angle)
        self.hists["lmax"]   = self._make_hist_1D("hMaxImageLayer", "lay")
        self.hists["exhmax"] = self._make_hist_1D("hMaxImageEneVsEta", "eta", "hit")
        self.hists["exrmax"] = self._make_hist_1D("hMaxImageEneVsRad", "rad", "hit")
        self.hists["examax"] = self._make_hist_1D("hMaxImageEneVsAng", "ang", "hit")
        self.hists["yxxmax"] = self._make_hist_1D("hMaxImageYVsX", "xy", "xy")
        self.hists["rxzmax"] = self._make_hist_1D("hMaxImageRVsZ", "zed", "rad")

        # event histograms
        self.hists["maxe"] = self._make_hist_1D("hEvtMaxImageEne", "hit")
        self.hists["minl"] = self._make_hist_1D("hEvtMinLayer", "lay")

        # objective histograms
        self.hists["eeff"]  = self._make_hist_1D("hEffEne", "ene")
        self.hists["heff"]  = self._make_hist_1D("hEffEta", "eta")
        self.hists["ares"]  = self._make_hist_1D("hAngRes", "res")
        self.hists["resxl"] = self._make_hist_1D("hAngResVsMaxHitLayer", "lay", "res")

        # TODO add efficiency * reso histogram

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
# Angular Resolution Calculation
# =============================================================================

def CalculateHitAngReso(opts: Options = DEFAULT_OPTS) -> Dict[str, float]:
    """Calculate angular resolution

    A function to calculate angular resolution for a 
    specified species of particle from BIC imaging
    hits according to this algorithm:

        1. Find the imaging cluster associated to thrown
           electron
        2. Locate the most energetic hit in each layer
           of the imaging cluster
        3. From these, select the hit in the most
           upstream layer and calculate the difference
           in angle
        4. Fit the main peak of the distribution of
           differences and extract the RMS of the
           peak
        5. Return the RMS as the resolution

    Args:
        opts: calculation options

    Returns:
        Dictionary of {key, value} where
        - key: the name of the objective associated with this script,
          in this case "resolution"
        - value: the value of the objective, in this case the RMS of
          the fit to the mc-reco differences
    """

    # sanitize coordinate input
    coord = opts.angle
    coord = coord.lower()

    # set up histograms, etc. -------------------------------------------------

    # set variable for axis accordingly 
    var = "x"
    match coord:
        case "theta":
            var = "#theta"
        case "eta":
            var = "#eta"
        case "phi":
            var = "#phi"
        case _:
            raise ValueError("Unknown coordinate specified!")

    # create histograms
    hist = Hists(str(opts.pdg).replace("-", "M"))
    hist.create()

    # event loops -------------------------------------------------------------

    # loop through input files
    for ifile in opts.ifiles:

        # loop through all events
        reader = get_reader(ifile)
        for iframe, frame in enumerate(reader.get("events")):

            # grab relevant branches
            rehits = frame.get(opts.hits)
            mcpars = frame.get(opts.pars)
            assocs = frame.get(opts.assocs)

            # pick out the primary particle
            primary = None
            for par in mcpars:
                status = par.getGeneratorStatus()
                if par.getPDG() == opts.pdg and status == 1:
                   primary = par
                    break

            # if for some reason no primary was found,
            # skip event
            if primary is None:
                print(f"Warning! Frame {iframe} has no primary in file:\n  -- {ifile}")
                continue

            # scrape particle info for histogramming
            pinfo = Info()
            pinfo.set_par_info(coord, primary)
            hpar.Fill(pinfo.energy)

            # dictionaries to keep track of max energy
            # hits in each layer
            maxenes = {
                1 : 0.0,
                2 : 0.0,
                3 : 0.0,
                4 : 0.0,
                5 : 0.0,
                6 : 0.0
            }
            maxhits = dict()

            # now identify the most energetic hit in
            # each layer associated with the primary
            cluster = None
            for assoc in assocs:

                if primary != assoc.getSim():
                    continue
                else:
                    cluster = assoc.getRec()

                # loop through hits to check layers
                for hit in assoc.getRec().getHits():

                    layer = hit.getLayer()
                    if layer > 6:
                        print(f"Warning! Hit {hit.getObjectID().index} has a layer above 6 ({layer})!")
                        continue

                    if layer in excludes:
                        continue

                    if hit.getEnergy() > maxenes[layer]:
                        maxenes[layer] = hit.getEnergy()
                        maxhits[layer] = hit

            if cluster is None or len(maxhits) == 0:
                continue

            # fill hists for efficiency
            heff.Fill(pinfo.energy)
            hclust.Fill(cluster.getEnergy())

            # pick out most upstream layer from
            # most energetic hits
            minlayer = min(maxhits.keys())

            # scrape info from max hit in most
            # upstream layer
            hinfo = Info()
            hinfo.set_hit_info(coord, maxhits[minlayer])

            # calculate difference
            hdiff.Fill(hinfo.angle - pinfo.angle)

            # fill hists
            hmax.Fill(hinfo.energy)
            hlay.Fill(minlayer)
            hmxl.Fill(minlayer, hinfo.energy)

    # resolution calculation --------------------------------------------------

    # extract hist properties to initialize fit
    muhist  = hdiff.GetMean()
    rmshist = hdiff.GetRMS()
    inthist = hdiff.Integral()

    # set up a gaussian to extract main peak
    #   - FIXME func range should be tied to hist range
    fdiff = ROOT.TF1("fAngRes", "gaus(0)", -0.2, 0.2)
    fdiff.SetParameters(
        inthist,
        muhist,
        rmshist
    )

    # fit histogram over nonzero bins
    ifirst   = hdiff.FindFirstBinAbove(0.0)
    ilast    = hdiff.FindLastBinAbove(0.0)
    first_lo = hdiff.GetBinLowEdge(ifirst)
    last_hi  = hdiff.GetBinLowEdge(ilast + 1)
    hdiff.Fit("fAngRes", "", "", first_lo, last_hi)

    # calculate full-width-half-max
    mumain     = fdiff.GetParameter(1)
    maximum    = fdiff.Eval(mumain)
    halfmax_lo = fdiff.GetX(maximum / 2.0, first_lo, mumain)
    halfmax_hi = fdiff.GetX(maximum / 2.0, mumain, last_hi)
    fwhm       = halfmax_hi - halfmax_lo

    # wrap up script ----------------------------------------------------------

    # save objects
    with ROOT.TFile(opts.ofile, "recreate") as out:
        hist.save(out)
        out.Close()

    # write out key info to a text file for
    # extraction later
    otext = opts.ofile.replace(".root", ".txt")
    with open(otext, 'w') as out:
        out.write(f"{fdiff.GetParameter(2)}\n")
        out.write(f"{fdiff.GetParError(2)}\n")
        out.write(f"{fdiff.GetParameter(1)}\n")
        out.write(f"{fdiff.GetParError(1)}\n")
        out.write(f"{fwhm}\n")

    # and return fit width as resolution
    return {f"{opts.angle}_resolution", fdiff.GetParameter(2)}


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
        "-c",
        "--angle",
        help = "Angular coordinate to calculate resolution on",
        nargs = '?',
        const = DEFAULT_OPTS.angle,
        default = DEFAULT_OPTS.angle,
        type = str
    )
    parser.add_argument(
        "-s",
        "--pdg",
        help = "PDG code of particle species to look for",
        nargs = '?',
        const = DEFAULT_OPTS.pdg,
        default = DEFAULT_OPTS.pdg,
        type = int
    )
    parser.add_argument(
        "-r",
        "--hits",
        help = "Reco hit collection to use",
        nargs = '?',
        const = DEFAULT_OPTS.hits,
        default = DEFAULT_OPTS.hits,
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
    parser.add_argument(
        "-a",
        "--assocs",
        help = "Cluster-particle associations to use",
        nargs = '?',
        const = DEFAULT_OPTS.assocs,
        default = DEFAULT_OPTS.assocs,
        type = str
    )
    parser.add_argument(
        "-e",
        "--excludes",
        help = "Add a layer to exclude",
        nargs = '?',
        action = 'append',
        type = int
    )

    # grab arguments
    args = parser.parse_args()

    # if no input files provided, use default one
    inputs = list()
    if args.ifiles is None:
        inputs.append(DEFAULT_OPTS.ifiles)
    else:
        inputs.extend(args.ifiles)

    # if no excluded layers provided, use default one
    excludes = list()
    if args.excludes is None:
        excludes.append(DEFAULT_OPTS.excludes)
    else:
        excludes.extend(args.excludes)

    # pack options and run analysis
    opts = Options(inputs, args.ofile, excludes)
    opts.set_opts_from_args(args)
    CalculateHitAngReso(opts)

# end =========================================================================

# =============================================================================
## @file   test-eic-tools.py
#  @author Derek Anderson
#  @date   09.02.2025
# -----------------------------------------------------------------------------
## @brief A small script to test various features
#    of the EICMOBOTestTools module.
#
#  TODO convert to use pytest
# =============================================================================

import pprint

import EICMOBOTestTools as emt



# (0) Test ConfigParser -------------------------------------------------------

# these should work
enable2 = emt.GetParameter("enable_staves_2", "../configuration/parameters.config")
enable3 = emt.GetParameter("enable_staves_3", "../configuration/parameters.config")

# grab variables
path2, type2, units2 = emt.GetPathElementAndUnits(enable2)
path3, type3, units3 = emt.GetPathElementAndUnits(enable3)

print(f"[0][enable_staves_2] path = {path2}, type = {type2}, units = {units2}")
print(f"[0][enable_staves_3] path = {path3}, type = {type3}, units = {units3}")

try:
    enable3 = emt.GetParameter("eanble_satvse_3", "parameters.config")
except:
    print(f"[0][enable_staves_3] exception raised!")
finally:
    print(f"[0][enable_staves_3] typo generated error as expected!")

# (1) Test GeometryEditor -----------------------------------------------------

# create a geometry editor
geditor1A = emt.GeometryEditor("../configuration/run.config", "test1A")
geditor1B = emt.GeometryEditor("../configuration/run.config", "test1B")

# copy geo source to run directories
geditor1A.CopyGeoToRunDir()
geditor1B.CopyGeoToRunDir()

# edit a couple parameters in one compact file
geditor1A.EditCompact(enable2, 1, "test1A")
geditor1A.EditCompact(enable3, 0, "test1A")
print(f"[1][test A] set values of staves 2, 3 to 1, 0 respectively")

# now edit config files associated with
# compact; the 2nd line should leave
# config files unmodified
geditor1A.EditRelatedFiles(enable2, "test1A")
geditor1A.EditRelatedFiles(enable3, "test1A")
print(f"[1][Test A] edited related files")

# create a 2nd compact file with multiple
# subsystems modified
enable5 = emt.GetParameter("enable_staves_5", "../configuration/parameters.config")
geditor1B.EditCompact(enable5, 1, "test1B")
print(f"[1][test B] set value of stave 5 to 1")

# now edit all related config files
geditor1B.EditRelatedFiles(enable5, "test1B")
print(f"[1][test B] edited related files")

# (2) Test generators  --------------------------------------------------------

# create a sim generator and parse enviroment
# config for easy use
simgen = emt.SimGenerator("../configuration/run.config")
enviro = emt.ReadJsonFile("../configuration/run.config")
intest = "single_electron"
inputs = enviro["sim_input"][intest]

# try to create a simulation command
dosimA = simgen.MakeCommand("test2A", intest, inputs["location"], "central.e5ele.py", inputs["type"])
dosimB = simgen.MakeCommand("test2B", intest, inputs["location"], "central.e5ele.py", inputs["type"])
print(f"[2][Test A] Created commands to do simulation:")
print(f"  {dosimA}")
print(f"  {dosimB}")

# grab config name
config = enviro["det_config"]

# now try to create a simulation driver script
runsimA = simgen.MakeScript("test2A", intest, "central.e5ele.py", config, dosimA)
runsimB = simgen.MakeScript("test2B", intest, "central.e5ele.py", config, dosimB)
print(f"[2][Test B] created driver scripts for simulation:")
print(f"  {runsimA}")
print(f"  {runsimB}")

# create a rec generator
recgen = emt.RecGenerator("../configuration/run.config")

# try to create a reco command
dorecA = recgen.MakeCommand("test2A", intest, "central.e5ele.py")
dorecB = recgen.MakeCommand("test2B", intest, "central.e5ele.py")
print(f"[2][Test C] Created commands to do reconstruction:")
print(f"  {dorecA}")
print(f"  {dorecB}")

# and now try to create a reconstruction driver script
runrecA = recgen.MakeScript("test2A", intest, "central.e5ele.py", config, dorecA)
runrecB = recgen.MakeScript("test2B", intest, "central.e5ele.py", config, dorecB)
print(f"[2][Test D] Created driver scripts for reconstruction:")
print(f"  {runrecA}")
print(f"  {runrecB}")

# create an ana generator
anagen = emt.AnaGenerator("../configuration/run.config", "../configuration/objectives.config")

# recreate output name for input to
# test ana generator
steeTag = emt.ConvertSteeringToTag("central.e5ele.py")
simOutA = emt.MakeOutName("test2A", intest, steeTag, "sim")
simOutB = emt.MakeOutName("test2B", intest, steeTag, "sim")
recOutA = emt.MakeOutName("test2A", intest, steeTag, "rec")
recOutB = emt.MakeOutName("test2B", intest, steeTag, "rec")
outDirA = enviro["out_path"] + "/test2A/" + recOutA
outDirB = enviro["out_path"] + "/test2B/" + recOutB

# try to create an analysis command
doanaA, ofileA = anagen.MakeCommand("test2A", intest, "ElectronEnergyResolution", simOutA, recOutA)
doanaB, ofileB = anagen.MakeCommand("test2B", intest, "ElectronEnergyResolution", simOutB, recOutB)
print(f"[2][Test E] Created commands to do analysis")
print(f"  (A) command = {doanaA}")
print(f"      output  = {ofileA}")
print(f"  (B) command = {doanaB}")
print(f"      output  = {ofileB}")

# try to create an analysis script
runanaA = anagen.MakeScript("test2A", intest, "ElectronEnergyResolution", doanaA)
runanaB = anagen.MakeScript("test2B", intest, "ElectronEnergyResolution", doanaB)
print(f"[2][Test F] Created driver scripts for analysis")
print(f"  {runanaA}")
print(f"  {runanaB}")

# create geo editors and edit a few parameters
geditor2A = emt.GeometryEditor("../configuration/run.config", "test2A")
geditor2B = emt.GeometryEditor("../configuration/run.config", "test2B")
geditor2A.CopyGeoToRunDir()
geditor2B.CopyGeoToRunDir()
geditor2A.EditCompact(enable2, 1, "test2A")
geditor2A.EditCompact(enable3, 0, "test2A")
geditor2A.EditRelatedFiles(enable2, "test2A")
geditor2A.EditRelatedFiles(enable3, "test2A")
geditor2B.EditCompact(enable5, 1, "test2B")
geditor2B.EditRelatedFiles(enable5, "test2B")

# now create scripts to build geo & check
# overlaps
rungeoA = geditor2A.MakeBuildScript("test2A", config)
rungeoB = geditor2B.MakeBuildScript("test2B", config)
print(f"[2][Test G] Created build scripts for geometry")
print(f"  {rungeoA}")
print(f"  {rungeoB}")

# (3) Test trial manager ------------------------------------------------------

# create a trial managers
trimanA = emt.TrialManager("../configuration/run.config",
                           "../configuration/parameters.config",
                           "../configuration/objectives.config",
                           "test3A")
trimanB = emt.TrialManager("../configuration/run.config",
                           "../configuration/parameters.config",
                           "../configuration/objectives.config")

# create new parameters to test
nupar3 = {
    "enable_staves_2" : 1,
    "enable_staves_3" : 0,
    "enable_staves_5" : 1,
    "enable_staves_6" : 1
}

# make run script
dorun3A, ofiles3A = trimanA.MakeTrialScript(nupar3)
print(f"[3][Test A] Created driver script for entire trial:")
print(f"  script  = {dorun3A}")
print(f"  outputs =")
pprint.pprint(ofiles3A)

# now try to make AND run an entire script
trimanB.DoTrial(nupar3)
print("[3][Test B] Created and ran entire trial")

# end =========================================================================

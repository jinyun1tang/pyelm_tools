import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--h0file', dest="h0file", metavar='h0file', type=str, nargs=1, default=[""],
  help='the original app to be cloned')


args = parser.parse_args()

histf=args.h0file[0]


elmfl=Dataset(histf,"r")

area=elmfl.variables["area"][:]
landfr=elmfl.variables["landfrac"][:]
nh3flx_soie=elmfl.variables["NBP"][:]
garea=landfr*area

g2pg=1.e6*365.0*86400.0*1.e-15
gnh3flx=np.squeeze(nh3flx_soie*garea)

elmfl.close()

print np.nansum(gnh3flx)*g2pg

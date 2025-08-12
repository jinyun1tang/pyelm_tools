import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse
import re
import warnings
warnings.filterwarnings("ignore")

def get_gppts(histf):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    gpp_flx=elmfl.variables["GPP"][:]
    garea=landfr*area
    nts=gpp_flx.shape[0]
    gppts=np.zeros(nts)
    for j in range(nts):
        gppflx=np.squeeze(gpp_flx[j,:,:]*garea)
        gppts[j]=np.nansum(gppflx)
    elmfl.close()
    return gppts

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--h0file', dest="h0file", metavar='h0file', type=str, nargs=1, default=[""],
  help='the original app to be cloned')


parser.add_argument('--model_year', dest="model_year", metavar='beg_year end_year', type=int, nargs=2, default=[],
  help='the start and end of model year')

parser.add_argument('--csv_file', dest="csv_file", metavar='csv_file', type=str, nargs=1, default=[""],
  help='csv file to output results')


args = parser.parse_args()

histf=args.h0file[0]
model_year=args.model_year

if not model_year:
    year1=0
    year2=-1
else:
    year1=model_year[0]
    year2=model_year[1]

g2pg=1.e6*86400.0*1.e-15

year_mon_match = re.search(r'\.h0\.(\d{4})-(\d{2})\.nc$', histf)
daz=[31.,28.,31.,30.,31.,30.,31.,31.,30.,31.,30.,31]

if year1 > year2:
    gppts=get_gppts(histf)
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    if year_mon_match:
        xmon=histf[(k+9):(k+11)]
        for year in range(year1,year2+1):
            syear='%04d'%year
            newf=histf.replace(xyear,syear)
            firstm=True
            for m in range(0,12):
                smon='%02d'%(m+1)
                newf1=newf.replace(xmon,smon)
                g2pg1=g2pg*daz[m]
                if firstm:
                    gpptsm=get_gppts(newf1)*g2pg1
                    firstm=False
                else:
                    ts=get_gppts(newf1)*g2pg1
                    gpptsm=np.concatenate((gpptsm,ts))
            if first:
                gppts=np.array([np.sum(gpptsm)])
                first=False
            else:
                ts=np.array([np.sum(gpptsm)])
                gppts=np.concatenate((gppts,ts))
    else:
        g2pg=g2pg*365.0
        for year in range(year1,year2+1):
            syear='%04d'%year
            newf=histf.replace(xyear,syear)
            if first:
                gppts=get_gppts(newf)*g2pg
                first=False
            else:
                ts=get_gppts(newf)*g2pg
                gppts=np.concatenate((gppts,ts))

print (gppts)


csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, gppts, delimiter=",")

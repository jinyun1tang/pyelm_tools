import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

import warnings
warnings.filterwarnings("ignore")

def get_varts(histf,varname):
    elmfl=Dataset(histf,"r")

    area=elmfl.variables["area"][:]
    landfr=elmfl.variables["landfrac"][:]
    gpp_flx=elmfl.variables[varname][:]
    garea=landfr*area
    nts=gpp_flx.shape[0]
    gppts=np.zeros(nts)
    for j in range(nts):
        gppflx=np.squeeze(gpp_flx[j,:,:]*garea)
        gppts[j]=np.nansum(gppflx)*g2tg
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

g2tg=1.e6*365.0*86400.0*1.e-15

#variables
# "NFIX_TO_ECOSYSN"
# 'NDEP_TO_SMINN'
# 'F_DENIT'
# 'SMIN_NO3_LEACHED'
# 'SMIN_NO3_RUNOFF'
# 'F_N2O_NIT'
# 'F_N2O_DENIT'
# 'F_NIT'
# 'COL_FIRE_NLOSS'   total loss to fire
# 'PROD1N_LOSS'
# 'WOOD_HARVESTN'
# 'PFT_FIRE_NLOSS'  vegetation loss to fire
if year1 > year2:
    gpp=get_varts(histf,'GPP')
    npp=get_varts(histf,'NPP')
    ar=get_varts(histf,'AR')
    hr=get_varts(histf,'HR')
    lithr=get_varts(histf,'LITHR')
    somhr=get_varts(histf,'SOMHR')
    cwdhr=get_varts(histf,'CWDC_HR')
    er=get_varts(histf,'ER')
    nep=get_varts(histf,'NEP')
    nbp=get_varts(histf,'NBP')
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            gpp=get_varts(histf,'GPP')
            npp=get_varts(histf,'NPP')
            ar=get_varts(histf,'AR')
            hr=get_varts(histf,'HR')
            lithr=get_varts(histf,'LITHR')
            somhr=get_varts(histf,'SOMHR')
            cwdhr=get_varts(histf,'CWDC_HR')
            er=get_varts(histf,'ER')
            nep=get_varts(histf,'NEP')
            nbp=get_varts(histf,'NBP')
            first=False
        else:
            ts=get_varts(newf,'GPP')
            gpp=np.concatenate((gpp,ts))
            ts=get_varts(newf,'NPP')
            npp=np.concatenate((npp,ts))
            ts=get_varts(newf,'AR')
            ar=np.concatenate((ar,ts))
            ts=get_varts(newf,'HR')
            hr=np.concatenate((hr,ts))
            ts=get_varts(newf,'LITHR')
            lithr=np.concatenate((lithr,ts))
            ts=get_varts(newf,'SOMHR')
            somhr=np.concatenate((somhr,ts))
            ts=get_varts(newf,'CWDC_HR')
            cwdhr=np.concatenate((cwdhr,ts))
            ts=get_varts(newf,'ER')
            er=np.concatenate((er,ts))
            ts=get_varts(newf,'NEP')
            nep=np.concatenate((nep,ts))
            ts=get_varts(newf,'NBP')
            nbp=np.concatenate((nbp,ts))


print ('gpp    ,npp    ,ar     ,hr     ,lithr  ,somhr  ,cwdhr  ,er     ,nep    ,nbp')
for j in range(len(gpp)):
    print ('%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f,%-7.2f'%(gpp[j],npp[j],ar[j],hr[j],lithr[j],somhr[j],cwdhr[j],er[j],nep[j],nbp[j]))

nbgt=np.transpose(np.array([gpp,npp,ar,hr,er,nbp]))
csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, nbgt, delimiter=",")

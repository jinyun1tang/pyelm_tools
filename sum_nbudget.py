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

g2tg=1.e6*365.0*86400.0*1.e-12

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
    nfix=get_varts(histf,'NFIX_TO_ECOSYSN')
    ndep=get_varts(histf,'NDEP_TO_SMINN')
    fden=get_varts(histf,'F_DENIT')
    no3lech=get_varts(histf,'SMIN_NO3_LEACHED')
    no3roff=get_varts(histf,'SMIN_NO3_RUNOFF')
    f_n2o_nit=get_varts(histf,'F_N2O_NIT')
    f_n2o_denit=get_varts(histf,'F_N2O_DENIT')
    fnit=get_varts(histf,'F_NIT')
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            nfix=get_varts(newf,'NFIX_TO_ECOSYSN')
            ndep=get_varts(newf,'NDEP_TO_SMINN')
            fden=get_varts(newf,'F_DENIT')
            no3lech=get_varts(newf,'SMIN_NO3_LEACHED')
            no3roff=get_varts(newf,'SMIN_NO3_RUNOFF')
            f_n2o_nit=get_varts(newf,'F_N2O_NIT')
            f_n2o_denit=get_varts(newf,'F_N2O_DENIT')
            fnit=get_varts(newf,'F_NIT')
            first=False
        else:
            ts=get_varts(newf,'NFIX_TO_ECOSYSN')
            nfix=np.concatenate((nfix,ts))
            ts=get_varts(newf,'NDEP_TO_SMINN')
            ndep=np.concatenate((ndep,ts))
            ts=get_varts(newf,'F_DENIT')
            fden=np.concatenate((fden,ts))
            ts=get_varts(newf,'SMIN_NO3_LEACHED')
            no3lech=np.concatenate((no3lech,ts))
            ts=get_varts(newf,'SMIN_NO3_RUNOFF')
            no3roff=np.concatenate((no3roff,ts))
            ts=get_varts(newf,'F_N2O_NIT')
            f_n2o_nit=np.concatenate((f_n2o_nit,ts))
            ts=get_varts(newf,'F_N2O_DENIT')
            f_n2o_denit=np.concatenate((f_n2o_denit,ts))
            ts=get_varts(newf,'F_NIT')
            fnit=np.concatenate((fnit,ts))

print ('nfix , ndep, denit, no3_lech, no3_roff, n2o_nit, n2o_denit, nit, res')
for j in range(len(nfix)):
    print ('%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f'%(nfix[j],ndep[j],-fden[j],-no3lech[j],-no3roff[j],-f_n2o_nit[j],\
        f_n2o_denit[j],fnit[j],nfix[j]+ndep[j]-fden[j]-no3lech[j]-no3roff[j]-f_n2o_nit[j]))

nbgt=np.transpose(np.array([nfix,ndep,fden,no3lech,no3roff,f_n2o_nit,f_n2o_denit,fnit]))
csv_file=args.csv_file[0]

if csv_file:
    np.savetxt(csv_file, nbgt, delimiter=",")

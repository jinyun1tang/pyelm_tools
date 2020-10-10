import numpy as np
from netCDF4 import Dataset
import os,time,sys,argparse

import warnings
warnings.filterwarnings("ignore")


def get_varlist(histf,w_nc_fid):
    elmfl=Dataset(histf,"r")
    w_nc_var = w_nc_fid.createVariable('time', 'f4', ('time'))
    for ncattr in elmfl.variables['time'].ncattrs():
        w_nc_var.setncattr(ncattr, elmfl.variables['time'].getncattr(ncattr))
    w_nc_var = w_nc_fid.createVariable('levgrnd', 'f4', ('levgrnd'))
    w_nc_var.setncatts({'long_name':u"coordinate soil levels",\
        'units':u"m"})
    w_nc_var = w_nc_fid.createVariable('levdcmp','f4',('levdcmp'))
    w_nc_var.setncatts({'long_name':u"coordinate soil levels",\
        'units':u"m"})
    w_nc_fid.variables['levgrnd'][:]=elmfl.variables['levgrnd'][:]
    w_nc_fid.variables['levdcmp'][:]=elmfl.variables['levdcmp'][:]
    keys=elmfl.variables.keys()
    vlist=[]

    for key in keys:
        dimname=elmfl.variables[key].dimensions
        if 'time' in dimname and 'lat' in dimname and 'lat' in dimname:
            addit=False
            if len(dimname) == 3:
                w_nc_var = w_nc_fid.createVariable(key,'f4',(dimname[0]))
                addit=True
            elif len(dimname) == 4 and \
                ('levdcmp' in dimname or \
                'levdcmp' in dimname or 'levtrc' in dimname):
                w_nc_var = w_nc_fid.createVariable(key,'f4',(dimname[0:2]))
                addit=True
            if addit:
                vlist.append(key)
                for ncattr in elmfl.variables[key].ncattrs():
                    if not ncattr=='_FillValue':
                        w_nc_var.setncattr(ncattr, elmfl.variables[key].getncattr(ncattr))
    elmfl.close()
    return vlist


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--h0file', dest="h0file", metavar='h0file', type=str, nargs=1, default=[""],
  help='the original app to be cloned')

parser.add_argument('--model_year', dest="model_year", metavar='beg_year end_year', type=int, nargs=2, default=[],
  help='the start and end of model year')

parser.add_argument('--ilocs', dest="ilocs", metavar='loc_lon loc_lat', type=int, nargs=2, default=[],
  help='location of the longitude and latitude')

parser.add_argument('--out_file', dest="out_file", metavar='out_file', type=str, nargs=1, default=[],
  help='netcdf file to output results')


args = parser.parse_args()

histf=args.h0file[0]
model_year=args.model_year
ilocs=args.ilocs
outfile=args.out_file
if not ilocs:
    print('grid location ilocs not defined')
    quit()
else:
    iloc_lon=ilocs[0]-1
    iloc_lat=ilocs[1]-1

if not outfile:
    outfile='output.nc'

print("write to %s\n"%outfile)

if not model_year:
    year1=0
    year2=-1
else:
    year1=model_year[0]
    year2=model_year[1]

w_nc_fid = Dataset(outfile, 'w', format='NETCDF4')
w_nc_fid.createDimension('time', None)
w_nc_fid.createDimension('levdcmp',15)
w_nc_fid.createDimension('levgrnd',15)
w_nc_fid.createDimension('levtrc', 10)
if year1 > year2:
    vlist=get_varlist(histf,w_nc_fid)
    elmfl=Dataset(histf,"r")
    ts1=elmfl.variables['time'][:]
    time=w_nc_fid.variables['time']
    time[0]=ts1
    for key in vlist:
        dimname=elmfl.variables[key].dimensions
        ts=elmfl.variables[key][:]
        if len(ts.shape)==3:
            ts1=np.squeeze(ts[:,iloc_lat,iloc_lon])
            tvar=w_nc_fid.variables[key]
            tvar[0]=ts1
        elif len(ts.shape)==4:
            ts1=np.squeeze(ts[:,:,iloc_lat,iloc_lon])
            tvar=w_nc_fid.variables[key]
            tvar[0,:]=ts1
    elmfl.close()
else:
    k=histf.find('.h0.')
    xyear=histf[(k+4):(k+8)]
    first=True
    nr=0
    for year in range(year1,year2+1):
        syear='%04d'%year
        newf=histf.replace(xyear,syear)
        if first:
            vlist=get_varlist(newf,w_nc_fid)
        elmfl=Dataset(newf,"r")
        ts1=np.squeeze(elmfl.variables['time'][:])
        time=w_nc_fid.variables['time']
        time[nr]=ts1
        for key in vlist:
            dimname=elmfl.variables[key].dimensions
            ts=elmfl.variables[key][:]
            if len(ts.shape)==3:
                ts1=np.squeeze(ts[:,iloc_lat,iloc_lon])
                tvar=w_nc_fid.variables[key]
                tvar[nr]=ts1
            elif len(ts.shape)==4:
                ts1=np.squeeze(ts[:,:,iloc_lat,iloc_lon])
                tvar=w_nc_fid.variables[key]
                tvar[nr,:]=ts1
        elmfl.close()
        nr=nr+1
        first=False
w_nc_fid.close()

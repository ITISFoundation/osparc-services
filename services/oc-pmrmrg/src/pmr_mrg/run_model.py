import OpenCOR
import sys
import json
import csv

from pathlib import Path


# modelpath = "/home/zhuang/Downloads/guyton_antidiuretic_hormone_2008.cellml"
inputjson= str(sys.argv[1])
modelpath = str(sys.argv[2])
mapfile = str(sys.argv[3])

# parse user inputs from json file
inputpath = Path(inputjson)
with inputpath.open("r") as fp:
    inputdata_unmapped = json.load(fp)

mapfilepath = Path(mapfile)
with mapfilepath.open("r") as fp:
    inputkeymap = json.load(fp)
inputdata = {newkey: inputdata_unmapped[oldkey] for (oldkey, newkey) in inputkeymap.items()}
print(inputdata)

starttime = float(inputdata["starttime"])
endtime = float(inputdata["endtime"])
timeincr = float(inputdata["timeincr"])

# some basic verification
if modelpath.endswith('cellml') or modelpath.endswith('sedml'):
    model = OpenCOR.openSimulation(modelpath)
else:
    sys.exit('Invalid file type: only .cellml and .sedml accepted')


if endtime<starttime:
    print('ending time must be greater than starting time, using 1000s after start instead')
    endtime = starttime +1000
if timeincr <=0:
    print('time increment should be greater than 0s. Setting to 1s')
    timeincr = 1
else:
    print('inputs are valid.')

try: 
    print('try running simulation')
    mdata = model.data()
    mdata.setStartingPoint(starttime)
    mdata.setEndingPoint(endtime)
    mdata.setPointInterval(timeincr)


    # update values using user input
    print('update constants and states')
    for k,v in mdata.constants().items():
        if k in inputdata : mdata.constants()[k]=float(inputdata[k])
    for k,v in mdata.states().items():
        if k in inputdata : mdata.states()[k]=float(inputdata[k])

    # run the model/simulation
    model.run()
    dat = model.results()
    
    print('model can be run with the given input params!')

    c = dat.constants() # constants
    s = dat.states()    # states 
    r = dat.rates()     # rates - unchanged during simulation, default used
    a = dat.algebraic() # outputs of simulation - to print

    titles = list()
    titles.append('time')
    
    # Write output variables and names to outputs.csv
    with open('outputs.csv', 'w') as csvOutput:
        writer = csv.writer(csvOutput)
        firstflag = 1
        for keys in a:
            if firstflag ==1:
                sampledat = a[keys].values()
                firstflag = 0
            titles.append(keys) 
        writer.writerow(titles)    
        dat = list()
        for row in range(1, len(sampledat)):
            thistime = starttime+(row-1)*timeincr
            dat = list()
            dat.append(thistime)
            for keys in a:
                dat.append(a[keys].values()[row])
            writer.writerow(dat)
    csvOutput.close()
    print('CSV output written')
except:
    print('Error during model run')


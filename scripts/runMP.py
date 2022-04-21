#!/usr/bin/python
import argparse, subprocess, sys, os.path, re
import glob
from utils import Parameter, printResults, getParamsFromModule,getMinimStr, beamspotAxialId, beamspotStereoId,paramMap
import buildSteering

pedeBin = 'MillepedeII/pede'

def getArgs():
    parser = argparse.ArgumentParser(description='MP help script')
    parser.add_argument('-i','--inputfiles',nargs='+', help='List of binary input files.',default="")
    parser.add_argument('-f','--float', nargs='+', help='List of MP parameters to float')
    parser.add_argument('-l','--flist',help="File list of binary input files.",default="")
    parser.add_argument('-y','--year',dest="year",help="Which detector geometry? (2016 or 2019 [default])",default="2019")
    parser.add_argument('-o','--outDir',dest="outDir",help="Path to folder to where to move the outputs",default="./MPII_results_")
    parser.add_argument('-z','--inDir',help="Folder containing the millepede.bin files")
    parser.add_argument('-M','--Modules', nargs='+', help='List of modules to float, e.g. L3b L5b')
    parser.add_argument('-p','--parameters', help='Default parameters')
    parser.add_argument('-m','--minimization', default='steering/steer_minimization_template.txt', help='Default minimization settings')
    parser.add_argument('-d','--debug', action='store_true', help='Debug flag')
    parser.add_argument('-n','--name', help='If given output files will get tagged by this name.')
    parser.add_argument('-b','--beamspot', action='store_true',help='Beamspot is included in the fit')
    parser.add_argument('-s','--subito', dest="subito",action='store_true',help='Activate subito mode',default=False)
    parser.add_argument('-c','--constraints', dest="constraints", help="Constraint file",default="")
    parser.add_argument('--SC', action='store_true',help='Survey constraint')
    parser.add_argument('--BSC', action='store_true',help='Beamspot constraint')
    parser.add_argument('--PC', action='store_true',help='Momentum constraint')
    parser.add_argument('--slot', action='store_true',help='onlySlot')
    parser.add_argument('--HC', dest="HierConstr", help="Hierarchical constraint",default="")
    args = parser.parse_args()

    print args
    return args


#This should parse the .txt!!! not hardcode values!
def getDefaultParams(beamspot=False,year="2019"):
    maxModules=-1
    if (year=="2016"):
        maxModules=19
    elif (year=="2019"):
        maxModules=21
    else:
        print "ERROR::getDefaultParams::year must be '2016' or '2019'"
    pars = []
    for h in range(1,3):
        for t in range(1,3):
            for d in range(1,4):
                r = range(1,maxModules)
                if beamspot:
                    r.append(beamspotStereoId)
                    r.append(beamspotAxialId)
                for sensor in r:
                    if sensor<10:
                        s = "0" + str(sensor)
                    else:
                        s = str(sensor)
                    mpId = str(h) + str(t) + str(d) + s
                    p = Parameter(int(mpId),0.0,-1.0)
                    pars.append(p)
                    
                #Add the modules
                r = range(61,68)
                for module in r:
                    mpId = str(h) + str(t) + str(d) + str(module)
                    p = Parameter(int(mpId),0.0,-1.0)
                    pars.append(p)
                
                #Add the support
                r = [80,90]
                for support in r:
                    mpId = str(h)+str(t) +str(d) + str(support)
                    p = Parameter(int(mpId),0.0,-1.0)
                    pars.append(p)
    
    return pars

def getParams(parfilename):
    pars = []
    if parfilename!=None:
        try:
            f_pars = open(parfilename,'r')
        except IOError:
            print 'cannot open ', parfilename
        else:
            for l in f_pars.readlines():
                if len(l.split())==3 or len(l.split())==5:
                    p = Parameter( int(l.split()[0]), float(l.split()[1]), float(l.split()[2]))
                    pars.append(p)
            f_pars.close()
    return pars


def updateFloatParams(pars,floats):
    print 'There are ',len(floats),' parameters to float'    
    for i in floats:
        pfound = None
        for p in pars:
            if p.i==int(i):
                pfound = p
        if pfound == None:
            print 'Cannot find parameter ', i
            sys.exit(1)
        if args.debug:
            print 'Float ', p.i
        pfound.active = 0
    return




def updateParams(pars,otherparms,resetActive=True):
    print 'There are ',len(otherparms),' to update'
    parsnew = []
    for p in pars:
        pfound = None
        for op in otherparms:
            if p.i==op.i:
                pfound = op
        if pfound != None:
            if resetActive:
                pfound.active=-1
            parsnew.append(pfound)
        else:
            parsnew.append(p)
    return parsnew


def buildSteerFile(name,args,pars,minimStr):
    
    
    inputfiles          = args.inputfiles
    flist               = args.flist
    constraintFile      = args.constraints
    surveyConstraints   = args.SC
    beamspotConstraints =  args.BSC


    #Build the input files list
    
    try:
        f = open(name,'w')
    except IOError:
        print 'cannot open file ', name
        return False
    else:
        f.write("CFiles\n")
        for ipf in inputfiles:
            f.write(ipf + "\n")
        
        #The CFiles list
        if (flist != ""):
            ilist = open (flist,'r')
            for line in ilist.readlines():
                f.write(line.strip() + "\n")
            ilist.close()
        
        if (args.inDir != None and len(args.inDir)>0):
            #The inputFolder with the files
            re="all_millepede_ST.bin"
            if (args.BSC):
                re+="BSC_"
            if (args.slot):
                re="*slot*"
            if (args.PC):
                #re+="*_PC_*"
                re="*PC*"


            print "Glob:",args.inDir+"/outputFiles/*/*"+re
            binFiles = glob.glob(args.inDir+"/outputFiles/*/*"+re)
        
            for ifile in binFiles:
                f.write(ifile.strip() +"\n")
        
        #The external constraint file
        if (constraintFile!=""):

            f.write("\n")
            f.write("!Constraint file\n")
            f.write(constraintFile+"\n")
            
        #The floating parameters
        f.write("\nParameter\n")
        for p in pars:
            #if p.isActive():
            #    print p.i
            f.write(p.toString() + "\n")
            
        #Apply survey constants
        if surveyConstraints:
            f.write(buildSteering.getSurveyMeasurements(paramMap))
            f.write("\n\n")
        
        #Apply beamspotConstraint (This I think is not correct)
        if beamspotConstraints:
#            f.write(buildSteering.getBeamspotConstraints(paramMap))
            f.write(buildSteering.getBeamspotConstraintsFloatingOnly(pars))
            f.write("\n\n")
        
        f.write("\n\n")
        f.write(minimStr)
        f.close()        
        return True


def saveResults(args):
    inputfilenames = args.inputfiles
    name = args.name
    outDir=args.outDir+args.name
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    names = [ os.path.splitext(os.path.basename(n))[0] for n in inputfilenames] 
    filename = '-'
    filename = filename.join(names)
    status = subprocess.call("cp millepede.res " + " "+outDir+"/millepede-" + filename + "-" + name + ".res", shell=True)
    status = subprocess.call("cp millepede.eve " + " "+outDir+"/millepede-" + filename + "-" + name + ".eve", shell=True)
    status = subprocess.call("cp millepede.log " + " "+outDir+"/millepede-" + filename + "-" + name + ".log", shell=True)
    status = subprocess.call("cp millepede.his " + " "+outDir+"/millepede-" + filename + "-" + name + ".his", shell=True)
    status = subprocess.call("cp steer.txt "     + " "+outDir+"/millepede-steer-" + filename + "-" + name + ".txt", shell=True) 
    

def runPede(filename,args):
    print "Clean up..."
    status = subprocess.call("rm millepede.res", shell=True)
    status = subprocess.call("rm millepede.eve", shell=True)
    status = subprocess.call("rm millepede.log", shell=True)
    status = subprocess.call("rm millepede.his", shell=True)
    
    s = pedeBin + " " + filename
    if args.subito:
        s+= " -s"
    print 'Execute: ', s
    status = subprocess.call(s, shell=True)

def main(args):

    print "just GO"

    # initialize all the parameters into a list
    pars = getDefaultParams(args.beamspot,args.year)
    print 'Found ', len(pars), 'default parameters'
    if args.debug:
        for p in pars:
            print p.toString()
    
    # check if there is a supplied parameter file.
    # this could be a result file from a previous fit
    print "Parameters:", args.parameters
    inputpars = getParams(args.parameters)
    print 'Found ', len(inputpars), ' parameters to update'
    if args.parameters != None:
        if len(inputpars) != len(pars):
            print 'Wrong number of input parameters. Require all to be present in the input file, but not all active'
            sys.exit(1)
    
    if args.debug:
        for p in pars:
            print p.toString()

    # update the default parameters with the new input file
    # normally require that they become inactive here
    pars = updateParams(pars,inputpars,True)

    floatingPars = []

    # find the floating parameter for this fit
    if args.Modules is not None:
        for m in args.Modules:
            floatingPars.extend([str(mp) for mp in getParamsFromModule(m)])
    
    if args.float is not None:
        floatingPars.extend(args.float)

    updateFloatParams(pars,floatingPars)

    print 'List of floating parameters:'
    nfloats = 0
    for p in pars:
        if p.active==0:
            print p.toString()
            nfloats=nfloats+1

    if nfloats<1:
        print 'Something is wrong. At least one parameter need to be floating before running.'
        sys.exit(1)
    

    # get MP minimization settings
    minimStr = getMinimStr(args.minimization)

    # build the actual steering file
    name = "steer.txt"
    
    if len(args.inputfiles)==0 and len(args.flist)==0 and len(args.inDir)==0:
        print "Specify input files [-i <inputfiles> ] or list of input files [-l <filelist>] or inputDirectory [-z <inDir>]"
        sys.exit(1)

    #ok = buildSteerFile(name,args.inputfiles,args.flist,pars,minimStr,args.constraints, args.SC,args.BSC)
    ok = buildSteerFile(name,args,pars,minimStr)
    
    if not ok:
        print "Couldn't build steering file"
        sys.exit(1)

    
    # run the fit
    runPede(name,args)

    # print results
    printResults()

    # save results to a specific name if supplied.
    if args.name != None:
        saveResults(args)

    
if __name__ == "__main__":

    args = getArgs()
    main(args)

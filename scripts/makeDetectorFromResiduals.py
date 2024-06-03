#script for building a detector from the millepede solutions
import argparse,sys,os,shutil
import subprocess

def OptionParse():
    parser = argparse.ArgumentParser(description='Det from residuals')
    parser.add_argument("-j","--javaFolder", required=True,help="javaFolder where to build the compact")
    parser.add_argument("-i","--inputTag", required=True,help="Input detector tag")
    parser.add_argument("-o","--outputTag",help="Output detector tag (if not specified, just increase iteration",default="")
    parser.add_argument("-r","--residuals",required=True,help="Residuals to add to the compact",default="")
    parser.add_argument("-c","--clean",help="Force cleaning of the output folder if it exists",action="store_true",default=False)
    parser.add_argument("-f","--flipRotations", help="Switches OFF the rotations flips. Only Rw should be not flipped", action="store_false",default=True)
    args = parser.parse_args()
    return args


def main():
    
    print ("makeDetectorFromResiduals.py")
    args = OptionParse()
    print(args)

    #Get the iteration out of the tag
    iteration = int(args.inputTag.split("iter")[-1])
    #print iteration
    
    #Increase iteration of 1
    iteration+=1 
    #print iteration
    
    #Make the outputTag. Always maintain the iteration number
    baseTag   = args.inputTag.split("_iter")[0]
    outputTag = args.outputTag
    if (outputTag != ""):
        if ("HPS_" not in outputTag):
            baseTag = "HPS_"+outputTag
        else:
            baseTag = outputTag

    Tag = baseTag + "_iter"+str(iteration)
    
    defaultDetectorLocation = args.javaFolder+"/detector-data/detectors/"
    print( "Copying: " + defaultDetectorLocation + args.inputTag +" to " + defaultDetectorLocation +Tag)
    cmd = "cp -r " + defaultDetectorLocation + args.inputTag + " " + defaultDetectorLocation +Tag
    
    if (os.path.exists(defaultDetectorLocation +Tag)):
        print( "ERROR:: "+defaultDetectorLocation +Tag+ " already exists! Exiting..")
        if (args.clean):
            print( "Removing " + defaultDetectorLocation +Tag )
            try:
                shutil.rmtree(defaultDetectorLocation +Tag)
            except OSError as e:
                print ("Error: %s - %s." % (e.filename, e.strerror))

        else:
            sys.exit(1)
    
    subprocess.check_call(cmd.split())
    

    #Now change the detector information inside the compact
    outputCompactXML =  defaultDetectorLocation +Tag + "/compact.xml"

    print( "Changing detector tag inside the compact")
    compact_file = open(outputCompactXML, "r")
    list_of_lines = compact_file.readlines()
    lineIndex = 0
    for index in range(len(list_of_lines)):
        if ("HPS_") in list_of_lines[index] and ("iter") in list_of_lines[index]:
            lineIndex = index
            break
            

    print( list_of_lines[lineIndex].strip() + "  --->  "  + '<info name="' + Tag + '">')
        
    list_of_lines[lineIndex] = '<info name="' + Tag + '"> \n'
    
    compact_file.close()
    
    out_compact_file = open(outputCompactXML,"w")
    out_compact_file.writelines(list_of_lines)
    out_compact_file.close()
    
    #Get the new compact, add the residual corrections and copy it back to the location
    
    #I assume i am in hps-mille
    cmd = "mv " + outputCompactXML + " ./compact.xml"
    print( cmd.split())
    subprocess.call(cmd.split())
    
    #Call buildCompact
    distributionBinary = args.javaFolder+"/distribution/target/hps-distribution-5.2.2-SNAPSHOT-bin.jar"
    residuals          = args.residuals
    
    
    cmd = "python3.6 scripts/buildCompact.py -c compact.xml -j " + distributionBinary + " -r " + args.residuals + " -t"

    if args.flipRotations:
        cmd += " -f"
    print( cmd.split())
    subprocess.call(cmd.split())
    
    #Copy the compact_millepede.xml to the original location

    cmd = "mv ./compact_" + (args.residuals.split("/")[-1]).split(".res")[0]+".xml " + outputCompactXML
    print( cmd)
    subprocess.call(cmd.split())


    #Remove the lcdd in the new folder
    cmd = "rm " + defaultDetectorLocation +Tag + "/"+args.inputTag+".lcdd"
    print( cmd.split())
    
    subprocess.check_call(cmd.split())
    
    

    
    
if __name__=="__main__":
    main()


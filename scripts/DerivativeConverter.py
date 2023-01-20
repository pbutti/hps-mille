import json
import numpy as np
import argparse

class DerivativeConverter:
    
    #Create the tree from the json file
    def __init__(self, json_file,debug=False):
        f = open(json_file)
        data = json.load(f)
        self.avs  = data["AlignableStructures"]
        #This dictionary holds all the results from MPII
        self.results = {}
        self._debug = debug
        
    
    #Finds the volume from the derivative label provided
    def HasParam(self,vol,der_label):
        print(self.avs[vol]["derivativeLabels"])
        if der_label in self.avs[vol]["derivativeLabels"]:
            return True
        else:
            return False

    #Add the global corrections for a sensor
    # a_tot_i = a_sensor_i + Cij*a_structure1_j + Cij*a_structure2_l + ... 
    
    def LoadResults(self,rFile):

        res_file = open(rFile)

        for line in res_file.readlines():
            if ("Parameter") in line:
                continue
                
            self.results[line.split()[0]] = line.split()[1]
                
        res_file.close()
        
    
    # This generates some misalignments of a structure and dumps them in a misalignment file
    # File has to be previously openend
    
    def generateMisalignments(self, 
                              s_name, 
                              outfile,
                              misalignments=[0.0,0.0,0.0,0.0,0.0,0.0],
                              threshold=1e-6):
        
        structure=self.avs[s_name]
        
        for ilabel in range(len(structure["derivativeLabels"])):
            
            outfile.write(" "+str(structure["derivativeLabels"][ilabel]) + "     "+str(round(misalignments[ilabel],4))+"     -1.0000\n")
            
    
        


        
    #This give the parents corrections
    def computeParentCorrections(self,s_name,
                                 d_Name="",
                                 corrections=np.array([0.0,0.0,0.0,0.0,0.0,0.0]),
                                 threshold=1e-6):
    
        structure = self.avs[s_name]

        if self._debug:
            print("Calling computeParentCorrections:",s_name,d_Name,corrections,threshold)
            

        if (structure["parent"] != ""):
            corrections = self.computeParentCorrections(structure["parent"],s_name,corrections)
                        
        #Get the corrections from MPII of this structure and add the ones from the parent. 
        this_corrections = np.array([float(self.results[str(x)]) if str(x) in self.results.keys() else 0.0 for x in structure["derivativeLabels"]])
        print(this_corrections)
        mpII_corrections = this_corrections + corrections
        
        #form a vector with the corrections of this structure
        if (self._debug):
            print("This Structure"  ,s_name)
            print("parent::"        ,structure["parent"])
            print("The daughter::"  ,d_Name)
            print("This derivatives",structure["derivativeLabels"])
            print(this_corrections)
            if (structure["parent"] != ""):
                print("Parents derivatives",self.avs[structure["parent"]]["derivativeLabels"])
            else:
                print("Parents derivatives", "None")
            print("Parents corrections", corrections)



        if (d_Name == ""):
            return mpII_corrections
        
        CMatrices   = {}
        Corrections = {}
        
        #Translate them to the daughter

        for key in structure["CMatrices"].keys():
            arr = structure["CMatrices"][key]
            arr = [0 if abs(a_) < threshold else a_ for a_ in arr]
            arr=np.array(arr)
            arr=arr.reshape(6,6)
            CMatrices[key]=arr


        #Fix this better
        for key in CMatrices.keys():
            if (key == d_Name):
                if (self._debug):
                    print(key)
                    print(CMatrices[key])

                Corrections[key] = CMatrices[key].dot(mpII_corrections.transpose())
        if (self._debug):
            print(Corrections)
        
        return Corrections[d_Name]
        
        
        #Get the alignment tree structures
    def getStructures(self):
        return self.avs
        

def getArgs():
    parser = argparse.ArgumentParser(description="MPII Hierarchy derivatives translator")
    parser.add_argument("-r","--residualfile",help="Input residual file",default="/nfs/slac/g/hps2/pbutti/alignment/hps-mille/TEST_COM/millepede.res")
    parser.add_argument("-d","--debug",help="Activate Debug",action="store_true",default=False)
    parser.add_argument("-o","--output",help="The residuals to be parsed from hps-java",default="./mpII_com_residuals.res")
    parser.add_argument("-j","--json",help="The json file",default="./AlignmentTree.json")
    args = parser.parse_args()
    print(args)
    return args


def main():

    args = getArgs()
    np.set_printoptions(formatter={'float': lambda x: "{0:0.4f}".format(x)})

    residualFile = args.residualfile
    print("Parsing::",residualFile)
    
    dc = DerivativeConverter(args.json,args.debug)
        
    dc.LoadResults(residualFile)

    #print(dc.results)
    
    SensorsList = [sname for sname in dc.avs.keys() if "sensor0" in sname and "ECal" not in sname]
    print(SensorsList)
    
    TotalCorrections={}
    
    out = open(args.output,"w")
    out.write(" Parameter  ! first 3 elements per line are significant (if used as input) \n")
    
    for sensor in SensorsList:
        TotalCorrections[sensor] = dc.computeParentCorrections(sensor)
        
    for sensor in SensorsList:
        print(sensor,TotalCorrections[sensor])
        for ilabel in range(len(dc.avs[sensor]["derivativeLabels"])):
            label = dc.avs[sensor]["derivativeLabels"][ilabel]
            out.write("     "+str(label)+"     "+str(round(TotalCorrections[sensor][ilabel],4)) +"     -1.0000\n")
        
    out.close()
    


if __name__=="__main__":
    main()

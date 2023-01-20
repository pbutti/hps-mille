from DerivativeConverter import DerivativeConverter
import numpy as np
import argparse

def getArgs():
    parser = argparse.ArgumentParser(description="MPII misalignment creator")
    parser.add_argument("-j","--json",help="The json file",default="./AlignmentTree.json")
    parser.add_argument("-i","--input",help="Input misalignment",default="")
    args = parser.parse_args()
    print(args)
    return args

def main():
    print("Misalignment Tool")
    args = getArgs()
    dc = DerivativeConverter(args.json,True)
    
    misfile = open("misalignmentFile.txt","w")
    misfile.write(" Parameter ! Generated misalignments\n")
    
    #dc.generateMisalignments("Volume_Top",
    #                         misfile,
    #                         [0.1,0.2,0.,0.,0.,0.])
    
    
    #VOLUME TOP 
    #Tu,Tv recoverable (BS constraint is necessary)
    #Rv not recoverable
    #Rw not recoverable
    #Tz
    #dc.generateMisalignments("Volume_Top",
    #                         misfile,
    #                         [0.0,0.0,0.4,0.000,0.000,0.000])
    
    
    # UChannel Rot Rv 2mrad
    #dc.generateMisalignments("UChannelL57_Top_AV",
    #                         misfile,
    #                         [0.1,0.0,0.0,0.0,0.00,0.0])
    

    #Recover UChannels relative rotations around U -  Recoverable only if rotations are freed
    
    #Front 1 mrad
    #dc.generateMisalignments("UChannelL14_Top_AV",
                             #misfile,
                             #[0.0,0.0,0.0,0.001,0.0,0.0])

    #Back -2 mrad
    #dc.generateMisalignments("UChannelL57_Top_AV",
                             #misfile,
                             #[0.0,0.0,0.0,0.-0.002,0.0,0.0])


    #2mrad opposite rotations for front and back Rw 

    #Front -5 mrad
    #dc.generateMisalignments("UChannelL14_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,0.0,0.0,0.0,-0.002])

    #Back 3 mrad
    #dc.generateMisalignments("UChannelL57_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,0.0,0.-0.000,0.0,0.001])
    
    #Tz Checks
    #dc.generateMisalignments("ModuleL4_Top_AV",
    #                         misfile,
    #                         [-0.,0.0,-2,0.0,0.0,0.0])

    #dc.generateMisalignments("ModuleL5_Top_AV",
    #                         misfile,
    #                         [-0.,0.0,2,0.0,0.0,0.0])

    
    #dc.generateMisalignments("ModuleL6_Top_AV",
    #                         misfile,
    #                         [-0.,0.0,2,0.0,0.0,0.0])
    
    
    #if (args.input == ""):
    #    print("ERROR: provide an input json with misalignments")
        
    #Back UChannel Opening Angle - 1mrad
    #dc.generateMisalignments("doublesensor_stereo_L5_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,2,0.0,0.0,0.0])

    #dc.generateMisalignments("doublesensor_stereo_L6_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,-2,0.0,0.0,0.0])

    #dc.generateMisalignments("doublesensor_stereo_L7_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,0,0.0,0.0,0.0])

    
    dc.generateMisalignments("module_L4t_halfmodule_stereo_sensor0_AV",
                             misfile,
                             [0.0,0.0, 1.0,0.0,0.0,0.0]) 

    dc.generateMisalignments("doublesensor_stereo_L5_Top_AV",
                             misfile,
                             [0.0,0.0,-1.0,0.0,0.0,0.0]) 

    dc.generateMisalignments("doublesensor_stereo_L6_Top_AV",
                             misfile,
                             [0.0,0.0, 1.0,0.0,0.0,0.0]) 


    #dc.generateMisalignments("UChannelL14_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,2.0,0.0,0.0,0.0]) 

    #dc.generateMisalignments("UChannelL57_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,2.0,0.0,0.0,0.0]) 

    

    #Opening Angle Front
    #Opening Angle Back


    #Tz sensors - stereo only
    
    #dc.generateMisalignments("doublesensor_stereo_L6_Top_AV",
    #                         misfile,
    #                         [0.0,0.0,2,0.0,0.0,0.0])
    


    #Rv sensors
    #Tz modules
    

    
    misfile.close()
    
    dc.LoadResults("misalignmentFile.txt")

    #Convert this in the HPS residuals

    SensorsList = [sname for sname in dc.avs.keys() if "sensor0" in sname and "ECal" not in sname]
    print(SensorsList)
    
    TotalCorrections={}
    
    out = open("mpII_mis_residuals.res","w")

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

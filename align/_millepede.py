"""Submodule helping construct the steering file for pede"""
import sys
import os
import math

def getBeamspotConstraints(parMap):
    s = '\n!Beamspot constraints\n'
    for d in ['u','v','w']:
        print('d=',d)
        for t in ['t','r']:
            for iAxial in range(2):
                active = False
                print('iAx=',iAxial)
                for p, name in utils.paramMap.iteritems():
                    print('look at ', name, ' ', p)
                    if utils.getModuleNrFromDeName(name) != 0: continue
                    if (utils.isAxial(name) and iAxial==0) or (not utils.isAxial(name) and iAxial==1): continue
                    if utils.getDir(p) == d and utils.getType(p) == t:
                        print('found one',name, ' ', p)
                        if not active:
                            print('ACTIVATE')
                            s += 'Constraint 0.\n'    
                            s += '%s %.1f\n' % (p, 1.0)
                            active = True
                        else:
                            print('ADD')
                            s += '%s %.1f\n' % (p, -1.0)
    return s

def getBeamspotConstraintsFloatingOnly(pars):
    s = '\n!Beamspot constraints\n'
    written1 = 0
    written2 = 0
    written3 = 0
    written4 = 0
    written5 = 0
    written6 = 0
    for p in pars:
        line = p.toString()
        if ('98' or '99') in line:
            parNum = int(line.split()[0])
            isFloat = float(line.split()[2])
            if('1198') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written1==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, 1.0)
#                        s += '%s %.1f\n' % (parNum+1, -1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum+10000, 1.0)
#                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                        s += '\n'
#                        written1 = 1
                    elif(parNum > 20000 and written1==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
#                        s += '\n'
                        written1 = 1
 
            if('2198') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written2==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, 1.0)
#                        s += '%s %.1f\n' % (parNum+1, -1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum+10000, 1.0)
#                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                        s += '\n'
                        written2 = 1
                    elif(parNum > 20000 and written2==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
#                        s += '\n'
                        written2 = 1

            if('1298') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written3==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, 1.0)
#                        s += '%s %.1f\n' % (parNum+1, -1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum+10000, 1.0)
#                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                        s += '\n'
                        written3 = 1
                    elif(parNum > 20000 and written3==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        written3 = 1

            if('2298') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written4==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                       s += 'Constraint 0.\n'    
#                       s += '%s %.1f\n' % (parNum, 1.0)
#                       s += '%s %.1f\n' % (parNum+1, -1.0)
#                       s += 'Constraint 0.\n'    
#                       s += '%s %.1f\n' % (parNum+10000, 1.0)
#                       s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                       s += '\n'
                        written4 = 1
                    elif(parNum > 20000 and written4==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
#                        s += '\n'
                        written4 = 1

            if('1398') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written5==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, 1.0)
#                        s += '%s %.1f\n' % (parNum+1, -1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum+10000, 1.0)
#                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                        s += '\n'
                        written5 = 1
                    elif(parNum > 20000 and written5==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
#                        s += '\n'
                        written5 = 1

            if('2398') in line:
                if(isFloat==0): 
                    if(parNum < 20000 and written6==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, 1.0)
                        s += '%s %.1f\n' % (parNum+10000, -1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, 1.0)
                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, 1.0)
#                        s += '%s %.1f\n' % (parNum+1, -1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum+10000, 1.0)
#                        s += '%s %.1f\n' % (parNum+1+10000, -1.0)
#                        s += '\n'
                        written6 = 1
                    elif(parNum > 20000 and written6==0):
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum, -1.0)
                        s += '%s %.1f\n' % (parNum-10000, 1.0)
                        s += 'Constraint 0.\n'    
                        s += '%s %.1f\n' % (parNum+1, -1.0)
                        s += '%s %.1f\n' % (parNum+1-10000, -1.0)
                        s += '\n'
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum, -1.0)
#                        s += '%s %.1f\n' % (parNum+1, 1.0)
#                        s += 'Constraint 0.\n'    
#                        s += '%s %.1f\n' % (parNum-10000, -1.0)
#                        s += '%s %.1f\n' % (parNum+1-10000, 1.0)
#                        s += '\n'
                        written6 = 1

    return s



def getMeasurementZ0(parMap):
    s = ''
    # Constraint:  <z0>_top + dz0_top = <z0>_bot + dz0_bot
    # i.e.  dz0_top - dz0_bot = -1 * ( <z0>_top - <z0>_bot)
    # where <z0>_top is the measured mean
    # measured z0 for top and bottom
    mean_t = 0.1
    mean_b = 0.05
    target = -1.0* ( mean_t - mean_b )
    uncertainty = 0.05
    s += '\n#z0 top/bottom constraint\nMeasurement %.3f %.3f\n' % (target, uncertainty)

    # Calculate d_top
    for p, info in utils.paramMap.iteritems():
        if utils.getDir(p) == 'u' and utils.getType(p) == 't' and utils.getHalf(int(p)) == 't':
            # stereo sensor have a cos stereo angle penalty
            # axial and stereo sensor have u in opposite directions globally
            f = 1.0/12.0 # weight from each sensor layer
            if not utils.isAxial( utils.getSensorName(p) ):
                if utils.getModuleNrFromDeName( utils.getSensorName(p) ) <= 3: st = 0.1
                else: st = 0.05
                f = -1.0 / 12.0 / math.cos(st)
            s += '%s %.3f\n' % (p, f)

    # Calculate d_bot
    # NOTE the minus sign applied applied to the factor f
    for p, info in utils.paramMap.iteritems():
        if utils.getDir(p) == 'u' and utils.getType(p) == 't' and utils.getHalf(int(p)) == 'b':
            f = 1.0/12.0
            if not utils.isAxial( utils.getSensorName(p) ):
                if utils.getModuleNrFromDeName( utils.getSensorName(p) ) <= 3: st = 0.1
                else: st = 0.05
                f = -1.0 / 12.0 *math.sin(st)
            s += '%s %.3f\n' % (p, f)
    
    return s

def getMeasurementD0(parMap):
    # similar to z0 constraint above
    s = ''
    mean_t = 0.1
    mean_b = 0.05
    target = -1.0* ( mean_t - mean_b )
    uncertainty = 0.05
    s += '\n#d0 top/bottom constraint\nMeasurement %.3f %.3f\n' % (target, uncertainty)

    # Calculate d_top
    for p, info in utils.paramMap.iteritems():
        if utils.getDir(p) == 'u' and utils.getType(p) == 't' and utils.getHalf(int(p)) == 't':
            # stereo sensor have a sin stereo angle penalty
            # axial and stereo sensor have v in same directions globally
            # axial don't contribute
            f = 1.0/6.0 # weight from each sensor layer
            if not utils.isAxial( utils.getSensorName(p) ):
                if utils.getModuleNrFromDeName( utils.getSensorName(p) ) <= 3: st = 0.1
                else: st = 0.05
                f = f/ math.cos(st)
            s += '%s %.3f\n' % (p, f)

    # Calculate d_bot
    # NOTE the minus sign applied applied to the factor f
    for p, info in utils.paramMap.iteritems():
        if utils.getDir(p) == 'u' and utils.getType(p) == 't' and utils.getHalf(int(p)) == 'b':
            f = -1.0/6.0
            if not utils.isAxial( utils.getSensorName(p) ):
                if utils.getModuleNrFromDeName( utils.getSensorName(p) ) <= 3: st = 0.1
                else: st = 0.05
                f = f * math.sin(st)
            s += '%s %.3f\n' % (p, f)
    
    return s


"""Submodule helping construct the steering file for pede"""
import sys
import os
import math

class Parameter :
    def __init__(self, idn, name, half, trans_rot, direction, mp_layer_id) :
        self.id = int(idn)
        self.name = name
        self.half = int(half) # 1 or 2
        self.trans_rot = int(trans_rot)
        self.direction = int(direction)
        self.mp_layer_id = int(mp_layer_id)

        self.val = 0.0
        self.error = -1.0
        self.active = -1.0
        self.change = None

    def isfloat(self) :
        return self.active >= 0.0

    def float(self, yes = True) :
        if yes :
            self.active = 0.0
        else :
            self.active = -1.0

    def from_map_file_line(line) :
        return Parameter(*line.split())

    def parse_map_file(map_filepath) :
        parameters = {}
        with open(map_filepath) as mf :
            for line in mf :
                # skip header line
                if 'MilleParameter' in line :
                    continue
                p = Parameter.from_map_file_line(line)
                parameters[p.id] = p

    def __from_res_file_line(self, line) :
        """Assumes line is for the same parameter as stored in self"""
        elements = line.split()
        # elements[0] is the ID number and we assume it is correct
        self.val = float(elements[1])
        self.active = float(elements[2])
        if len(elements) > 4 :
            self.val = float(elements[3])
            self.error = float(elements[4])

    def parse_pede_res(res_file, destination = None, skip_nonfloat = False) :
        parameters = {}
        with open(res_file) as rf :
            for line in rf :
                # skip header line
                if 'Parameter' in line :
                    continue
                idn = int(line.split()[0])
                if destination is None :
                    p = Parameter(idn,'UNKNOWN',-1,-1,-1,-1)
                    p.__from_res_file_line(line)
                    if p.active >= 0.0 or not skip_nonfloat :
                        parameters[p.id] = p
                else :
                    if idn not in destination :
                        raise ValueError(f'Attempting to load parameter {idn} which is not in parameter map')
                    destination[idn].__from_res_file_line(line)
        return parameters if destination is None else destination

    def pede_format(self) :
        """Print this parameter as it should appear in the pede steering file"""
        return f'{self.id} {self.val} {self.active} {self.name}'


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


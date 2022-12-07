"""An alignment parameter representation"""

class Parameter :
    """Representation of a single alignment parameter

    This class also contains helpful functions for operating on sets of alignment
    parameters e.g. parsing the map file or pede res file

    Attributes
    ----------
    id : int
        pede ID number as written in compact.xml, pede steering, and map files
    name : str
        human-readable name as written in map file
    half : int
        1 is for top and 2 is for bottom
    trans_rot : int
        1 is for translation and 2 is for rotation
    direction : int
        1 is for 'u', 2 is for v, and 3 is for w
    mp_layer_id : int
        "layer" ID number in millepede (i.e. axial and stereo sensors are separated)
    val : float
        value of parameter (if loaded from res file)
    error : float
        error of parameter (if loaded from res file)
    active : bool
        true if parameter is floating, false otherwise
    """
    def __init__(self, idn, name, half, trans_rot, direction, mp_layer_id) :
        self.id = int(idn)
        self.name = name
        self.half = int(half) # 1 or 2
        self.trans_rot = int(trans_rot)
        self.direction = int(direction)
        self.mp_layer_id = int(mp_layer_id)

        self.val = 0.0
        self.error = -1.0
        self.active = False

    def float(self, yes = True) :
        """Set whether this parameter is floating/active or not"""
        self.active = yes

    def from_map_file_line(line) :
        """parse a line from the map file

        we assume that the constructor's arguments are in the same
        order as a line in the sensor map file
        """
        return Parameter(*line.split())

    def parse_map_file(map_filepath) :
        """load the entire parameter set from a map file

        Returns
        -------
        dict
            map from ID number to a Parameter
        """
        parameters = {}
        with open(map_filepath) as mf :
            for line in mf :
                # skip header line
                if 'MilleParameter' in line :
                    continue
                p = Parameter.from_map_file_line(line)
                parameters[p.id] = p
        return parameters

    def __from_res_file_line(self, line) :
        """Assumes line is for the same parameter as stored in self

        A line in the pede result file has either 3 or 5 columns.

        1. ID
        2. value
        3. activity (0.0 if floating, -1.0 if not)
        4. (if active) value
        5. (if active) error in value
        
        We ignore the first column and assume that we are only calling
        this function if the line has already been deduced to correspond
        to the parameter we represent.
        """
        elements = line.split()
        # elements[0] is the ID number and we assume it is correct
        self.val = float(elements[1])
        self.active = (float(elements[2]) >= 0.0)
        if len(elements) > 4 :
            self.val = float(elements[3])
            self.error = float(elements[4])

    def parse_pede_res(res_file, destination = None, skip_nonfloat = False) :
        """parse a pede results file
        
        Parse the results file into a dictionary. If no destination dictionary
        is provided, a new dictionary is created with the ID numbers as keys
        and Parameter instances as values. Since this mapping is created without
        the sensor mapping, the rest of the Parameter attributes are assigned
        non-sensical values. 

        Parameters
        ----------
        res_file : str
            path to results file we are going to parse
        destination : dict, optional
            if provided, load the values from the file into parameters in this dict
        skip_nonfloat : bool, optional
            skip non-floating parameters 
        """
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
                    if p.active or not skip_nonfloat :
                        parameters[p.id] = p
                else :
                    if idn not in destination :
                        raise ValueError(f'Attempting to load parameter {idn} which is not in parameter map')
                    if destination[idn].active or not skip_nonfloat :
                        destination[idn].__from_res_file_line(line)
        return parameters if destination is None else None

    def pede_format(self) :
        """Print this parameter as it should appear in the pede steering file"""
        return f'{self.id} {self.val} {0.0 if self.active else -1.0} {self.name}'

    def __repr__(self) :
        """Representation of this parameter"""
        return str(self.id)

    def __str__(self) :
        """Human printing of this parameter"""
        s = repr(self)
        if self.trans_rot == 1 :
            # translation
            #   stored as mm, print as um
            s += f' {self.val*1000} +- {self.error*1000} um'
        else :
            # rotation
            #   stored as rad, print as mrad
            s += f' {self.val*1000} +- {self.error*1000} mrad'
        return s


"""Internal configuration of this alignment runner

deduces variables on first input and then holds them for
later access
"""

import os
import shutil
import json

class cfg :
    __instance = None
    def __init__(self, jarfile = None, javadir = None, javaopts = ['-XX:+UseSerialGC','-Xmx5000m'], 
                 mvnopts = ['-DskipTests','-Dcheckstyle.skip'], 
                 gbldir = None, pede = 'pede', scratch = '/tmp/',
                 kf_steer = None, st_steer = None) :

        package = os.path.abspath(os.path.dirname(__file__))
        self.container = False
        if os.path.exists('/singularity') :
            self.container = True

        if javadir is None :
            if 'HPS_JAVA_DIR' in os.environ :
                javadir = os.environ['HPS_JAVA_DIR']
            else :
                # we weren't told so lets check some options
                parent = os.path.dirname(package)
                grandparent = os.path.dirname(parent)
                opts = [parent, grandparent, os.path.dirname(grandparent)]
                if 'HPS_HOME' in os.environ :
                    opts.append(os.environ['HPS_HOME'])

                opts = [os.path.join(d,s) for d in opts for s in ['java','hps-java']]

                for sd in opts :
                    if os.path.exists(sd) :
                        javadir = sd
                        break
        
        if javadir is None :
            raise KeyError('Unable to deduce directory of hps-java. Please provide it.')

        self.javadir = javadir

        if jarfile is None :
            if 'HPS_JAVA_JAR' in os.environ :
                jarfile = os.environ['HPS_JAVA_JAR']
            elif os.path.exists(os.path.join(self.javadir,'distribution/target/hps-distribution-5.2-SNAPSHOT-bin.jar')) :
                jarfile = os.path.join(self.javadir,'distribution/target/hps-distribution-5.2-SNAPSHOT-bin.jar')

        if jarfile is None :
            raise KeyError('Unable to deduce location of jar file. Please provide it.')
        
        self.jarfile = jarfile

        if self.container :
            javaopts.extend(['-Dorg.lcsim.cacheDir=/externals'])
        else :
            if gbldir is None :
                # deduce GBL location
                print('WARN: Unable to deduce gbldir. Set with cfg.set_gbldir before attempting to run')
            if gbldir is not None :
                javaopts.extend(['-Djna.library.path={gbldir}/lib'])
        
        self.javaopts = javaopts

        self.mvnopts = mvnopts

        pede_fp = shutil.which(pede)
        if pede_fp is None :
            print(f'WARN: {pede} not found. Please provide full path to the configuration object.')
        self.pede = pede_fp

        if not os.path.isdir(scratch) :
            raise KeyError(f'Scratch directory {scratch} does not exist')

        if scratch is None :
            scratch = os.getcwd()

        self.scratch = os.path.join(scratch,'hps-align-scratch')
        os.makedirs(self.scratch, exist_ok=True)

        if kf_steer is None :
            kf_steer = os.path.join(package,'tracking_kf_alignment.lcsim')

        self.kf_steer = kf_steer

        if st_steer is None :
            st_steer = os.path.join(package,'tracking_st_alignment.lcsim')

        self.st_steer = st_steer

    def __str__(self) :
        return json.dumps(self.__dict__, indent=2)

    def cfg(**kwargs) :
        if cfg.__instance is None :
            cfg.__instance = cfg(**kwargs)
        return cfg.__instance

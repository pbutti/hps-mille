"""apply deduced alignment parameters to the compact"""

import os
import re
import shutil

import typer

from _cfg import cfg
from _parameter import Parameter
from _cli import app, typer_unpacker

@app.command()
@typer_unpacker
def apply(pede_res : str, detector : str,
        bump : bool = typer.Option(True,
            help='Bump detector iteraction number and create a new copy?'),
        interactive : bool = typer.Option(False,
            help='Ask before applying any parameters'),
        force : bool = typer.Option(False,
            help='Force re-creation even if new iteraction already exists')
        ) :
    """
    Apply the deduce alignment parameters from pede to the detector
    """

    if bump :
        # deduce source directory and check that it exists
        src_path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
        if not os.path.isdir(src_path) :
            raise typer.BadParameter(f'Detector {detector} is not in hps-java')
        
        # deduce iter value, using iter0 if there is no iter suffix
        matches = re.search('.*iter([0-9]*)', detector)
        if matches is None :
            if interactive :
                N = typer.prompt('No "_iterN" suffix on detector name. What should the first N be? (negative to abort)')
                if not N.isnumeric() :
                    typer.echo('Provided N not a number.')
                    typer.Abort()
                N = int(N)
                if N < 0 :
                    typer.Exit()
            else :
                N = 0
            detector = detector + '_iter' + str(N)
        else :
            i = int(matches.group(1))
            detector = detector.replace(f'_iter{i}',f'_iter{i+1}')

        # deduce destination path, and make sure it does not exist
        dest_path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
        if os.path.isdir(dest_path) :
            if not interactive and not force :
                raise ValueError(f'Detector {detector} already exists and so it cannot be created')
            if interactive :
                typer.confirm(f'Overwite already existing detector {detector}?', abort=True)

        # make copy
        shutil.copytree(src_path, dest_path, dirs_exist_ok = True)

    # now we have bumped or not, so reconstruct detector path and check that it exists
    path = os.path.join(cfg.cfg().javadir, 'detector-data', 'detectors', detector)
    if not os.path.isdir(path) :
        raise typer.BadParameter(f'Detector {detector} is not in hps-java')

    # make sure compact exists
    detdesc = os.path.join(path,'compact.xml')
    if not os.path.isfile(detdesc) :
        raise typer.BadParameter(f'Detector {detector} has no compact.xml in {path} to apply parameter to.')

    # get list of parameters and their MP values
    parameters = Parameter.parse_pede_res(pede_res, skip_nonfloat=True)

    # modify file in place
    original_cp = detdesc + '.prev'
    shutil.copy2(detdesc,original_cp)
    f = open(detdesc,'w')
    with open(detdesc,'w') as f :
        with open(original_cp) as og :
            for line in og :
                if 'millepede_constant' not in line :
                    f.write(line)
                    continue

                line_edited = False
                for i in parameters :
                    if str(i) in line :
                        # the parameter with ID i is being set on this line
                        # format:
                        #   (whitespace) <millepede_constant name="<id>" value="<val>"/>

                        # get to value
                        i_value = line.find('value')
                        pre_val = line[:i_value]
                        post_val = line[i_value:]

                        # get to opening "
                        quote_open = post_val.find('"')
                        pre_val += post_val[:quote_open+1]
                        post_val = post_val[quote_open+1:]

                        # get to closing "
                        quote_close = post_val.find('"')
                        value = post_val[:quote_close]
                        post_val = post_val[quote_close:]

                        # we flip the sign of the alignment parameter
                        #  to "undo" the "misalignment"
                        op = '-' if parameters[i].val > 0 else '+'
                        new_value = f'{value} {op} {abs(parameters[i].val)}'

                        if interactive :
                            doit = typer.confirm(f'Update {i} from "{value}" to "{new_value}"?')
                            if doit :
                                f.write(f'{pre_val}{new_value}{post_val}')
                                line_edited = True
                        else :
                            f.write(f'{pre_val}{new_value}{post_val}')
                
                if not line_edited :
                    f.write(line)

    # if interactive, just ask user otherwise, delete original copy if we bump'ed
    #   because if we bumped then the original copy is available in the previous
    #   iteration of the detector
    if (interactive and typer.confirm('Delete original copy?')) or bump :
        os.remove(original_cp)

if __name__ == '__main__' :
    app()

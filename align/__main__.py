"""Main entrypoint when running this package

    python3 align <args>

Calls into this module.
"""

import os
from typing import List

import typer

from _cli import app
from _cfg import cfg
import construct
import tracking
import pede
import apply

@app.command()
def config() :
    """
    Print the deduced/parsed config for debugging
    """

    print(cfg.cfg())
    return

@app.command()
def iteration(detector : str, input_file : str,
    to_float : List[str] = typer.Option(...,
      help='parameters to float during pede minimization'),
    run : int = typer.Option(1194550,
      help='run number to use during tracking, default is for "perfect" 2019 MC run'),
    out_dir : str = typer.Option(os.getcwd(),
      help='base output directory to write output files to'),
    interactive : bool = typer.Option(False,
      help='ask for confirmation about stuff before progressing')
    ) :
    """
    Do a full iteration of construct -> tracking -> alignment -> application
    on the input detector and *single* input file.
    """

    od = os.path.join(str(out_dir),detector)

    if interactive and typer.confirm(f'Construct detector {detector}?') :
        construct.construct(detector)
    tracking.tracking(detector, run, input_file, out_dir = od, method = 'kf')
    pede.pede([od], to_float = to_float, 
        prefix = 'no-constraint-', out_dir = od)
    typer.confirm('Apply these deduced parameters by making a new iter?', abort=True)
    apply.apply(f'{od}/no-constraint-millepede.res', detector, 
        bump = True, force = False, interactive = interactive)

@app.callback()
def main(config : str =  typer.Option(None,help='JSON config file')):
    """
    run alignment sub commands
    """

    conf_kw = dict()
    if config is not None :
        with open(config) as f :
             conf_kw = json.load(f)

    cfg.cfg(**conf_kw)

if __name__ == '__main__' :
    app()

# mille/align

Run alignment steps from one Python3 interface.

There is one centralized CLI that you can access by running
this directory in python.
```
python3 mille/align --help
```

You can also run the sub-steps directly if you wish.
For example.
```
python3 mille/align/construct.py --help
```

## Set Up
Besides system packages, this CLI requires [typer](https://typer.tiangolo.com/).
```
python3 -m pip install -U typer
```

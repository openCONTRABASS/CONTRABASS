[![PyPI version](https://badge.fury.io/py/contrabass.svg)](https://badge.fury.io/py/contrabass) 
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) 
[![CI-CD](https://github.com/openCONTRABASS/CONTRABASS/actions/workflows/main.yml/badge.svg)](https://github.com/openCONTRABASS/CONTRABASS/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/openCONTRABASS/CONTRABASS/branch/main/graph/badge.svg?token=C9F6FT0PAV)](https://codecov.io/gh/openCONTRABASS/CONTRABASS)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=openCONTRABASS_CONTRABASS&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=openCONTRABASS_CONTRABASS) 
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
[![Documentation Status](https://readthedocs.org/projects/contrabass/badge/?version=latest)](https://contrabass.readthedocs.io/en/latest/?badge=latest) 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/openCONTRABASS/CONTRABASS/HEAD?labpath=docs%2Fsource%2FCORE.ipynb)
[![DOI](https://zenodo.org/badge/427404496.svg)](https://zenodo.org/badge/latestdoi/427404496)

## CONTRABASS - Constraint-based model vulnerabilities analysis

```CONTRABASS``` is a tool for the detection of vulnerabilities in metabolic models. The main purpose of the tool is to compute chokepoint and essential reactions by taking into account both the topology and the dynamic information of the model. In addition to the detection of vulnerabilities, CONTRABASS can compute essential genes, compute and remove dead-end metabolites, compute different sets of growth-dependent reactions, and update the flux bounds of the reactions according to the results of Flux Variability Analysis.

CONTRABASS takes as input the SBML file of a metabolic model, and provides as output a spreadsheet file and an html file reporting the obtained results. CONTRABASS accounts for the following sets of reactions and metabolites:

- **Chokepoint reactions:**  A reaction is a chokepoint if it is the unique consumer or the only producer of a given metabolite.
- **Essential Reactions:** A reaction is essential if its deletion, or equivalently, restricting its flux to zero, causes a significant decrease in the objective function (e.g. cellular growth). 
- **Dead-End Metabolites (DEM):** A metabolite is a dead-end metabolite if it is not produced or not consumed by any reaction.
- **Essential reactions for optimal growth:** A reaction is essential for optimal growth if its deletion, or equivalently, restricting its flux to zero, causes a decrease in the objective function.
- **Dead reactions:** A reaction is dead is its upper flux bound and its lower flux bound are equal to zero.
- **Blocked reactions:** A reaction is blocked if its flux is necessarily zero at any possible steady state of the model.
- **Reversible reactions:** A reaction is reversible if its upper flux bound is strictly positive and its lower flux bound is strictly negative.
- **Non-reversible reactions:** A reaction is non-reversible if it is not dead and not reversible.
- **Essential genes:** A gene is essential if the objetive function (e.g. cellular growth) is zero when it is knocked down.

<div align="center">
    <img alt="Example" title="Example" src="https://github.com/openCONTRABASS/CONTRABASS/blob/main/docs/source/_static/chokepoints_example.png" width="600">
    <p>Figure: In the network, reactions <i>Reac_2</i>, <i>Reac_5</i>, <i>Reac_6</i>, <i>Reac_7</i> and <i>Reac_8</i> are chokepoint reactions.<br>Metabolites <i>Lysine</i> and <i>Glutamate</i> are dead-end metabolites. </p>
</div>

The computation of vulnerabilities can also be exploited programmatically via the [Low Level API](#low-level-api) which is based on [COBRApy](https://github.com/opencobra/cobrapy). You can also [try the Low Level API with Binder](https://mybinder.org/v2/gh/openCONTRABASS/CONTRABASS/HEAD?labpath=docs%2Fsource%2FCORE.ipynb).


## Table of Contents
- [License](#license)
- [Install](#Install)
- [Quickstart](#Quickstart)
- [Documentation](#documentation)
- [Tool commands](#tool-commands)
- [Low Level API](#low-level-api)
- [Maintainers](#maintainers)
- [Contributing](#contributing)


## License

CONTRABASS is released under [GPLv3 license](LICENSE).

## Install
```CONTRABASS``` can be installed via **pip** package manager:
```shell
  $ pip install contrabass
```

## Quickstart

Generate report on vulnerabilities on input model ```MODEL.xml```

```shell
  $ contrabass report critial-reactions MODEL.xml
```

Generate report on growth-dependent reactions on input model ```MODEL.xml```

```shell
  $ contrabass report growth-dependent-reactions MODEL.xml
```

## Documentation

Documentation is available at [readthedocs](https://contrabass.readthedocs.io/en/latest/) and can also be [downloaded](https://contrabass.readthedocs.io/_/downloads/en/latest/pdf/). 
The previous links include examples and descriptions of the operations that can be performed with the tool.

## Tool commands

The next flowchart provides a graphical description of the available operations that can be performed with CONTRABASS and their respective commands:

<h1 align="center">
    <img alt="flowchart" title="flowchart" src="https://github.com/openCONTRABASS/CONTRABASS/blob/main/docs/source/_static/contrabass_flowchart.png" width="550">
</h1>

More information about the parameters of the tool can be obtained by executing ``contrabass -h``. 
For a detailed description of the operations see the [documentation](https://contrabass.readthedocs.io/en/latest/index.html). 

```shell
  $ contrabass

    Usage: contrabass [OPTIONS] COMMAND [ARGS]...
    
      Compute vulnerabilities on constraint-based models
    
    Options:
      -h, --help     Show this message and exit.
      -V, --version  Show the version and exit.
    
    Commands:
      new-model  Export refined constraint-based model.
      report     Compute vulnerabilities on constraint-based models.
```

## Low Level API

The computation of vulnerabilities can also be exploited via the COBRApy based low level API. For further information see the [Low Level API documentation](https://contrabass.readthedocs.io/en/latest/CORE.html). 
You can also [try it with Binder](https://mybinder.org/v2/gh/openCONTRABASS/CONTRABASS/HEAD?labpath=docs%2Fsource%2FCORE.ipynb).

Example of network refinement and chokepoint computation:
```python
from contrabass.core import CobraMetabolicModel

model = CobraMetabolicModel("aureus.xml")

# update flux bounds with FVA
model.fva(update_flux=True)

# compute chokepoints
model.find_chokepoints()

# get chokepoints
model.chokepoints()
```

## Maintainers

[@alexOarga](https://github.com/alexOarga)

## Contributing

Feel free to dive in! [Open an issue](https://github.com/openCONTRABASS/CONTRABASS/issues/new) or submit PRs.

Standard Readme follows the [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) Code of Conduct.





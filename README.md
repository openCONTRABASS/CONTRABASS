[![PyPI version](https://badge.fury.io/py/contrabass.svg)](https://badge.fury.io/py/contrabass) 
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) 
[![CI-CD](https://github.com/openCONTRABASS/CONTRABASS/actions/workflows/main.yml/badge.svg)](https://github.com/openCONTRABASS/CONTRABASS/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/openCONTRABASS/CONTRABASS/branch/main/graph/badge.svg?token=C9F6FT0PAV)](https://codecov.io/gh/openCONTRABASS/CONTRABASS)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=openCONTRABASS_CONTRABASS&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=openCONTRABASS_CONTRABASS) 
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
[![Documentation Status](https://readthedocs.org/projects/contrabass/badge/?version=latest)](https://contrabass.readthedocs.io/en/latest/?badge=latest) 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/openCONTRABASS/CONTRABASS/HEAD?labpath=docs%2Fsource%2FCORE.ipynb)

## CONTRABASS - Constraint-based model vulnerabilities analysis

```CONTRABASS``` is a command line python-tool for the computation of vulnerabilities reactions in genome-scale metabolic models. 
The main purpose of the tool is to compute vulnerabilities by taking into account both the topology and the dynamic information of the network. In addition to the computation of chokepoints, CONTRABASS can compute and remove dead-end metabolites, find essential reactions and update the flux bounds of the reactions according to the results of Flux Variability Analysis. 

CONTRABASS takes as input an SBML files of genome-scale models, and provides as output a spreadsheet file and html report file with the results of the vulnerabilities computation.

**Chokepoint reactions:** Chokepoint reactions are those reactions that are either the unique consumer or the only producer of a given metabolite. CONTRABASS makes use of the flux bounds of the model to determine consumer and producer reactions, and in turn, to compute chokepoint reactions.

**Dead-End Metabolites (DEM):** Dead-end metabolites are those metabolites that are not produced or consumed by any reaction.

**Essential Reactions:** A reaction is considered an essential reaction if its deletion, this is, restricting its flux to zero, causes the objective (e.g. cellular growth) to be zero.


_Figure:_ Chokepoint reactions and dead-end metabolites example:
![Chokepoint reactions and Dead-end metabolites example](docs/chokepoints_example.png)

The computation of vulnerabilities can also be exploited programmatically via the [Low Level API](#low-level-api) which is based on [COBRApy](https://github.com/opencobra/cobrapy). You can also [try the Low Level API with Binder](https://mybinder.org/v2/gh/openCONTRABASS/CONTRABASS/HEAD?labpath=docs%2Fsource%2FCORE.ipynb).


## Table of Contents
- [License](#license)
- [Install](#Install)
- [Quickstart](#Quickstart)
- [Documentation](#documentation)
- [Tool parameters](#tool-parameters)
- [Low Level API](#low-level-api)
- [Maintainers](#maintainers)
- [Contributing](#contributing)


## License

CONTRABASS is released under [GPLv3 license](LICENSE).


For citation purposes please refer to:

Oarga et al. **Growth Dependent Computation of Chokepoints in Metabolic Networks.** International Conference on Computational Methods in Systems Biology. Springer, Cham, 2020. https://doi.org/10.1007/978-3-030-60327-4_6


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

## Tool parameters

More information about the parameters of the tool can be obtained by executing ``contrabass -h``. 
For a detailed description of the operations see the [documentation](https://contrabass.readthedocs.io/en/latest/). 

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

The computation of vulnerabilities can also be exploited via the COBRApy based low level API. For further information see [Low Level API documentation](https://contrabass.readthedocs.io/en/latest/CORE.html). 
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





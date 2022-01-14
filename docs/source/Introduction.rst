.. _introduction:

1. Introduction
===============

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

1.1. Example
~~~~~~~~~~~~~~
Chokepoint reactions and dead-end metabolites example:

.. image:: _static/chokepoints_example.png
    :align: center
    :alt: alternate text

The computation of vulnerabilities can also be exploited programmatically via the Low Level API (see `core <CORE.html>`_) which is based on COBRApy_.

.. _COBRApy: https://github.com/opencobra/cobrapy

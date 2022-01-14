.. _fva-documentation:

7. Refine model with FVA
====================================

``contrabass`` can generate a new model in which the flux bounds of the reactions have been updated with the values obtained in the computation of FVA .
In this way the model can receive a different topology and the number of chokepoints, essential reactions or dead reactions, among others, can vary.
The pseudocode of this operation is presented below:


7.1. Pseudocode
+++++++++++++++++
- Update model flux bounds with Flux Variability Analysis
.. code-block::

    function update_flux_bounds_with_fva(model, fraction_of_optmimum_growth)
        max_fva, min_fva = flux_variability_analysis(model, fraction_of_optmimum_growth)
        for reaction in model
            reaction.upper_flux_bound = max_fva[reaction]
            reaction.lower_flux_bound = min_fva[reaction]
        return model


7.2. Command
+++++++++++++++++

Apart from computing vulnerabilities and generating reports, CONTRABASS can also produce a new model with refined
fluxes (procedure explained above). This can be achieved with command:

::

    $ contrabass new-model fva-constrained MODEL.xml


Alternatively a new model can be generated refined with FVA and with DEMs removed after.

::

    $ contrabass new-model fva-constrained-without-dem MODEL.xml

.

Note that the previous command is equivalent as first constraining the model with FVA (running command ``contrabass new-model fva-constrained``) and then removing DEM on the output model (running command ``contrabass new-model without-dem``):
::
    $ contrabass new-model fva-constrained MODEL.xml
    $ mv output.xml MODEL_FVA.xml
    $ contrabass new-model without-dem MODEL_FVA.xml

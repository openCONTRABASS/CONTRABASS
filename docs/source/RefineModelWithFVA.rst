
7. Refine model with FVA
====================================

``contrabass`` can generate a new model in which the flux bounds of the reactions have been updated with the values obtained in the computation of FVA .
In this way the model can receive a different topology and the number of chokepoints, essential reactions or dead reactions, among others, can vary.


::

    $ contrabass new-model fva-constrained MODEL.xml


Alternatively a new model can be generated refined with FVA and with DEMs removed after.

::

    $ contrabass new-model fva-constrained-without-dem MODEL.xml


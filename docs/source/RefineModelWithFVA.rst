
7. Refine model with FVA
====================================

findCPcli can generate a new model in which the flux bounds of the reactions have been updated with the values obtained in the computation of FVA . 
In this way the model can receive a different topology and the number of chokepoints, essential reactions or dead reactions, among others, can vary.


::

    $ findCPcli -i model.xml -sF new_model.xml


Alternatively a new model can be generated refined with FVA and with DEMs removed after.

::

    $ findCPcli -i model.xml -swDF new_model.xml


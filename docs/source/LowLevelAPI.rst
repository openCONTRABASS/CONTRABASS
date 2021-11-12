
9. Low Level API
================

The computation of chokepoints can also be exploited via findCPcore_ which is used by findCPcli. 
findCPcore_ documentation can be found at readthedocs_.

Example of network refinement and chokepoint computation:    

.. code-block:: python

  from findCPcore import CobraMetabolicModel

  model = CobraMetabolicModel("aureus.xml")

  # update flux bounds with FVA
  model.fva(update_flux=True)

  # compute chokepoints
  model.find_chokepoints()

  # get chokepoints
  model.chokepoints()


.. _findCPcore:  https://github.com/findCP/findCPcli/blob/master/LICENSE
.. _readthedocs: https://findcpcore.readthedocs.io/en/latest/

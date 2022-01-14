.. _dem-documentation:

6. Remove Dead-End Metabolites
====================================

6.1. Pseudocode
+++++++++++++++++
This sections presents the pseudocode of the procures that imply finding and removing dead-end metabolites:

- Find dead-end metabolites on a model
.. code-block::

    function find_dead_end_metabolites(model)
      dem_list = empty list
      for metabolite in model
          if length(metabolite.consumers) == 0 or length(metabolite.producers) == 0
              dem_list = dem_list + metabolite
      return dem_list

- Remove dead-end metabolites on a model
.. code-block::

    function remove_dead_end_metabolites(model)

        do while previous_metabolites != current_metabolites:

            previous_metabolites = model metabolites
            delete all metabolites in find_dead_end_metabolites(model)
            for reaction that produced or consumed dead-end metabolites:
                if reaction produces or consumes 0 metabolites [and is not exchange nor demand]:
                    delete reaction on model
            current_metabolites = model metabolites

        return model

6.2. Command
+++++++++++++++++

The following command exports a new generated model without Dead-End Metabolites from an input SBML model.

::

    $ contrabass new-model without-dem MODEL.xml



3. Pseudocode
===============

The following section includes pseudocode of some of the main operations performed by ``contrabass``.

- Find chokepoints on a model
.. code-block::

    function find_chokepoints(model)
        chokepoint_list = empty list
        for reaction in model
            if reaction upper flux bound not equal 0 and lower flux bound not equal 0
                for reactant in reaction
                    if reaction is the only consumer of reactant
                        chokepoint_list = chokepoint_list + (reaction, reactant)
                for product in reaction
                    if reaction is the only producer of product
                        chokepoint_list = chokepoint_list + (reaction, product)
        return chokepoint_list


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
        while number of metabolites in model does not change:
            find_dead_end_metabolites(model)
            delete all dead-end metabolites in model
            for reaction that produced or consumed dead-end metabolites:
                if reaction produces or consumes 0 metabolites [and is not exchange nor demand]:
                    delete reaction on model
            find_dead_end_metabolites(model)
        return model


- Update model flux bounds with Flux Variability Analysis
.. code-block::

    function update_flux_bounds_with_fva(model, fraction_of_optmimum_growth) 
        max_fva, min_fva = flux_variability_analysis(model, fraction_of_optmimum_growth)
        for reaction in model
            reaction.upper_flux_bound = max_fva[reaction]
            reaction.lower_flux_bound = min_fva[reaction]
        return model


- Find essential reactions
.. code-block::

    function find_essential_reactions(model)
      essential_reactions = empty list
      for reaction in model
          knock out reaction
          if flux_balance_analysis on model is 0
              essential_reactions = essential_reactions + reaction
          undo knock out
      return essential_reactions

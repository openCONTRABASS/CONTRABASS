
5. Compute growth dependent reactions
=======================================

contrabass can be used to compute `Growth Dependent Chokepoints <https://doi.org/10.1007/978-3-030-60327-4_6>`_  (amongst other reactions) as follows:
    1. the flux of the objective function is set to a given fraction of its optimal value;
    2. FVA is run to compute lower and upper flux bounds of the reactions;
    3. the flux bounds are used to identify reversible, non reversible and dead reactions (i.e. reaction with lower and upper bound equal to 0);
    4. this directionality of reactions is used to determine consumer and producer reactions, and in turn, chokepoints. The tool produces a spreadsheet and html report showing how the size of the set of chokepoints varies with the fraction of the optimal value set to the objective function.


::

    $ contrabass report growth-dependent-reactions MODEL.xml


5.1. Procedure pseudocode
**************************

The pseudocode of this task is included below:

::

    model = read_model()
    initial_reversible_reactions     = all reactions with upper flux bound > 0 and lower flux bound < 0
    initial_dead_reactions           = all reactions with both upper and lower flux bound equal to 0
    initial_non_reversible_reactions = (model.reactions - reversible_reactions) - dead_reactions
    initial_chokepoint_reactions     = find_chokepoints(model)
    
    for fraction in [0,0 ... 1,0]
        model = read_model()
        model = update_flux_bounds_with_fva(model, fraction)
        reversible_reactions[fraction]     = all reactions with upper flux bound > 0 and lower flux bound < 0
        dead_reactions[fraction]           = all reactions with both upper and lower flux bound equal to 0
        non_non_reversible_reactions[fraction] = (model.reactions - reversible_reactions) - dead_reactions
        chokepoint_reactions[fraction]     = find_chokepoints(model)

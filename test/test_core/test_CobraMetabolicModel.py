import logging
import sys
from enum import Enum

sys.path.append("src")

from contrabass.core.CobraMetabolicModel import CobraMetabolicModel
from generate_data import (
    TESTDATA_PRECOMPUTED_DEM,
    TESTDATA_PRECOMPUTED_CHOKEPOINTS,
    TESTDATA_PRECOMPUTED_GROWTH_CP,
)

LOGGER = logging.getLogger(__name__)
LOGGER_MSG = "Executing cli file: {} {}"

TEST_MODEL = "test/test_core/data/MODEL1507180056_url.xml"

EPSILON = 1e-8


class Direction(Enum):
    FORWARD = 0
    BACKWARD = 1
    REVERSIBLE = 2


def reaction_direction(reaction):
    if -EPSILON < reaction.upper_bound < EPSILON:
        upper = 0
    else:
        upper = reaction.upper_bound
    if -EPSILON < reaction.lower_bound < EPSILON:
        lower = 0
    else:
        lower = reaction.lower_bound

    if lower == 0 and upper == 0:
        # Note that reactions with upper and lower bound equal to 0 are considered FORWARD by default
        return Direction.FORWARD
    elif lower >= 0:
        return Direction.FORWARD
    elif upper > 0:
        return Direction.REVERSIBLE
    else:
        return Direction.BACKWARD


def flux_dependent_reactants_products(reaction):
    if reaction_direction(reaction) == Direction.FORWARD:
        reactants1 = reaction.reactants
        products1 = reaction.products
    elif reaction_direction(reaction) == Direction.REVERSIBLE:
        reactants1 = reaction.reactants + reaction.products
        products1 = reaction.reactants + reaction.products
    elif reaction_direction(reaction) == Direction.BACKWARD:
        reactants1 = reaction.products
        products1 = reaction.reactants
    else:
        raise RuntimeError("Error flux_dependent_reactants_products()")

    return reactants1, products1


"""
    Check that dead reactions have flux <closer> to zero.
"""
# @pytest.mark.skip(reason="")
def test_dead_reactions():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    for r in model.dead_reactions():
        assert EPSILON > abs(r.upper_bound)

    model.fva(update_flux=True)

    for r in model.dead_reactions():
        assert EPSILON > abs(r.upper_bound)


"""
    Check dead end metabolites corectness.
"""


def test_dead_end_metabolites():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    model.find_dem()
    model.dem()

    # A reversible reaction cannot produce/consume a DEM
    for c in model.compartments():
        for dem in model.dem()[c]:
            for r in dem.reactions:
                assert reaction_direction(r) != Direction.REVERSIBLE

    # Check they are only produced / consumedç
    for c in model.compartments():
        for dem in model.dem()[c]:
            reactants, products = flux_dependent_reactants_products(
                list(dem.reactions)[0]
            )
            is_product = dem in products

            for r in dem.reactions:
                reactants, products = flux_dependent_reactants_products(r)
                if is_product:
                    assert dem in products
                else:
                    assert dem in reactants


"""
    Check dead end metabolites corectness.
"""


def test_precomputed_dem():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    model.find_dem()
    model.dem()

    sets = set()
    for c in model.compartments():
        for dem in model.dem()[c]:
            sets.add(dem.id)

    # check both sets are identical
    assert len(sets.intersection(TESTDATA_PRECOMPUTED_DEM)) == len(sets)


"""
    Check dead end are removed.
"""


def test_remove_dem():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    model.find_dem()
    model.remove_dem()
    model.find_dem()

    for c in model.compartments():
        assert len(model.dem()[c]) == 0


"""
    Check chokepoint reactions are the only produced/consumer of metabolites
"""


def test_chokepoints():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    dead_reactions = model.dead_reactions()

    model.find_chokepoints()
    for r, m in model.chokepoints():
        counter_produced = 0
        counter_consumed = 0

        for r_test in m.reactions:
            if r_test not in dead_reactions:  # dead reactions are not chokepoints
                reactants, products = flux_dependent_reactants_products(r_test)
                if m in products:
                    counter_produced += 1
                if m in reactants:
                    counter_consumed += 1

                if counter_produced > 1 and counter_consumed > 1:
                    print(m.id + " --- " + r_test)

        assert counter_consumed <= 1 or counter_produced <= 1


"""
    Check pre-computed chokepoint reactions
"""


def test_precomputed_chokepoints():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    cps = set()

    model.find_chokepoints()
    for r, m in model.chokepoints():
        cps.add(r.id)

    # check both sets are identical
    assert len(cps.intersection(TESTDATA_PRECOMPUTED_CHOKEPOINTS)) == len(cps)


"""
    Check pre-computed growth dependent chokepoint reactions
"""


def test_precomputed_growth_chokepoints():
    model = CobraMetabolicModel(TEST_MODEL)
    EPSILON = model.epsilon()

    model.fva(update_flux=True)

    cps = set()

    model.find_chokepoints()
    for r, m in model.chokepoints():
        cps.add(r.id)

    # check both sets are identical
    assert len(cps.intersection(TESTDATA_PRECOMPUTED_GROWTH_CP)) == len(cps)

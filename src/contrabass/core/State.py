import itertools
import json
from json import JSONEncoder


class Reaction:
    id = None
    name = None
    reaction = None
    upper_bound = None
    lower_bound = None
    gene_reaction_rule = None
    metabolites = None
    genes = None

    def __init__(self, id, name, reaction, upper_bound, lower_bound, gene_reaction_rule):
        self.id = id
        self.name = name
        self.reaction = reaction
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.gene_reaction_rule = gene_reaction_rule
        self.metabolites = []
        self.genes = []

    def add_metabolite(self, metabolite):
        self.metabolites.append(metabolite)

    def add_gene(self, genes):
        self.genes.append(genes)

class Metabolite:
    id = None
    name = None
    compartment = None
    reactions = None

    def __init__(self, id, name, compartment):
        self.id = id
        self.name = name
        self.compartment = compartment
        self.reactions = []

    def add_reaction(self, reaction):
        self.reactions.append(reaction)

class Gene:
    id = None
    name = None
    reactions = None

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.reactions = []

    def add_reaction(self, reaction):
        self.reactions.append(reaction)

class State:
    __id = None
    __objective = None
    __objective_value = None

    __reactions = None
    __metabolites = None
    __genes = None

    __dem = None
    __chokepoints = None
    __fva = None
    __essential_genes = None
    __essential_genes_reactions = None
    __knockout_growth = None
    __essential_reactions = None

    def id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def objective(self):
        return self.__objective

    def set_objective(self, objective):
        self.__objective = objective

    def objective_value(self):
        return self.__objective_value

    def set_objective_value(self, objective_value):
        self.__objective_value = objective_value

    def reactions(self):
        return self.__reactions

    def set_reactions(self, reactions):
        self.__reactions = reactions

    def metabolites(self):
        return self.__metabolites

    def set_metabolites(self, metabolites):
        self.__metabolites = metabolites

    def genes(self):
        return self.__genes

    def set_genes(self, genes):
        self.__genes = genes

    def dem(self):
        return self.__dem

    def set_dem(self, dem):
        self.__dem = dem

    def chokepoints(self):
        return self.__chokepoints

    def set_chokepoints(self, chokepoints):
        self.__chokepoints = chokepoints

    def fva(self):
        return self.__fva

    def set_fva(self, fva):
        self.__fva = fva

    def essential_genes(self):
        return self.__essential_genes

    def set_essential_genes(self, essential_genes):
        self.__essential_genes = essential_genes

    def essential_genes_reactions(self):
        return self.__essential_genes_reactions

    def set_essential_genes_reactions(self, essential_genes_reactions):
        self.__essential_genes_reactions = essential_genes_reactions

    def knockout_growth(self):
        return self.__knockout_growth

    def set_knockout_growth(self, knockout_growth):
        self.__knockout_growth = knockout_growth

    def essential_reactions(self):
        return self.__essential_reactions

    def set_essential_reactions(self, essential_reactions):
        self.__essential_reactions = essential_reactions

    def reversible_reactions(self):
        return self.__reversible_reactions

    def set_reversible_reactions(self, reversible_reactions):
        self.__reversible_reactions = reversible_reactions

    def dead_reactions(self):
        return self.__dead_reactions

    def set_dead_reactions(self, dead_reactions):
        self.__dead_reactions = dead_reactions

    def to_json(self):
        return {
            "id": self.__id,
            "objective" : self.__objective,
            "objective_value": self.__objective_value,
            "reactions" : [r.id for r in self.__reactions],
            "metabolites": [m.id for m in self.__metabolites],
            "genes": [g.id for g in self.__genes],
            "dem": [m.id for m in list(itertools.chain.from_iterable(self.__dem.values()))],
            "chokepoints": [(r.id, m.id) for (r, m) in self.__chokepoints],
            "fva": [(reaction.id, upper, lower) for (reaction, upper, lower) in self.__fva],
            "essential_genes": [g.id for g in self.__essential_genes],
            "essential_genes_reactions": [r.id for r in self.__essential_genes_reactions],
            "knockout_growth": [(r.id, g) for r, g in self.__knockout_growth.items()],
            "essential_reactions":  self.__essential_reactions,
            "dead_reactions": self.__dead_reactions,
            "reversible_reactions": self.__reversible_reactions
        }

class CobraMetabolicStateBuilder:

    reactions = None
    metabolites = None
    genes = None

    def buildState(self, model):
        state = State()
        state.set_id(self.id(model))
        state.set_objective(self.objective(model))
        state.set_objective_value(self.objective_value(model))
        state.set_reversible_reactions(self.reversible_reactions(model))
        state.set_dead_reactions(self.dead_reactions(model))
        (metabolites, reactions, genes) = self.metabolic_network(model)
        state.set_reactions(reactions)
        state.set_metabolites(metabolites)
        state.set_genes(genes)
        state.set_essential_reactions(self.essential_reactions(model))
        state.set_dead_reactions(self.dead_reactions(model))
        state.set_reversible_reactions(self.reversible_reactions(model))
        try:
            state.set_dem(self.dem(model))
        except Exception:
            state.set_dem({})
        try:
            state.set_chokepoints(self.chokepoints(model))
        except Exception:
            state.set_chokepoints([])
        try:
            state.set_fva(self.fva(model))
        except Exception:
            state.set_fva([])
        try:
            state.set_essential_genes(self.essential_genes(model))
        except Exception:
            state.set_essential_genes([])
        try:
            state.set_essential_genes_reactions(self.essential_genes_reactions(model))
        except Exception:
            state.set_essential_genes_reactions({})
        try:
            state.set_knockout_growth(self.knockout_growth(model))
        except Exception:
            state.set_knockout_growth({})

        return state

    def id(self, model):
        return model.id()

    def objective(self, model):
        return model.objective()

    def objective_value(self, model):
        if model.objective_value() is None:
            return None
        else:
            return model.objective_value()

    def metabolic_network(self, model):
        metabolites = {}
        for metabolite in model.metabolites():
            metabolites[metabolite.id] = Metabolite(metabolite.id, metabolite.name, metabolite.compartment)
        reactions = {}
        for reaction in model.reactions():
            reactions[reaction.id] = Reaction(reaction.id, reaction.name, reaction.reaction, reaction.upper_bound, reaction.lower_bound, reaction.gene_reaction_rule)
        genes = {}
        for gene in model.genes():
            genes[gene.id] = Gene(gene.id, gene.name)

        self.metabolites = metabolites
        self.reactions = reactions
        self.genes = genes

        for reaction in model.reactions():
            new_reaction = reactions[reaction.id]
            for gene in reaction.genes:
                new_gene = genes[gene.id]
                new_reaction.add_gene(new_gene)
        for gene in model.genes():
            new_gene = genes[gene.id]
            for reaction in gene.reactions:
                new_reaction = reactions[reaction.id]
                new_gene.add_reaction(new_reaction)
        for metabolite in model.metabolites():
            new_metabolite = metabolites[metabolite.id]
            for reaction in metabolite.reactions:
                new_reaction = reactions[reaction.id]
                new_metabolite.add_reaction(new_reaction)

        return (list(metabolites.values()), list(reactions.values()), list(genes.values()))


    def dem(self, model):
        result = None
        dem = model.dem()
        if dem is not None:
            result = {}
            for compartment in dem.keys():
                list_c = [self.metabolites[metabolite.id] for metabolite in dem[compartment]]
                result[compartment] = list_c
        return result

    def chokepoints(self, model):
        result = None
        chokepoints = model.chokepoints()
        if chokepoints is not None:
            result = []
            for (reaction, metabolite) in chokepoints:
                result.append((self.reactions[reaction.id], self.metabolites[metabolite.id]))
        return result

    def fva(self, model):
        try:
            result = []
            model_fva = model.get_fva()
            if model_fva is not None:
                for el in model_fva:
                    (reaction, upper, lower) = el
                    local_reaction = self.reactions[reaction.id]
                    result.append((local_reaction, upper, lower))
            return result
        except Exception:
            return []

    def essential_genes(self, model):
        try:
            result = []
            genes = model.essential_genes()
            if genes is not None:
                gen_list = [self.genes[gen.id] for gen in genes]
                result = gen_list
            return result
        except Exception:
            return []

    def essential_genes_reactions(self, model):
        try:
            result = {}
            egr = model.essential_genes_reactions()
            if egr is not None:
                result = {}
                for reaction in egr:
                    for gen in egr[reaction]:
                        if reaction.id not in result:
                            result[self.reactions[reaction.id]] = [self.genes[gen.id]]
                        else:
                            result[self.reactions[reaction.id]].append(self.genes[gen.id])
            return result
        except Exception:
            return {}

    def knockout_growth(self, model):
        try:
            result = None
            essr = model.knockout_growth()
            if essr is not None:
                result = {}
                for reaction in essr.keys():
                    result[self.reactions[reaction.id]] = essr[reaction]
            return result
        except Exception:
            return {}

    def essential_reactions(self, model):
        model.compute_essential_reactions()
        return [r.id for r in model.essential_reactions()]

    def reversible_reactions(self, model):
        return [r.id for r in model.reversible_reactions()]

    def dead_reactions(self, model):
        return [r.id for r in model.dead_reactions()]


class StateEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, State):
            return o.to_json()
        return json.JSONEncoder.default(self, o)


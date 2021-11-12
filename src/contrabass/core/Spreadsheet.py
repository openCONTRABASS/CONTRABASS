import xlwt
import itertools
from math import isnan


class Spreadsheet:

    __spreadsheet = None

    def spreadsheet_init(self):
        """Initialize the xlwt Workbook"""
        self.__spreadsheet = xlwt.Workbook()

    def set_workbook(self, workbook):
        self.__spreadsheet = workbook

    def get_workbook(self):
        return self.__spreadsheet

    def spreadsheet_write_model_info(self, state, sheet_name):
        """Writes in a sheet of the xlwt Workbook '__spreadsheet' info of the model with the following format:

                        MODEL_ID | REACTIONS | METABOLITES | GENES
                        ---------+-----------+-------------+-------
                        model id | len(reac.)| len(metab.) | len(genes)

        Args:
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "MODEL_ID", style=style)
        sheet.write(0, 1, state.id())
        sheet.write(1, 0, "REACTIONS", style=style)
        sheet.write(1, 1, len(state.reactions()))
        sheet.write(2, 0, "METABOLITES", style=style)
        sheet.write(2, 1, len(state.metabolites()))
        sheet.write(3, 0, "GENES", style=style)
        sheet.write(3, 1, len(state.genes()))
        sheet.write(4, 0, "OBJECTIVE FUNCTION", style=style)
        sheet.write(4, 1, state.objective())

    def __id(self, e):
        return e.id

    def __spreadsheet_write_metabolites(
        self, list, sheet_name, ordered=True, print_reactions=False
    ):
        """Writes in a sheet of the xlwt Workbook '__spreadsheet' the metabolites of the model with the following format:

                METABOLITE ID | METABOLITE NAME | METABOLITE COMPARTMENT | REACTION ID | REACTION NAME | REACTION
                --------------+-----------------+------------------------+-------------+---------------+----------
                mtb 1         | metabolite 1    | compartment 1          | react1      | reaction 1    | mtb 1 -> mtb 2
                --------------+-----------------+------------------------+-------------+---------------+----------
                                          |                 |                        | react2      | reaction 2    | mtb 1 -> mtb 3

        Args:
                list (): List of cobra.core.metabolites to be written.
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
                ordered (): Write the metabolites in alphabetical order by id.
                print_reactions (): Write the reactions in which a metabolite appears.
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()
        metabolites = list
        if ordered:
            metabolites.sort(key=self.__id)

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "METABOLITE ID", style=style)
        sheet.write(0, 1, "METABOLITE NAME", style=style)
        sheet.write(0, 2, "METABOLITE COMPARTMENT", style=style)
        if print_reactions:
            sheet.write(0, 3, "REACTION ID", style=style)
            sheet.write(0, 4, "REACTION NAME", style=style)
            sheet.write(0, 5, "UPPER BOUND", style=style)
            sheet.write(0, 6, "LOWER BOUND", style=style)
            sheet.write(0, 7, "REACTION", style=style)
        i = 1
        for metabolite in metabolites:
            sheet.write(i, 0, metabolite.id)
            sheet.write(i, 1, metabolite.name)
            sheet.write(i, 2, metabolite.compartment)
            if print_reactions:
                reactions = []
                for r in metabolite.reactions:
                    reactions.append(r)
                reactions.sort(key=self.__id)
                for reaction in reactions:
                    sheet.write(i, 3, reaction.id)
                    sheet.write(i, 4, reaction.name)
                    sheet.write(i, 5, reaction.upper_bound)
                    sheet.write(i, 6, reaction.lower_bound)
                    sheet.write(i, 7, reaction.reaction)
                    i = i + 1
            if not print_reactions or len(reactions) == 0:
                i = i + 1

    def spreadsheet_write_reactions(
        self, state, sheet_name, ordered=True, print_genes=False
    ):
        """Writes in a sheet of the xlwt Workbook '__spreadsheet' the reactions of the model with the following format:

                REACTION ID | REACTION NAME | REACTION | UPPER BOUND | LOWER BOUND | CHOKEPOINT | ESSENTIAL GENE
                ------------+---------------+----------+-------------+-------------+------------+----------------
                react 1     | reaction 1    | mt1->mt2 | 1000        | 0           | TRUE       |
                ------------+---------------+----------+-------------+-------------+------------+----------------
                react 2     | reaction 2    | mt3->mt4 | 2000        | 0           |            | TRUE

        Args:
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
                ordered (): Print the reactions in alphabetical order by id
                tag_chokepoints (): mark a reaction with 'TRUE' if chokepoint reaction
                tag_essential_genes (): mark a reactions with 'TRUE' if associated to an essential gene
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        reactions = state.reactions()
        if ordered:
            reactions.sort(key=self.__id)

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "REACTION ID", style=style)
        sheet.write(0, 1, "REACTION NAME", style=style)
        sheet.write(0, 2, "REACTION GPR", style=style)
        sheet.write(0, 3, "REACTION", style=style)
        sheet.write(0, 4, "UPPER BOUND", style=style)
        sheet.write(0, 5, "LOWER BOUND", style=style)
        i = 1
        for reaction in reactions:
            sheet.write(i, 0, reaction.id)
            sheet.write(i, 1, reaction.name)
            sheet.write(i, 2, reaction.gene_reaction_rule[:32760])
            sheet.write(i, 3, reaction.reaction)
            sheet.write(i, 4, reaction.upper_bound)
            sheet.write(i, 5, reaction.lower_bound)
            i = i + 1

    def spreadsheet_write_metabolites(
        self, state, sheet_name, ordered=True, print_reactions=False
    ):
        """Writes the metabolites of the model with the function '__spreadsheet_write_metabolites'"""
        self.__spreadsheet_write_metabolites(
            state.metabolites(), sheet_name, ordered, print_reactions
        )

    def spreadsheet_write_genes(
        self, state, sheet_name, ordered=False, print_reactions=False
    ):
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        genes = state.genes()
        if ordered:
            genes.sort(key=self.__id)

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "GENE ID", style=style)
        sheet.write(0, 1, "GENE NAME", style=style)
        if print_reactions:
            sheet.write(0, 2, "GENE RELATION", style=style)
            sheet.write(0, 3, "REACTION ID", style=style)
            sheet.write(0, 4, "REACTION NAME", style=style)
        i = 1
        for gen in genes:
            sheet.write(i, 0, gen.id)
            sheet.write(i, 1, gen.name)
            if print_reactions:
                reactions = []
                for r in gen.reactions:
                    reactions.append(r)
                reactions.sort(key=self.__id)
                for reaction in reactions:
                    gpr = (
                        (reaction.gene_reaction_rule[:32760] + "...")
                        if len(reaction.gene_reaction_rule) > 32765
                        else reaction.gene_reaction_rule
                    )
                    sheet.write(i, 2, gpr)
                    sheet.write(i, 3, reaction.id)
                    sheet.write(i, 4, reaction.name)
                    i = i + 1
            if not print_reactions or len(reactions) == 0:
                i = i + 1

    def spreadsheet_write_dem(
        self, state, sheet_name, ordered=False, print_reactions=False, compartment="ALL"
    ):
        """Writes the dead end metabolites of the model with the function '__spreadsheet_write_metabolites'"""
        if state.dem() is not None:
            if compartment == "ALL":
                all_dems = list(itertools.chain.from_iterable(state.dem().values()))
                self.__spreadsheet_write_metabolites(
                    all_dems, sheet_name, ordered, print_reactions
                )
            else:
                if compartment in state.dem().keys():
                    self.__spreadsheet_write_metabolites(
                        state.dem()[compartment], sheet_name, ordered, print_reactions
                    )

    def __reaction_id(self, obj):
        """Given an object _MetaboliteReact it returns the 'id' of the reaction

        Args:
                obj (): Object cobra.core.reaction

        Returns: 'id' field of the reaction

        """
        (reaction, metabolite) = obj
        return reaction.id

    def spreadsheet_write_chokepoints(self, state, sheet_name, ordered=False):
        """"""
        if self.__spreadsheet is None:
            self.spreadsheet_init()
        if state.chokepoints() is not None:
            chokepoints = state.chokepoints()
            if ordered:
                chokepoints.sort(key=self.__reaction_id)
            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.bold = True
            style.font = font
            sheet = self.__spreadsheet.add_sheet(sheet_name)
            sheet.write(0, 0, "REACTION ID", style=style)
            sheet.write(0, 1, "METABOLITE ID", style=style)
            i = 1
            for (reaction, metabolite) in chokepoints:
                sheet.write(i, 0, reaction.id)
                sheet.write(i, 1, metabolite.id)
                i = i + 1

    def spreadsheet_write_reversible_reactions(
        self, sheet_name, state_initial, state_fva, ordered=False
    ):
        """"""
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        reactions = state_initial.reactions()
        if ordered:
            reactions.sort(key=self.__id)

        reversible_initial = state_initial.reversible_reactions()
        reversible_fva = state_fva.reversible_reactions()

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "REACTION ID", style=style)
        sheet.write(0, 1, "REVERSIBLE INITIAL", style=style)
        sheet.write(0, 2, "REVERSIBLE FVA", style=style)
        i = 1
        for reaction in reactions:
            sheet.write(i, 0, reaction.id)
            if reaction.id in reversible_initial:
                sheet.write(i, 1, "TRUE")
            if reaction.id in reversible_fva:
                sheet.write(i, 2, "TRUE")
            i = i + 1

    def __reaction_id_fva(self, obj):
        (react, max, min) = obj
        return react.id

    def spreadsheet_write_fva(self, state, sheet_name, ordered=False):
        """Writes in a sheet of the xlwt Workbook '__spreadsheet' the result of the Flux Variability Analysis.

                REACTION ID | REACTION NAME | REACTION | MAXIMUN | MINIMUM
                ------------+---------------+----------+---------+------------
                react 1     | reaction 1    | mt1->mt2 | 1000    | 0
                ------------+---------------+----------+---------+------------
                react 2     | reaction 2    | mt3->mt4 | 2000    |

        Args:
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
                ordered (): Print the reactions in alphabetical order by id
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        if state.fva() is not None:
            fva = state.fva()
            if ordered:
                fva.sort(key=self.__reaction_id_fva)
            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.bold = True
            style.font = font
            sheet = self.__spreadsheet.add_sheet(sheet_name)
            sheet.write(0, 0, "REACTION ID", style=style)
            sheet.write(0, 1, "REACTION NAME", style=style)
            sheet.write(0, 2, "MAX", style=style)
            sheet.write(0, 3, "MIN", style=style)
            i = 1
            for obj in fva:
                (reaction, max, min) = obj
                sheet.write(i, 0, reaction.id)
                sheet.write(i, 1, reaction.name)
                sheet.write(i, 2, max)
                sheet.write(i, 3, min)
                i = i + 1

    def spreadsheet_write_essential_genes(self, state, sheet_name, ordered=False):
        """If the model has genes, writes in a sheet of the xlwt Workbook '__spreadsheet'
                the essential genes of the model with the following format:

                GENE ID | REACTION ID | REACTION NAME | REACTION
                --------+-------------+---------------+-------------
                gene 1  | react 1     | reaction 1    | mt1 + mt2 -> mt3
                --------+-------------+---------------+-------------
                        | react 2     | reaction 2    | mt4 -> mt5
                --------+-------------+---------------+-------------
                gene 2  | react 1     | reaction 1    | mt1 + mt2 -> mt3

        Args:
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
                ordered (): Print the genes in alphabetical order by id
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        if state.essential_genes() is not None:

            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.bold = True
            style.font = font
            sheet = self.__spreadsheet.add_sheet(sheet_name)
            sheet.write(0, 0, "GENE ID", style=style)
            sheet.write(0, 1, "GENE NAME", style=style)
            sheet.write(0, 2, "REACTION GENE RELATION", style=style)
            sheet.write(0, 3, "REACTION ID", style=style)
            sheet.write(0, 4, "REACTION NAME", style=style)

            genes = state.essential_genes()
            if ordered:
                genes.sort(key=self.__id)
            row = 1
            for gene in genes:
                reactions = gene.reactions
                sheet.write(row, 0, gene.id)
                sheet.write(row, 1, gene.name)
                gpr = (
                    (reactions[0].gene_reaction_rule[:32760] + "...")
                    if len(reactions[0].gene_reaction_rule) > 32765
                    else reactions[0].gene_reaction_rule
                )
                sheet.write(row, 2, reactions[0].gene_reaction_rule)
                sheet.write(row, 3, reactions[0].id)
                sheet.write(row, 4, reactions[0].name)
                row = row + 1
                i = 1
                while i < len(reactions):
                    gpr = (
                        (reactions[i].gene_reaction_rule[:32760] + "...")
                        if len(reactions[i].gene_reaction_rule) > 32765
                        else reactions[i].gene_reaction_rule
                    )
                    sheet.write(row, 2, gpr)
                    sheet.write(row, 3, reactions[i].id)
                    sheet.write(row, 4, reactions[i].name)
                    i = i + 1
                    row = row + 1

    def spreadsheet_write_essential_genes_reactions(
        self, state, sheet_name, ordered=False
    ):
        """If the model has genes, writes in a sheet of the xlwt Workbook '__spreadsheet'
                the reactions associated to the essential genes of the model with the following format:

                REACTION ID | REACTION NAME | REACTION | GENE ID
                ------------+---------------+----------+-------------
                react 1     | reaction 1    | mt1->mt2 | gene1
                ------------+---------------+----------+-------------
                            |               |          | gene2
                ------------+---------------+----------+-------------
                react 2     | reaction 2    | mt1->mt2 | gene3

        Args:
                sheet_name (): Name of the new sheet. Two diffetent sheets can't have the same name.
                ordered (): Print the reactions in alphabetical order by id
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()
        if state.essential_genes_reactions() is not None:
            reactions = state.essential_genes_reactions()

            style = xlwt.XFStyle()
            font = xlwt.Font()
            font.bold = True
            style.font = font
            sheet = self.__spreadsheet.add_sheet(sheet_name)
            sheet.write(0, 0, "REACTION ID", style=style)
            sheet.write(0, 1, "REACTION NAME", style=style)
            sheet.write(0, 2, "GENE REACTION RELATION", style=style)
            sheet.write(0, 3, "GENE ID", style=style)
            sheet.write(0, 4, "GENE NAME", style=style)
            reactions_key = reactions.keys()
            if ordered:
                reactions_key = sorted(reactions.keys(), key=self.__id)
            row = 1
            for reaction in reactions_key:
                genes = reactions[reaction]
                sheet.write(row, 0, reaction.id)
                sheet.write(row, 1, reaction.name)
                gpr = (
                    (reaction.gene_reaction_rule[:32760] + "...")
                    if len(reaction.gene_reaction_rule) > 32765
                    else reaction.gene_reaction_rule
                )
                sheet.write(row, 2, gpr)
                sheet.write(row, 3, genes[0].id)
                sheet.write(row, 4, genes[0].name)
                row = row + 1
                i = 1
                while i < len(genes):
                    sheet.write(row, 3, genes[i].id)
                    sheet.write(row, 4, genes[i].name)
                    i = i + 1
                    row = row + 1

    def spreadsheet_write_essential_reactions(
        self,
        sheet_name,
        state_initial,
        state_dem,
        state_fva,
        state_fva_dem,
        ordered=True,
    ):
        """"""
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        reactions_initial = {}
        if state_initial.knockout_growth() is not None:
            for reaction, growth in state_initial.knockout_growth().items():
                reactions_initial[reaction.id] = growth
        reactions_dem = {}
        if state_dem.knockout_growth() is not None:
            for reaction, growth in state_dem.knockout_growth().items():
                reactions_dem[reaction.id] = growth
        reactions_fva = {}
        if state_fva.knockout_growth() is not None:
            for reaction, growth in state_fva.knockout_growth().items():
                reactions_fva[reaction.id] = growth
        reactions_fva_dem = {}
        if state_fva_dem.knockout_growth() is not None:
            for reaction, growth in state_fva_dem.knockout_growth().items():
                reactions_fva_dem[reaction.id] = growth

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "REACTION ID", style=style)
        sheet.write(0, 1, "REACTION NAME", style=style)
        sheet.write(0, 2, "OBJECTIVE INITIAL", style=style)
        sheet.write(0, 3, "OBJECTIVE DEM", style=style)
        sheet.write(0, 4, "OBJECTIVE FVA", style=style)
        sheet.write(0, 5, "OBJECTIVE FVA DEM", style=style)
        reactions_initial_key = reactions_initial.keys()
        reactions_dem_key = reactions_dem.keys()
        reactions_fva_key = reactions_fva.keys()
        reactions_fva_dem_key = reactions_fva_dem.keys()
        if ordered:
            reactions = sorted(
                state_initial.knockout_growth().keys(), key=self.__id
            )
        row = 1
        for reaction in reactions:
            sheet.write(row, 0, reaction.id)
            sheet.write(row, 1, reaction.name)
            if reaction.id in reactions_initial_key:
                sheet.write(row, 2, reactions_initial[reaction.id])
            if reaction.id in reactions_dem_key:
                sheet.write(row, 3, reactions_dem[reaction.id])
            if reaction.id in reactions_fva_key:
                sheet.write(row, 4, reactions_fva[reaction.id])
            if reaction.id in reactions_fva_dem_key:
                sheet.write(row, 5, reactions_fva_dem[reaction.id])
            row = row + 1

    def spreadsheet_write_essential_genes_comparison(
        self,
        sheet_name,
        state_initial,
        state_dem,
        state_fva,
        state_fva_dem,
        ordered=True,
    ):
        """"""
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        essential_genes_initial = [g.id for g in state_initial.essential_genes()]
        essential_genes_dem = [g.id for g in state_dem.essential_genes()]
        essential_genes_fva = [g.id for g in state_fva.essential_genes()]
        essential_genes_fva_dem = [g.id for g in state_fva_dem.essential_genes()]

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "GENE ID", style=style)
        sheet.write(0, 1, "GENE NAME", style=style)
        sheet.write(0, 2, "MODEL INITIAL", style=style)
        sheet.write(0, 3, "MODEL WITHOUT DEM", style=style)
        sheet.write(0, 4, "MODEL FVA", style=style)
        sheet.write(0, 5, "MODE FVA WITHOUT DEM", style=style)

        if ordered:
            genes = sorted(state_initial.genes(), key=self.__id)
        else:
            genes = state_initial.genes()

        row = 1
        for gene in genes:
            sheet.write(row, 0, gene.id)
            sheet.write(row, 1, gene.name)
            if gene.id in essential_genes_initial:
                sheet.write(row, 2, True)
            if gene.id in essential_genes_dem:
                sheet.write(row, 3, True)
            if gene.id in essential_genes_fva:
                sheet.write(row, 4, True)
            if gene.id in essential_genes_fva_dem:
                sheet.write(row, 5, True)
            row = row + 1

    def spreadsheet_write_summary_reactions(
        self, sheet_name, state_initial, state_dem, state_fva, state_fva_dem
    ):
        """

        Args:
                sheet_name ():

        Returns:

        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        reactions = state_initial.reactions()
        reactions.sort(key=self.__id)

        #
        initial_chokepoints_dict = {}
        if state_initial.chokepoints() is not None:
            for el in state_initial.chokepoints():
                (reaction, metabolite) = el
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in initial_chokepoints_dict:
                    initial_chokepoints_dict[reaction].append(metabolite)
                else:
                    initial_chokepoints_dict[reaction] = [metabolite]
        #
        chokepoints_dem_dict = {}
        if state_dem.chokepoints() is not None:
            for el in state_dem.chokepoints():
                (reaction, metabolite) = el
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in chokepoints_dem_dict:
                    chokepoints_dem_dict[reaction].append(metabolite)
                else:
                    chokepoints_dem_dict[reaction] = [metabolite]
        #
        chokepoints_fva_dict = {}
        if state_fva.chokepoints() is not None:
            for el in state_fva.chokepoints():
                (reaction, metabolite) = el
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in chokepoints_fva_dict:
                    chokepoints_fva_dict[reaction].append(metabolite)
                else:
                    chokepoints_fva_dict[reaction] = [metabolite]
        #
        chokepoints_fva_dem_dict = {}
        if state_fva_dem.chokepoints() is not None:
            for el in state_fva_dem.chokepoints():
                (reaction, metabolite) = el
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in chokepoints_fva_dem_dict:
                    chokepoints_fva_dem_dict[reaction].append(metabolite)
                else:
                    chokepoints_fva_dem_dict[reaction] = [metabolite]

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font
        sheet = self.__spreadsheet.add_sheet(sheet_name, cell_overwrite_ok=True)
        sheet.write(0, 0, "REACTION ID", style=style)
        sheet.write(0, 1, "REACTION", style=style)
        sheet.write(0, 2, "CHOKEPOINT INITIAL", style=style)
        sheet.write(0, 3, "CHOKEPOINT AFTER DEM REMOVE", style=style)
        sheet.write(0, 4, "CHOKEPOINT AFTER FVA", style=style)
        sheet.write(0, 5, "CHOKEPOINT AFTER FVA AND DEM REMOVE", style=style)
        i = 1
        for reaction in reactions:
            sheet.write(i, 0, reaction.id)
            sheet.write(i, 1, reaction.reaction)
            j = 0
            if reaction.id in initial_chokepoints_dict:
                for metabolite in initial_chokepoints_dict[reaction.id]:
                    sheet.write(i + j, 2, metabolite)
                    sheet.write(i + j, 6, " ")
                    j = j + 1
            else:
                sheet.write(i + j, 2, " ")
            k = 0
            if reaction.id in chokepoints_dem_dict:
                for metabolite in chokepoints_dem_dict[reaction.id]:
                    sheet.write(i + k, 3, metabolite)
                    sheet.write(i + k, 6, " ")
                    k = k + 1
            else:
                sheet.write(i + k, 3, " ")
            l = 0
            if reaction.id in chokepoints_fva_dict:
                for metabolite in chokepoints_fva_dict[reaction.id]:
                    sheet.write(i + l, 4, metabolite)
                    sheet.write(i + l, 6, " ")
                    l = l + 1
            else:
                sheet.write(i + l, 4, " ")
            m = 0
            if reaction.id in chokepoints_fva_dem_dict:
                for metabolite in chokepoints_fva_dem_dict[reaction.id]:
                    sheet.write(i + m, 5, metabolite)
                    sheet.write(i + m, 6, " ")
                    m = m + 1
            else:
                sheet.write(i + m, 5, " ")
            maxim = max(j, k, l, m)
            if maxim == 0:
                i = i + 1
            else:
                i = i + maxim

    def spreadsheet_write_summary_metabolites(
        self, sheet_name, state_initial, state_fva
    ):

        if self.__spreadsheet is None:
            self.spreadsheet_init()

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font

        aux_dem_init = []
        if state_initial.dem() is not None:
            aux = list(itertools.chain.from_iterable(state_initial.dem().values()))
            aux_dem_init = [e.id for e in aux]
        aux_dem_fva = []
        if state_fva.dem() is not None and state_fva.fva() is not None:
            aux = list(itertools.chain.from_iterable(state_fva.dem().values()))
            aux_dem_fva = [e.id for e in aux]
        metabolites = state_initial.metabolites()
        metabolites.sort(key=self.__id)
        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(0, 0, "METABOLITE ID", style=style)
        sheet.write(0, 1, "METABOLITE NAME", style=style)
        sheet.write(0, 2, "METABOLITE COMPARTMENT", style=style)
        sheet.write(0, 3, "DEM", style=style)
        sheet.write(0, 4, "DEM AFTER FVA", style=style)
        i = 1
        for metabolite in metabolites:
            sheet.write(i, 0, metabolite.id)
            sheet.write(i, 1, metabolite.name)
            sheet.write(i, 2, metabolite.compartment)
            if metabolite.id in aux_dem_init:
                sheet.write(i, 3, "TRUE")
            if metabolite.id in aux_dem_fva:
                sheet.write(i, 4, "TRUE")
            i = i + 1

    def __aux_spreadsheet_write_chokepoints_genes(self, state):
        chokepoints_dict = {}
        if state.chokepoints() is not None:
            for (reaction, metabolite) in state.chokepoints():
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in chokepoints_dict:
                    chokepoints_dict[reaction].append(metabolite)
                else:
                    chokepoints_dict[reaction] = [metabolite]
        genes_reactions_dict = {}
        if state.essential_genes_reactions() is not None:
            for reaction in state.essential_genes_reactions().keys():
                for gen in state.essential_genes_reactions()[reaction]:
                    reaction = reaction.id
                    gen = gen.id
                    if reaction in genes_reactions_dict:
                        genes_reactions_dict[reaction].append(gen)
                    else:
                        genes_reactions_dict[reaction] = [gen]
        knockout_growth = {}
        if state.knockout_growth() is not None:
            for reaction, growth in state.knockout_growth().items():
                knockout_growth[reaction.id] = growth

        return (chokepoints_dict, genes_reactions_dict, knockout_growth)

    def spreadsheet_write_chokepoints_genes(
        self, sheet_name, state_initial, state_dem, state_fva, state_fva_dem
    ):
        """

        Args:
                sheet_name ():

        Returns:

        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font

        sheet = self.__spreadsheet.add_sheet(sheet_name)
        sheet.write(1, 0, "REACTION ID", style=style)
        sheet.write(0, 2, "INITIAL MODEL", style=style)
        sheet.write(0, 6, "MODEL AFTER D.E.M. REMOVED", style=style)
        sheet.write(0, 10, "MODEL AFTER F.V.A.", style=style)
        sheet.write(0, 14, "MODEL AFTER F.V.A. AND D.E.M. REMOVED", style=style)

        sheet.write(1, 2, "CHOKEPOINT", style=style)
        sheet.write(1, 3, "ESSENTIAL GENE REACTION", style=style)
        sheet.write(1, 4, "OBJECTIVE VALUE", style=style)
        sheet.write(1, 6, "CHOKEPOINT", style=style)
        sheet.write(1, 7, "ESSENTIAL GENE REACTION", style=style)
        sheet.write(1, 8, "OBJECTIVE VALUE", style=style)
        sheet.write(1, 10, "CHOKEPOINT", style=style)
        sheet.write(1, 11, "ESSENTIAL GENE REACTION", style=style)
        sheet.write(1, 12, "OBJECTIVE VALUE", style=style)
        sheet.write(1, 14, "CHOKEPOINT", style=style)
        sheet.write(1, 15, "ESSENTIAL GENE REACTION", style=style)
        sheet.write(1, 16, "OBJECTIVE VALUE", style=style)

        models = [state_initial, state_dem, state_fva, state_fva_dem]
        j = 2
        reactions = state_initial.reactions()
        reactions.sort(key=self.__id)
        for model in models:
            i = 2
            (
                chokepoints,
                genes_reactions,
                knockout_growth,
            ) = self.__aux_spreadsheet_write_chokepoints_genes(model)
            for reaction_obj in reactions:
                reaction = reaction_obj.id
                if j == 2:
                    sheet.write(i, 0, reaction)
                    sheet.write(i, 1, " ")
                if reaction in chokepoints.keys():
                    sheet.write(i, j, "TRUE")
                if reaction in genes_reactions.keys():
                    sheet.write(i, j + 1, "TRUE")
                if reaction in knockout_growth.keys():
                    sheet.write(i, j + 2, knockout_growth[reaction])
                i = i + 1
            j = j + 4

    def __aux_spreadsheet_get_data(self, state):
        dem = []
        if state.dem() is not None:
            metabolites = list(itertools.chain.from_iterable(state.dem().values()))
            dem = [m.id for m in metabolites]

        chokepoints_dict = {}
        if state.chokepoints() is not None:
            for (reaction, metabolite) in state.chokepoints():
                reaction = reaction.id
                metabolite = metabolite.id
                if reaction in chokepoints_dict:
                    chokepoints_dict[reaction].append(metabolite)
                else:
                    chokepoints_dict[reaction] = [metabolite]
        genes_reactions_dict = {}
        if state.essential_genes_reactions() is not None:
            for reaction in state.essential_genes_reactions().keys():
                for gen in state.essential_genes_reactions()[reaction]:
                    reaction = reaction.id
                    gen = gen.id
                    if reaction in genes_reactions_dict:
                        genes_reactions_dict[reaction].append(gen)
                    else:
                        genes_reactions_dict[reaction] = [gen]
        knockout_growth = {}
        if state.knockout_growth() is not None:
            for reaction, growth in state.knockout_growth().items():
                knockout_growth[reaction.id] = growth

        essential_genes = []
        if state.essential_genes() is not None:
            essential_genes = [g.id for g in state.essential_genes()]

        er_g0 = []
        er_g005 = []
        objective_value = state.objective_value()
        if state.objective_value() is not None:
            if not isnan(state.objective_value()):
                objective_value_005 = state.objective_value() * 0.05
            else:
                objective_value_005 = 0
            for reaction, value in knockout_growth.items():
                if not isnan(objective_value):
                    if isnan(value) or value == 0:
                        er_g0.append(reaction)
                        er_g005.append(reaction)
                    elif value < objective_value_005:
                        er_g005.append(reaction)
                else:
                    er_g0.append(reaction)
                    er_g005.append(reaction)

        reversibles = state.reversible_reactions()

        dead_reactions = state.dead_reactions()

        return [
            dem,
            list(chokepoints_dict.keys()),
            essential_genes,
            genes_reactions_dict,
            knockout_growth,
            er_g0,
            er_g005,
            reversibles,
            dead_reactions,
        ]

    #
    def __aux_spreadsheet_write_two_model_summary(
        self, sheet, style, x, y, title, list_model_1, list_model_2
    ):
        sheet.write(x, y, title, style=style)
        sheet.write(x + 2, y + 1, "Dead-end metabolites", style=style)
        sheet.write(x + 3, y + 1, "Chokepoint reactions", style=style)
        sheet.write(x + 4, y + 1, "Essential genes", style=style)
        sheet.write(x + 5, y + 1, "Essential genes reactions", style=style)
        sheet.write(x + 6, y + 1, "Essential reactions (objective=0)", style=style)
        sheet.write(
            x + 7,
            y + 1,
            "Essential reactions (objective < 5% max objective)",
            style=style,
        )
        sheet.write(x + 8, y + 1, "Reversible reactions", style=style)
        sheet.write(x + 9, y + 1, "Dead reactions", style=style)
        sheet.write(x + 1, y + 2, "Before", style=style)
        sheet.write(x + 1, y + 3, "After", style=style)
        sheet.write(x + 1, y + 5, "Only before", style=style)
        sheet.write(x + 1, y + 6, "Intersection", style=style)
        sheet.write(x + 1, y + 7, "Only after", style=style)

        for i in range(0, len(list_model_1)):
            sheet.write(x + i + 2, y + 2, len(list_model_1[i]))
            sheet.write(x + i + 2, y + 3, len(list_model_2[i]))

        for i in range(0, len(list_model_1)):
            if isinstance(list_model_1[0], list):
                d1 = set(list_model_1[i])
                d2 = set(list_model_2[i])
                set_1 = d1.difference(d2)
                set_2 = d1.intersection(d2)
                set_3 = d2.difference(d1)
                sheet.write(x + i + 2, y + 5, str(len(set_1)))
                sheet.write(x + i + 2, y + 6, str(len(set_2)))
                sheet.write(x + i + 2, y + 7, str(len(set_3)))
            else:
                d1 = list_model_1[i].keys()
                d2 = list_model_2[i].keys()
                set_1 = d1 - d2
                set_2 = d1 & d2
                set_3 = d2 - d1
                sheet.write(x + i + 3, y + 5, str(len(set_1)))
                sheet.write(x + i + 3, y + 6, str(len(set_2)))
                sheet.write(x + i + 3, y + 7, str(len(set_3)))

    def sets_intersection(self, set_list):
        list_non_void_sets = []
        for st in set_list:
            if len(st) != 0:
                list_non_void_sets.append(st)
        if list_non_void_sets == []:
            return set()
        else:
            aux = list_non_void_sets[0]
            for i in range(1, len(list_non_void_sets)):
                aux = aux.intersection(list_non_void_sets[i])
            return aux

    def sets_union(self, set_list):
        if set_list == []:
            return set()
        else:
            aux = set_list[0]
            for i in range(1, len(set_list)):
                aux = aux.union(set_list[i])
            return aux

    def __aux_write_sets(self, sheet, x, y, ls):
        for i in range(len(ls)):
            st = ls.pop(i)
            if len(st) != 0:
                val = st.difference(self.sets_union(ls))
                sheet.write(x, y + i + 2, len(val))
            ls.insert(i, st)
        val = self.sets_intersection(ls)
        sheet.write(x, y + 6, len(val))
        val = self.sets_union(ls)
        sheet.write(x, y + 7, len(val))

    def __aux_spreadsheet_write_four_model_summary(
        self, sheet, style, x, y, title, model_results
    ):
        sheet.write(x, y, title, style=style)
        sheet.write(x + 2, y + 1, "Dead-end metabolites", style=style)
        sheet.write(x + 3, y + 1, "Chokepoint reactions", style=style)
        sheet.write(x + 4, y + 1, "Essential genes", style=style)
        sheet.write(x + 5, y + 1, "Essential genes reactions", style=style)
        sheet.write(x + 6, y + 1, "Essential reactions (objective=0)", style=style)
        sheet.write(
            x + 7,
            y + 1,
            "Essential reactions (objective < 5% max objective)",
            style=style,
        )
        sheet.write(x + 8, y + 1, "Reversible reactions", style=style)
        sheet.write(x + 1, y + 2, "Only: initial model", style=style)
        sheet.write(x + 1, y + 3, "Only: model without D.E.M.", style=style)
        sheet.write(x + 1, y + 4, "Only: model updated with F.V.A.", style=style)
        sheet.write(x + 1, y + 5, "Only: model with F.V.A. without D.E.M.", style=style)
        sheet.write(x + 1, y + 6, "Intersection (only non void sets)", style=style)
        sheet.write(x + 1, y + 7, "Union 4 models", style=style)

        # turn data to sets to operate with
        for model in model_results:
            for i in range(0, len(model)):
                if isinstance(model[i], list):
                    model[i] = set(model[i])
                else:
                    # instance dict
                    model[i] = set(model[i].keys())

        for i in range(0, len(model)):
            set_list = [
                model_results[0][i],
                model_results[1][i],
                model_results[2][i],
                model_results[3][i],
            ]
            self.__aux_write_sets(sheet, x + i + 2, y, set_list)

    #
    def __aux_write_four_model_two_summary(
        self,
        sheet,
        style,
        x,
        y,
        title,
        subtitle1,
        list_set1,
        subtitle2,
        list_set2,
        subtitle3=None,
        list_set3=None,
    ):

        sheet.write(x, y, title, style=style)
        sheet.write(x + 2, y + 1, subtitle1, style=style)
        sheet.write(x + 3, y + 1, subtitle2, style=style)
        if subtitle3 is None:
            sheet.write(x + 4, y + 1, "Intersection", style=style)
            sheet.write(x + 5, y + 1, "Union", style=style)
        else:
            sheet.write(x + 4, y + 1, subtitle3, style=style)
            sheet.write(x + 5, y + 1, "Intersection", style=style)
            sheet.write(x + 6, y + 1, "Union", style=style)
        sheet.write(x + 1, y + 2, "Initial model", style=style)
        sheet.write(x + 1, y + 3, "Model without D.E.M.", style=style)
        sheet.write(x + 1, y + 4, "Model updated with F.V.A.", style=style)
        sheet.write(x + 1, y + 5, "Model with F.V.A. without D.E.M.", style=style)

        i = 0
        for aux_y in range(2, 6):
            if subtitle3 is None:
                if list_set1[i] is not None and list_set2[i] is not None:
                    sheet.write(
                        x + 2, aux_y, len(list_set1[i].difference(list_set2[i]))
                    )
                    sheet.write(
                        x + 3, aux_y, len(list_set2[i].difference(list_set1[i]))
                    )
                    sheet.write(
                        x + 4, aux_y, len(list_set1[i].intersection(list_set2[i]))
                    )
                    sheet.write(x + 5, aux_y, len(list_set1[i].union(list_set2[i])))
                else:
                    for aux_x in range(2, 6):
                        sheet.write(x + aux_x, aux_y, "Nan")
            else:
                if (
                    list_set1[i] is not None
                    and list_set2[i] is not None
                    and list_set3[i] is not None
                ):
                    sheet.write(
                        x + 2,
                        aux_y,
                        len(list_set1[i].difference(list_set2[i].union(list_set3[i]))),
                    )
                    sheet.write(
                        x + 3,
                        aux_y,
                        len(list_set2[i].difference(list_set1[i].union(list_set3[i]))),
                    )
                    sheet.write(
                        x + 4,
                        aux_y,
                        len(list_set3[i].difference(list_set2[i].union(list_set1[i]))),
                    )
                    sheet.write(
                        x + 5,
                        aux_y,
                        len(
                            list_set1[i]
                            .intersection(list_set2[i])
                            .intersection(list_set3[i])
                        ),
                    )
                    sheet.write(
                        x + 6,
                        aux_y,
                        len(list_set1[i].union(list_set2[i]).union(list_set3[i])),
                    )
                else:
                    for aux_x in range(2, 7):
                        sheet.write(x + aux_x, aux_y, "Nan")
            i = i + 1

    def spreadsheet_write_summary(
        self, sheet_name, state_initial, state_dem, state_fva, state_fva_dem
    ):
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.bold = True
        style.font = font

        sheet = self.__spreadsheet.add_sheet(sheet_name)

        list_model_initial_results = self.__aux_spreadsheet_get_data(state_initial)
        list_model_fva_results = self.__aux_spreadsheet_get_data(state_fva)
        list_model_dem_results = self.__aux_spreadsheet_get_data(state_dem)
        list_model_fvadem_results = self.__aux_spreadsheet_get_data(state_fva_dem)
        models = [
            list_model_initial_results,
            list_model_dem_results,
            list_model_fva_results,
            list_model_fvadem_results,
        ]

        # remove essential_reactions list with objective values
        for m in models:
            del m[4]

        list_metabolites = [
            len(state_initial.metabolites()),
            len(state_dem.metabolites()),
            len(state_fva.metabolites()),
            len(state_fva_dem.metabolites()),
        ]
        list_reactions = [
            len(state_initial.reactions()),
            len(state_dem.reactions()),
            len(state_fva.reactions()),
            len(state_fva_dem.reactions()),
        ]

        # 1: list(chokepoints_dict.keys()),
        # 3: genes_reactions_dict,
        # 5: er_g0
        reactions_data = []
        for i in [1, 3, 5]:
            rdl = [
                list_model_initial_results[i],
                list_model_dem_results[i],
                list_model_fva_results[i],
                list_model_fvadem_results[i],
            ]
            for j in range(len(rdl)):
                if isinstance(rdl[j], list):
                    rdl[j] = set(rdl[j])
                else:
                    rdl[j] = set(rdl[j].keys())
            reactions_data.append(rdl)

        x = 0
        y = 0
        sheet.write(x, y, "MODELS DATA", style=style)
        sheet.write(x + 2, y + 1, "Metabolites", style=style)
        sheet.write(x + 3, y + 1, "Reactions", style=style)
        sheet.write(x + 1, y + 2, "Initial model", style=style)
        sheet.write(x + 1, y + 3, "Model without D.E.M.", style=style)
        sheet.write(x + 1, y + 4, "Model updated with F.V.A.", style=style)
        sheet.write(x + 1, y + 5, "Model with F.V.A. without D.E.M.", style=style)
        y = 2
        for m, r in zip(list_metabolites, list_reactions):
            sheet.write(x + 2, y, m)
            sheet.write(x + 3, y, r)
            y = y + 1

        self.__aux_spreadsheet_write_two_model_summary(
            sheet,
            style,
            7,
            0,
            "INITIAL MODEL BEFORE AND AFTER F.V.A.",
            list_model_initial_results,
            list_model_fva_results,
        )
        self.__aux_spreadsheet_write_two_model_summary(
            sheet,
            style,
            18,
            0,
            "INITIAL MODEL BEFORE AND AFTER D.E.M. REMOVAL",
            list_model_initial_results,
            list_model_dem_results,
        )
        self.__aux_spreadsheet_write_two_model_summary(
            sheet,
            style,
            29,
            0,
            "MODEL FIRST UPDATED WITH F.V.A. BEFORE AND AFTER D.E.M. REMOVAL",
            list_model_fva_results,
            list_model_fvadem_results,
        )

        self.__aux_spreadsheet_write_four_model_summary(
            sheet, style, 40, 0, "FOUR MODEL COMPARISON", models
        )

        self.__aux_write_four_model_two_summary(
            sheet,
            style,
            51,
            0,
            "CHOKEPOINT REACTIONS - ESSENTIAL GENES REACTIONS",
            "Only chokepoint reaction",
            reactions_data[0],
            "Only essential genes reactions",
            reactions_data[1],
        )
        self.__aux_write_four_model_two_summary(
            sheet,
            style,
            58,
            0,
            "CHOKEPOINT REACTIONS - ESSENTIAL REACTIONS (objectite value < 5% max objective value)",
            "Only chokepoints",
            reactions_data[0],
            "Only essential reactions",
            reactions_data[2],
        )
        self.__aux_write_four_model_two_summary(
            sheet,
            style,
            66,
            0,
            "ESSENTIAL GENES REACTIONS - ESSENTIAL REACTIONS (objectite value < 5% max objective value)",
            "Only essential genes reactions",
            reactions_data[1],
            "Only essential reactions",
            reactions_data[2],
        )

        self.__aux_write_four_model_two_summary(
            sheet,
            style,
            74,
            0,
            "CHOKEPOINT REACTIONS - ESSENTIAL GENES REACTIONS - ESSENTIAL REACTIONS (objectite value < 5% max objective value)",
            "Only chokepoints reactions",
            reactions_data[0],
            "Only essential genes reactions",
            reactions_data[1],
            "Only essential reactions",
            reactions_data[2],
        )

    def spreadsheet_save_file(self, filename):
        """Saves the xlwt Workbook '__spreadsheet' to a valid file.

        Args:
                filename (): output file.
        """
        if self.__spreadsheet is None:
            self.spreadsheet_init()

        if (
            (filename[-4:] == ".xls")
            or (filename[-4:] == ".ods")
            or (filename[-5:] == ".xlsx")
        ):
            self.__spreadsheet.save(filename)
        else:
            raise Exception("File must be: '.xls', '.ods', '.xlsx'")

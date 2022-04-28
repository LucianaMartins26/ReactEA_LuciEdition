import copy
import random
from typing import List

from jmetal.core.operator import Mutation, Crossover
from rdkit.Chem import MolToSmiles

from reactea.chem.compounds import Compound
from reactea.chem.reaction_rules import ReactionRule
from reactea.chem.standardization import MolecularStandardizer
from reactea.optimization.solution import ChemicalSolution
from reactea.utilities.chem_utils import ChemUtils


class ReactorMutation(Mutation[ChemicalSolution]):
    """
    Class representing a reactor mutation operator.
    A reactor mutation applies alterations in a ChemicalSolution by transforming a reagent (present solution)
    into a product (mutated solution) using reaction rules.
    """

    def __init__(self,
                 probability: float = 0.1,
                 reaction_rules: List[ReactionRule] = None,
                 standardizer: MolecularStandardizer = None,
                 coreactants: List[Compound] = None,
                 configs: dict = None,
                 logger: callable = None):
        """
        Initializes a ReactorMutation operator.

        Parameters
        ----------
        probability: float
            probability of mutation to occur
        reaction_rules: List[ReactionRule]
            pool or reaction rules to use
        standardizer: MolecularStandardizer
            standardizer to standardize new solutions
        coreactants: List[Compound]
            list of coreactants to use (when available)
        configs: dict
            configurations of the experiment
        logger: callable
            function to save all intermediate transformations (accepted and not accepted)
        """
        super(ReactorMutation, self).__init__(probability=probability)
        self.reaction_rules = reaction_rules
        self.standardizer = standardizer
        self.coreactants = coreactants
        self.configs = configs
        self.logger = logger

    def execute(self, solution: ChemicalSolution):
        """
        Executes the mutation by trying to apply a set os reaction rules to the compound.
        Random reaction rules are picked until one can match and produce a product using the present compound.
        If a maximum number of tries is reached without a match the mutation doesn't happen and the compound
        remains the same.

        Parameters
        ----------
        solution: ChemicalSolution
            solution to mutate
        Returns
        -------
        ChemicalSolution
            mutated solution
        """
        if random.random() <= self.probability:
            compound = solution.variables
            rule = self.reaction_rules[random.randint(0, len(self.reaction_rules) - 1)]
            products = []
            i = 0
            while len(products) < 1 and i < self.configs["rules"]["max_rules_by_iter"]:
                if self.coreactants is not None:
                    rule_reactants_ids = rule.coreactants_ids
                    reactants = self.set_coreactants(rule_reactants_ids, compound, self.coreactants)
                    reactants = [reac.mol for reac in reactants]
                else:
                    reactants = compound.mol

                products = ChemUtils.react(reactants, rule.reaction)

                if len(products) > 0:
                    rp = random.randint(0, len(products) - 1)
                    mutant = products[rp]
                    mutant_id = f"{compound.cmp_id}--{rule.rule_id}_"
                    mutant = Compound(MolToSmiles(mutant), mutant_id)
                    mutant = self.standardizer().standardize(mutant)
                    solution.variables = mutant
                    if 'original_compound' not in solution.attributes.keys():
                        solution.attributes['original_compound'] = [compound.smiles]
                        solution.attributes['rule_id'] = [rule.rule_id]
                    else:
                        solution.attributes['original_compound'].append(compound.smiles)
                        solution.attributes['rule_id'].append(rule.rule_id)
                    if self.logger:
                        self.logger(self.configs, solution, mutant.smiles, rule.rule_id)
                i += 1
        return solution

    @staticmethod
    def set_coreactants(reactants: str,
                        compound: Compound,
                        coreactants: List[Compound]):
        """
        Sets coreactant information.
        If coreactant information is available from the reaction rules and from a list of coreactants
        it can be used to match the reaction rules allowing for instance the use of reactions with multiple
        reagents.

        Parameters
        ----------
        reactants: str
            string with the reaction rule coreactant ids
            (Any matches with the compound to mutate, other ids are looked for in the coreactant list)
        compound: Compound
            molecule to mutate
        coreactants: List[Compound]
            pool of available coreactants

        Returns
        -------
        List
            list of reagents (coreactants and molecule to mutate) in the correct order
        """
        reactants_list = []
        if len(reactants.split(';')) > 1:
            for r in reactants.split(';'):
                if r == 'Any':
                    reactants_list.append(compound)
                else:
                    found = False
                    for cor in coreactants:
                        if cor.cmp_id == r:
                            reactants_list.append(cor)
                            found = True
                            break
                    if not found:
                        return None
            return reactants_list
        else:
            return compound

    def get_name(self):
        """
        Get the name of the operator.

        Returns
        -------
        str:
            name of the operator.
        """
        return 'Reactor Mutation'


class ReactorPseudoCrossover(Crossover[ChemicalSolution, ChemicalSolution]):
    """
    Class representing a reactor pseudo crossover operator.
    A reactor pseudo crossover applies a ReactorMutation operator to both parents producing two children
    compounds.
    """

    def __init__(self,
                 probability: float = 1.0,
                 reaction_rules: List[ReactionRule] = None,
                 standardizer: MolecularStandardizer = None,
                 coreactants: List[Compound] = None,
                 configs: dict = None,
                 logger: callable = None):
        """
        Initializes a ReactorPseudoCrossover operator.

        Parameters
        ----------
        probability: float
            probability of mutation to occur
        reaction_rules: List[ReactionRule]
            pool or reaction rules to use
        standardizer: MolecularStandardizer
            standardizer to standardize new solutions
        coreactants: List[Compound]
            list of coreactants to use (when available)
        configs: dict
            configurations of the experiment
        logger: callable
            function to save all intermediate transformations (accepted and not accepted)
        """
        super(ReactorPseudoCrossover, self).__init__(probability=probability)
        self.reaction_rules = reaction_rules
        self.standardizer = standardizer
        self.coreactants = coreactants
        self.configs = configs
        self.logger = logger

    def execute(self, parents: List[ChemicalSolution]):
        """
        Executes the operator by trying to apply a set os reaction rules to both parents to produce
        the offspring.

        Parameters
        ----------
        parents: List[ChemicalSolution]
            parent solutions to mutate
        Returns
        -------
        List[ChemicalSolution]
            mutated offspring solutions
        """
        if len(parents) != 2:
            raise Exception('The number of parents is not two: {}'.format(len(parents)))
        offspring = [copy.deepcopy(parents[0]), copy.deepcopy(parents[1])]

        if random.random() <= self.probability:
            stepbro = ReactorMutation(self.probability,
                                      self.reaction_rules,
                                      self.standardizer,
                                      self.coreactants,
                                      self.configs,
                                      self.logger).execute(offspring[0])

            stepsis = ReactorMutation(self.probability,
                                      self.reaction_rules,
                                      self.standardizer,
                                      self.coreactants,
                                      self.configs,
                                      self.logger).execute(offspring[1])
            offspring[0] = stepbro
            offspring[1] = stepsis
        return offspring

    def get_number_of_parents(self) -> int:
        """
        Number of parent compounds used.

        Returns
        -------
        int
            number of parent compounds
        """
        return 2

    def get_number_of_children(self) -> int:
        """
        Number of children compounds created.

        Returns
        -------
        int
            number of children compounds
        """
        return 2

    def get_name(self):
        """
        Get the name of the operator.

        Returns
        -------
        str:
            name of the operator.
        """
        return 'Reactor One Point Crossover'

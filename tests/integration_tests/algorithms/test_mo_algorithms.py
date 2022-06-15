from unittest import TestCase

from _utils import initialize_population, load_initial_population_smiles, initialize_rules
from base_test_cases import AlgorithmsBaseTestCase
from reactea.case_studies.compound_quality import CompoundQuality
from reactea.optimization.jmetal.ea import ChemicalEA
from reactea.utilities.io import Writers


class TestMOAlgorithms(AlgorithmsBaseTestCase, TestCase):

    def run_algorithm(self, algorithm):
        # set up algorithm
        self.configs['algorithm'] = algorithm

        # define number of molecules to use to only 1 in the case of RandomSearch
        if algorithm == 'RandomSearch':
            self.configs['compounds']['init_pop_size'] = 1
        # initialize population
        init_pop = initialize_population(self.configs)
        self.assertEqual(len(init_pop), self.configs['compounds']['init_pop_size'])

        # initialize population smiles
        init_pop_smiles = load_initial_population_smiles(self.configs)
        self.assertEqual(len(init_pop_smiles), self.configs['compounds']['init_pop_size'])

        # case study
        case_study = CompoundQuality(init_pop_smiles, self.configs)

        # set up objective
        objective = case_study.objective

        # initialize reaction rules
        reaction_rules, coreactants = initialize_rules(self.configs)

        # set up folders
        Writers.set_up_folders(self.output_folder)

        # initialize objectives
        problem = objective()

        # Initialize EA
        ea = ChemicalEA(problem, initial_population=init_pop, reaction_rules=reaction_rules,
                        coreactants=coreactants, max_generations=self.configs['generations'], mp=False,
                        visualizer=False, algorithm=self.configs['algorithm'], configs=self.configs)

        # Run EA
        final_pop = ea.run()
        self.assertIsInstance(final_pop, list)

        # Save population
        Writers.save_final_pop(final_pop, self.configs, case_study.feval_names())
        # Save Transformations
        Writers.save_intermediate_transformations(final_pop, self.configs)

        # save configs
        Writers.save_configs(self.configs)

    def test_algorithms(self):
        self.run_algorithm('NSGAIII')
        self.run_algorithm('NSGAII')
        self.run_algorithm('IBEA')
        self.run_algorithm('RandomSearch')
        self.run_algorithm('SPEA2')
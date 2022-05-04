from typing import List

import cytoolz
from jmetal.algorithm.singleobjective import GeneticAlgorithm

from reactea.optimization.solution import ChemicalSolution


class ReactorGeneticAlgorithm(GeneticAlgorithm):
    """
    Class representing a Reactor Genetic Algorithm.
    """

    def __init__(self, **kwarg):
        """
        Initializes a ReactorGeneticAlgorithm object.
        Parameters
        ----------
        kwarg
            kwargs to use (see GeneticAlgorithm arguments)
        """
        super(ReactorGeneticAlgorithm, self).__init__(**kwarg)

    def replacement(self, population: List[ChemicalSolution], offspring_population: List[ChemicalSolution]):
        """
        Performs replacement of the less fit solutions by better solutions without repetitions (if possible)

        Parameters
        ----------
        population: List[ChemicalSolution]
            previous list of solutions
        offspring_population: List[ChemicalSolution]
            new list of solutions

        Returns
        -------
        List[ChemicalSolution]:
            new set solutions without repetitions (if possible)
        """
        population.extend(offspring_population)

        population.sort(key=lambda s: s.objectives[0])

        unique_population = list(cytoolz.unique(population, key=lambda x: x.variables.smiles))

        if len(unique_population) >= self.population_size:
            unique_population = unique_population[:self.population_size]
        else:
            unique_population.extend(population[:len(offspring_population) - len(unique_population)])

        return unique_population

    def get_result(self):
        """
        Get the EA results.

        Returns
        -------
        List[Solutions]:
            list of the EA solutions.
        """
        return self.solutions

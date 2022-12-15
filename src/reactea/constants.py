from jmetal.algorithm.multiobjective.nsgaiii import UniformReferenceDirectionFactory
from jmetal.operator import BinaryTournamentSelection
from jmetal.util.comparator import DominanceComparator, MultiComparator
from jmetal.util.density_estimator import CrowdingDistance
from jmetal.util.ranking import FastNonDominatedRanking
from jmetal.util.termination_criterion import StoppingByEvaluations

from reactea.optimization.comparators import ParetoDominanceComparator
from reactea.optimization.jmetal.operators import ReactorPseudoCrossover, ReactorMutation
from reactea.standardizers import ChEMBLStandardizer


class ExperimentConstants:
    """
    Class containing a set of the experiment constants
    """
    EXP_NAME = 'Experiment1'
    INITIAL_POPULATION_PATH = '/data/compounds/ecoli_sink.tsv'
    POPULATION_SIZE = 10
    RULES_PATH = '/data/reactionrules/retrorules/retrorules_forward_score.5.tsv'
    MAX_RULES_BY_ITER = 1000
    MULTI_OBJECTIVE = False
    BATCHED = True


class EAConstants:
    """
    Class containing a set of EA parameters constants
    """
    # Maximum number of generations (used as stopping criteria for the EA)
    MAX_GENERATIONS = 100
    # Multiprocessing
    MP = True
    # Default MOEA
    ALGORITHM = 'NSGAIII'
    # Visualizer
    VISUALIZER = False
    # Termination Criterion
    TERMINATION_CRITERION = StoppingByEvaluations
    # Mutation
    MUTATION = ReactorMutation
    # Mutation Probability
    MUTATION_PROBABILITY = 1.0
    # Crossover
    CROSSOVER = ReactorPseudoCrossover
    # Crossover probability
    CROSSOVER_PROBABILITY = 1.0


class SAConstants:
    """
    Class containing a set of Simulated Annealing parameters constants
    """
    TEMPERATURE = 1.0
    MINIMUM_TEMPERATURE = 0.000001
    ALPHA = 0.95


class GAConstants:
    """
    Class containing a set of Genetic Algorithm parameters constants
    """
    SELECTION = BinaryTournamentSelection


class ESConstants:
    """
    Class containing a set of Evolutionary Strategy parameters constants
    """
    ELITIST = False


class LSConstants:
    """
    Class containing a set of Local Search parameters constants
    """
    COMPARATOR = ParetoDominanceComparator()


class NSGAIIIConstants:
    """
    Class containing a set of NSGAIII parameters constants
    """
    REFERENCE_DIRECTIONS = UniformReferenceDirectionFactory
    DOMINANCE_COMPARATOR = DominanceComparator()
    SELECTION = BinaryTournamentSelection(MultiComparator([FastNonDominatedRanking.get_comparator(),
                                                           CrowdingDistance.get_comparator()]))


class NSGAIIConstants:
    """
    Class containing a set of NSGAII parameters constants
    """
    DOMINANCE_COMPARATOR = DominanceComparator()
    SELECTION = BinaryTournamentSelection(MultiComparator([FastNonDominatedRanking.get_comparator(),
                                                           CrowdingDistance.get_comparator()]))


class IBEAConstants:
    """
    Class containing a set of IBEA parameters constants
    """
    KAPPA = 1.0


class SPEA2Constants:
    """
    Class containing a set of SPEA2 parameters constants
    """
    DOMINANCE_COMPARATOR = DominanceComparator()


class ChemConstants:
    """
    Class containing a set of chemical constants
    """
    # Default standardizer
    STANDARDIZER = ChEMBLStandardizer

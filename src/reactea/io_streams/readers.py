import os
import time
from datetime import datetime

import yaml

import pandas as pd

from reactea.chem import Compound, ReactionRule

try:
    from deepsweet_models import DeepSweetRF, DeepSweetDNN, DeepSweetGCN, DeepSweetSVM, DeepSweetBiLSTM
    from ensemble import Ensemble
except ImportError:
    pass

from reactea.constants import ChemConstants


ROOT_DIR = os.path.dirname(__file__)[:-10]


class Loaders:
    """
    Class containing a set of input utilities
    """

    @staticmethod
    def from_root(file_path: str):
        """
        Gets path of file from root.

        Parameters
        ----------
        file_path: str
            file path

        Returns
        -------
        str:
            file path from root
        """
        return f"{ROOT_DIR}/{file_path}"

    @staticmethod
    def get_config_from_yaml(yaml_file: str):
        """
        Reads the configuration file.

        Parameters
        ----------
        yaml_file: str
            path to yaml file

        Returns
        -------
        dict:
            dictionary containing the configurations of the experiment
        """
        with open(yaml_file, 'r') as config_file:
            config_dict = yaml.safe_load(config_file)
        config_dict['time'] = datetime.now().strftime('%m-%d_%H-%M-%S')
        config_dict['start_time'] = time.time()
        return config_dict

    @staticmethod
    def initialize_population(configs: dict):
        """
        Loads the initial population.

        Parameters
        ----------
        configs: dict
            configurations of the experiment (containing path to initial population file)

        Returns
        -------
        List[Compound]:
            list of compounds to use as initial population
        """
        cmp_df = pd.read_csv(configs['init_pop_path'], header=0, sep='\t')
        cmp_df = cmp_df.sample(configs["init_pop_size"])
        return [ChemConstants.STANDARDIZER().standardize(
            Compound(row['smiles'], row["compound_id"])) for _, row in cmp_df.iterrows()], cmp_df.smiles.values

    @staticmethod
    def initialize_rules():
        """
        Loads the reaction rules.

        Parameters
        ----------
        configs: dict
            configurations of the experiment (containing path to reaction rules file)

        Returns
        -------
        List[ReactionRule]:
            list of reaction rules to use
        """
        rules_df = pd.read_csv(Loaders.from_root('/data/reactionrules/reaction_rules_reactea.tsv.bz2'),
                               header=0,
                               sep='\t',
                               compression='bz2')
        return [ReactionRule(row['SMARTS'], row["InternalID"], row['Reactants']) for _, row in rules_df.iterrows()]

    @staticmethod
    def load_deepsweet_ensemble():
        """
        Loads the deepsweet models tu use in the ensemble.

        Returns
        -------
        ensemble:
            deepsweet ensemble to classify compound sweetness
        """
        models_folder_path = Loaders.from_root('/evaluation_models/deepsweet_models/')
        list_of_models = [DeepSweetRF(models_folder_path, "2d", "SelectFromModelFS"),
                          DeepSweetDNN(models_folder_path, "rdk", "all"),
                          # it is necessary to insert the gpu number because it is a torch model and the device needs
                          # to be specified
                          DeepSweetGCN(models_folder_path, "cuda"),
                          DeepSweetSVM(models_folder_path, "ecfp4", "all"),
                          DeepSweetDNN(models_folder_path, "atompair_fp", "SelectFromModelFS"),
                          DeepSweetBiLSTM(models_folder_path)]

        ensemble = Ensemble(list_of_models, models_folder_path)
        return ensemble

    @staticmethod
    def load_results_case(index: int, configs: dict):
        """
        Loads the results file.

        Parameters
        ----------
        index: int
            index of the case to load
        configs: dict
            configurations of the experiment (containing path to results file)

        Returns
        -------
        pandas.DataFrame:
            dataframe containing the results
        """
        return pd.read_csv(configs["transformations_path"], header=0, sep=';').iloc[index]
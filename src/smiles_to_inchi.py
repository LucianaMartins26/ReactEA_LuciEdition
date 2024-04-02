from rdkit import Chem
import pandas as pd

def smiles_to_inchi(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Não foi possível converter o SMILES para uma molécula."
    inchi = Chem.MolToInchi(mol)
    return inchi


if __name__ == "__main__":

    building_blocks = pd.read_csv("ReactEA_LuciEdition/ReactEA_LuciEdition/src/building_blocks_all.tsv", sep='\t')

    building_blocks['InChI'] = building_blocks['smiles'].apply(smiles_to_inchi)

    new_building_blocks = building_blocks[['name', 'InChI']]

    new_building_blocks.to_csv("ReactEA_LuciEdition/ReactEA_LuciEdition/building_blocks_with_inchi.tsv", sep='\t', index=False)

    new_building_blocks.to_csv("ReactEA_LuciEdition/ReactEA_LuciEdition/building_blocks_with_inchi.csv", index=False)
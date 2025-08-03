import os
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw

# Ensure the assets directory exists
IMAGE_DIR = "static/molecule_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def fetch_and_draw_molecule(drug_name):
    """
    Fetches a drug's SMILES from PubChem, draws its 2D structure,
    and saves it as a PNG file.

    Args:
        drug_name (str): The common or IUPAC name of the drug.

    Returns:
        tuple: A tuple containing (smiles_string, image_path) if successful,
               otherwise (None, None).
    """
    print(f"-> Querying PubChem for '{drug_name}'...")
    try:
        # Search for the compound by name
        compounds = pcp.get_compounds(drug_name, 'name')
        if not compounds:
            print(f"<- No compound found for '{drug_name}'.")
            return None, None

        # Take the first result
        compound = compounds[0]
        smiles = compound.canonical_smiles
        print(f"<- Found SMILES: {smiles}")

        # Generate molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            print("<- RDKit could not parse the SMILES string.")
            return smiles, None # Return SMILES even if drawing fails

        # Define image path and save the file
        safe_filename = drug_name.lower().replace(' ', '_') + ".png"
        image_path = os.path.join(IMAGE_DIR, safe_filename)
        Draw.MolToFile(mol, image_path, size=(300, 300))
        print(f"<- Molecule image saved to: {image_path}")

        return smiles, image_path

    except Exception as e:
        print(f"An error occurred during chemistry handling: {e}")
        return None, None
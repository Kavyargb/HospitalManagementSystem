import os
import urllib.request
import urllib.parse
import json

# Ensure the assets directory exists
IMAGE_DIR = "static/molecule_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def fetch_and_draw_molecule(drug_name):
    """
    Fetches a drug's SMILES from PubChem, draws its 2D structure,
    and saves it as a PNG file.
    Tries to use local pubchempy and rdkit if available,
    otherwise falls back to the PubChem PUG REST API.

    Args:
        drug_name (str): The common or IUPAC name of the drug.

    Returns:
        tuple: A tuple containing (smiles_string, image_path) if successful,
               otherwise (None, None).
    """
    safe_name = drug_name.strip()
    if not safe_name:
        return None, None
        
    safe_filename = safe_name.lower().replace(' ', '_') + ".png"
    image_path = os.path.join(IMAGE_DIR, safe_filename)
    
    print(f"-> Querying PubChem for '{safe_name}'...")
    
    # Try using local pubchempy + rdkit first
    try:
        import pubchempy as pcp
        from rdkit import Chem
        from rdkit.Chem import Draw
        
        compounds = pcp.get_compounds(safe_name, 'name')
        if compounds:
            compound = compounds[0]
            smiles = compound.canonical_smiles
            print(f"<- Found SMILES via pubchempy: {smiles}")
            
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                Draw.MolToFile(mol, image_path, size=(300, 300))
                print(f"<- Molecule image saved locally via RDKit to: {image_path}")
                return smiles, image_path
            else:
                print("<- RDKit could not parse the SMILES string.")
                return smiles, None
    except ImportError:
        print("<- local pubchempy/rdkit not found. Using HTTP fallback...")
    except Exception as e:
        print(f"<- Local query failed: {e}. Trying HTTP fallback...")
        
    # HTTP Fallback: fetch SMILES and image using standard urllib
    try:
        # Query SMILES
        url_smiles = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(safe_name)}/property/CanonicalSMILES/JSON"
        req = urllib.request.Request(url_smiles, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            properties = data.get("PropertyTable", {}).get("Properties", [])
            if properties:
                smiles = properties[0].get("CanonicalSMILES")
                print(f"<- Found SMILES via HTTP REST: {smiles}")
            else:
                print(f"<- No SMILES found in properties for '{safe_name}'.")
                return None, None
                
        # Fetch Image
        url_png = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(safe_name)}/PNG"
        req_png = urllib.request.Request(url_png, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_png, timeout=8) as response:
            with open(image_path, 'wb') as f:
                f.write(response.read())
            print(f"<- Downloaded molecule image via REST to: {image_path}")
            return smiles, image_path
            
    except Exception as e:
        print(f"<- HTTP fallback failed for '{safe_name}': {e}")
        return None, None
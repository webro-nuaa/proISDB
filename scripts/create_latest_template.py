import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from app.models.is_element import ISElement

def create_latest_template():
    """
    Generates an Excel template based on the ISElement model definition.
    """
    # These are fields managed by the system or submitter forms, not for bulk import
    excluded_columns = [
        'id', 'submitter_id', 'reviewer_id', 'submission_date', 
        'review_date', 'review_comment', 'status', 'created_at', 'updated_at',
        'submitter_first_name', 'submitter_last_name', 'submitter_institution',
        'submitter_department', 'submitter_postal_address', 'submitter_postal_code',
        'submitter_country', 'submitter_email', 'submitter_telephone'
    ]
    
    # Get column names from the SQLAlchemy model
    # model_columns = [c.name for c in ISElement.__table__.columns if c.name not in excluded_columns]

    # Define the exact column order based on the user's SQL schema.
    ordered_columns = [
        'name', 'family', 'group', 'synomyns', 'iso', 'origin', 'length', 'tam', 
        'le_cleavage_site', 're_cleavage_site', 'orf1', 'orf2', 'accession_number', 
        'mge_type', 'related_element_s', 'isoform', 'host', 'transposition', 
        'is_sequence', 'is_length', 'orf_number', 'orf_1', 'orf_1_length', 
        'orf_1_begin', 'orf_1_end', 'orf_1_strand', 'fusion_orf_1', 'orf_1_function', 
        'orf_1_chemistry', 'orf_1_sequence', 'orf_2', 'orf_2_length', 'orf_2_begin', 
        'orf_2_end', 'orf_2_strand', 'fusion_orf_2', 'orf_2_function', 
        'orf_2_chemistry', 'orf_2_sequence', 'comment', 'references'
    ]
    
    # Create an empty DataFrame with the correct columns in the correct order
    df = pd.DataFrame(columns=ordered_columns)
    
    # Define the output path
    output_dir = "app/static/templates"
    output_filename = "is_element_template_latest.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the empty DataFrame to an Excel file
    df.to_excel(output_path, index=False)
    
    print(f"Successfully created template at: {output_path}")
    print(f"Columns: {ordered_columns}")

if __name__ == '__main__':
    # This requires the Flask app context to access the model
    from run import app
    with app.app_context():
        create_latest_template()

#!/usr/bin/env python3
"""Build BLAST databases from IS elements in the database."""
import os
import sys
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import ISElement

BLAST_DB_DIR = os.path.join(os.path.dirname(__file__), 'blast_db')
NUCL_DB = os.path.join(BLAST_DB_DIR, 'is_elements')
PROT_DB = os.path.join(BLAST_DB_DIR, 'is_elements_prot')


def build_databases():
    app = create_app(os.environ.get('FLASK_ENV', 'production'))

    with app.app_context():
        elements = ISElement.query.filter(
            ISElement.is_sequence.isnot(None),
            ISElement.is_sequence != '',
            ISElement.status == 'approved'
        ).all()

        if not elements:
            print("No IS elements with sequences found. Nothing to build.")
            return

        os.makedirs(BLAST_DB_DIR, exist_ok=True)

        nucl_fasta = os.path.join(BLAST_DB_DIR, 'is_sequences.fasta')
        with open(nucl_fasta, 'w') as f:
            for el in elements:
                if el.is_sequence:
                    f.write(f">{el.name}\n{el.is_sequence}\n")

        print(f"Wrote {len(elements)} nucleotide sequences to {nucl_fasta}")

        subprocess.run(
            ['makeblastdb', '-in', nucl_fasta, '-dbtype', 'nucl',
             '-out', NUCL_DB, '-title', 'IS Elements Nucleotide'],
            check=True, capture_output=True, text=True
        )
        print(f"Nucleotide BLAST database built at {NUCL_DB}")

        orf_fasta = os.path.join(BLAST_DB_DIR, 'orf_sequences.fasta')
        orf_count = 0
        with open(orf_fasta, 'w') as f:
            for el in elements:
                for orf_num, orf_seq in [(1, el.orf_1_sequence), (2, el.orf_2_sequence)]:
                    if orf_seq and orf_seq.strip():
                        f.write(f">{el.name}_ORF{orf_num}\n{orf_seq.strip()}\n")
                        orf_count += 1

        if orf_count > 0:
            print(f"Wrote {orf_count} ORF sequences to {orf_fasta}")
            subprocess.run(
                ['makeblastdb', '-in', orf_fasta, '-dbtype', 'prot',
                 '-out', PROT_DB, '-title', 'IS Elements Protein'],
                check=True, capture_output=True, text=True
            )
            print(f"Protein BLAST database built at {PROT_DB}")
        else:
            print("No ORF sequences found; skipping protein database.")


if __name__ == '__main__':
    build_databases()

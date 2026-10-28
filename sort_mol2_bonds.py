
#!/usr/bin/env python3

"""
sort_mol2_bonds.py

Reorder bonds in a MOL2 file according to these conventions:
1. The lower atom number appears first in each bond.
2. Bonds are sorted by ascending first atom number.
3. Bonds with the same first atom are sorted by ascending second atom.
4. Bond IDs are renumbered sequentially.

Usage:
    python sort_mol2_bonds.py input.mol2 output.mol2
"""

import sys
from pathlib import Path


def sort_mol2_bonds(input_file, output_file):
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Read the complete MOL2 file
    try:
        with input_path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
    except OSError as exc:
        raise SystemExit(f"Cannot open {input_file}: {exc}")

    # Validate the MOL2 header
    if not lines or "TRIPOS" not in lines[0]:
        header = lines[0].rstrip() if lines else "(empty file)"
        raise SystemExit(
            f"Nonstandard header found: {header}\n"
            "Please remove header lines until the TRIPOS "
            "molecule definition."
        )

    # Find the molecule and bond sections
    molecule_index = next(
        (i for i, line in enumerate(lines)
         if line.strip() == "@<TRIPOS>MOLECULE"),
        None
    )

    if molecule_index is None or molecule_index + 2 >= len(lines):
        raise SystemExit("Invalid MOL2 file: molecule section not found.")

    # Parse atom and bond counts
    try:
        counts = lines[molecule_index + 2].split()
        n_atoms = int(counts[0])
        n_bonds = int(counts[1])
    except (IndexError, ValueError):
        raise SystemExit("Cannot read atom and bond counts from MOL2 file.")

    print(f"Found {n_atoms} atoms in the molecule, "
          f"with {n_bonds} bonds.")

    # Find the bond section
    bond_header_index = next(
        (i for i, line in enumerate(lines)
         if line.strip() == "@<TRIPOS>BOND"),
        None
    )

    if bond_header_index is None:
        raise SystemExit("Invalid MOL2 file: BOND section not found.")

    # Identify where the bond section ends
    bond_start = bond_header_index + 1
    bond_end = bond_start

    while bond_end < len(lines):
        if lines[bond_end].lstrip().startswith("@<TRIPOS>"):
            break
        bond_end += 1

    # Parse and normalize bonds
    bonds = []

    for line_number, line in enumerate(
        lines[bond_start:bond_end], start=bond_start + 1
    ):
        if not line.strip():
            continue

        fields = line.split()

        if len(fields) < 4:
            raise SystemExit(
                f"Invalid bond record at line {line_number}: {line.strip()}"
            )

        try:
            bond_id = int(fields[0])
            atom1 = int(fields[1])
            atom2 = int(fields[2])
        except ValueError:
            raise SystemExit(
                f"Invalid bond numbers at line {line_number}: "
                f"{line.strip()}"
            )

        # Ensure the lower atom number comes first
        atom1, atom2 = sorted((atom1, atom2))

        # Preserve the bond type and any additional fields
        bond_type = fields[3]
        extra_fields = fields[4:]

        bonds.append((atom1, atom2, bond_type, extra_fields))

    if len(bonds) != n_bonds:
        raise SystemExit(
            f"Bond count mismatch: expected {n_bonds}, "
            f"but found {len(bonds)} bond records."
        )

    # Sort by first atom, then second atom
    bonds.sort(key=lambda bond: (bond[0], bond[1]))

    # Format the sorted bond records
    sorted_bond_lines = []

    for new_id, (atom1, atom2, bond_type, extra) in enumerate(
        bonds, start=1
    ):
        record = (
            f"{new_id:6d}{atom1:6d}{atom2:6d}{bond_type:>5s}"
        )

        if extra:
            record += " " + " ".join(extra)

        sorted_bond_lines.append(record + "\n")

    # Reconstruct the file without modifying other sections
    output_lines = (
        lines[:bond_start]
        + sorted_bond_lines
        + lines[bond_end:]
    )

    try:
        with output_path.open("w", encoding="utf-8", newline="") as file:
            file.writelines(output_lines)
    except OSError as exc:
        raise SystemExit(f"Cannot write {output_file}: {exc}")

    print(f"Successfully sorted {len(bonds)} bonds.")
    print(f"Output written to: {output_path}")


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python sort_mol2_bonds.py "
            "input.mol2 output.mol2"
        )
        sys.exit(1)

    sort_mol2_bonds(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()

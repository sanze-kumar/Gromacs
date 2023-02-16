#!/bin/bash

# Set up simulation parameters
PROTEIN="protein.pdb"
LIGAND="ligand.pdb"
FORCEFIELD="amber99sb-ildn"
SOLVENT="tip3p"
BOXSIZE=1.0
IONS="NA+ CL-"
MDRUNOPTIONS="-v -nb auto gpu"

# Create GROMACS topology files
gmx pdb2gmx -f $PROTEIN -ignh -ff $FORCEFIELD -water $SOLVENT -o processed.gro -p system.top
gmx editconf -f processed.gro -d $BOXSIZE -bt dodecahedron -o boxed.gro

# Add ligand to system
gmx editconf -f $LIGAND -o ligand.gro
gmx insert-molecules -f boxed.gro -ci ligand.gro -nmol 1 -o complex.gro

# Solvate system
gmx solvate -cp complex.gro -cs $SOLVENT -o solvated.gro -p system.top

# Neutralize system
gmx grompp -f ions.mdp -c solvated.gro -p system.top -o ions.tpr
gmx genion -s ions.tpr -p system.top -pname $IONS -nname $IONS -neutral -o neutral.gro

# Energy minimize system
gmx grompp -f minim.mdp -c neutral.gro -p system.top -o em.tpr
gmx mdrun -deffnm em $MDRUNOPTIONS

# Equilibrate system
gmx grompp -f nvt.mdp -c em.gro -p system.top -o nvt.tpr
gmx mdrun -deffnm nvt $MDRUNOPTIONS
gmx grompp -f npt.mdp -c nvt.gro -p system.top -o npt.tpr
gmx mdrun -deffnm npt $MDRUNOPTIONS

# Production run
gmx grompp -f md.mdp -c npt.gro -p system.top -o md_0_1.tpr
gmx mdrun -deffnm md_0_1 $MDRUNOPTIONS

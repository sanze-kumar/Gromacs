# Author : Sanjay Kumar, PhD
# Year : 2023
# Script version 0.1
# The City College of New York, NY-10031
# Email: sanze_kumar@outlook.com

echo "This bash script compatible for GROMACS v2022"
echo ""
echo "Bash script for the simulation of Protein in water only"
echo ""
echo "Step 1 : Protein preparation"
gmx pdb2gmx -f protein.pdb -o processed.gro -water spc -ignh <<EOF 
8
1
EOF
echo ""
echo "Step 1 Completed"
echo ""
echo "Step 2 : Simulation box"
gmx editconf -f processed.gro -o newbox.gro -c -d 1.0 -bt cubic
echo ""
echo "Step 2 Completed"
echo ""
echo "Step 3 : Solvation"
gmx solvate -cp newbox.gro -cs spc216.gro -o solv.gro -p topol.top
echo ""
echo "Step 3 Completed"
echo ""
echo "Step 4 : Ions"
gmx grompp -f ions.mdp -c solv.gro -p topol.top -o ions.tpr
gmx genion -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral <<EOF 
13
EOF
echo ""
echo "Step 4 Completed"
echo ""
echo "Step 5 : Energy minimization"
gmx grompp -f minim.mdp -c solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em
echo ""
echo "Step 5 Completed"
echo ""
echo "Step 6 : NVT Equilibration"
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -v -deffnm nvt
echo "Step 6 Completed"
echo ""
echo "Step 7 : NPT Equilibration"
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -v -deffnm npt
echo "Step 7 Completed"
echo ""
echo "Step 8 : Final MD Simulation"
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md50.tpr
gmx mdrun -v -deffnm md50 -nb gpu

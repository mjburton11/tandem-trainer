AIRFOIL=naca652
Re="1000 1500 2000 2500 3000 3500 4000"
for r in $Re
do
    ./genpolar.sh $AIRFOIL $r
done

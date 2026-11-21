# L'année d'équilibre de la page Coût : celle d'où le solde ne redevient plus négatif

*Le 21 novembre 2026, une session corrige l'année de retour à l'équilibre
que la page Coût donnait pour la proposition. Écrit sous Opus 5.5, relu sous
Fable 5.2.*

**Le défaut.** `Solde.premiere_annee_equilibree` rendait la première année
projetée au solde positif ou nul. Depuis la correction du 20 novembre sur la
complémentaire des libéraux, le scénario libéral est à +0,05 % du PIB en
2029, retombe en déficit de 2030 à 2051 (jusqu'à −0,21 % en 2041), et n'est
en excédent qu'à partir de 2052 (+0,02 %). La page écrivait « les comptes se
rééquilibrent en 2029 ».

**La correction.** L'année est désormais la première d'où le solde reste
positif ou nul jusqu'en 2070, et aucune quand il est négatif à l'horizon.
Une fonction commune, `cout.annee_d_equilibre`, porte la règle :
`Solde.premiere_annee_equilibree` et `scripts/postes_ecartes.py`, qui
refaisait le calcul à part, l'appellent tous deux. Le portage lit l'année
figée dans le paquet. La phrase dit « se rééquilibrent durablement en
2052 », puisque la courbe montre toujours l'excédent isolé de 2029.

**Ce qui bouge.** La page Coût, sa phrase et la colonne d'équilibre de son
tableau des scénarios : 2029 devient 2052. `docs/chiffrage_plf.md`, de même.
La variante dérivée (2055), les scénarios 4 et 5 (2026) et la colonne
prospective du chiffrage (2066) ne bougent pas, ni aucun solde ni aucune
pension.

**Laissé ouvert.** Un excédent à la seule année 2070 ferait écrire
« durablement en 2070 ». Aucun scénario n'y est ; le traiter demanderait une
durée minimale d'excédent, qui est une convention à choisir.

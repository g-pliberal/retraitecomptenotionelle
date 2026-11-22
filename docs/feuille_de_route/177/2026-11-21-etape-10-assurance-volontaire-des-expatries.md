# Étape 10 : l'assurance volontaire vieillesse des salariés expatriés

**Le 21 novembre 2026, ce qui est fait.** Le salarié parti hors de France qui
cotise à l'assurance volontaire (L. 742-1, 3e alinéa, 1°) le dit sur sa
période à l'étranger, par sa catégorie (`etranger<n>_avv`, 1 à 3) ; le régime
général le porte au compte comme une période d'assurance obligatoire. Tests :
`tests/js/assurance-volontaire.test.js` (quatorze essais, valeurs du barème
de la Cnav) et `tests/test_assurance_volontaire_formulaire.py`.

1. *Le droit.* R. 742-4 : quatre catégories, en part du plafond — 100 %,
   75 %, 50 %, et 25 % pour les moins de vingt-deux ans, jusqu'à la fin du
   trimestre civil de leur anniversaire (exposé « Assurance volontaire » de la
   Cnav, arrêté du 9 décembre 1968). L'assuré est « censé avoir perçu les
   salaires correspondant à ses cotisations », et « les trimestres
   d'assurance se décomptent comme les périodes d'assurance obligatoire »
   (R. 742-8, R. 351-9). Le barème « Montants des cotisations par trimestre »
   (circulaires 2014/24 à 2026/23) donne le salaire forfaitaire de chaque
   classe : 4 755 € par trimestre en 3e classe en 2015, 5 796 € en 2024.
2. *La saisie* (`saisie.js`). Le champ se lit, se réécrit dans l'adresse, et
   se refuse : une 4e catégorie (qui s'applique d'elle-même), une activité
   non salariée (L. 742-6, non modélisée), une période sans trimestre civil
   entier, avant juillet 1966 (loi n° 65-555, décret n° 66-303), avec un
   relevé (qui porte déjà les salaires, sous le statut), avant le début de la
   carrière.
3. *La carrière* (`chronologie.js`, `carriere.js`). Un fait d'emploi cumulé
   par période, au statut `assure_volontaire_expatrie` (`affiliations.yaml`,
   hors du menu des métiers) ; son revenu est le salaire forfaitaire,
   trimestre par trimestre, la 4e catégorie jusqu'au trimestre des vingt-deux
   ans. La ligne est cotisée : SAM, trimestres, durée cotisée ; aucune
   complémentaire. Le revenu forfaitaire n'est pas un revenu d'activité
   (`AnneeCarriere.remuneree`) : ni net, ni impôt, ni dernier salaire.
4. *Le site.* Une liste « Assurance volontaire » sur chaque période hors de
   France, avec sa bulle d'explication ; deux témoins
   (`assurance_volontaire_3e_categorie`, `assurance_volontaire_avant_22_ans`).

**Exemple.** Née le 15 mars 1962, salariée depuis 1984 au salaire moyen,
hors de France sans accord de 2015 à 2024, partie le 1er avril 2027 : sans
assurance volontaire, 133 trimestres, taux 45 %, régime général 14 023 € par
an ; en 3e catégorie, 173 trimestres, taux 52,5 %, 20 789 € ; l'Arrco passe de
4 809 € à 5 227 €, sa minoration suivant le taux du régime général.

**Reste.** La CFE publie 2 148 € de cotisation de 1re catégorie en 2026, la
Cnav 2 158 € : sans effet sur le salaire porté. Les catégories d'avant 1969
et la 4e d'avant 2013 sont supposées celles d'aujourd'hui. La superposition
à une période que la coordination fait compter, la complémentaire
individuelle, les non-salariés et le rachat de L. 742-2 ne sont pas portés.

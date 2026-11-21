# Action 194 : la surcote des régimes spéciaux, comptée pour la durée des services

Erreur du moteur relevée par la note des pistes du balayage
(`2026-11-21-pistes-du-balayage.md`), corrigée sans accord préalable (règle 1
du projet, du 20 novembre 2026).

## Le texte, relu dans l'index LEGI du 16 novembre 2026

Les six articles de surcote écrivent la même chose : SNCF (décret
n° 2008-639, article 13, LEGIARTI000054622824), RATP (n° 2008-637, article
24, LEGIARTI000047914227), IEG (annexe 3 du statut, article 10,
LEGIARTI000052046924), CRPCEN (n° 90-1215, article 85-1,
LEGIARTI000047909834), Comédie-Française (n° 68-960, article 12,
LEGIARTI000029134341), Opéra (n° 68-382, article 14, LEGIARTI000029135161).
Les trimestres de la surcote sont ceux « d'assurance au sens du III
ci-après, cotisés et effectués après le 1er juillet 2008, au-delà de
l'âge », et « sont pris en compte pour ce calcul les trimestres entiers
cotisés ». Le III (le IV à la Comédie-Française et à l'Opéra) : « La durée
d'assurance totalise la durée des services » (des « périodes » à la RATP et
à la CRPCEN). Une nuance : la RATP compte des « trimestres de services
effectués après le 1er juillet 2008 », les cinq autres des « trimestres
d'assurance au sens du III […] cotisés et effectués » ; pour un agent sans
autre régime, les deux reviennent au même. Partout, la durée des services
d'après l'âge, au mois, puis les trimestres entiers du total.

## Le défaut et la correction

`trimestresDeSurcoteRegimesSpeciaux` et `coefficientSurcoteRegimesSpeciaux`
(`moteur/js/droit/liquider.js`) comptaient, par `trimestresDeLaLigneEntre`,
les trimestres de chaque année civile étalés sur ses mois : l'année du départ
ne gardait que ses trimestres civils entiers (trois pour dix ou onze mois).
Ils comptent désormais par `trimestresCotisesAuMois`, la fonction que la
surcote de la Banque de France employait déjà : un mois de services vaut un
tiers de trimestre, l'année du départ comprise, et seul le total s'arrondit.

Le test : `tests/test_surcote_regimes_speciaux.py`, sept cas nés en 1954,
partis à 63 ans et 9 mois, quinze trimestres à 1,25 % (taux 89,0625 %) ; le
moteur en comptait quatorze pour les nés en février et en mars. Agent des IEG
né le 1er février 1954 : 37 225,82 € à 37 621,84 € par an (+1,06 %).

## Ce qui bouge

Huit témoins sur 937 au scénario 1, tous en hausse, de +0,33 %
(`enfants_sncf_partie_avant_2008`) à +1,19 % (`statut_agent_sncf_1965`,
`statut_agent_ratp_1965`), +1,05 % en médiane ; cinq aux scénarios 3 et 5 ;
aucune page.

## Ce qui reste, de la même classe

- La décote des mêmes régimes (`borneDeLaDuree`) retranche les trimestres
  « cotisés et effectués au-delà de l'âge auquel le droit à pension est
  ouvert », comptés de même par année civile ; mais le texte y arrondit « à
  l'entier supérieur » le nombre de trimestres correspondant : la correction
  demande sa propre lecture.
- La durée d'assurance totale de ces régimes compte, elle aussi, les
  trimestres civils de l'année d'entrée et de l'année du départ, et non la
  durée des services : un agent de l'Opéra né en avril 1954 compte 183
  trimestres, né en février 182, pour la même durée de 45 ans et 9 mois.
  Elle touche la proratisation et le plafond de la surcote : chantier à part.
  C'est elle qui borne encore la surcote de l'Opéra, dont l'âge de la surcote
  est bas : la correction ne le répare pas, il garde 33, 32 ou 32 trimestres
  de surcote selon le mois de naissance (nés en 1954, partis à 63 ans et
  9 mois), et le test n'a pas de cas de l'Opéra.
- Les six textes réduisent les trimestres de surcote d'un agent à temps
  partiel (« Lorsque l'activité est exercée à temps partiel, le nombre de
  trimestres ainsi déterminé… ») ; le moteur ne le faisait pas avant cette
  correction et ne le fait pas après.

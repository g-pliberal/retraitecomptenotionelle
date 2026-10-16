# Étape 8, huitième partie : DM1 au-delà du chef, et les seuls points de RCO de chef dans le complément différentiel

**Le 16 octobre 2026, la demande.** Les points 2 et 3 de « Ce qui reste » de la
note du 14 octobre sur le statut : les périodes de collaborateur régularisées
de 1999 à 2008 (D. 732-110, II, 3°) et celles de qui peut prétendre à une
réversion (2°) reçoivent PMR1, quand le modèle leur servait PMR2 ; la formule
différentielle de D. 732-166-4 ne retranche que les points de RCO de chef,
quand le modèle retranchait tous ceux de la RCO. Session du modèle, une de
treize.

**Ce que dit le droit** (journal de veille du 16 octobre, index LEGI).

- *DM1* compte « les périodes définies aux 1° et 2°, ou au 3°, du II de
  l'article D. 732-110 », et « les périodes mentionnées aux 1° et 3° [...] sont
  retenues en priorité » (D. 732-111). Le 3° : les périodes de collaborateur
  « cotisées » de 1999 à 2008 par qui justifie « de la régularité de [sa]
  situation » au sens du deuxième alinéa du II de L. 732-54-2 d'avant 2009 —
  qui était conjoint au 31 décembre 1998 n'est collaborateur que s'il a opté
  avant 2001 et gardé le statut « de manière durable » ; depuis 2011, aussi les
  périodes de conjoint d'avant 1999 rachetées avant 2009. Le 2° : toutes les
  périodes de qui peut prétendre à une réversion du régime (L. 732-41 à
  L. 732-46).
- *N*, dans la formule de novembre 2021 et de 2026, est le nombre de points
  acquis « par cotisation ou à titre gratuit [...] au titre des périodes
  d'assurance accomplies par l'assuré en qualité de chef d'exploitation »
  (D. 732-166-4).

**Ce qui est fait**, dans les deux moteurs.

- *La PMR* : `EligibleAgricole.collaborateur_regularise` (champ de plus au
  schéma de l'étape « liquider »), les trimestres de collaborateur principal de
  1999 à 2008, entrent dans DM1 avec ceux du chef, en priorité. Tous sont
  présumés régularisés ; l'aide familial, que la saisie ne distingue pas du
  collaborateur, en reçoit PMR1 à tort. Les périodes de conjoint d'avant 1999
  sont présumées non rachetées.
- *Le 2°* ne trouve personne : la chronologie ne porte que le décès de
  l'assuré, non celui de son conjoint, et la saisie ne le demande pas. Déclaré
  dans la fiche ; le servir demande un champ de saisie, que cette session ne
  pouvait toucher.
- *Le complément* : `points_rco_de_chef` (`pointsRcoDeChef`) lit N des crédits
  de points de la RCO année par année, ne gardant que ceux des années de chef
  (principal, et secondaire depuis 2026), plus les points gratuits ; le
  relèvement de septembre 2023 le relit (`ChefDExploitation.points`). Une
  carrière de chef seul garde exactement son compte d'avant.
- *Les tests* (`tests/test_minima_agricoles.py`, deux de plus, un cas de plus
  dans la comparaison des deux moteurs). Le cliquet des textes descend d'une
  rédaction (9 750).

**Les mesures.** La conjointe collaboratrice de 1972 à 2016 : PMR1 sur ses
quarante trimestres de 1999 à 2008, 410 € par an de plus. Vingt-neuf ans de
chef puis quinze de collaborateur, parti en 2026 : 2 250 points retranchés au
lieu de 3 434, 1 184 points de complément de plus, 468 € par an.

**Ce qui reste**, de cette partie :

1. Le 2° de D. 732-110, II : le décès du conjoint de l'assuré, et son régime,
   à saisir (session du site), puis PMR1 sur toutes les périodes de qui peut
   prétendre à une réversion du régime.
2. Distinguer l'aide familial du collaborateur, et le collaborateur qui n'a
   pas régularisé (le décret qui fixe le « caractère durable » est à lire).
3. Les restes de l'étape, inchangés : les points des conjoints et aides
   familiaux des plans ; la PMR unique de 2022 aux pensions prises depuis
   2009 ; avant 1997, la révision des plans ; un montant de la MSA pour 2015 à
   2017 et 2019.

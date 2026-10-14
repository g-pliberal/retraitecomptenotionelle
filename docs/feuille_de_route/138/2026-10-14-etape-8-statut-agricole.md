# Étape 8, quatrième partie : le statut du non-salarié agricole — conjoint collaborateur, aide familial, chef à titre secondaire

**Le 14 octobre 2026, la demande.** Le quatrième reste de l'étape, au rang
moyen du classement par poids (note du 9 octobre) : « le modèle leur sert la
PMR et le complément du chef, quand la loi réduisait la PMR de 2009 à 2021 et
réserve le complément au chef ; un champ de saisie ». Session du site, seule
sur les pages et la saisie ce jour.

**Ce que dit le droit** (journal de veille du 14 octobre, index LEGI).

- *La PMR de 2009 à 2021* : PMR = PMR1 × DM1 / DR + PMR2 × DM2 / DR
  (D. 732-111). DM1, les périodes de chef, retenues en priorité ; DM2, celles du
  collaborateur, du conjoint participant aux travaux et de l'aide familial
  (D. 732-110, II, 4°). La condition de dix-sept ans et demi de chef, qui
  renvoyait au 4° le chef plus bref, n'est que dans la rédaction de 2009, en
  vigueur jusqu'au 1er janvier 2011 : le décret n° 2010-1759 l'a ôtée. Le dépôt
  l'appliquait jusqu'en 2021, et servait PMR2 au chef de moins de dix-sept ans
  et demi de 2011 à 2021 : une erreur trouvée en chemin, corrigée.
- *Le titre secondaire* : la PMR (D. 732-110, I) et le complément (L. 732-63 ;
  D. 732-166-1) ne comptent que les périodes « à titre exclusif ou principal » ;
  depuis le 1er janvier 2026, aussi celles à titre secondaire.
- *Le complément différentiel* s'ouvre, se proratise et compte ses points sur
  la seule durée de chef (D. 732-166-1, II ; D. 732-166-3) ; il se borne à la
  cible au prorata de la durée agricole (D. 732-166-5).
- *Les points gratuits de la RCO* : cent points par année de chef à titre
  exclusif ou principal d'avant 2003, à qui l'a été dix-sept ans et demi
  (L. 732-56 ; D. 732-151, D. 732-154).
- *La RCO* s'ouvre aux collaborateurs et aux aides familiaux le 1er janvier
  2011 (L. 732-56, IV, rédaction du 11 novembre 2010).

**Ce qui est fait.**

- *Le statut* : une affiliation de plus, `collaborateur_agricole`, « Conjoint
  collaborateur ou aide familial d'exploitation agricole » — un seul statut,
  que la règle traite de même —, au régime des non-salariés agricoles depuis
  1952, à la RCO depuis 2011. La saisie le propose dans le groupe
  « Agriculture » du menu des statuts, qui se lit d'`affiliations.yaml` : aucun
  champ de plus. Le chef à titre secondaire se saisit comme une activité qui
  s'ajoute à une autre (« s'ajoute à celle en cours ») : la ligne du chef n'est
  alors pas la première de son année.
- *La qualité de chaque année* : `Carriere.qualite_agricole` et son jumeau
  `qualiteAgricole` disent « chef », « chef_secondaire » ou « collaborateur ».
- *Les deux moteurs* : `EligibleAgricole` porte la durée agricole sans les
  années de chef secondaire d'avant 2026, et la durée de chef, `chef` (champ
  de plus au schéma de l'étape « liquider ») ; la PMR sert PMR1 et PMR2 au
  prorata, la cascade dit les deux termes (« PMR 7 671,96 € × 0/160 +
  6 096,36 € × 160/160 ») ; le complément s'ouvre et se proratise sur la durée
  de chef, se borne sur la durée agricole ; les points gratuits ne comptent que
  les années de chef principal. Les fiches `pension_majoree_reference` (le
  seuil ôté des versions de 2011 et de 2014, deux citations lues) et
  `complement_differentiel_rco` le disent.
- *Les tests* (`tests/test_minima_agricoles.py`, quatre de plus, et quatre
  carrières de plus dans la comparaison des deux moteurs) : la conjointe
  collaboratrice de 2016, à PMR2, sans points gratuits ni complément ; la
  carrière mêlée de 2019, PMR1 et PMR2 au prorata ; le chef de seize ans de
  2016, à PMR1 ; le salarié chef à titre secondaire, parti en 2024 (rien) et
  en 2030 (ses années depuis 2026).

**Ce qui reste**, de cette partie, aux sessions du modèle :

1. *L'assiette du collaborateur et de l'aide familial* : leurs cotisations, et
   donc leurs points de retraite proportionnelle et de RCO, se prennent d'une
   assiette forfaitaire que la loi fixe ; le modèle les prend du revenu saisi.
2. *DM1 au-delà du chef* : les périodes de collaborateur régularisées de 1999 à
   2008 (D. 732-110, II, 3°) et toutes celles de qui peut prétendre à une
   réversion (2°) reçoivent PMR1 ; le modèle leur sert PMR2.
3. *Les points de RCO de chef* : la formule différentielle de D. 732-166-4 ne
   retranche que les points acquis comme chef ; le modèle retranche tous ceux
   de la RCO, ceux du collaborateur depuis 2011 compris.
4. *La pension de base du chef à titre secondaire*, qui ne cotisait pas à la
   retraite forfaitaire avant 2026 : le modèle la lui calcule comme au chef
   principal (4 900 € par an au salarié de 1958 chef à côté depuis ses trente
   ans) ; seuls les deux minima et les points gratuits l'écartent. À lire avant
   d'y toucher.

**Laissé à la session du site suivante** : la saisie des PCV (138.18) — la
profession sous le statut de la CARCDSF (dentiste ou sage-femme) et sous celui
du pharmacien (biologiste ou non), le secteur du médecin —, que cette session
n'a pas eu le temps d'ouvrir ; la demande est au bloc de l'étape 18.

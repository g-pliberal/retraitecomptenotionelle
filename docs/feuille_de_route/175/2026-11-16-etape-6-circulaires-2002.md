# Étape 6, circulaires de 2002 : les 102 références sans thème de la neuvième période, relues par l'API

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2002 : 102, comme la consigne les comptait.
- *La lecture* : les 102, relues par l'API le 16 novembre 2026 à 10 h 50 UTC
  (`/reference/referencesByFileLeafRef/`, par `_reference` de `cnav_legislation.py`),
  toutes servies : 84 circulaires, 9 lettres, 6 diffusions d'instructions ministérielles,
  2 lettres circulaires, une note d'information ; 79 de la Cnav, 19 ministérielles, une
  de l'Acoss, trois sans origine ou d'une autre ; 60 en page, 558 096 octets de texte ;
  42 en PDF, pièces de circulaires, lues au site (`/Pdf/`) par leur texte (`pdftotext`,
  211 034 octets), dont six scans sans texte lus en image par la session (`pdftoppm`,
  60 points par pouce) : les annexes 1, 2 et 4 de la n° 2002/27 (intégration des
  magistrats), la demande d'attestation de l'allocation équivalent retraite de la
  n° 2002/40, l'avis de décision de l'allocation des travailleurs de l'amiante de la
  n° 2002/56, et les six pages des barèmes de la lettre circulaire Acoss n° 2002/16.
- *Le rapprochement* : la base est la seule source des 102 ; l'index de la DILA n'a pas
  servi. Une diffusion se range comme le texte qu'elle transmet, une pièce comme sa
  circulaire, sauf ce qu'elle dit d'autre ; 26 pièces ont leur circulaire hors de la
  période (rangée avec un thème, ou à une autre date), et prennent son sort.
- *Qui a lu* : les 102 en entier, par cinq agents de la session sur Opus, un lot chacun
  (de 51 000 à 202 000 octets), lancés ensemble, qui ont proposé le sort avec une citation
  par texte, sur une consigne commune (les raisons du registre et les renvois déjà
  employés, avec leur effectif, les rangements des périodes d'avant pour précédents). Les
  97 citations des textes servis ont été retrouvées mot pour mot, par script, dans le
  texte servi (blancs normalisés), chaque raison hors modèle dans la liste du registre,
  chaque renvoi dans le dépôt ; celles des cinq scans rangés sont le titre que la session
  y a lu. La session a lu elle-même les scans et les passages qui décident de l'écart neuf
  et des écarts de la Nouvelle-Calédonie, et retenu les sorts proposés.
- *Les sorts* : 102 références rangées, 47 `limite`, 55 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 102 lignes, les colonnes
  `sort` et `renvoi` seules, le reste de chaque ligne gardé, vérifié par script). Aucune
  raison neuve.

**Par ce qu'elles disent.**

- *À `cotisation_maladie_des_non_residents`* (14 en premier renvoi) : les onze formulaires
  de la CSG et de la cotisation maladie des retraités qui quittent la France, pièces de la
  n° 2002/4 (30648 à 30665), comme `CR_CN_200063` et `LE_MIN_31102001` ; la cotisation
  maladie des retraites supplémentaires des résidents de l'Union (n° 2002/323, et sa
  diffusion `D_IM_20024`), comme la n° 349/2001.
- *À `docs/limites/3-systeme-actuel.md`* (10 en premier renvoi) : l'intégration des
  magistrats et ses quatre annexes (n° 2002/27), l'allocation équivalent retraite et ses
  attestations (n° 2002/40, avec `fin_indemnisation_chomage`), les plafonds des veuves de
  guerre (n° 2002/21).
- *Ailleurs* : la réversion (n° 2002/44, et la n° 2002/57 avec l'Union) ; le minimum
  vieillesse (n° 2002/46 ; le contrôle allégé des ressources, n° 2002/65 et ses exemples,
  sur le précédent de la n° 2001/56) ; l'inaptitude et la pension d'invalidité substituée
  (n° 2002/45) ; la majoration pour conjoint à charge (n° 2002/66 et ses formulaires) ;
  l'allocation des travailleurs de l'amiante (n° 2002/369, n° 2002/56 et son avis) ; la
  validation des trimestres en 2003 (n° 2002/62) ; la revalorisation de 2003
  (n° 2002/63) ; les rentes ouvrières et paysannes (n° 2002/70) ; l'arrangement n° 9
  avec l'Algérie (n° 2002/321) ; la coordination avec la Nouvelle-Calédonie
  (n° 2002/620) ; les accords entre la Suisse et l'Union, en vigueur le 1er juin 2002
  (`NI_MIN_2642002_30042002`) ; le service national (lettre ministérielle du 3 mai
  2002) ; la majoration de durée pour enfant (lettre de la Cnav du 4 juin 2002) ; le
  chômage non indemnisé (lettre ministérielle du 9 avril 2002) ; les médecins
  hospitaliers de Mayotte (`LE_MIN_17072002`).
- *Hors modèle* : l'action sociale (11, dont l'allocation personnalisée d'autonomie,
  n° 2002/6, et les barèmes de la n° 2002/67) ; la demande et son instruction (5) ;
  l'application administrative d'une convention bilatérale (5, dont la Pologne,
  n° 2002/3 et ses pièces) ; le régime local d'Alsace-Moselle (six pièces de la
  n° 2002/71) ; les monnaies (4) ; les règles générales de l'administration (4, dont la loi
  n° 2000-321, n° 2002/56 ministérielle) ; l'assurance veuvage (n° 2002/68 et 2002/69 et
  leurs formulaires) ; l'instruction coordonnée entre États (3) ; et treize autres, une ou
  deux par raison.

**Les montants relus, conformes.** Le plafond de 2002, 2 352 € par mois et 28 224 € par
an (`macro/plafond_securite_sociale.csv`) ; l'assiette trimestrielle de l'AVPF de 2002,
3 382 €, « 507 fois le montant du SMIC » (scan de la lettre circulaire n° 2002/16), soit
trois fois les 1 127,23 € de `legislation/assiette_avpf.csv` (ligne 68) ; de la
n° 2002/63, la revalorisation de 1,015 (`legislation/revalorisation_pensions.csv`), le
minimum contributif de 6 402,23 € (`legislation/minimum_contributif.csv`), le seuil du
versement forfaitaire unique de 132,44 €, la majoration pour enfant de la réversion de
979,80 € par an, les coefficients des salaires de 1947 à 2002, et le salaire qui valide
un trimestre en 2003, 1 366 €, sur le SMIC de 6,83 €.

**Un écart neuf, chiffré** (candidat), pour les sessions du modèle, sans y toucher.
*Le plafond de ressources de la réversion, au SMIC de la date de la demande.* Circulaire
Cnav n° 2002/44 du 25 juillet 2002 (`CR_CN_200244_25072002`) : les ressources du conjoint
ne doivent pas dépasser « le montant annuel du SMIC calculé sur la base de 2080 heures, en
vigueur à la date de la demande de pension de réversion » ; « Le montant horaire du SMIC
ayant été porté à 6,83 euros à compter du 1er juillet 2002 [...] le plafond annuel de
ressources à retenir à partir de cette date est le suivant : 6,83 euros x 2080 = 14 206,40
euros ». Le moteur prend `2 080 × smic_horaire(an)`
(`src/retraite_notionnelle/droit/reversion.py`, lignes 998 et 999), où la série ne tient
que le SMIC du 1er janvier (`macro/smic_horaire.csv`, 6,67 € en 2002 ; la docstring de
`smic_horaire` dans `donnees/macro.py` le dit) ; la fiche `reversion` (lignes 341 à 350)
ne dit pas lequel. Pour une demande du second semestre 2002, le plafond du moteur est de
13 873,60 €, celui de la caisse de 14 206,40 € : 332,80 € de moins. Cas, à la main :
conjoint survivant aux ressources de 14 000 € par an, demande au 1er septembre 2002 ;
selon la circulaire, réversion servie, réduite à ce qui dépasse le plafond, 206,40 € par
an ; selon le moteur, plafond dépassé, rien. L'écart revient à chaque relèvement du SMIC
en cours d'année, au 1er juillet jusqu'en 2009 ; les moteurs n'ont pas tourné sur le cas.

**Écarts relevés, plus petits ou déjà proches d'un écart déclaré.**

- *La Nouvelle-Calédonie* (n° 2002/620, décret n° 2002-1371) : côté calédonien, la pension
  par totalisation affecte à la durée totale « un nombre de points minimum correspondant,
  tel que prévu par la législation calédonienne », la proratise, et « L'intéressé a droit
  à la pension la plus élevée » ; `cafat_pension_de_base.yaml` (ligne 194) ne porte pas ce
  minimum. Le trimestre y vaut « 3 mois, 13 semaines ou 66 jours », quand le modèle
  compte trois mois (`docs/limites/3-systeme-actuel.md`, ligne 624, qui le dit pour
  l'Union).
- *La CSG des retraités partis de France* (formulaires 30648 et 30655a de la n° 2002/4) :
  qui déclare encore ses revenus « à l'administration fiscale française » doit la CSG ; la
  fiche `cotisation_maladie_des_non_residents` présume que « qui réside hors de France n'y
  a pas son domicile fiscal » (ligne 24). Non chiffré.
- *La CSG du résident de France couvert par un autre État de l'Union* (n° 2002/345) :
  exonéré de CSG et de CRDS ; la fiche `csg_des_pensions_selon_le_revenu` ne lit pas qui
  prend ses soins en charge. Cas rare, non chiffré.
- *Le service national* (`LE_MIN_03052002`) : validé par le premier régime de base où
  l'assuré est affilié ensuite, un régime spécial d'abord ; déjà déclaré
  (`docs/limites/3-systeme-actuel.md`, lignes 394 à 398). La lettre dit aussi que la
  CNAVPL ne le validait pas avant le 1er janvier 2002 : non vérifié dans le modèle.
- *Le chômage non indemnisé de l'assuré de cinquante-cinq ans* (`LE_MIN_09042002`) : le
  ministre demande à la Cnav d'abandonner sa lecture de l'article R. 351-12, qui exigeait
  les vingt ans de cotisations au seul régime général (circulaire Cnav n° 39-80), pour
  les compter tous régimes, comme le modèle (`carriere.py`) ; pour une pension d'avant
  2002, le modèle est donc plus large que la caisse. Non chiffré.
- *La majoration forfaitaire pour enfant*, non cumulable avec une prestation d'orphelin,
  même étrangère (n° 2002/321) : la fiche le dit déjà (lignes 213 à 217).

**Points non tranchés, les sorts retenus.** La n° 2002/57 (réversion et Union), la
n° 2002/65 (contrôle des ressources), la n° 2002/369 (amiante), `D_IM_20024` et
`LE_MIN_17072002` (Mayotte) sont en `limite`, sur leurs précédents, quand `hors_modele` se
défendrait ; la n° 2002/3 (Pologne) et ses pièces en `hors_modele`, quand le certificat
sert la majoration de l'article L. 814-2 ; l'annexe de la n° 2001/72, une lettre qui juge
une demande irrecevable, en `hors_modele`, quand sa circulaire est en `limite`. La notice
du formulaire SE 352 (Algérie) borne l'âge du conjoint à 65 ans : sans doute le champ du
formulaire, non une condition de la réversion.

**Ce que la base sert de travers.**

- Des pièces mal rattachées ou mal datées : le formulaire 30057, attestation de
  l'allocation équivalent retraite de la n° 2002/40, servi sous la n° 2002/4 ; l'annexe de
  la n° 2002/56 datée du 2 février pour le 2 octobre ; l'annexe 2 de la n° 2002/57 du
  10 février pour le 10 octobre ; l'annexe « 1-2 » de la n° 2002/58, qui porte aussi
  l'annexe 3 ; la pièce 30369, « Réf. 30359 » à son pied ; `D_IM_20023`, à la date de la
  circulaire qu'elle transmet ; `D_IM_20024`, du 28 mai au titre, du 4 juillet au texte.
- Des chiffres et des renvois : les décrets de la Mongolie et de la Tchécoslovaquie, dont
  numéro et date ne concordent pas, et la loi n° 83-376 ou 83-676 (n° 2002/12) ; la
  référence du JOCE du 3 mai reprise de celle du 5 février (n° 2002/33) ; le Cerfa
  « 1137 *02 » au résumé, « 11372*02 » au texte (n° 2002/55) ; des taux écrits avec un
  point, et la Suisse sans valeur (n° 2002/51 et 2002/60) ; l'arrangement général avec
  l'Algérie daté du « 1er octobre 1980 » (n° 2002/321) ; la lettre « DSS/SDGSI/4B/2000/6605 »
  pour le n° 02-6605 (`D_IM_20027`) ; une ligne de coefficients sans son article
  (n° 2002/63).
- Des mentions d'annulation : la n° 2002/17, « Annulée et remplacée par circulaire CNAV
  2004/15 » ; la n° 2002/9, « par circulaire Cnav 2017/37 du 8 avril 2010 », incohérente.
- Des annexes non servies : l'arrangement n° 9 joint à la n° 2002/321 (`AR_ADC_9`, à
  lire), les formulaires SE 988 de la n° 2002/620, l'annexe 1 de la n° 2002/197 ; la
  n° 2002/345, qui semble tronquée ; les notes de la n° 2002/56 ministérielle, servies en
  vrac ; du formulaire 30664, le seul en-tête turc ; six scans sans texte.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les lois, décrets et arrêtés que ces
textes appliquent n'ont pas été relus au Journal officiel, ni le décret n° 2002-1371 ; les
montants l'ont été aux séries du dépôt. Les moteurs n'ont tourné sur aucun cas.

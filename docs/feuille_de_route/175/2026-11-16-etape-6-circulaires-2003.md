# Étape 6, circulaires de 2003 : les 54 références sans thème de la dixième période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées ; la quatrième, les
circulaires, lettres et instructions sans thème, l'est de 1936 à 2003 (cette note et celles
des périodes d'avant). Restent 818 circulaires, de 2004 à 2026, par période (73 en 2004, 66
en 2005, 61 en 2006, 120 en 2007, 60 en 2008) ; puis, une session par nature : les 96
autres textes, les 74 que la base nomme sans les servir, les 107 accords. Méthode : la
base relue par l'API (`_reference` de `cnav_legislation.py`), les pièces PDF lues au site
sous `/Pdf/<nom>`, chaque texte lu en entier, la citation d'un agent retrouvée par script
dans le texte servi. Candidats neufs : la pension de l'inapte suspendue au-delà d'un plafond
de revenus d'activité ; la convention franco-tchécoslovaque, sans prorata dans le modèle
(ici).

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2003 : 54, comme la note de 2002 les
  comptait.
- *La lecture* : les 54, relues par l'API le 16 novembre 2026 à 11 h 05 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies : 40 en page (409 735 octets de
  texte), 14 en PDF, pièces de circulaires, lues au site (`/Pdf/<nom>`, et non au chemin
  `textes/…` que la fiche de l'API donne, qui répond 404) par leur texte (`pdftotext`,
  156 283 octets) ; aucun scan. 29 circulaires de la Cnav et leurs 14 pièces, 4
  circulaires ministérielles, 5 diffusions d'instructions ministérielles, 2 lettres.
- *Qui a lu* : les 54 en entier, par quatre agents de la session sur Opus, un lot chacun
  (de 118 000 à 166 000 octets), lancés ensemble, sur une consigne commune (les raisons du
  registre et les renvois déjà employés, avec leur effectif ; les rangements de 2001 et
  2002 pour précédents). Les 54 citations ont été retrouvées mot pour mot, par script,
  dans le texte servi (blancs normalisés), chaque raison hors modèle dans le registre,
  chaque renvoi dans le dépôt. La session a relu elle-même les passages et le code qui
  décident des deux écarts neufs, et tranché entre deux lectures du moteur (plus bas).
- *Les sorts* : 54 références rangées, 19 `limite`, 35 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 54 lignes, les colonnes `sort`
  et `renvoi` seules, vérifié par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : la convention franco-tchécoslovaque (circulaire ministérielle
  n° 2003/88, Cnav n° 2003/32 et sa rectificative) ; la convention avec Andorre, en vigueur
  le 1er juin 2003 (n° 2003/287) ; les règlements étendus aux ressortissants des pays
  tiers (règlement n° 859/2003, n° 2003/318 et sa diffusion) ; les médecins hospitaliers de
  Mayotte (diffusion n° 2003/1, comme la lettre du 17 juillet 2002) ; les pensions
  allemandes des ghettos, hors des ressources (diffusion n° 2003/2) ; les plafonds des
  veuves de guerre (n° 2003/1) ; l'allocation équivalent retraite et son imprimé
  (n° 2003/10, comme la n° 2002/40) ; les avantages en nature dans les ressources du
  minimum vieillesse (n° 2003/20) et dans l'assiette des cotisations (circulaire
  ministérielle n° 2003/7) ; le plafond de la réversion au 1er juillet 2003
  (n° 2003/30) ; le plafond de revenus de l'inapte (n° 2003/31) ; les seuils de la CSG
  de 2004 (n° 2003/38) ; le trimestre de 2004 (n° 2003/49) ; les rentes ouvrières et
  paysannes (n° 2003/53) ; le service national (lettre de la Cnav du 1er juillet 2003).
- *Hors modèle* : l'action sociale (22 : l'aide ménagère, ses barèmes et imprimés, le
  retour à domicile, les coordinations gérontologiques, les prix plafonds, le plan
  commun avec l'assurance maladie, n° 2003/41) ; les monnaies (4) ; la tenue du relevé de
  carrière (la convention d'échange des données de carrière entre régimes, n° 2003/48 et
  son annexe) ; et sept autres, une par raison (le titre de séjour, l'allocation de retour
  à l'activité, la retenue à la source, les entretiens franco-espagnols, la forclusion des
  rachats levée, le Québec, les commissions de recours amiable).

**Les montants relus, conformes.** Le SMIC de 7,19 € au 1er juillet 2003
(`macro/smic_horaire_releves.csv`) ; le plafond de la réversion à cette date,
14 955,20 € ; le trimestre de 2004, 1 438 € (`legislation/validation_trimestres.csv`) ; la
revalorisation de 1,5 % au 1er janvier 2003 ; les plafonds des veuves de guerre
(`legislation/minimum_vieillesse_avant_2007.csv`) ; le seuil de la CSG de 2004, 7 046 €
pour une part (`legislation/csg_pensions_seuils.csv`) ; le demi-plafond de 2003, 1 216 €
par mois ; la durée maximum de 150 trimestres (`legislation/duree_proratisation.csv`) ;
l'entrée en vigueur de la convention andorrane.

**Deux écarts neufs** (candidats), pour les sessions du modèle, sans y toucher.

- *La pension de l'inapte, suspendue au-delà d'un plafond de revenus d'activité.*
  Circulaire Cnav n° 2003/31 du 10 juillet 2003 : selon l'article R. 352-2, les pensions
  substituées à une pension d'invalidité et celles attribuées au titre de l'inaptitude
  « ne sont servies, lorsque les titulaires sont âgés de moins de 65 ans, que si les
  revenus professionnels des intéressés ne dépassent pas, par trimestre, 50% du salaire
  minimum de croissance calculé sur la base de 520 heures » ; 1 869,40 € par trimestre
  depuis le 1er juillet 2003. Rien dans le dépôt ne porte l'article (ni les fiches
  `inaptitude_au_travail` et `pension_d_invalidite_substituee`, ni les limites) ; la
  fiche `cumul_emploi_retraite_et_retraite_progressive` sert la pension « entière » chez
  un autre employeur (lignes 57 à 64, jusqu'en 2004). Cas, à la main : inapte de 62 ans
  en 2003, salarié d'un autre employeur à 2 000 € par trimestre ; la caisse ne sert rien
  ce trimestre, le modèle la pension entière. Les circulaires de 2000 à 2002 qui
  relevaient ce plafond ont été rangées sans que l'écart soit dit.
- *La convention franco-tchécoslovaque, sans prorata dans le modèle.* Circulaire
  ministérielle n° 2003/88 du 21 février 2003 : la seule convention sans droit d'option
  « impose toujours la règle de la totalisation-proratisation », prorata de la carrière
  entière, « non limitée au maximum de 150 trimestres » ; depuis la circulaire du
  9 novembre 1990, elle est abandonnée pour l'assuré résidant en France qui a 150
  trimestres français ; depuis le 21 février 2003, à 65 ans ou au taux plein, la caisse
  compare à la pension des seules périodes françaises et sert la plus élevée (Cnav
  n° 2003/32 rectificative). Le tableau des accords porte la convention, pour la
  République tchèque et la Slovaquie jusqu'au 1er mai 2004, en `calcul: non_lu`
  (`accords_internationaux.yaml`, lignes 160 à 165 et 314 à 320) ; une convention non
  lue fait compter ses périodes pour le taux de la pension nationale, sans prorata
  (`pension_proratisee.yaml`, lignes 51 à 54 ; `etranger.py`, ligne 152 : seules
  `comparaison` et `option` comparent, et une période non comparée compte aux
  trimestres de la pension nationale). Cas, à la main : 120 trimestres français, 60
  tchèques, départ à 60 ans en 2002, salaire moyen S ; le modèle sert 50 % × S × 120/150,
  0,400 S ; la caisse 50 % × S × 120/180, 0,333 S : le modèle sert 20 % de trop. Le texte
  permet de lever le `non_lu` (totalisation-proratisation, puis comparaison sous
  conditions). Un agent avait lu le moteur à l'inverse, la pension proratisée seule
  servie : le code ne le dit pas.

**Écarts relevés, déjà déclarés ou plus petits.**

- *Le plafond de la réversion au SMIC de la date de la demande* (n° 2003/30 : 7,19 €
  au 1er juillet 2003, 14 955,20 € contre 14 206,40 € au modèle, 5,3 % de moins) : déjà
  déclaré dans la fiche `reversion` (lignes 1135 à 1137, et 1150 à 1154 pour 2004).
  L'écart que la note de 2002 donnait pour neuf l'était donc déjà.
- *Andorre avant le 1er juin 2003* (n° 2003/287) : les accords administratifs du 9 juin
  1970 et du 20 août 1973 totalisaient déjà ; le tableau des accords n'a rien avant la
  convention. Déjà relevé par la note de l'étape 4 sur les accords (première moitié),
  qui ne nomme pas l'arrangement de 1973.
- *Les déductions forfaitaires pour frais professionnels* (circulaire ministérielle
  n° 2003/7) : une soixantaine de professions, sous 7 600 € par an ; la limite
  (`3-systeme-actuel.md`, lignes 163 à 165) ne nomme que le VRP. Rien à calculer : la
  saisie dit le salaire porté au compte.

**Points non tranchés, les sorts retenus.** La n° 2003/7 ministérielle en `limite`, quand
la raison des avantages en nature (`hors_modele`) se défendrait ; la n° 2003/9 (entretiens
franco-espagnols) en `hors_modele`, quand la totalisation se défendrait ; la levée de la
forclusion des rachats en `hors_modele`, quand la fiche `rachats_et_versements` se
défendrait ; la n° 2003/48 sous la tenue du relevé de carrière, aucune raison ne nommant
les échanges entre régimes.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2003/20, « Annulée par circulaire CNAV 2003/50 » ; la
  n° 2003/48, par la n° 2004/55 ; deux circulaires sous le numéro 2003/32, la première
  annulée par la rectificative.
- Des annexes annoncées et non servies : les lettres des diffusions n° 2003/1, 2003/2 et
  2003/6, l'arrangement administratif de la n° 2003/287, le règlement de la n° 2003/318.
- Des erreurs : la n° 2003/35 date la décision du conseil d'administration du 2 puis du
  3 juillet ; le dollar libérien de la n° 2003/37 au taux des Bahamas ; des valeurs « . »
  à l'annexe 2 de la n° 2003/52 ; l'annexe de la n° 2003/48 porte deux fois le dossier
  technique, la version de travail avec sa note « FAUX ÆA reformuler » ; la lettre
  ministérielle du 4 août 2003 est de la DRASS Midi-Pyrénées ; la pièce « Aah » de la
  n° 2003/57 est l'aide à l'amélioration de l'habitat.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les textes que ces circulaires
appliquent n'ont pas été relus au Journal officiel, ni l'article R. 352-2 dans ses
versions ; les moteurs n'ont tourné sur aucun cas.

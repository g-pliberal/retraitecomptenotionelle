# Retouches de la relecture R-D3 : le doute sur le forfait de l'artisan rendu, R. 242-16 ôté de la complémentaire des commerçants, le tableau de la circulaire n° 2008/017 et le rectificatif de 2004 cités (Retouches 4)

**Le 5 novembre 2026, « Retouches 4 ».** La relecture R-D3
(`2026-11-05-relecture-de-d3.md`) jugeait D3 conforme, avec deux écarts faibles
(§ 4) et un point 5 fait pour moitié. Chaque source a été rouverte ici, à la
version qui compte ; aucune valeur du modèle, aucun témoin, aucun test ne bouge,
rien n'est corrigé dans les moteurs. Les retouches de D3 à R-D2 (commit 6585726)
que R-D3 n'avait pas vues, l'invalide exonéré et le minimum au revenu nul, ne sont
pas refaites. Index LEGI à jour du 2 novembre 2026 et index JORF à jour du 3,
récupérés dans la session ; circulaires du RSI retéléchargées de la base de la
Cnav, leur empreinte recalculée : celles que la note de D3 donne pour les n° 2007/013,
2008/017 et 2008/031 sont les mêmes.

## 1. A1 — le forfait de l'artisan régularisé de 2009 à 2011 : une lecture, rendue comme telle (écart 1)

**Ce que j'ai lu.**

- D. 635-7 : `dila_cherche.py legi --num D635-7 --le 2009-06-01`, puis `--le 2011-06-01`
  rendent le même article, **une seule rédaction du 1er janvier 2008 au 1er janvier
  2012** (LEGIARTI000017869802). Il dit, mot pour mot : « Pour les assurés commençant
  l'exercice d'une profession artisanale ou assimilée, la cotisation annuelle est
  assise : 1° Pour l'année ou la fraction d'année de début d'exercice, sur un revenu
  correspondant au tiers du plafond mentionné à l'article L. 241-3 ; 2° Pour l'année
  suivante, sur un revenu correspondant à la moitié dudit plafond. » « Assise », non
  « à titre provisionnel ».
- D. 635-2 (LEGIARTI000020032159, du 29 décembre 2008 au 5 avril 2012) : « La cotisation
  annuelle au régime complémentaire obligatoire d'assurance vieillesse est calculée
  suivant les modalités prévues au cinquième alinéa de l'article L. 131-6. Sous réserve
  des dispositions des articles D. 635-7 et D. 635-10, elle est recouvrée dans les
  conditions prévues aux articles R. 133-26 et R. 133-27 [...] ». Par `--diff`, la même
  réserve est dans la rédaction de 2008 (LEGIARTI000006738017, du 1er janvier au 29
  décembre 2008), où D3 tient le forfait pour définitif : R-D3 avait raison, elle ne
  tranche rien.
- L. 131-6, cinquième alinéa (LEGIARTI000020169101, LEGIARTI000020675442) : « Elles
  sont calculées, à titre provisionnel, en pourcentage du revenu professionnel de
  l'avant-dernière année ou des revenus forfaitaires. Lorsque le revenu professionnel
  est définitivement connu, les cotisations font l'objet d'une régularisation. » Le
  forfait du commerçant est, lui, dit « à titre provisionnel » par le texte : « les
  cotisations [...] dues au titre de la première année civile d'activité sont
  calculées à titre provisionnel sur une base forfaitaire qui ne peut excéder
  dix-huit fois [...] ». Le doute ne porte donc que sur l'artisan.
- La circulaire RSI n° 2008/031 (6 mai 2008, sha256 a7212c2d…bf00c034), relue aux
  § 3.1.1 et 3.1.2. § 3.1.1, des assurés qui commencent une profession
  artisanale : « la cotisation annuelle reste assise pour l'année ou la fraction
  d'année de début d'exercice (« 1ère année civile »), sur un revenu correspondant au
  tiers du plafond de la sécurité sociale et pour l'année suivante (« 2ème année
  civile »), sur un revenu correspondant à la moitié dudit plafond. Ainsi, pour ses
  catégories d'assurés, seul le taux correspondant à la « première tranche » (7 % en
  2008, 7,1 % en 2009, 7,2 % en 2010) devrait être appliqué. » § 3.1.2 : « Il a été
  décidé par la section des professions artisanales de mettre en place une
  régularisation des cotisations du RCO qui s'effectuerait dans les mêmes conditions
  que celle applicable au régime légal de base. Cette régularisation serait applicable
  à compter de 2010 sur les revenu 2009 ». Le conditionnel est celui de la circulaire,
  écrite sept mois et demi avant le décret n° 2008-1427 (22 décembre 2008) ; elle ne
  nomme pas le forfait de début parmi ce qu'elle régularise.
- Les autres : la circulaire n° 2008/017 (sha256 61efc134…582a3f82) dit, de 2008, que
  « les cotisations RCO, NRCO et ID ne sont pas régularisées » et qu'elles « sont
  calculées à titre définitif sur le revenu N-2 » ; les n° 2009/017 (12 mars 2009,
  sha256 add2fcbb…2341967), n° 2009/035 (2 juillet 2009, sha256 9263bb5d…18137ad3) et
  n° 2009/044 (15 octobre 2009, sha256 5c85e8d7…92434b4), cherchées par mots
  (« régularis », « forfait », « début d'activité », « 1/3 »), ne disent pas le forfait de
  début de l'artisan régularisé ; la n° 2009/035 ne parle de « la régularisation des
  cotisations » que pour les points gratuits de l'artisan en dispense d'activité.
- Le décret n° 2011-2038 (JORFTEXT000025055789) est « relatif à l'assiette forfaitaire
  des cotisations de sécurité sociale de début d'activité dues, à titre provisionnel,
  par les travailleurs indépendants non agricoles », et « Entrée en vigueur : le 1er
  janvier 2012 » : il va dans le sens de la lecture, mais pour 2012 et après.

**Ce que j'ai écrit.** La lecture est la plus solide, et aucun document de la caisse ne
la confirme.

- Fiche `assiette_rco_independants`, une approximation neuve, version
  `regularisation_2009`, avec D. 635-7 mot pour mot ci-dessus, ce qui fonde la lecture, ce
  qui ne la tranche pas, et l'effet : les deux témoins qui bougent depuis D3,
  `metiers_prive_puis_independant` (2 437,35 points du RCO à la lecture retenue, 1 257,17
  si le forfait était définitif ; sa pension du scénario 1 de 46 148,69 à 46 702,03 €,
  +1,20 %) et `metier_change_en_cours_d_annee` (1 346,42 points contre 886,01 ; de
  46 841,53 à 47 061,17 €, +0,47 %). Les chiffres sont ceux de D3, que R-D3 a refaits à
  la main (§ 2 de sa note).
- La même fiche : l'intitulé, le `droit` de la version `regularisation_2009`, l'effet
  d'ensemble et la première approximation (« la question tombe » devient « tombe si »)
  disent la lecture ; `a_relire` demande une circulaire ou un barème de la caisse qui dise
  le forfait de l'artisan régularisé, ou définitif.
- `docs/limites/3-systeme-actuel.md`, l'article sur l'assiette de la complémentaire : la
  phrase que D3 avait retirée, remise sous une forme qui dit la lecture, avec D. 635-7
  mot pour mot.

## 2. A2 — trois imprécisions de rédaction (écart 2)

**(a) R. 242-16 n'est pas le texte du forfait de la complémentaire des commerçants.**

- L. 131-6 (LEGIARTI000006740118) n'en fait qu'un plafond : « une base forfaitaire qui ne
  peut excéder dix-huit fois la valeur de la base mensuelle de calcul des prestations
  familiales en vigueur au 1er octobre de l'année précédente ; celles dues au titre de
  la deuxième année civile d'activité [...] qui ne peut excéder vingt-sept fois cette
  valeur ». D. 635-10 ne renvoie qu'à lui.
- R. 242-16 (LEGIARTI000006748778) dit « une base forfaitaire égale à dix-huit fois ». C'est
  la règle de la cotisation d'allocations familiales : le décret n° 2000-841 du 30 août
  2000 (LEGITEXT000005629904), dont les visas citent L. 131-6 et R. 242-16, est « relatif au
  calcul des cotisations d'allocations familiales dues à titre personnel par les employeurs
  et travailleurs indépendants et modifiant la section 5 du chapitre 2 du titre IV du livre
  II du code de la sécurité sociale » ; sa date d'effet à l'index, le 2 septembre 2000, est
  celle de la rédaction de R. 242-16 qui pose la base forfaitaire de dix-huit fois
  (LEGIARTI000006748777). D. 633-6
  (LEGIARTI000006737897) la reprend pour la base vieillesse : « la cotisation
  provisionnelle [...] au titre de l'année ou de la fraction d'année de début d'exercice est
  calculée sur la base du revenu mentionné au premier alinéa de l'article R. 242-16 ».
- Dans l'index LEGI du dépôt, les articles du code de la sécurité sociale qui citent
  « 242-16 » sont D. 242-17, D. 612-6, D. 633-6, L. 531-5, R. 133-27, R. 133-29, R. 241-3 et
  R. 243-26 : aucun article D. 635-x de la complémentaire, ni D. 635-7 ni D. 635-10.
- Que le forfait de la complémentaire soit ce plafond, c'est la caisse qui le dit :
  circulaire RSI n° 2007/013 (23 janvier 2007, sha256 05ce2821…8e6e3e70), § 2.2, « Situation
  en début d'activité » : « Pour le groupe professionnel des commerçants, tous les risques,
  y compris régime complémentaire et invalidité-décès sont calculés sur la base de 18 puis
  27 BMPF. » Pour l'artisan, le même paragraphe dit : « les cotisations du régime
  invalidité-décès et du régime complémentaire obligatoire sont calculées sur la base de
  un tiers du plafond en 1ère année et de un demi-plafond en 2ème année ».
- Corrigé : la fiche (le `droit` de la version de 2004, les deux approximations qui citaient
  R. 242-16 pour le prorata et pour la reprise, une approximation neuve, version
  `avant_derniere_annee_des_deux_regimes_2004`, dont l'effet est nul tant que la caisse a
  pris le plafond) et les limites. Pas la note de D3, qui est un récit.
- **Une précision de plus, à la même place.** La note de D3 (§ 2) dit : « Le régime de base
  régularise les forfaits de début (R. 242-16, D. 633-6) ». De 2004 à 2007 c'est juste :
  R. 242-16 (LEGIARTI000006748778) porte la régularisation (« celles-ci font l'objet d'une
  régularisation »). Sa rédaction du 1er janvier 2008 (LEGIARTI000006748779) ne la porte
  plus (`--diff` : l'alinéa est supprimé) ; de 2009 à 2011, la régularisation de la base
  repose sur L. 131-6, ci-dessus. Je n'ai pas relu R. 133-20 et suivants, que la
  circulaire n° 2008/031 dit porter désormais la cotisation provisionnelle et sa
  régularisation. Aucune valeur n'en dépend.

**(b) Le tableau de la circulaire n° 2008/017 est celui du plafonnement des micro-entreprises.**

- Son objet : « Présentation du régime micro-social. » Le tableau (« 1/3 PSS » puis « 1/2 PSS »
  pour l'artisan, « 18 BMAF » puis « 27 BMAF » pour le commerçant, au poste « Retraite
  complémentaire et invalidité-décès ») est au « I. VOLET 1 : PLAFONNEMENT DU MONTANT DES
  COTISATIONS », « B. Modalités d'application », « 1. Calcul des cotisations provisionnelles »,
  « (a) Situation des débuts d'activité », qui s'ouvre sur « On effectue le calcul des
  cotisations sur les bases forfaitaires de 1ère année et 2ème année, sans application du
  plafonnement. » La mesure s'applique, pour 2008, à « toutes les entreprises soumises au
  régime fiscal micro-entreprise existantes ou en début d'activité au 1er janvier 2008 ».
- La note 2 de la circulaire DSS/5 B/5 C n° 2007-431, reproduite en annexe (« Il est rappelé
  que pour le calcul définitif, la cotisation invalidité-décès et la cotisation de retraite
  complémentaire restent celles qui ont été établies au moment de l'appel provisionnel ») est
  elle aussi dans une circulaire sur le régime micro-social. Je n'ai pas retrouvé, dans le
  texte extrait du PDF, l'appel de cette note.
- Les deux pièces restent des pièces de la caisse sur ces forfaits, et sur leur caractère
  définitif en 2008 ; ce ne sont pas des textes de la complémentaire. La fiche le dit
  maintenant dans la lecture de la caisse (celle du 5 novembre 2026), et dans la nouvelle
  approximation.

**(c) Le rectificatif du décret n° 2004-848.** Ouvert à l'index du JORF : « Rectificatif au
Journal officiel du 24 août 2004, édition papier, page 15158, 2e colonne, et édition
électronique, texte n° 35, article D. 635-10, dernière ligne, au lieu de : « ...
quatrième... », lire : « ... sixième... ». » (JORFARTI000002107853, du 28 août 2004). Il règle
l'écart entre le Journal officiel (« quatrième alinéa », JORFARTI000001334654, que j'ai rouvert) et
LEGI (« sixième »). Cité à la fiche, dans la lecture qui relevait l'écart, et dans une
lecture neuve.

## 3. A3 — la cessation en janvier de la deuxième année : la fiche la dit, depuis 6585726

R-D3 a lu 4cf6b96 ; la phrase est dans le commit suivant, 6585726 (`git log -S"cesse en
janvier"` ne rend que lui). La fiche `assiette_rco_independants`, effet de l'approximation
de la version `avant_derniere_annee_des_deux_regimes_2004`, dit pour la deuxième année :
l'artisan, « à la moitié du plafond, sous 1,16 à 1,24 mois, s'il cesse en janvier » ; le
commerçant, « sous 1,91 à 2,01 mois, s'il cesse en janvier, ou en février 2008 ».
**Rien à écrire.** Le calcul, refait à la main sur les séries du dépôt (plafond annuel de
la sécurité sociale, Smic horaire du 1er janvier, base mensuelle des prestations familiales
du 1er octobre) :

| Année | Minimum (200 × Smic) | Artisan, 2e année, un mois (PSS / 24) | Seuil, en mois | Commerçant, 2e année, un mois (27 × base / 12) | Seuil, en mois |
|---|---|---|---|---|---|
| 2004 | 200 × 7,19 = 1 438,00 | 29 712 / 24 = 1 238,00 | 1,162 | 27 × 347,68 / 12 = 782,28 | 1,838 |
| 2005 | 200 × 7,61 = 1 522,00 | 30 192 / 24 = 1 258,00 | 1,210 | 27 × 353,59 / 12 = 795,58 | 1,913 |
| 2006 | 200 × 8,03 = 1 606,00 | 31 068 / 24 = 1 294,50 | 1,241 | 27 × 361,37 / 12 = 813,08 | 1,975 |
| 2007 | 200 × 8,27 = 1 654,00 | 32 184 / 24 = 1 341,00 | 1,233 | 27 × 367,87 / 12 = 827,71 | 1,998 |
| 2008 | 200 × 8,44 = 1 688,00 | 33 276 / 24 = 1 386,50 | 1,217 | 27 × 374,12 / 12 = 841,77 | 2,005 |

Un mois, c'est donc sous le minimum toute l'année, pour l'artisan comme pour le
commerçant ; deux mois ne le sont pas, sauf en février 2008 pour le commerçant : 2 × 841,77
= 27 × 374,12 × 2 / 12 = 1 683,54 € sous 1 688 €. Février 2007 y échappe de 1,42 € :
27 × 367,87 × 2 / 12 = 1 655,415 € contre 1 654 €. Les seuils sont ceux de la fiche ; le
champ cite bien les deux cas.

**Une case que la fiche n'a pas, relevée ailleurs.** La ligne de 2004 du commerçant, celui
qui a commencé en 2003 et cotise sa deuxième année en 2004, manque au champ : il dit « sous
1,91 à 2,01 mois », là où le seuil de 2004 est 1,84 (1 438 / 782,28). Elle a été relevée
par la relecture des retouches de R-D2 (`2026-11-05-relecture-des-retouches-de-r-d2.md`,
§ 1), qui ne change pas la conclusion (un mois, 782,28 € sous 1 438 € ; deux mois, 1 564,56 €
au-dessus). Je ne la retouche pas : elle n'est pas dans la liste de cette tâche.

## Ce qui n'est pas fait, et pourquoi

- **Les commentaires du code, des tests et des données** citent R. 242-16 pour le forfait du
  commerçant : `acquerir.py` (l. 699, 715), `regimes.py` (l. 866), `macro.py` (l. 590),
  `macro.js` (l. 178), `construire_donnees.py` (l. 207), `tests/test_independants.py`
  (l. 1272, 1364), `data/sources.yaml` (l. 5307), `data/reference/regimes/_schema.yaml`
  (l. 1146, 1162), l'en-tête de `base_mensuelle_prestations_familiales.csv` (l. 12). Ce sont
  des fichiers que cette tâche ne touche pas (code, tests, données, fichiers partagés) :
  le même ôté, vers L. 131-6 et la circulaire n° 2007/013, est à faire dans une session
  qui y travaille, sans changer une valeur (des commentaires : `Sans-test: commentaire`).
- **Le paquet.** `python scripts/construire_donnees.py` : `moteur/donnees.json` ne change pas.

## Sources ouvertes dans la session

- **Index LEGI** (à jour au 2 novembre 2026) : D. 635-7, `--num` `--le` 2009-06-01 et 2011-06-01 ;
  D. 635-2, toutes ses rédactions (`--diff`) ; LEGIARTI000020032159, LEGIARTI000020032165 ;
  L. 131-6, LEGIARTI000006740118, LEGIARTI000020169101, LEGIARTI000020675442 ; R. 242-16, toutes
  ses rédactions (`--diff`) ; D. 633-6, LEGIARTI000006737897 ; D. 612-6, LEGIARTI000006738291 ;
  le décret n° 2000-841, LEGITEXT000005629904 ; la recherche des articles qui citent « 242-16 ».
- **Index JORF** (à jour au 3 novembre 2026) : décret n° 2004-848, article 1er
  (JORFARTI000001334654) ; son rectificatif du 28 août 2004 (JORFARTI000002107853) ; décret
  n° 2011-2038, notice (JORFTEXT000025055789).
- **Base de législation de la Cnav**, PDF téléchargés le 5 novembre 2026 : circulaires RSI
  n° 2007/013, 2008/017, 2008/031, 2009/017, 2009/035, 2009/044.
- **Dépôt** : `plafond_securite_sociale.csv`, `smic_horaire.csv`,
  `base_mensuelle_prestations_familiales.csv` ; la fiche `assiette_rco_independants`.

# Étape 10, troisième partie : le contrôle d'un relevé, chaque année de salarié contre les trimestres que son revenu valide

**La demande.** Le reste 2 de la note du 16 octobre
(`2026-10-16-etape-10-ages-de-depart-au-site.md`, « Ce qui reste ») : le
contrôle d'un relevé. Le registre le tient du calculateur
« calcul-verification-pension-retraite » (`calcul_verification_pension`,
chantier 138.10) : « Il recalcule les trimestres d'un relevé réel depuis ses
montants, et le contrôle ainsi » ; dans le dépôt, le relevé faisait foi, et rien
ne signalait une année sous-validée. Ni l'indice majoré, ni le solveur inverse.
Session du 19 octobre, la seule sur les pages.

**La veille.** Aucune règle du scénario 1 ne change, et le journal de veille
n'a pas d'entrée. Lue pour la bulle du site : R. 351-9 dans l'index LEGI, sa
rédaction du 1er janvier 2026 (LEGIARTI000053335598) — 150 heures du SMIC en
vigueur au 1er janvier depuis 2014, 200 heures de 1972 à 2013, le trimestre de
l'allocation aux vieux travailleurs salariés de 1949 à 1971, « avec un maximum
de quatre trimestres par année civile ». Elle commence en 1949 : les années
d'avant viennent de ses rédactions antérieures (LEGIARTI000028751530,
LEGIARTI000006749353), que le modèle applique depuis l'étape 6.

**Ce qui est fait.**

- Le modèle, Python puis portage : `seuil_d_un_trimestre(annee, outre_mer)`
  (`donnees/macro.py`) et `seuilDUnTrimestre` (`macro.js`), le revenu qui
  valide un trimestre dans l'année — infini outre-mer avant 1948, `None` avant
  1946, où la retenue les fait. `trimestres_valides` y lit désormais son seuil,
  un remaniement : aucune pension des 888 témoins ne bouge. Le test,
  `test_le_seuil_d_un_trimestre_est_celui_qu_un_releve_se_lit_contre`, pose les
  seuils à la main — 1 742 € en 2009, 1 886 € en 2013, 1 429,50 € en 2014,
  1 441,50 € en 2015 — ; son jumeau est dans `tests/js/moteur.test.js`.
- Le contexte : `controleDuReleve(saisie)` (`contexte.js`, sans jumeau
  Python, comme `balayageDeLEstimation`). Pour chaque année du relevé qui porte
  ses trimestres, sous un statut de salarié dont le régime de base est cette
  année-là le régime général ou celui des salariés agricoles (`auRevenu`) : les
  trimestres que le calcul en retient, ceux que son revenu valide — la carrière
  du même relevé rebâtie sans ses trimestres, sous les mêmes bornes, celle de
  l'année du départ comprise —, et le seuil de l'année. La fonction publique et
  les régimes spéciaux, qui comptent leurs services au temps, n'y sont pas, ni
  l'indépendant, qui valide aussi par son assiette minimale et les cotisations
  qu'il a payées.
- La page des résultats : le dépliant « Votre relevé, contrôlé »
  (`releveControle`, `pages.js`), le premier de « Pour aller plus loin ». Les
  années qui ne s'accordent pas, en un tableau — le revenu, le seuil d'un
  trimestre, ce que le revenu valide, ce que le relevé retient —, puis ce qu'il
  faut en dire : moins de trimestres que le revenu n'en valide, la ligne est à
  vérifier sur le relevé, puis auprès de la caisse, bulletins de paie à
  l'appui, et le calcul garde ceux du relevé ; plus, le relevé y compte
  d'ordinaire des périodes validées sans revenu. Un relevé d'accord le dit. Le
  résumé du relevé (`resumeReleve`) renvoie au dépliant quand une année est
  sous-validée (`sousValidees`, `data-vers="releve-controle"`).
- Les tests : `tests/test_controle_du_releve.py`. Un relevé fictif dont 2009 et
  2015 retiennent un trimestre que le revenu ne valide pas, au seuil posé à la
  main, et dont 2016 en retient quatre sans revenu ; la fonctionnaire de 2017
  et l'artisane de 2018 hors du contrôle ; le revenu valide ce que le modèle
  Python compte du même relevé sans ses trimestres. Puis l'année d'un départ de
  juillet, que les deux comptes bornent à deux trimestres ; un relevé d'accord ;
  un relevé sans trimestres et une carrière décrite par ses métiers, sans
  dépliant. Au registre, le point de `calcul_verification_pension` passe à
  `repris`.

**Ce que montrent les mesures.** Sur le relevé du test, 27 années se
contrôlent et 3 ne s'accordent pas. Le contrôle rebâtit deux carrières : 1,7 ms
à chaud dans node. Aucun des 888 témoins de simulation ne bouge de mon fait ;
un rendu de page sur 79 gagne le dépliant, le relevé d'essai, d'accord sur ses
41 années. Les témoins refaits portent aussi ce que l'étape 12 a poussé sans
eux (2ffc33d) : la seconde retraite du RCI de `seconde_pension_commercant_2025`
et le cas neuf `seconde_pension_artisane_au_minimum_2026`.

Hors de l'étape, le filet du site a un rouge qui n'est pas d'elle :
`test_rien_n_echappe_au_catalogue` trouve sur la page Carrières types « Un
coefficient inférieur à un est un manque », la branche que l'étape 7 a quittée
(b4fa4e6, l'ex-invalide de la Cnav, qui repasse 2070 au-dessus de un) en
récrivant l'affirmation ; les agrégats et les témoins que GitHub refait n'ont
pas encore suivi. La prochaine course de GitHub doit le lever ; sinon, c'est à
l'étape 7.

**Ce qui reste.**

1. Le contrôle des autres régimes : l'indépendant, dont l'assiette minimale et
   les cotisations payées font aussi les trimestres ; le libéral ; l'exploitant
   agricole. Et l'outre-mer : la saisie d'un relevé ne porte pas le
   département (R. 753-21), et le contrôle, comme le calcul, compte au seuil de
   la métropole.
2. Ce que les trimestres manquants changeraient, rétablis : le départ au taux
   plein et la pension, que le dépliant ne chiffre pas.
3. Les restes de la note du 16 octobre, dans l'ordre, une session par point :
   l'indice majoré, le solveur inverse ; puis, s'il le faut, le dépliant des
   âges de départ.

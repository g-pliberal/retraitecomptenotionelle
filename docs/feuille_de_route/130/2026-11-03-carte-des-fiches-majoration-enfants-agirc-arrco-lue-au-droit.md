# La carte des fiches : la majoration pour enfants de l'Agirc-Arrco lue au droit, huitième lot

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la
file E un nouveau lot de la carte (action 130), hors des zones des autres
files et de ce qui est déjà lu, l'Agirc-Arrco par exemple. Deux fiches de
l'Agirc-Arrco n'étaient pas mûres : `majoration_enfants_agirc_arrco` et
`coefficients_anticipation_agirc_arrco`. Le lot pris : la première ; la
seconde est un lot à elle seule (plus bas). Aucun chiffre du modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés, à jour de l'incrément du 2 novembre, et du 3 pour le JORF ;
  `textes.py --inscrire`, aucune rédaction nouvelle.
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de ses six manques ; un fichier neuf,
  `tests/test_agirc_arrco_au_droit.py`, vu rouge faute de versions. Chaque
  paramètre d'une version porte le nom de ce qui le porte au dépôt : le
  barème, la colonne `bareme` de `legislation/majoration_enfants_points.csv`,
  lue sur chaque année d'acquisition que la version couvre, avant sa date
  d'effet ; le plafond, les champs des périodes de chaque régime, lus aux
  années de liquidation ; la génération du plafond, ce que le portage en
  tranche (`completer.js`). Trois tests refont les chiffres publiés sur les
  données du dépôt : le plafond au 1er novembre 2016 du guide n° 9 de la
  caisse, 1 028,12 € à l'Agirc et 1 031,15 € à l'Arrco ; celui du régime
  unifié, cumul des deux plafonds de 2018, 2 071,58 €, que les 2 367,48 € de
  2025 revalorisent ; les deux exemples du même guide, 338,11 € à l'Arrco,
  1 305,60 € ramenés au plafond à l'Agirc. Une valeur altérée, un taux ou le
  plafond, fait rougir la fiche.
- **Les textes**, hors du Journal officiel, dans les copies de la caisse :
  l'accord Arrco du 25 avril 1996, articles 1er, 2 et 11 ; l'accord du 18 mars
  2011, articles 7 et 8 ; l'article 17 de l'annexe A de l'accord de 1961 et
  l'article 6 bis de l'annexe I de la convention de 1947, dans leur rédaction
  de 2012 ; l'article 94 de l'accord du 17 novembre 2017, relu, et l'arrêté
  du 24 avril 2018 qui l'étend ; le guide des salariés n° 9, « Majorations
  pour enfants », de mars 2017.
- **`majoration_enfants_agirc_arrco`**, du domaine des enfants et de l'étape
  qui complète, approchée, de conforme : neuf versions, sur deux dates. La
  date d'effet choisit l'accord et son plafond — avant 1999, les règlements
  des caisses de l'Arrco, supposés ; de 1999 à 2011, le régime unique de
  l'accord de 1996, sans plafond ; de 2012 à 2018, l'accord de 2011, 1 000 €
  par régime au 1er janvier 2012, revalorisés comme le point de chacun ;
  depuis 2019, l'article 94, le cumul des deux. L'année d'acquisition choisit
  le taux : les points de l'Arrco d'avant 1999, au règlement de leur caisse ;
  ceux de 1999 à 2011, 5 % ; ceux de l'Agirc d'avant 2012, 8 à 24 % ; tous
  depuis 2012, 10 %. La question ouverte le 16 octobre, le plafond des
  générations d'avant le 2 août 1951, est tranchée : les annexes de 2012 et
  l'article 94 l'écrivent.
- **Le cliquet des textes** ne bouge pas, 9 389 : la fiche ne cite aucune
  rédaction de LEGI. **La carte** passe de 89 fiches à lire au droit à 88, de
  527 manques à 521. `conservation.py --depuis HEAD` dit changée la ligne de
  veille de la fiche, refaite depuis elle, ce que la référence figée admet.

## Ce que l'étape laisse

- **Cinq écarts du modèle, déclarés** (la file E ne touche pas au modèle) :
  - l'assiette : le modèle calcule la majoration sur l'allocation,
    coefficient d'anticipation compris, quand la caisse la calcule sans lui
    depuis 2019 (circulaire n° 2020-02-DRJ), et l'Arrco déjà de 2012 à 2018
    (guide n° 9) ; la majoration de qui part avant l'âge du taux plein est
    sous-estimée de la part que le coefficient retire, 1 à 22 % sur vingt
    trimestres ;
  - les caisses de l'Arrco d'avant 1999, présumées toutes au barème de
    l'accord : dans l'exemple du guide, 2 000 points d'une caisse qui ne
    majorait pas en prennent 250,26 € de trop, pour 338,11 € dus ;
  - la génération du plafond, 1952 au modèle pour le 2 août 1951 ;
  - le plafond revalorisé d'un coup, quand la caisse l'arrondit d'année en
    année : un centime ;
  - les conditions des droits d'avant 1999, remplies au 31 décembre 1998
    selon l'accord de 1996, que le modèle apprécie à la date d'effet.
- **Deux lectures divergentes** : la proratisation du plafond de 2012 à 2018,
  que l'accord de 2011 écrit et que ni les annexes, ni le guide, ni le modèle
  ne font ; la date des conditions des droits d'avant 2012, le 31 décembre
  2011 selon l'accord, la date d'effet selon les annexes.
- **L'AGFF des cultes**, que le lot précédent signalait : elle manque à
  `data/reference/legislation/contributions_equilibre_agirc_arrco.yaml`, dans
  la liste `regimes` de la contribution `agff` (2001 à 2018), qui nomme
  l'Arrco, ses deux tranches et l'Agirc, mais pas `arrco_cultes` ; la file E
  n'y touche pas. Aucun effet sur la pension.
- **`coefficients_anticipation_agirc_arrco`**, l'autre fiche de l'Agirc-Arrco,
  reste à lire : le moteur lit ses versions (`FichesDatees`, que le paquet du
  site porte), et sept entrées de ses `textes_a_rattacher` attendent d'y
  être coupées, des accords de 1996 et de la structure financière à l'avenant
  n° 15 de 2023 de l'accord de 2017 ; couper ses versions refait le paquet.
  Un lot à lui seul, le prochain de la file E.
- **À relire** : les règlements des caisses de l'Arrco d'avant 1999, et les
  rédactions d'avant 2012 de l'article 6 bis de l'annexe I et de l'article 17
  de l'annexe A, que la copie du Medef ne sert plus ; inscrire au registre
  des exemples officiels ceux de la caisse, Justine et les deux du guide ;
  la circulaire du 7 juillet 2011, non retrouvée.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Une question : ouvrir une étape du modèle pour calculer la majoration pour
enfants de l'Agirc-Arrco sans le coefficient d'anticipation, comme la caisse
depuis 2019 ? Avis : oui, sans urgence ; elle ne touche que les parents de
trois enfants partis avant l'âge du taux plein, de un à vingt-deux pour cent
de leur majoration. Pour le reste, rien de neuf : les questions des notes
précédentes attendent toujours.

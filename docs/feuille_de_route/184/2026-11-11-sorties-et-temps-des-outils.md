# Les outils de lecture, allégés et accélérés ; ce qui attend le propriétaire

Faite le 11 novembre 2026, à la demande du propriétaire : « Que peut-on faire
pour améliorer l'efficacité de notre travail sur ce projet ? On peut mieux
lire les bases de données de droit ? », puis « on améliore quoi alors ? ».
La session a d'abord mesuré ce que coûtent les outils de l'action, sur `main`
et sur l'index LEGI récupéré puis mis à jour jusqu'à l'incrément du
11 novembre. Elle a retouché les trois outils qui ne demandaient aucune
décision, et laisse au propriétaire celles qui lui reviennent. Aucune règle
du scénario 1 n'est touchée.

**Ce qui est fait.**

- *La veille tient en une ligne une fiche à relire pour une rédaction non
  lue.* Depuis l'étape 2, `scripts/veille_droit.py` imprimait, pour chaque
  fiche à relire, toutes ses questions ouvertes (`sources.a_relire`), qui ne
  disent rien de la rédaction. La fonction `a_relire` du script ne les redit
  plus que pour une fiche à relire pour autre chose : à vérifier, manquante,
  lue il y a trop longtemps, date de relecture passée. Le 11 novembre, 56
  fiches sur 59 n'étaient là que pour une rédaction : la sortie de
  `--sans-cnav` passe de 86 126 octets à 12 710. Test :
  `tests/test_carte.py`.
- *Le détail d'une fiche montre ses rédactions en vigueur ou à venir, et
  compte les passées.* `python scripts/textes.py --non-lues <fiche>`
  imprimait toute l'histoire, avec le mot à mot de chaque rédaction :
  211 846 octets pour `csg_des_pensions_selon_le_revenu`, 168 919 pour
  `retraite_progressive`, dont une seule rédaction est en vigueur. Les
  rédactions passées se montrent désormais par `--toutes`. Pour les 56 fiches
  que la veille signale, la somme des sorties passe de 1 141 548 octets à
  182 280. Test : `tests/test_textes.py`.
- *Un index SQL mène à l'article de LEGI.* `selection()` et `mot_a_mot()` de
  `scripts/textes.py` cherchent par le titre du texte et le numéro dans la
  table `doc`, qui n'avait d'index SQL que sur l'identifiant : un parcours des
  328 000 lignes par texte cité. La sélection de `--inscrire`, rejouée à
  blanc, dépassait 280 secondes ; elle en prend une. L'index SQL
  (`ARTICLES_DE_LEGI`, dans `scripts/fetch/dila_index.py`) naît à la
  construction, à `--recuperer` ou à `--mettre-a-jour` : 1,7 seconde, 52 Mo de
  plus sur 1,58 Go. La release n'a pas à être refaite, ni le workflow touché ;
  l'index du JORF, qui ne se lit que par requête ou par identifiant, s'en
  passe. Test : `tests/test_dila_index.py`.

**Ce que la mesure a trouvé d'autre, et qui attend une décision du
propriétaire.**

1. *L'inscription des rédactions n'a pas tourné depuis le 3 novembre.*
   `data/reference/textes/inscription.yaml` date du 3 novembre, alors que des
   fiches ont été écrites depuis. Rejouée à blanc le 11 novembre, elle
   apporterait 1 942 rédactions « à examiner », dont 394 en vigueur ou à
   venir. 1 834 viennent de 52 textes nouveaux à la liste, qu'une fiche cite
   et qui entrent en entier (`perimetre.yaml`) : 23 par la fiche
   `cotisation_vieillesse_agricole_avant_2003`, née le 3 novembre au soir.
   Quatre textes généraux de la fonction publique en font 856 : les lois
   n° 84-16 (126), n° 84-53 (286) et n° 86-33 (158), et le décret n° 85-1148
   (286). Deux questions : un statut général entre-t-il en entier dans une
   liste de contrôle des retraites, ou par ses seuls articles cités ? et qui
   lance l'inscription — une session quand elle y pense, ou GitHub, chaque
   lundi, dans le workflow `index-dila.yml` qui met déjà l'index à jour (une
   garde : accord du propriétaire, ligne `Garde-modifiée`) ? **Ne pas lancer
   `textes.py --inscrire` pour de bon avant la réponse à la première.**
2. *La lecture des rédactions en vigueur n'avance pas.* Le 3 novembre, 57
   fiches et 94 rédactions en vigueur ou à venir non lues ; le 11, 56 fiches
   et 92 rédactions. Trois seulement ont le texte de leur précédente ; les 89
   autres font 120 186 octets de mot à mot. Au moins 33 ont pris effet depuis
   décembre 2025 ou prendront effet en 2027. La décision du 3 novembre confie
   cette lecture aux sessions de chaque zone, par la veille : une passe
   dédiée, zone par zone, la mènerait à son terme.
3. *La base KALI de la DILA n'est pas dans l'index.* Les conventions
   collectives, au format de LEGI : un dump global de 184 Mo, des incréments
   quotidiens (`echanges.dila.gouv.fr/OPENDATA/KALI/`). Lu en flux le
   11 novembre, il porte des textes titrés « Régime AGIRC-ARRCO de retraite
   complémentaire » et ses avenants n° 1 et n° 2, que `perimetre.yaml` dit ne
   pas tenir faute d'index ; pas la convention du 14 mars 1947 (déjà relevé
   par la note `138/2026-10-13-etape-16-coefficients-de-1947.md`). La note
   `153/2026-10-16-etape-2-points-enfants-arrco.md` dit l'accord du 18 mars
   2011 « à KALI, que la session n'a pas lu ».

**Ce qui est écarté, mesure faite.**

- *Un compte PISTE comme priorité.* Les serveurs de PISTE répondent depuis la
  session, seul le compte manque ; mais l'API sert les fonds que les dumps
  donnent déjà. Ce que les fiches disent ne pas trouver dans l'index (environ
  150 mentions, relevées par mots-clés) : des règlements de caisses, des
  textes anciens dont la base n'a que la notice ou le dispositif, des
  arrêtés ; une seule nomme un texte hors du champ social. Non vérifié : si
  l'API sert les fac-similés du Journal officiel.
- *Le réglage réseau de la session.* Légifrance et Gallica opposent un défi
  Cloudflare, l'Urssaf coupe la connexion après l'ouverture du tunnel : les
  sites refusent, non le relais.
- *La NOTA à part, seule.* 49 des 89 mots à mot en vigueur s'ouvrent sur une
  note d'application ; la séparer reconstruit l'index, et se fera avec l'étape
  3 si elle se mène.

**Comment refaire les mesures.** La veille : `python scripts/veille_droit.py
--sans-cnav | wc -c`. Le détail : `python scripts/textes.py --non-lues
<fiche> | wc -c`, avec et sans `--toutes`. L'inscription à blanc :
`selection()` de `scripts/textes.py` sur l'index ouvert en lecture, comparée
aux identifiants de `redactions.csv`, sans rien écrire.

# Le taux et la limite de la surcote des régimes spéciaux

**La demande.** Dans la nuit du 2 au 3 novembre 2026, le propriétaire fait mener
la correction que la note `130/2026-11-02-duree-des-agents-sncf-et-ratp-qui-partent-tot.md`
laissait hors de son étape : la surcote de la SNCF à 0,75 % par trimestre de
2009 à 2017, quand la RATP, sous la même phrase, sert 1,25 % ; et la limite de
vingt trimestres, que `trimestres_de_surcote_regimes_speciaux` ne portait pas.
La session d'orchestration la confie à la file G.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF récupérés,
  à jour de l'incrément du 2 novembre 2026 (aucun depuis). Lues, rédaction par
  rédaction, depuis le 1er juillet 2008 : l'article 13 du décret n° 2008-639
  (SNCF), l'article 24 du décret n° 2008-637 (RATP), l'article 10 de l'annexe 3
  du statut des IEG, l'article 85-1 du décret n° 90-1215 (CRPCEN), l'article 12
  du décret n° 68-960 (Comédie-Française), l'article 14 du décret n° 68-382
  (Opéra) ; L. 14 du code des pensions civiles et militaires, de 2004 à 2023 ;
  au Journal officiel, l'article 89 de la loi n° 2008-1330.
- **Ce que le texte établit.** Les six décrets écrivent : « Le taux du
  coefficient de majoration est égal, par trimestre supplémentaire dans la
  limite de vingt trimestres, à celui prévu pour les fonctionnaires de l'Etat en
  application du III de l'article L. 14 ». Ce taux est de 0,75 % jusqu'au
  18 décembre 2008, puis de 1,25 % ; mais la loi n° 2008-1330 (article 89, III)
  ne l'applique qu'« aux trimestres d'assurance cotisés et effectués à compter
  du 1er janvier 2009 » : les deux trimestres du second semestre de 2008 gardent
  0,75 %. La limite tombe le 19 septembre 2011 à la CRPCEN, le 23 septembre 2011
  à la Comédie-Française, le 1er janvier 2017 à la SNCF, à la RATP, aux IEG et à
  l'Opéra. Le 0,75 % de la SNCF était donc faux pour tout trimestre de 2009 et
  après, et le 1,25 % des cinq autres pour les trimestres de 2008 : la même
  règle, la classe et non le cas.
- **Le test d'abord** : `tests/test_surcote_regimes_speciaux.py`, huit cas
  posés à la main depuis ces textes, que le portage calcule et que son jumeau
  refait au bit près (`droit_et_refait`) — la SNCF en 2016, 2013 et 2009, la
  RATP en 2009 et 2016, la CRPCEN en 2009, l'Opéra en 2016, la
  Comédie-Française en 2016. Vus rouges, six : la SNCF à 0,75 % (1,15 au lieu
  de 1,25 et de 1,24), les trimestres de 2008 à 1,25 % (1,025 au lieu de 1,015),
  l'Opéra sans limite (vingt-six trimestres au lieu de vingt).
- **Le code**, dans le portage puis son jumeau :
  `coefficientSurcoteRegimesSpeciaux` (`moteur/js/droit/liquider.js`) et
  `coefficient_surcote_regimes_speciaux` (`droit/liquider.py`). Les trimestres
  de surcote, les derniers de la carrière, prennent le taux de la période s'ils
  sont de 2009 ou après, et, s'ils sont de 2008, celui que le barème
  `fonction_publique` de `legislation/surcote_baremes.csv` donne à leur date,
  0,75 % ; au plus `surcote_trimestres_maximum`, ceux de 2009 d'abord.
- **La donnée.** `regimes/sncf.yaml` : la période de 2009 à 2017 devient celle
  de 2009 à 2016, à 1,25 % et vingt trimestres au plus, et une période de 2017,
  à 1,25 % sans limite. La limite de vingt trimestres sur les périodes de 2009
  à 2016 de `regimes/ratp.yaml` et `regimes/ieg.yaml`, et sur celles de 2009 à
  2013 et de 2014 à 2016 de `regimes/opera_de_paris.yaml`, coupée de 2017. Rien
  à la CRPCEN ni à la Comédie-Française : leur limite tombe en septembre 2011,
  quand nul n'a pu compter vingt trimestres depuis juillet 2008.
- **Ce que les témoins déplacent** : quatre témoins, l'agent de la RATP, le
  clerc de notaire, le sociétaire et l'agent de l'Opéra nés en 1945, partis à
  soixante-quatre ans en 2009 : leurs deux seuls trimestres de surcote, de 2008, passent
  de 1,25 % à 0,75 %, le taux de 76,875 % à 76,125 %, la pension de 0,98 %. Deux
  témoins neufs (`scripts/construire_temoins.py`) : `sncf_surcote_de_2016`,
  l'agent de conduite né en 1951 parti à sa limite d'âge, dix-neuf trimestres
  de surcote à 1,25 %, un taux de 92,813 % et non de 85,688 % ; et
  `opera_limite_de_la_surcote`, né en 1950, parti à soixante-six ans, que la
  limite arrête à vingt trimestres, 93,750 %. Les autres témoins qui bougent
  depuis `HEAD` (Nouvelle-Calédonie, Wallis-et-Futuna, la réversion du clerc,
  les deux témoins de la CRPCEN et de la Comédie-Française lus à soixante ans)
  viennent d'autres sessions, dont GitHub n'avait pas encore refait les
  témoins.
- **La limite ne joue, parmi les témoins et les cas du test, qu'à l'Opéra** :
  à la SNCF et à la RATP, la limite d'âge de soixante-cinq ans arrête la
  surcote, comptée depuis soixante ans et depuis juillet 2008, à vingt
  trimestres au plus. Elle est portée pour le texte ; aux IEG, elle peut jouer
  selon l'âge d'où la surcote se compte, que la fiche laisse à relire.
- **Les fiches.** `surcote_regimes_speciaux` : l'intitulé dit le taux et la
  limite, deux lectures datées du 3 novembre, une question de plus à relire,
  le code ; elle reste `transcrite`. `age_surcote_sncf_ratp` : la question du
  taux, résolue, quitte ses `a_relire`.

## Ce que l'étape laisse

- **Les deux trimestres de 2008 sont lus par renvoi** : aucune caisse ne
  l'écrit dans ce que le dépôt a lu, et la circulaire de la CNIEG n° 2021-04,
  « La surcote », que les moteurs de recherche indexent, répond 404. À
  confirmer auprès de la CPRPSNCF ou de la CNIEG ; un écart d'au plus 1 % de
  pension, pour les agents nés avant juillet 1948.
- **La même limite chez le fonctionnaire, hors de cette étape** : L. 14, III,
  garde « dans la limite de vingt trimestres » jusqu'au 10 novembre 2010, quand
  le barème `fonction_publique` ne limite que les trimestres de 2004 à 2008.
  Un fonctionnaire parti en 2009 ou 2010 avec plus de vingt trimestres de
  surcote — que seul un recul de sa limite d'âge permet — en recevrait trop.
  À vérifier, par la session qui tient la fonction publique.
- **Le second semestre de 2008** reste sans surcote, liquidé sous la période
  d'avant la réforme (fiche `age_surcote_sncf_ratp`, approximation déclarée).

## Ce qui attend le propriétaire

Rien pour cette étape.

# Les écarts de R-E11 repris, et la Cipav de `surcote_par_age_seul` relue au Journal officiel (E11)

Action 130, file E, vague 11, le 6 novembre 2026, sur Opus. E11 reprend les quatre
écarts de R-E11 (`2026-11-06-relecture-r-e11.md`, « Ce qui repart en « -bis » »), puis
commence la lecture au droit de `surcote_par_age_seul` par la Cipav. Elle s'arrête là, à
un point propre : les six autres régimes de la fiche restent à lire (bloc « Reprise »).
Aucune erreur n'est corrigée ; aucun taux, aucune valeur servie ne change ; le paquet
(`moteur/donnees.json`), reconstruit, est inchangé.

**Sources ouvertes pendant la session.** Les index de la DILA, JORF à jour du 6 novembre
2026 et LEGI du 5 novembre, par `dila_cherche.py` ; les « Statuts Cipav au 01/01/2023 »
publiés par la caisse
(`https://www.lacipav.fr/sites/default/files/2023-04/Statuts%20CIPAV_1janvier2023.pdf`,
téléchargés et lus le 6 novembre 2026, SHA-256
e5034d618178585fdae444ec690247ef83c7e94d7e9ca741682fb98562093790, le même fichier que
R-E11). Les montants : le moteur Python du dépôt (`pont.carrieres_des_saisies`, puis
`Simulateur.simuler`), un espion posé sur `acquerir` pendant l'essai qui relève
`Droits.cotisations` de `cipav_complementaire`, année par année (deux entrées par an,
sommées), sans rien écrire au dépôt ; la pension servie par le pont du portage
(`pont.scenario_actuel`), identique. Réglages de R-E11 : `profil` plat, `euros` 2026,
`enfants` 0, `sexe` F, `salaire` 2, `debut` 22, `statut` `profession_liberale`, les
autres ceux de `tests/test_complementaires_liberales_a_leur_age.py`.

## (b) La Cipav, du 1er janvier 2023 au 30 juin 2026 : l'erreur déclarée

**Les textes, relus.** Statuts au 1er janvier 2023, article 3.15, ses quatre alinéas :
« L'adhérent qui a atteint l'âge prévu au deuxième alinéa du 1° de l'article 3.13 et
comptant un minimum de trente années d'affiliation à la C•I•P•A•V, peut différer la date
d'entrée en jouissance de la pension de retraite complémentaire de 1 à 5 ans. » ; « Le
compte de points qui est alors établi est majoré de 5% par année entière de
prorogation. » ; « Cette majoration s'applique uniquement aux points acquis au titre des
trente premières années de cotisation à la C•I•P•A•V. » ; « Pour la détermination des
trente années de cotisation, les années au titre desquelles l'adhérent a obtenu une
exonération ou une réduction de cotisation sont prises en compte. » L'article 3.13, 1° :
« A taux plein : - à partir de l'âge du taux plein prévu au 1° de l'article L. 351-8 du
code de la sécurité sociale ».

Arrêté du 20 mars 2023 (JORFARTI000047334800), 17° : « L'article 3.15 est ainsi modifié :
a) Au dernier alinéa, les mots : « , telles qu'elles sont définies à l'article 3.6 » sont
supprimés ; b) L'article est complété par un alinéa ainsi rédigé : « Pour la
détermination des trente années de cotisation, les années au titre desquelles l'adhérent
a obtenu une exonération ou une réduction de cotisation sont prises en compte. » » ;
article 2 (JORFARTI000047334796) : « L'annexe au présent arrêté est applicable aux
cotisations et aux prestations dues au titre des périodes courant à compter du
1er janvier 2023. » Arrêté du 16 décembre 2021 (JORFARTI000044554134), 19° : « Au premier
alinéa de l'article 3.15, les mots : « âgé de 65 ans » sont remplacés par les mots :
« qui a atteint l'âge prévu au deuxième alinéa du 1° de l'article 3.13, » » ; article 2
(JORFARTI000044554130) : « […] entrent en vigueur le 1er janvier 2022. » Depuis 2023,
l'arrêté du 27 décembre 2023 (JORFARTI000048880676) nomme les articles 3.6, 3.13, 3.14,
3.16 et 3.19, non 3.15 ; celui du 4 septembre 2025 (JORFARTI000052200390) les statuts
généraux, et celui du 17 septembre 2025 le rectifie (JORFARTI000052263541).

**Le cas de R-E11, refait.** Née le 10 mars 1957, cotisante depuis le 10 mars 1979,
pension au 1er janvier 2026 (68 ans et 9 mois ; 67 ans le 10 mars 2024 : un an entier de
report). Servis : 22 677,41 € (« cotisations revalorisées 354,058 € × rendement 6.10% ×
coefficient de majoration 1.0500 »). Relevés : 1979, 1 595,1659 € ; 2009, 9 123,4904 € ;
47 années, 354 057,8613 € ; de 1979 à 2008, 168 552,9726 €.

À la main. 0,05 × 0,061 = 0,00305. Servie : 354 057,8613 × 0,003 = 1 062,1736 ;
× 0,00005 = 17,7029 ; **1 079,8765 €** ; contrôle, 354 057,8613 × 0,061 × 1,05 =
354 057,8613 × 0,06405 = 22 677,4060. De 1979 à 2008 : 168 552,9726 × 0,003 = 505,6589 ;
× 0,00005 = 8,4276 ; 514,0866 ; 1 079,8765 − 514,0866 = **565,79 €** par an de trop. De
1979 à 2009 : 168 552,9726 + 9 123,4904 = 177 676,4630 (177 676,4629 à la somme des
valeurs non arrondies) ; × 0,003 = 533,0294 ; × 0,00005 = 8,8838 ; 541,9132 ;
1 079,8765 − 541,9132 = **537,96 €**. De 1980 à 2009 : 177 676,4629 − 1 595,1659 =
176 081,2970 ; × 0,003 = 528,2439 ; × 0,00005 = 8,8041 ; 537,0480 ;
1 079,8765 − 537,0480 = **542,83 €**. Les trois montants de R-E11 tiennent au centime.
L'erreur, au moins 537,96 € par an, est déclarée dans `decret_2026_418_liberaux`
(`sources.a_relire`, l'article de E9, récrit), là où E9 et E10 l'avaient déclarée, et
le bloc « Reprise ».

## Avant 2023 : l'article 3.15 relu par différence, et deux erreurs neuves

R-E11 laissait « la date d'avant 2023 » au Bulletin officiel. E11 a relevé, dans l'index
JORF, tous les arrêtés qui approuvent des modifications des statuts de la Cipav de 2006
à 2025 (titres qui portent « architectes », « CIPAV » ou « interprofessionnelle de
prévoyance »). Seul l'arrêté du 3 octobre 2006 (JORFARTI000002050100) renvoie au
Bulletin officiel : « L'arrêté, accompagné de son annexe, sera publié intégralement au
Bulletin officiel d'octobre 2006 » ; il approuve la « troisième partie « Régime de
retraite complémentaire » » et abroge les statuts de 1979 « à compter du 1er janvier
2007 ». Tous les suivants sont publiés en entier : 17 décembre 2007, 3 décembre 2010,
6 juillet 2012, 7 octobre 2014, 18 décembre 2015, 19 janvier 2016, 3 août 2017, 22 juin
2020, 16 mars 2021, 16 décembre 2021, 20 mars 2023, 27 décembre 2023, 4 et 17 septembre
2025 (identifiants dans la fiche). Cherchés dans leur texte, « 3.13 » à « 3.16 »,
« trente », « prorogation », « différ », « renum », « devien » : seuls ceux du 16
décembre 2021 et du 20 mars 2023 nomment l'article 3.15 ; celui de 2017 renumérote la
deuxième partie (« L'article 2.14 devient l'article 2.13 », etc.), non la troisième.

L'article 3.15 du 1er janvier 2007 au 31 décembre 2021 est donc celui de 2023, ces deux
modifications ôtées : le premier alinéa avec « âgé de 65 ans », le deuxième tel quel, le
dernier avec les mots « , telles qu'elles sont définies à l'article 3.6 », à une place
que l'arrêté de 2023 ne montre pas. La restriction aux points des trente premières années
tient donc depuis 2007 ; la lecture contraire supposerait un arrêté que le Journal
officiel n'a pas publié, ce que rien n'indique. Ce qui reste ouvert : le décompte des
trente années avant 2023, renvoyé à l'article 3.6, dont aucune rédaction d'alors n'est
lue (les arrêtés de 2015, de mars et de décembre 2021 en retouchent des alinéas ; celui de
2023 en supprime les trois derniers). Les montants ci-dessous valent sous les trois
décomptes de la première année ; un autre décompte de l'article 3.6 pourrait les
déplacer. Le Guide pratique 2019 de la caisse, cité par la fiche, l'écrit déjà
(« appliquée sur les points acquis au titre des 30 premières années de cotisations »).

**(1) De 2013 à 2022, le modèle majore tous les points.** Née le 10 mars 1949, même
carrière, pension au 1er janvier 2016 (66 ans et 9 mois ; 65 ans le 10 mars 2014 : un an
entier). Servis : 12 625,51 € (« cotisations revalorisées 193,940 € × rendement 6.20% ×
coefficient de majoration 1.0500 »). Relevés : de 1979, première année du régime
(1 558,2124 €), à 2015, 37 années, 193 940,3125 € ; de 1979 à 2008, 137 466,6071 € ; de
1980 à 2009, 143 335,1748 € ; de 1979 à 2009, 144 893,3872 €. À la main : 0,05 × 0,062 =
0,0031 ; 193 940,3125 × 0,003 = 581,8209 ; × 0,0001 = 19,3940 ; **601,2150 €** servis
(contrôle : 193 940,3125 × 0,0651 = 12 625,5143) ; 137 466,6071 × 0,0031 = 412,3998 +
13,7467 = 426,1465, **175,07 €** de trop ; 143 335,1748 × 0,0031 = 430,0055 + 14,3335 =
444,3390, **156,88 €** ; 144 893,3872 × 0,0031 = 434,6802 + 14,4893 = 449,1695,
**152,05 €**. Au moins 152,05 € par an.

**(2) De 2007 à 2012, le modèle ne majore rien.** Ses périodes de 1979 à 2012
(`cipav_complementaire.yaml`) portent `surcote_par_trimestre: null` ; la majoration
n'est servie que depuis 2013, « borne de période, et rien avant » (notes du régime).
Née le 10 mars 1945, même carrière, pension au 1er janvier 2012 (66 ans et 9 mois ; 65
ans le 10 mars 2010 : un an entier ; trente années d'affiliation, depuis 1967). Servis :
9 791,17 € (« cotisations revalorisées 157,922 € × rendement 6.20% », sans
coefficient). Relevés : de 1979 (1 533,6360 €) à 2011, 157 922,1741 € ; de 1979 à 2008,
135 298,4577 € ; de 1980 à 2009, 141 074,4652 € ; de 1979 à 2009, 142 608,1012 €. À la
main : 157 922,1741 × 0,062 = 9 791,1748 ; le texte ajoute 0,0031 fois les trente
premières années : 135 298,4577 × 0,003 = 405,8954 ; × 0,0001 = 13,5298 ;
**419,43 €** ; 141 074,4652 × 0,0031 = 423,2234 + 14,1074 = **437,33 €** ;
142 608,1012 × 0,0031 = 427,8243 + 14,2608 = **442,09 €**. Au moins 419,43 € par an servis
en moins.

Les deux erreurs sont déclarées, non corrigées, dans `surcote_par_age_seul`
(`sources.a_relire`, l'article de la Cipav, récrit ; deux lectures ajoutées) ; son
`effet` ne dit plus l'article 3.15 de 2006 à lire au Bulletin officiel. Avant 2007, les
statuts de 1979 restent au seul Bulletin officiel (question 22). Les `versions` de la
fiche ne sont pas encore écrites : la règle de la Cipav y prendra quatre versions (2007,
2022, 2023, 1er juillet 2026), et la période d'avant 2007, non tranchée.

## Le test du décret : la table article, texte, fiches

`test_chaque_article_du_decret_2026_418_est_rapporte_a_la_fiche_de_sa_regle` tient
désormais ce que son nom dit : `ARTICLES_DU_DECRET_2026_418` donne, pour chacun des 32
documents, le texte qu'il modifie (le visa relu par R-E11 ; D. 641-6 pour l'article 1er ;
rien pour 29 à 31) et les fiches auxquelles la fiche du décret le rapporte ; le test
compare, article par article, le premier texte que la lecture nomme après l'identifiant
et l'ensemble des fiches qu'elle nomme. Éprouvé hors du dépôt, la fiche ou la table
altérées en mémoire : la table qui renvoie l'article 5 à `carpv_minoration_age_seul`,
rouge ; la fiche qui le fait, rouge ; un nom de fiche remplacé par `assiette`, rouge ;
l'article 4 rapporté au décret n° 49-579, rouge ; l'article 10 ôté, rouge ; la fiche
juste, verte. R-E11 avait trouvé verts les deux premiers cas de la fiche.

## La CARMF : les deux facultés nommées

Les deux erreurs de E10 nomment désormais ce que la correction devra dire. Article 4-2, I
(LEGIARTI000054168114, en vigueur le 1er juillet 2026) : « un point par trimestre
d'exercice en qualité de non salarié, antérieur au 1 er juillet 1949 ou trimestre
assimilé dans les conditions prévues à l'article 4-4 ou trimestres ayant donné lieu à
dispense dans les conditions prévues au I de l'article 4 » peut être racheté. Article 4-3
(LEGIARTI000054168112) : « Tout médecin qui continue d'exercer en qualité de non salarié
et qui n'est plus tenu de cotiser à titre obligatoire, à partir du premier jour du
semestre civil qui suit son soixante-quinzième anniversaire, peut continuer à cotiser
volontairement, quel que soit son âge. » Deux facultés, sur demande ; le modèle simule le
médecin qui ne rachète pas et l'assuré obligatoire : les erreurs tiennent.

## La question 22 : les décrets d'avant le 1er juillet 2026

Écrite dans `decret_2026_418_liberaux` (`sources.a_relire`, un article neuf, et une
lecture). Décret n° 49-579, article 4, du 27 août 1996 au 30 décembre 2024
(LEGIARTI000006781644) et jusqu'au 1er juillet 2026 (LEGIARTI000050865157) : « Des
dispenses de cotisations peuvent être accordée aux adhérents impécunieux et aux
professionnels âgés de moins de quarante ans lors de leur affiliation, dans les
conditions prévues par les statuts mentionnés à l'article 5 du présent décret. » Décret
n° 50-28, article 2, du 14 novembre 2025 au 1er juillet 2026 (LEGIARTI000052567910) :
« Les statuts fixent les conditions dans lesquelles des exonérations, des dispenses, des
réductions ou des reports de cotisations peuvent être accordés dans les premières années
d'activité professionnelle, en cas d'insuffisance de revenus, d'incapacité d'exercice ou
de maternité. » ; du 24 septembre 1981 au 4 août 1982 (LEGIARTI000006760429) : « dans les
premières années d'activité professionnelle ou en cas d'infortune ou d'incapacité
d'exercice de la profession ». Le principe au décret, ses conditions aux statuts : la
question 22 en part. `docs/feuille_de_route/130/2026-11-03-decisions-du-proprietaire.md`
est un récit : E11 n'y récrit rien.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 98 verts ; sous `PRESOMPTIONS_DECALEES=1`, 97 verts et
un sauté. Aucun autre fichier de tests ne lit les deux fiches touchées. La suite rapide :
voir le message du commit.

## Ce qui reste

- `surcote_par_age_seul`, lue au droit : `lit`, `versions`, `dates_qui_decident` pour
  ses sept régimes ; la Cipav d'abord, sur ce qui précède ; puis la CARMF, l'ASV, la
  CARPIMKO, la CAVEC, la CAVP et la CPRN, dont la fiche porte déjà les lectures de
  septembre 2026, à relire à leur date.
- Au propriétaire : les deux erreurs neuves de la Cipav (2007 à 2012, 2013 à 2022) ; le
  décompte des trente années avant 2023 (article 3.6, non lu).
- Puis `cotisation_par_classes_liberales`.

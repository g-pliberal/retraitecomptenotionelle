# Étape 11 : la page dit la fin de l'emploi des autres régimes spéciaux

**Le 18 octobre 2026 : quand le départ saisi passe la limite d'âge, la note des départs dit
la fin de l'emploi dans les mots du statut de l'agent des industries électriques et
gazières, du personnel de l'Opéra, de l'agent de la SEITA et de celui de la Banque de France,
comme elle le disait du fonctionnaire, du contractuel, de l'ouvrier de l'État et du cheminot.
Le maintien présumé du mineur ne paraît toujours pas : où le dire revient au propriétaire.**

## Ce que fait la page

- **`FIN_A_LA_LIMITE`** (`moteur/js/pages.js`) nomme quatre fiches de plus, dans les mots de
  leur texte, que les notes des étapes 6, 8 et 9 relevaient : pour l'agent des IEG, « vous
  êtes mis en inactivité à 70 ans » (statut national, annexe, article 4, depuis 2008), et,
  sous la version `decret_de_1954` de sa fiche, « vous êtes admis d'office à la retraite à
  55 ans » (décret n° 54-50, article 2) ; pour le personnel de l'Opéra, « vos fonctions
  cessent à 67 ans » (décret n° 2008-240, article 2) ; pour l'agent de la SEITA,
  « obligatoirement retraité » (décret n° 62-766, article 111), « vous êtes mis à la
  retraite à 65 ans » ; pour celui de la Banque, « vous devez prendre votre retraite à
  67 ans » (statut du personnel, article 241). Chaque entrée reçoit la version de la limite,
  que seule celle des IEG lit.
- **Contrôlé** : `test_la_page_dit_la_fin_de_l_emploi_dans_les_mots_de_chaque_statut`
  (`tests/test_web_saisie.py`), vu rouge sur la phrase de repli, « votre emploi prend fin
  à » : l'agent des IEG né en 1975 et parti à soixante-quinze ans, et celui né en 1945 ;
  celui de l'Opéra né en 1975 ; celui de la SEITA né en 1940 ; celui de la Banque né en
  1960. Aucun témoin de page ne portait la phrase de repli, et aucun ne bouge ; aucune
  phrase en gras neuve.

## Au propriétaire : où la page dit le maintien du mineur

Le modèle présume le mineur maintenu dans l'intérêt du service jusqu'à son départ (étape 10,
choix 1) : sa radiation n'est jamais forcée, sa pension part de son départ, et la note des
départs, seule à dire les exceptions présumées, ne paraît pas. Le nommer, c'est faire parler
la page d'une limite que le départ passe sans que l'emploi prenne fin, ce qu'elle ne fait
pour personne, et qu'aucune note n'a décidé. Trois lectures :

1. **Le mineur seul**, dans une note neuve, quand son départ passe sa limite : « La limite
   d'âge de votre emploi est de 55 ans. Nous présumons que vous avez demandé et obtenu le
   maintien en activité dans l'intérêt du service, autant que votre départ le demande. »
2. **Tout agent qu'une exception présumée garde jusqu'à son départ**, dans la même note : le
   fonctionnaire né en 1975 et parti à soixante-neuf ans, présumé maintenu jusqu'à
   soixante-dix, n'en lit aujourd'hui rien non plus.
3. **Rien**, la présomption ne déplaçant pas la date de la pension.

## Un constat

Sur `main` (2a19325), sans cette étape, neuf tests de la suite rapide échouaient — la
CNAVPL de l'action 131, le cliquet des textes, des confrontations du portage —, et quatre de
`test_web.py` : le paquet et les témoins de pages à refaire, deux confrontations du portage.
Aucun ne tient au site ; GitHub les juge à l'envoi.

## Ce qui reste

- Au modèle et au propriétaire, ce que le bloc « Reprise » de l'action dit.
- La page dit au militaire que son grade n'est pas saisi, mais ne dit pas ce que la saisie
  ne porte pas des autres : la catégorie de l'agent de l'Opéra et de la SEITA, le niveau de
  celui de la Banque. À trancher avec la question ci-dessus.

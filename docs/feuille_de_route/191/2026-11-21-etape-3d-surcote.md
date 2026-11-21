# Étape 3 de la note 0009, quatrième session : la surcote lue dans les versions de sa fiche

**Reprise, au 21 novembre 2026.** La surcote du régime général se lit dans
les quatre versions de sa fiche : la date d'effet de la pension choisit la
rédaction de D. 351-1-4, la date de chaque trimestre son taux. Les lignes du
régime général ont quitté le barème daté ; l'âge des 1,25 % est un paramètre
de version ; l'âge légal de la surcote se lit à la date d'effet. Aucun
résultat ne bouge. L'étape 3 est finie : c'est le point d'arrêt de la note.
Le propriétaire décide de l'étape 4, les renvois des régimes, sur le compte
qui clôt cette note ; ne pas l'ouvrir avant.

Le 21 novembre 2026, la nuit, sur Opus 5.5, au choix du propriétaire, et non
sur Fable 5.2 que le dépôt règle pour le scénario 1 ; aucun point n'a demandé
de consulter Fable. Préparée sur les trois premières sessions de l'étape, les
deux dernières encore non publiées, et remise au coordinateur en correctif,
sans envoi sur `main`. Deux heures et demie environ ; un commit de code, un
de documentation ; le coût en jetons n'a pas été mesuré.

**Le texte**, lu dans l'index LEGI (à jour au 16 novembre 2026) et dans celui
du Journal officiel. D. 351-1-4 a cinq rédactions, la surcote quatre versions,
comme la note le disait :

| Version | Date d'effet | Taux, par date du trimestre | Texte |
|---|---|---|---|
| `sans_surcote` | avant 2004 | aucun | L. 351-1-2, « périodes accomplies à compter du 1er janvier 2004 » |
| `loi_de_2003` | 2004 à 2006 | 0,75 % | décret n° 2004-156 |
| `decret_de_2006` | 2007 et 2008 | depuis 2004 : 0,75 % les quatre premiers, 1 % ensuite, 1,25 % après 65 ans | décret n° 2006-1611, art. 1er et 3 |
| `lfss_2009` | depuis 2009 | les mêmes pour 2004-2008, 1,25 % depuis 2009 | décret n° 2008-1509, art. 5 |

Les rédactions de 2011 et de 2026 vont en `textes_sans_effet` : la première
remplace le soixantième anniversaire par l'âge légal, qui valait soixante ans
pour toute pension d'avant juillet 2011 ; la seconde ne change que la mention
de son application.

**La borne de 2009 est le 1er janvier, et non le 1er avril** que le brief
proposait. LEGI date la rédaction du 1er avril parce qu'il y fond l'article 6
du décret n° 2008-1509 (la surcote calculée avant la majoration de L. 351-12),
que son article 8 réserve aux pensions prenant effet depuis cette date.
L'article 5, qui porte le taux de 1,25 %, n'est pas différé : il vaut dès le
1er janvier 2009, la date de la réforme `lfss_2009_surcote`. Les deux coupes
donnent le même résultat, aucun trimestre de 2009 n'étant accompli avant le
31 mars ; celle du 1er janvier évite d'écrire la réforme comme « portée
ailleurs ». La version `loi_de_2003` commence de même au 1er janvier 2004,
date de L. 351-1-2, et non au 19 février, date du décret.

**Le moteur.** `SurcoteBaremes` (`moteur/js/regimes.js`) lit la fiche pour le
barème `regime_general` et garde le fichier pour la fonction publique et la
CNBF ; la ligne se choisit au rang du mois, et non plus à une année décimale.
`SURCOTE_AGE_MAJORE` est parti : `age_majore` est un paramètre des versions
de 2006 et de 2009, nul avant. `ouvrir.ageLegalALaDateDEffet` lit l'âge
légal de la surcote dans la version en vigueur à la date d'effet, et non dans
celle sous laquelle le droit de la personne s'est ouvert ; les deux ne
diffèrent sous aucun droit réel (les lois n'ont relevé l'âge que de
générations qui ne pouvaient pas encore partir), et un test le montre sur une
version fictive. La durée requise de la surcote se lisait déjà à la date
d'effet depuis la deuxième session. Les renvois ne sont pas écrits en
`contenu.renvois` : le contrôle des renvois exige qu'une version lue couvre
toute l'étendue de la version qui lit, ce que l'âge légal, coupé en sept
versions depuis 2009, ne fait pas ; la version le dit en prose.

**Tests.** `tests/test_surcote_versions.py` et
`tests/js/surcote-versions.test.js`, vus rouges : les quatre cas du brief
recomptés au texte (le troisième pris sur des trimestres d'avril 2005 à
janvier 2006, le premier trimestre de 2005 n'étant pas « après le
soixante-cinquième anniversaire » du né le 15 janvier 1940), l'exemple de la
circulaire Cnav 2004/37, point 41 (« 5 x 0,75 % = 0,0375 », le seul exemple
officiel de la version de 2004), le renvoi du né en 1955 parti en 2030
(62 ans). `tests/test_surcote_2004_2006.py` n'est pas touché, et passe.

**Ce qui bouge.** Aucune pension : les témoins de la liquidation et du droit
sont identiques. Cliquets abaissés : constantes du droit 167 → 166, sans fiche
104 → 103 ; couples réforme et fiche à classer 89 → 87 ; rédactions sans
statut 9 203 → 9 198.

**Pour le propriétaire, sans question bloquante.**

- La rédaction de 2004 réduit « au prorata » les trimestres de l'année du
  soixantième anniversaire quand cette année compte moins de quatre
  trimestres. La Cnav attendait encore, en juillet 2004, « des précisions de
  la Direction de la Sécurité sociale » (circulaire 2004/37, point 32) : la
  pratique de la caisse est inconnue, et le moteur compte ces trimestres comme
  dans les rédactions suivantes. Pensions de 2004 à 2006 seulement ; un
  trimestre de 0,75 % au plus. Noté en `a_relire`.
- La CNAVPL (R. 643-8) et la MSA des non-salariés (D. 732-42 du code rural)
  ont leur propre texte, que D. 351-1-4 ne régit pas : elles restent hors des
  versions, au taux plat de leur période. D. 732-42, rédaction de 2006, donne
  1 % « au-delà de cent soixante-quatre trimestres » aux nés avant 1949 partis
  avant 2009, une règle de rang qui n'est pas celle du régime général. Écart
  possible, non mesuré : c'est l'étape 4 ou une correction à part.
- L. 351-1-2 reste à couper : ses rédactions de 2010 et de 2011 changent le
  décompte des trimestres (bonifications exclues), non leur taux.

## Le compte de l'étape 3

| Session | Fiche | Commits | Fichiers | Durée |
|---|---|---|---|---|
| 3a | `age_annulation_decote` | 6, dont la réparation de la certification | 30 environ | deux heures, plus la réparation |
| 3b | `duree_requise_par_generation` | 2 | 32 | quatre heures |
| 3c | `carriere_longue` | 3 (dont les fichiers fabriqués) | 26, hors fabriqués | cinq heures |
| 3d | `surcote_regime_general` | 2 | une trentaine | deux heures et demie |

Quatre sessions, treize commits, quinze heures environ, toutes sur Opus 5.5
la nuit du 20 au 21 novembre ; aucune pension n'a bougé, sauf l'assuré né
avant 1930 corrigé au texte par 3a. Les cliquets de la note, du 20 novembre
(`da519c9`) à la fin de l'étape : constantes du droit à migrer 175 → 166 ;
sans fiche 104 → 103 ; couples réforme et fiche à classer 94 → 87 ;
rédactions sans statut 9 212 → 9 198 ; citées sans réponse 433 → 431.
Restent : 1 442 valeurs de repli, 306 renvois sans texte, 237 versions sans
leurs preuves, 153 versions lues sans trace — le terrain de l'étape 4, les
renvois des régimes (216 changements de renvoi selon la note).

**Point d'arrêt.** Le propriétaire décide de l'étape 4 et de son budget sur
ce compte. Deux questions de 3a l'attendent aussi (l'âge opposé, après le
1er septembre 2023, à l'assuré né avant 1955 ; le minimum du parent de trois
enfants resté dans le code).

# Étape 18, neuvième partie : les champs de saisie de la Lodeom et du conjoint collaborateur

**La demande.** La session des pages de la vague du 18 octobre 2026, où le
propriétaire demandait de faire toutes les actions de la feuille de route qui
n'ont pas besoin de lui : les champs de saisie du conjoint collaborateur et de
la Lodeom, que la cinquième partie (`2026-10-16-etape-18-conjoint-collaborateur.md`)
et la septième (`2026-10-17-etape-18-lodeom.md`) renvoyaient à la session des
pages. Les classes d'avant 1973, qui demandent le fac-similé, restent à une
autre session. Aucun texte n'a été relu : les deux champs suivent les fiches
transcrites les 16 et 17 octobre.

**La Lodeom.** Un menu des options repliées, sous les dispenses : « Lodeom de
l'employeur », « non » ou l'un des trois barèmes, sous leur libellé
(`BAREMES_LODEOM`, que les deux saisies portent et qu'un test tient au bloc
`lodeom` des données). La bulle dit chaque barème et ses seuils, lus au paquet.
Tous les emplois le portent : chaque métier, principal ou ajouté
(`Metier.lodeom`, l'attribut `lodeom` de la chronologie), chaque ligne d'emploi
du relevé (`LigneRelevee.lodeom`), et les années qui prolongent le relevé ;
seule la fiche de paie du salarié du privé le lit. Elle dit alors, dans « Comment
ce chiffre est calculé », l'exonération, son barème, T et ses seuils, lus au
paquet (`salaireNetAllegement`), au lieu des 40,21 % et des trois SMIC de la
réduction générale, écrits en dur. Les deux phrases en gras ne changent pas ; le
contrôle `allegement_au_smic` les éprouve désormais sur la Lodeom aussi.

**Le conjoint collaborateur.** Un menu sous les métiers, comme celui du
micro-entrepreneur, qui ne paraît qu'avec une période de conjoint collaborateur,
d'activité ou d'après le départ, ou une option déjà dite : « Conjoint
collaborateur, vous cotisez sur » le forfait, le tiers du plafond, qui est le
défaut (R. 662-1), ou 33,33 % ou 50 % du revenu du chef d'entreprise
(D. 633-19-2, 2° et 3° ; la même fraction en partage avant 2021). Le revenu de
ses périodes est celui du chef, que le champ dit « Revenu brut mensuel du chef
d'entreprise », « sans effet au forfait » ou « vous en cotisez 50 % »
(`champRevenuDuChef`). La saisie en oppose les bornes, puis n'en garde que la
part de l'option (`assiette_du_collaborateur`, `PARTS_COLLABORATEUR`) : rien au
forfait, où la règle de la cinquième partie donne le tiers du plafond depuis
2007 et rien avant, l'assurance volontaire tenue pour non souscrite ; 0,3333 ou
0,5 à l'option, l'assurance volontaire d'avant 2007 tenue pour souscrite sur la
même part (D. 742-26). Saisie par la pension, la carrière prend un seul niveau,
dans l'unité du revenu saisi, dont la ligne du conjoint ne cotise que sa part
(`niveaux_de_la_pension`, dans les deux contextes) : au forfait, le niveau
trouvé n'y change rien, et « Reprendre cette carrière en saisissant le revenu »
retrouve la même. Un relevé, qui porte l'assiette de chaque année, n'en dépend
pas.

**Ce que montrent les mesures.**

- *La Lodeom* ne déplace aucune pension : aucun des témoins de simulation ne
  bouge, le neuf (`lodeom_innovation_et_croissance`) compris. Les treize pages
  qui figent le formulaire gagnent le menu, et lui seul ; la page neuve
  `simuler_lodeom` dit le barème de compétitivité renforcée. À 1,5 SMIC en 2026,
  32 814,60 € de brut, ce barème exonère T fois le brut, 10 636 € par an, quand
  la réduction générale en efface 4 384 €.
- *Le conjoint collaborateur* : les quatorze témoins par statut des deux
  conjoints, saisis au revenu par défaut sans option, passent au forfait. Au
  scénario 1, la conjointe d'artisan née en 1975 descend de 38 422 à 9 092 € par
  an, celle de 1955 de 18 704 à 2 220 €, celles de 1925 et de 1935 à rien : elles
  n'ont collaboré qu'avant 2007. Les deux témoins neufs, une conjointe de
  commerçant née en 1966, salariée puis collaboratrice depuis 1998, chef à 1,5
  fois le salaire moyen : 16 672 € par an au tiers, 9 384 € au forfait. La page
  neuve `simuler_conjoint_collaborateur` fige le formulaire, son menu et son
  champ.

**Les tests.** `tests/test_saisie_de_la_lodeom.py` : le menu tenu aux données,
la lecture, l'adresse, le relevé et ses années prolongées, les métiers
principaux et ajoutés, l'exonération de la fiche de paie posée à la main (T fois
le brut sous les 2 SMIC du barème renforcé), les deux moteurs confrontés.
`tests/test_saisie_du_collaborateur.py` : le menu, la lecture et l'adresse, le
forfait au tiers des plafonds de 2010, 2020 et 2026 et rien avant 2007, les deux
parts du revenu du chef, les bornes, l'inversion par la pension qui retrouve la
carrière reprise, le relevé que l'option ne touche pas, les deux moteurs
confrontés. `tests/test_formulaire.py` : l'aller-retour des deux champs, les
menus et le libellé du revenu du chef ; `tests/test_web.py` : l'allègement sous
chaque barème de la Lodeom ; `tests/test_affirmations.py` : le contrôle étendu.

**Trouvé en chemin.**

- Le paquet de `main` est périmé depuis `48c7f81` (étape 8) : la présomption
  `pas_de_reversion_agricole` n'est pas dans `moteur/donnees.json`, et
  `test_le_paquet_est_a_jour` rougit en local. La fabrique de GitHub le refait ;
  il n'est pas touché ici. La même étape attend une session des pages pour la
  saisie de la réversion agricole.
- `test_les_incises_en_tiret_restent_rares` borne à quatorze les phrases à
  incise en tiret du simulateur : une bulle de plus en tiret la fait rougir.

**Ce qui reste**, de ce point.

1. *Au propriétaire, à confirmer* : le forfait par défaut, que la cinquième
   partie prévoyait et que le droit applique à défaut de choix, mais qui fait
   tomber les témoins des conjoints saisis sans option. Garder l'ancien sens,
   le revenu saisi comme assiette, serait une option de plus du menu.
2. La période du conjoint au forfait demande encore un revenu, qui ne compte
   pas : le rendre facultatif toucherait la lecture des lignes.
3. La Lodeom vaut pour tous les emplois : une carrière de plusieurs employeurs
   ne peut pas dire lequel l'applique. Si le propriétaire retient la forme (a)
   du champ de l'outre-mer (étape 6, `2026-10-18-etape-6-outre-mer.md`), le menu
   pourrait se loger dans ses périodes.
4. Le partage d'avant 2021, un tiers, se lit comme les 33,33 % ; l'écart est
   d'un dix-millième du revenu du chef.

De l'étape, une session : au fac-similé, les classes d'avant 1973. CAVEC,
CNBF : action 131 ; Mayotte : action 121.

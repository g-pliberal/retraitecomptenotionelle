# Étape 4 : les biens du survivant dans les ressources de la réversion, dits à la saisie

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot du code de la sécurité sociale l'a relevé
(`184/2026-11-12-etape-6-code-de-la-securite-sociale.md`, « Ce qui change une
règle », point 2) : article R. 815-25 (LEGIARTI000006753705, depuis le 13
janvier 2007), par renvoi de R. 353-1. La fiche `reversion` tient désormais la
rédaction à rattacher.

**Ce qu'il y a à faire.**

1. Lire les deux articles, et ce que la caisse publie des ressources prises en
   compte.

2. Le test, vu rouge, de ce que la saisie dit des ressources du survivant
   (`moteur/CLAUDE.md`, la liste d'un champ de saisie).

3. La saisie et la fiche. Si un champ de plus paraît nécessaire — la valeur
   des biens —, le proposer au propriétaire avant de l'ajouter.

**Fini quand** le lecteur sait, en saisissant ses ressources, que ses biens y
comptent et pour combien.

**Ce qui a été fait, le 12 novembre 2026.** L'étape est close : la saisie
l'explique, et ne demande rien de plus.

1. *Les textes, lus dans l'index LEGI à jour au 11 novembre 2026.* R. 815-25
   (LEGIARTI000006753705, depuis le 13 janvier 2007) : les biens mobiliers et
   immobiliers du demandeur, et ceux qu'il a donnés à ses descendants dans les
   cinq ans, « sont réputés lui procurer un revenu évalué à 3 % de leur valeur
   vénale fixée à la date de la demande » ; 1,5 % pour une donation de plus de
   cinq ans et de moins de dix ; une rente viagère pour le bien donné à un
   autre qu'un descendant depuis moins de dix ans. R. 815-22, 1° et 2°, en
   excepte la résidence principale et les bâtiments de l'exploitation
   agricole ; R. 353-1, 3°, les biens « acquis du chef du conjoint décédé ou
   disparu ou en raison de ce décès ». La règle n'est pas née en 2007 :
   R. 815-28 la portait avant, mot pour mot ou presque, et les rédactions
   d'avant 2007 de R. 815-25 portaient la liste que R. 815-22 porte depuis.

2. *Ce que la caisse en publie.* L'exposé « Evaluation des ressources » de la
   base de législation de la Cnav (23 janvier 2026) dit le « revenu fictif
   annuel égal à 3 % », la somme qui a « le caractère d'un capital », la seule
   part de l'indivisaire, et 11,797 % pour le bien donné à un autre qu'un
   descendant ; sa liste des ressources exclues nomme les biens propres du
   défunt, ceux issus du décès, ceux de la communauté, la résidence
   principale, les meubles meublants. Aucun exemple chiffré.

3. *La décision : expliquer, sans champ de plus.* Le champ « Ses ressources »
   demande un montant annuel. Un champ « valeur de ses biens » n'y ajouterait
   que trois centièmes de ce qu'on y écrit : le lecteur à qui l'on dit le taux
   fait cette multiplication, et la saisie comme le moteur restent tels quels.
   Rien n'a donc été proposé au propriétaire, et ni le modèle ni son portage
   n'ont été touchés.

4. *Le test d'abord.*
   `test_le_formulaire_dit_que_les_biens_du_survivant_comptent_dans_ses_ressources`
   (`tests/test_web_saisie.py`), vu rouge sur l'ancien texte : le champ dit
   3 % de la valeur, 1,5 % pour le bien donné aux descendants depuis cinq à
   dix ans, et ce qui n'y compte pas ; le champ des ressources du nouveau
   conjoint dit que ses biens comptent de même.

5. *La saisie* (`moteur/js/pages.js`, `conjointFormulaire`). L'aide du champ
   dit « sa retraite et 3 % de ses biens compris » ; son point d'interrogation,
   le taux, l'épargne et le logement loué pour exemples, les biens donnés, et
   les trois exclusions. Un « et non pour ce qu'ils rapportent » a été refusé
   par `test_le_procede_ce_n_est_pas_x_c_est_y_a_disparu` : c'est « quoi
   qu'ils rapportent ». Dix-huit rendus de page changent, aucun témoin de
   simulation.

6. *La fiche `reversion`.* La rédaction de 2007 de R. 815-25 quitte
   `textes_a_rattacher` : la version `age_52`, sous laquelle elle paraît, la
   cite. L'approximation des ressources déclarées dit que le modèle n'évalue
   pas les biens ; deux lectures de plus, le code et la base de la Cnav.
   `docs/limites/3-systeme-actuel.md` dit que c'est la saisie qui le dit au
   lecteur.

**Ce qui reste, et qui n'est pas de cette étape.** Deux écarts, tous deux
dans ce que le modèle calcule, donc au propriétaire :

- quand le lecteur date la retraite personnelle du survivant après sa
  réversion (champ « Sa propre retraite, depuis »), le formulaire dit que ses
  ressources hors de son activité ne commencent qu'alors : les biens qu'il y
  a comptés commencent avec elles, quand la caisse les compte dès la demande.
  Lu dans l'aide du champ, non rejoué ;
- le bien donné à un autre qu'un descendant, compté pour une rente viagère,
  n'est dit ni par la saisie ni par le modèle.

Aucun n'est mesuré. Le premier seul déplacerait une réversion : celle du
survivant qui a des biens et prend sa retraite après le décès.

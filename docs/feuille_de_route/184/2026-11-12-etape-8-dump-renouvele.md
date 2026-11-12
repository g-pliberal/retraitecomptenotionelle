# Étape 8 : la mise à jour d'un index refuse quand la DILA a renouvelé son dump

**La demande, le 12 novembre 2026.** La session de l'étape 5 a constaté que la
DILA avait renouvelé le 8 novembre 2026 les dumps globaux des trois bases et
retiré les incréments antérieurs (note
`2026-11-11-etape-5-kali-dans-l-index.md`). La question posée au propriétaire
: « Quand la DILA renouvelle un dump avant que l'index JORF ou LEGI l'ait
rattrapé, la mise à jour doit-elle refuser (le workflow passe au rouge, on le
relance en cochant "reconstruire", une heure à une heure et demie sur GitHub)
ou reconstruire d'elle-même ? » Les deux sessions recommandaient de refuser.
Sa réponse : « Pour les décisions à trancher : je choisis tes recommandations
».

**Ce qui est su.** `scripts/fetch/dila_index.py`, `mettre_a_jour` : la
détection existe déjà, et pour KALI elle reconstruit l'index du dump neuf. Les
index publiés du JORF et de LEGI ont enjambé le renouvellement du 8 novembre
sans trou.

**Ce qu'il y a à faire.**

1. Le test, vu rouge : un index du JORF ou de LEGI arrêté avant un dump
   renouvelé, dont les incréments manquants ne sont plus servis ; la mise à
   jour refuse, ne publie rien, et dit comment reconstruire.

2. Le code, sans toucher à `.github/workflows/index-dila.yml` : le refus fait
   échouer la course, ce qui suffit à l'alerte.

3. `docs/veille_droit.md` : ce que la session fait quand la course du lundi
   est rouge pour cette raison.

**Fini quand** un index troué ne peut plus être publié sans bruit. Si le
changement exigeait malgré tout de toucher au workflow, s'arrêter et le
demander.

**Fait, le 12 novembre 2026.** `mettre_a_jour`, dans
`scripts/fetch/dila_index.py`, cherchait déjà pour KALI si le dump de la DILA
est postérieur au dernier incrément de l'index. Elle le cherche maintenant
pour les trois bases. KALI se reconstruit comme avant. Le JORF et LEGI
refusent : une `RuntimeError`, levée avant tout incrément, que `main` rend en
« Échec : la DILA a renouvelé son dump (…) », code de sortie 1. L'index reste
tel quel ; le message nomme le dump neuf, la date où l'index s'arrête, et les
deux façons de reconstruire — le workflow relancé en cochant « reconstruire »,
ou `dila_index.py <base>` sur un poste.

**Les tests**, dans `tests/test_dila_index.py`, sur des listes de fichiers
construites à la main, sans réseau :

- le refus, pour le JORF et pour LEGI, vu rouge d'abord (« DID NOT RAISE » :
  l'incrément du 9 s'appliquait à un index arrêté au 1er, devant un dump du
  8) : l'exception, son message, l'index inchangé, le code de sortie 1 ;
- la situation des index publiés, qui ne doit pas refuser : arrêtés au 11
  novembre à 21 h 15, au-delà du dump du 8 à 14 h, ils prennent l'incrément
  suivant et lui seul ;
- ce que le refus attend du workflow, lu sans y toucher : le script de son
  étape de mise à jour est joué tel quel par `bash -eo pipefail`, le shell
  que GitHub lui donne, devant un `python` de paille dont `--mettre-a-jour`
  échoue. L'étape échoue, ne reconstruit pas à sa place et n'imprime pas
  l'état ; aucune étape d'après ne porte `always()` ni `failure()`. Qui
  retoucherait le workflow au point d'étouffer le refus verrait ce test rouge.

Le test de KALI, qui reconstruit, reste vert sans retouche.

**Le workflow n'a pas eu à changer.** Le code de sortie 1 suffit : dans
`if … --recuperer; then … --mettre-a-jour; else …; fi`, un échec de la
branche `then` arrête le script sous `-e`, et la branche `else`, qui
reconstruit, ne se joue que si la récupération échoue ou si « reconstruire »
est coché. Une étape en échec fait sauter les suivantes : rien n'est publié,
et pour LEGI rien n'est inscrit. `fail-fast: false` laisse les deux autres
bases aller au bout. L'en-tête du workflow ne dit rien du refus ; l'y écrire
toucherait une garde, et n'a pas été fait.

**La course du lundi 16 novembre 2026, à 4 h UTC.** Relevé le 12 novembre :
la release `index-dila` porte un JORF et un LEGI à jour au
`20261111-211545`, et le répertoire de la DILA un dump
`20261108-140000` pour chaque base. Le dump est antérieur aux index : la
mise à jour ne refuse pas, applique les incréments parus depuis le 11,
publie, et inscrit pour LEGI. KALI, à jour au `20261110-213159`, fait de
même. La course ne passerait au rouge, pour le JORF et LEGI, que si la DILA
renouvelait ses dumps d'ici lundi ; ce serait alors le refus voulu, et KALI
se reconstruirait seul.

**Deux effets de bord, voulus.** Construire le JORF ou LEGI d'une archive
ancienne passée par `--archive`, quand la DILA sert un dump plus récent,
finit par le même refus : cet index-là ne peut pas être mis à jour. Et la
mise à jour du JORF ou de LEGI échoue désormais, comme celle de KALI, si le
répertoire de la DILA ne liste aucun dump global : elle ne peut plus savoir
s'il a été renouvelé.

**La procédure** est dans `docs/veille_droit.md`, « Chercher dans le JORF ou
LEGI » : la session qui voit la course rouge pour cette raison ne touche pas
au workflow et le dit au propriétaire, qui relance en cochant
« reconstruire ».

**Ce qui reste.** Rien pour cette étape. Le bloc « Reprise » de l'action, qui
ne se récrit plus tant que ses étapes se mènent en parallèle, annonce encore
deux étapes : celle-ci est finie.

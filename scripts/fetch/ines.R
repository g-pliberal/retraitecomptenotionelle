# Exécute Ines (INSEE, DREES, Cnaf) sur les foyers que `ines.py` décrit.
#
#     Rscript ines.R <code d'Ines> <dossier des entrées> <dossier des sorties>
#
# Ce script appartient au dépôt ; Ines n'y entre pas. Son code se télécharge à
# part (https://gitlab.com/insee_drees_cnaf/ines-public, programmes sous CeCILL
# 2.1, paramètres sous ODbL et DbCL), et ce script n'en lit que les fonctions,
# chargées depuis le dossier de ses programmes, et ses fichiers de paramètres.
# Seules les sorties entrent au dépôt, figées dans `tests/temoins/ines.json`.
#
# L'ERFS n'est pas lue : elle demande une habilitation. Les foyers sont ceux
# que `ines.py` écrit en CSV, avec `options.json`. Trois exécutions :
#
# - LES PRÉLÈVEMENTS DES PENSIONS. `calcule_cotis` (R/12_cotisations.R) traite
#   d'un bloc les salariés, les chômeurs, les retraités et les indépendants de
#   l'ERFS. Le script n'en évalue que les instructions qui touchent une
#   pension : le classement du foyer par son revenu fiscal de l'avant-dernière
#   année (`param_cotisations2`, `impot_ind`), puis la section des retraités
#   (`param_retraite`, `retraites`), telles qu'Ines les écrit, extraites de la
#   fonction par le nom de ce qu'elles assignent. La table `prof`, qui les
#   relie, est la seule que le script écrive lui-même : Ines y joint aux
#   classements les colonnes de l'individu, et le script n'y met que celles que
#   la section lit (âge, profession, pension imposable, pension d'invalidité).
# - L'ASPA. `modelise_aspa_asi` (R/14_minima_pa.R), appelée entière, sur des
#   pensions brutes données. Les barèmes mensuels de l'année viennent de
#   `import_param_mensuel`, à une profondeur nulle : Ines ne tient de barème au
#   mois que depuis janvier 2021, et son chargeur ordinaire
#   (`importe_parametres`) remonte deux ans.
# - LA CHAÎNE. Les deux, l'une après l'autre : l'ASPA lit la pension brute
#   (`zrstbrut`) que la section des retraités reconstitue de la pension
#   imposable.

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(rlang)
  library(stringr)
})

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 3) {
  stop("usage : Rscript ines.R <code d'Ines> <entrees> <sorties>")
}
code_ines <- normalizePath(arguments[1], mustWork = TRUE)
entrees <- normalizePath(arguments[2], mustWork = TRUE)
dir.create(arguments[3], showWarnings = FALSE, recursive = TRUE)
sorties <- normalizePath(arguments[3], mustWork = TRUE)

reglages <- jsonlite::fromJSON(file.path(entrees, "options.json"))

# Ines lit ses paramètres par un chemin relatif (« parametres/ ») : le script
# travaille dans son dossier.
setwd(code_ines)
for (fichier in c("fonctions_utiles.R", "01_initialisation.R", "12_cotisations.R",
                  "14_minima_pa.R")) {
  sys.source(file.path("R", fichier), envir = globalenv())
}
# La profondeur d'historique que `import_param` prend par défaut.
profondeur_historique <- 5

# Une table d'entrée : tout en texte, puis les colonnes numériques converties,
# pour que `noi`, `idfoyer` ou la profession gardent leurs zéros.
lire <- function(nom, numeriques) {
  table <- read.csv(file.path(entrees, paste0(nom, ".csv")), colClasses = "character",
                    na.strings = character(0))
  for (colonne in numeriques) table[[colonne]] <- as.numeric(table[[colonne]])
  table
}

ecrire <- function(table, nom) {
  write.csv(table, file.path(sorties, paste0(nom, ".csv")), row.names = FALSE, na = "")
}

# Une instruction de premier niveau d'une fonction d'Ines, par la variable
# qu'elle assigne : si Ines la renomme ou la déplace, le script s'arrête au
# lieu d'évaluer autre chose.
instruction <- function(fonction, cible, rang = 1L) {
  corps <- as.list(body(fonction))
  assignations <- Filter(function(s) {
    is.call(s) && identical(s[[1]], as.name("<-")) && identical(s[[2]], as.name(cible))
  }, corps)
  if (length(assignations) < rang) {
    stop("Ines n'assigne plus « ", cible, " » (rang ", rang, ") dans cette fonction")
  }
  assignations[[rang]]
}

definir_annee <- function(anleg) {
  p_m <- list(anleg = anleg, anref = anleg - 2)
  # `modelise_aspa_asi` et les chargeurs de paramètres lisent `p_m` global.
  assign("p_m", p_m, envir = globalenv())
  p_m
}

# ---- Les prélèvements des pensions --------------------------------------------

NOMS_PRELEVEMENTS <- c(
  "pm_exo_csg_remp", "pm_exo_csg_remp_pac", "pm_plaf_csg_remp", "pm_plaf_csg_remp_pac",
  "pm_plaf2_csg_ret", "pm_plaf2_csg_ret_pac", "pm_tcsgprd1", "pm_tcsgprd1bis",
  "pm_tcsgprd2", "pm_tcsgpri", "pm_tcrdspr", "pm_tcasa", "pm_tcomapr",
  "pm_retrncp_q1", "pm_retrncp_q2", "pm_retrncp_q3", "pm_retrncp_q4",
  "pm_retrncp_t1", "pm_retrncp_t2", "pm_retrncp_t3", "pm_retrncp_t4", "pm_retrncp_t5",
  "pm_retrcp_q1", "pm_retrcp_q2", "pm_retrcp_q3", "pm_retrcp_q4",
  "pm_retrcp_t1", "pm_retrcp_t2", "pm_retrcp_t3", "pm_retrcp_t4", "pm_retrcp_t5"
)

prelevements <- function(foyers, anleg) {
  p_m <- definir_annee(anleg)
  parametres <- suppressMessages(importe_parametres(p_m))
  env <- new.env(parent = globalenv())
  env$p_m <- p_m
  env$param <- parametres$param
  env$erfs_individu_an <- foyers |>
    transmute(annee = anleg, ident, noi, idfoyer, coldec, quelfic)
  # Le revenu fiscal de référence et les parts de l'avant-dernière année.
  env$erfs_foyer_fiscaux_an <- foyers |>
    transmute(annee = anleg - 2, idfoyer, impot7 = 0, npart, rfr)
  eval(instruction(calcule_cotis, "param_cotisations2"), env)
  eval(instruction(calcule_cotis, "impot_ind"), env)
  env$prof <- env$impot_ind |>
    select(annee, ident, noi, idfoyer, coldec, impot, pth, pir, reduc_csg, exo_csg,
           interm_csg, quelfic) |>
    distinct() |>
    left_join(foyers |> transmute(ident, noi, ag, pcstot4_comp, zrsti, zpii = 0),
              by = c("ident", "noi")) |>
    filter(ag >= 16 & quelfic != "POTE")
  eval(instruction(calcule_cotis, "param_retraite"), env)
  eval(instruction(calcule_cotis, "retraites", 1L), env)
  resultats <- env$retraites |>
    transmute(annee, ident, noi, exo_csg, reduc_csg, interm_csg, ancienne_prof,
              partretrcompl, zrsti, zpenu, zpenug, zpenuc, coprmal, csgprd, csgpri,
              csgpr_mal, crdspr, casapr, zrstbrut)
  lus <- parametres$param |>
    filter(annee == anleg, nom %in% NOMS_PRELEVEMENTS) |>
    transmute(annee, nom, valeur, source = "param_prelev")
  list(resultats = resultats, parametres = lus)
}

# ---- L'ASPA --------------------------------------------------------------------

NOMS_ASPA <- c("pm_mv_mi", "pm_mv_plfi", "pm_mv_plfc", "pm_abat_aspa_celib",
               "pm_abat_aspa_couple")

aspa <- function(personnes, anleg) {
  definir_annee(anleg)
  param_presta <- suppressMessages(
    import_param_mensuel("param_presta_mensuel", "Minima", annee = anleg, profondeur = 0)
  ) |>
    mutate(nom = paste0("pm_", nom), annee = as.double(annee))
  erfs_individu_an <- personnes |>
    transmute(ident, noi, anleg = anleg, wpela_anr2 = 1, noicon, idfoyer, idfoyer2 = "",
              naia = anleg - ag, naim = "07", ag, elig_aspa_asi = 0, quelfic = "EE&FIP",
              coldec, lprl, etamatri_y_comp = "")
  base_individu_an <- personnes |>
    transmute(ident, noi, annee = anleg, zragi = 0, zrici = 0, zrnci = 0, zalri = 0,
              zrtoi = 0, zpii = 0)
  # Aucun individu fiscal hors de l'enquête : la table, vide, garde ses types.
  erfs_indfip_an <- data.frame(
    ident = character(0), noi = character(0), anfip = character(0), naim = character(0),
    ag = numeric(0), quelfic = character(0), idfoyer = character(0),
    idfoyer2 = character(0), coldec = character(0), zragi = numeric(0),
    zrici = numeric(0), zrnci = numeric(0), zalri = numeric(0), zrtoi = numeric(0),
    zpii = numeric(0))
  erfs_foyer_fiscaux_an <- personnes |>
    distinct(idfoyer, sif_mcdv) |>
    transmute(annee = anleg, idfoyer, noivous = "", sif_casez = "", sif_mcdv,
              sif_datez = "", zracf = 0, zfonf = 0, zetrf = 0, zvamf = 0, zvalf = 0)
  modele_cotis <- personnes |>
    transmute(annee = anleg, ident, noi, zsalbrut = salaire_brut, zchobrut = 0,
              zrstbrut = pension_brute, zpibrut = 0)
  erfs_menage_an <- personnes |> distinct(ident) |> transmute(ident, annee = anleg,
                                                                produitfin = 0)
  servie <- modelise_aspa_asi(
    erfs_individu_an = erfs_individu_an, base_individu_an = base_individu_an,
    imput.aspa_asi = NULL, erfs_indfip_an = erfs_indfip_an,
    erfs_foyer_fiscaux_an = erfs_foyer_fiscaux_an, modele.cotis = modele_cotis,
    erfs_menage_an = erfs_menage_an, param_presta = param_presta)$aspa_asi
  resultats <- personnes |>
    transmute(annee = anleg, ident, noi) |>
    left_join(servie |> transmute(ident, noi, nb_elig_aspa, en_couple, rev_tot_aspa_abat,
                                   aspa_eli, asi),
              by = c("ident", "noi"))
  # Les barèmes de l'année tels que la fonction les lit : la moyenne des
  # douze mois (`temp_agreg_param_mois`).
  moyennes <- data.frame(anleg = anleg) |>
    temp_agreg_param_mois(param_presta, NOMS_ASPA, var_annee = "anleg") |>
    pivot_longer(-anleg, names_to = "nom", values_to = "valeur") |>
    transmute(annee = anleg, nom, valeur, source = "param_presta_mensuel, moyenne de l'année")
  mensuels <- param_presta |>
    filter(nom %in% NOMS_ASPA) |>
    transmute(annee, nom = paste0(nom, "_mois_", sprintf("%02d", as.integer(mois))), valeur,
              source = "param_presta_mensuel")
  list(resultats = resultats, parametres = bind_rows(moyennes, mensuels))
}

# ---- Les exécutions ------------------------------------------------------------

resultats_prelevements <- list()
resultats_aspa <- list()
resultats_chaine <- list()
parametres_lus <- list()

foyers <- lire("prelevements", c("annee", "ag", "zrsti", "npart", "rfr"))
for (anleg in reglages$annees_prelevements) {
  calcul <- prelevements(foyers |> filter(annee == anleg), anleg)
  resultats_prelevements[[length(resultats_prelevements) + 1]] <- calcul$resultats
  parametres_lus[[length(parametres_lus) + 1]] <- calcul$parametres
}

personnes <- lire("aspa", c("annee", "ag", "pension_brute", "salaire_brut"))
for (anleg in reglages$annees_aspa) {
  calcul <- aspa(personnes |> filter(annee == anleg), anleg)
  resultats_aspa[[length(resultats_aspa) + 1]] <- calcul$resultats
  parametres_lus[[length(parametres_lus) + 1]] <- calcul$parametres
}

chaine <- lire("chaine", c("annee", "ag", "zrsti", "npart", "rfr", "salaire_brut"))
for (anleg in reglages$annees_chaine) {
  du_moment <- chaine |> filter(annee == anleg)
  preleve <- prelevements(du_moment, anleg)$resultats
  avec_brut <- du_moment |>
    left_join(preleve |> transmute(ident, noi, pension_brute = zrstbrut),
              by = c("ident", "noi")) |>
    mutate(pension_brute = coalesce(pension_brute, 0))
  servie <- aspa(avec_brut, anleg)$resultats
  resultats_chaine[[length(resultats_chaine) + 1]] <- preleve |>
    left_join(servie |> select(ident, noi, nb_elig_aspa, en_couple, rev_tot_aspa_abat,
                               aspa_eli, asi),
              by = c("ident", "noi"))
}

ecrire(bind_rows(resultats_prelevements), "prelevements")
ecrire(bind_rows(resultats_aspa), "aspa")
ecrire(bind_rows(resultats_chaine), "chaine")
ecrire(distinct(bind_rows(parametres_lus)), "parametres")

versions <- list(
  R = R.version.string,
  dplyr = as.character(packageVersion("dplyr")),
  tidyr = as.character(packageVersion("tidyr")),
  readxl = as.character(packageVersion("readxl")),
  rlang = as.character(packageVersion("rlang"))
)
writeLines(jsonlite::toJSON(versions, auto_unbox = TRUE, pretty = TRUE),
           file.path(sorties, "versions.json"))

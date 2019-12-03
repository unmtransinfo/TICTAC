#!/usr/bin/env Rscript
###
library(readr)
library(data.table)
library(tm)
library(stringr)

truncate.ellipsis <- function(txt, maxlen) {
  return (ifelse(nchar(txt)<maxlen, txt, sprintf("%s...", substr(txt, 1, maxlen-3))));
}

# JensenLab Tagger targets NER (human proteins)
# 
# Many false positives due to synonomy collisions with common words (e.g. "Aim 1", "Nut").

studies <- read_delim("data/aact_studies.tsv", "\t")
setDT(studies)
studies[["start_year"]] <- as.integer(format(studies$start_date, "%Y"))
studies <- studies[study_type=="Interventional"]
studies$phase[studies$phase == "N/A"] <- NA

drugs <- read_delim("data/aact_drugs.tsv", "\t", col_types = "dcc")
setDT(drugs)

studies <- studies[nct_id %in% drugs$nct_id]

descs <- read_delim("data/aact_descriptions.tsv", "\t", col_types=cols(.default=col_character()), escape_double=F, trim_ws=T)


tner <- read_delim("data/aact_descriptions_tagger_target_matches.tsv", "\t", 
                   col_names = c("id", "term", "serialnm" ), col_types="c----c-c")
tent <- read_delim("/home/data/jensenlab/data/human_entities.tsv", "\t", col_names=c("serialnm", "ensp"), col_types="c-c")
setDT(tner)
setDT(tent)
tner <- merge(tner, tent, by="serialnm", all.x=T, all.y=F)
tner <- merge(tner, descs, by="id", all.x=T, all.y=F)
tner[, id:=NULL]
tner[, serialnm:=NULL]
tner <- tner[grepl("^ENSP", ensp)]
tbad <- c("post", "end", "type", "aim", "impact", "pilot", "arms", "large", "set", "mass",
"men", "light", "step", "damage", "tube", "task", "rest", "past", "sex", "call",
"art", "simple", "find", "white", "bid", "stop", "met", "ask", "soft",
"fast", "red", "lab", "gas", "app", "aid", "great", "act", "held", "mask",
"kit", "minor", "fusion", "statin", "prep", "tip", "flap", "mail", "prep",
"top", "rank", "map", "era", "gamma", "hrs", "net", "hot", "cap", "april", "cap",
"spatial", "pad", "max", "sit", "bag", "chop", "wire", "med", "grip", "coil",
"mark", "nodal", "arch", "gov", "bad", "talk", "killer", "nail", "cope", "lobe",
"pace", "fur", "van", "cast", "mix", "flame", "flip", "opt", "lamp", "heel",
"spin","miss", "pick", "shot", "traits", "tele", "cat", "prof", "lap", "pen", 
"mast", "lethal", "yrs", "bite", "toll", "wise", "fats", "clip", "grid", "apps",
"fix", "std", "jet", "flash", "tactile", "bright", "clock", "caps")
tbad <- union(tbad, stopwords("SMART"))
tner <- tner[!(tolower(term) %in% tbad)]
sprintf("Total target mentions: %d (in %d studies)", nrow(tner), uniqueN(studies$nct_id))

## Target mention totals by merging to resolved Ensembl ID (ENSP).

tner_totals <- tner[, .(N_mentions = .N), by=c("ensp", "term")]
tner_totals <- tner_totals[, .(N_mentions = sum(N_mentions), terms=paste0(term, collapse="; ")), by=c("ensp")]
tner_totals <- tner_totals[order(-N_mentions)]
tner_totals$terms <- truncate.ellipsis(tner_totals$terms, 200)
#knitr::kable(tner_totals[1:20], caption="Top 20 human proteins by total mentions")

## Target mentions by study.
# Sort synonyms terms by frequency.

tner <- tner[, .(N_mentions = .N), by=c("nct_id", "ensp", "term")]
tner <- tner[order(nct_id, -N_mentions)]
tner <- tner[, .(N_mentions = sum(N_mentions), target_terms=paste0(term, collapse=";")), by=c("nct_id", "ensp")]
#knitr::kable(tner[nct_id %in% base::sample(unique(tner$nct_id), 10)], caption="Target mentions by study (Random sample of studies)")

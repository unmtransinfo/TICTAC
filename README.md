# `TICTAC` - Target illumination clinical trials analytics with cheminformatics


<img align="right" src="/doc/images/IDG_logo.png" height="120">
Mining ClinicalTrials.gov via AACT-CTTI-db for target hypotheses, with strong
cheminformatics and medical terms text mining, powered by NextMove LeadMine
and JensenLab Tagger.  This project is supported by the NIH [Illuminating the Druggable Genome (IDG) Program](https://commonfund.nih.gov/idg).

### Dependencies

* [ClinicalTrials.gov](https://ClinicalTrials.gov)
* [AACT-CTTI-db](https://aact.ctti-clinicaltrials.org/)
* [NextMove LeadMine](https://nextmovesoftware.com)
* [JensenLab](https://jensenlab.org/) [Tagger](https://bitbucket.org/larsjuhljensen/tagger/).
* [BioClients](https://github.com/jeremyjyang/BioClients)
* [IDG Pharos/TCRD](https://pharos.nih.gov/)
* [PubChem REST API](https://pubchem.ncbi.nlm.nih.gov/rest/pug/)
* [ChEMBL REST API](https://www.ebi.ac.uk/chembl/ws)
* [ChEMBL webresource client](https://github.com/chembl/chembl_webresource_client) \(Python client library\).
* [nextmove-tools](https://github.com/unmtransinfo/nextmove-tools)

### About AACT:

* [AACT-CTTI](https://aact.ctti-clinicaltrials.org/) database from Duke.
  * CTTI = [Clinical Trials Transformation Initiative](https://ctti-clinicaltrials.org/)
  * AACT = Aggregate Analysis of ClinicalTrials.gov
* According to website (accessed June 2022), data is refreshed daily.
* AACT structure changed in November 2021, reflecting newer ClinicalTrials.gov API.
* Identify drugs by intervention ID, since may be multiple drugs per trial \(NCT\_ID\).

### References:

* [AACT Data Dictionary](https://aact.ctti-clinicaltrials.org/data_dictionary), which references <https://prsinfo.clinicaltrials.gov/definitions.html> and <https://prsinfo.clinicaltrials.gov/results_definitions.html>.
* [The Database for Aggregate Analysis of ClinicalTrials.gov (AACT) and Subsequent Regrouping by Clinical Specialty](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0033677), Tasneem et al., <https://doi.org/10.1371/journal.pone.0033677> (2012).
* [The Clinical Trials Transformation Initiative. One Decade of Impact. One Vision Ahead](https://journals.sagepub.com/toc/ctja/15/1_suppl), Clinical Trials (2018).
* [How to avoid common problems when using ClinicalTrials.gov in research: 10 issues to consider](https://www.bmj.com/content/361/bmj.k1452), Tse et al., BMJ 2018; 361, <https://doi.org/10.1136/bmj.k1452> (2018).
* See also: <https://www.ctti-clinicaltrials.org/briefing-room/publications>

### Text mining, aka Named Entity Recognition (NER)

* Chemical NER by [NextMove LeadMine](https://nextmovesoftware.com).
* Disease NER by [JensenLab](https://jensenlab.org/) [Tagger](https://github.com/larsjuhljensen/tagger/).

### Purpose:

* Associate drugs with diseases/phenotypes.
* Associate drugs with protein targets.
* Associate protein targets with diseases/phenotypes (via drugs).
* Predict and score disease-target associations.

___Drugs___ may be experimental candidates.

### AACT tables of interest:
| *Table* | *Notes* |
| ---: | :--- |
| **studies** | titles |
| **keywords** | Reported; multiple vocabularies. |
| **brief\_summaries** | (max 5000 chars) |
| **detailed\_descriptions** | (max 32000 chars) |
| **conditions** | diseases/phenotypes |
| **browse\_conditions** | MeSH links |
| **interventions** | Our focus is drugs only among several types. |
| **browse\_interventions** | MeSH links |
| **intervention\_other\_names** | synonyms |
| **study\_references** | PubMed links |
| **reported\_events** | including adverse events |

### Overall workflow:

See top level script `Go_tictac_Workflow.sh`.

1. Data:
  1. `Go_aact_GetData.sh` - Fetch data from AACT db.
  1. `Go_jensenlab_GetData.sh` - Fetch dictionary data from JensenLab.
  1. `Go_pubmed-aact_GetData.sh` - Fetch referenced records from PubMed API.
1. Cross-references:
  1. `Go_pubchem_GetXrefs.sh` - PubChem IDs via APIs.
  1. `Go_chembl_GetXrefs.sh` - ChEMBL IDs via APIs.
1. LeadMine (chemical NER):
  1. `Go_aact_NER_leadmine_chem.sh` - LeadMine NER, CT descriptions.
  1. `Go_pubmed-aact_NER_leadmine_chem.sh` - LeadMine NER, referenced PubMed abstracts.
1. Tagger (disease NER):
  1. `Go_aact_NER_tagger_disease.sh` - Tagger NER, CT descriptions.
  1. `Go_pubmed-aact_NER_tagger_disease.sh` - Tagger NER, referenced PubMed abstracts.
1. Results, analysis:
  1. `tictac.Rmd` - Results described and analyzed.

### Association semantics:
* **keywords**, **conditions**, **studies** and **summaries**: reported terms and free text which may be text mined for intended associations.
* **descriptions**:  may be text mined for both the intended and other conditions, symptoms and phenotypic traits, which may be non-obvious from the study design.
* **study\_references**: via PubMed, text mining of titles, abstracts can associate disease/phenotypes, protein targets, chemical entities and more.  The "results\_reference" type may include findings not anticipated in the design/protocol.
* **interventions** include drug names which can be recognized and mapped to standard IDs, a task for which NextMove LeadMine is particularly suited.
* LeadMine chemical NER also resolves entities to structures via SMILES, enabling downstream cheminformatics such as aggregation by chemical substructure and similarity.

### NextMove Leadmine

Running NextMove Leadmine NER via `nextmove-tools`.

```
$ java -jar ${LIBDIR}/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar
usage: LeadMine_Utils [-config <CFILE>] [-h] -i <IFILE> [-idcol <IDCOL>]
       [-lbd <LBD>] [-max_corr_dist <MAX_CORR_DIST>] [-min_corr_entity_len
       <MIN_CE_LEN>] [-min_entity_len <MIN_E_LEN>] [-o <OFILE>]
       [-spellcorrect] [-textcol <TEXTCOL>] [-unquote] [-v]
LeadMine_Utils: NextMove LeadMine chemical entity recognition
 -config <CFILE>                     Input configuration file
 -h,--help                           Show this help.
 -i <IFILE>                          Input file
 -idcol <IDCOL>                      # of ID input column
 -lbd <LBD>                          LeadMine look-behind depth
 -max_corr_dist <MAX_CORR_DIST>      LeadMine Max correction (Levenshtein)
                                     distance
 -min_corr_entity_len <MIN_CE_LEN>   LeadMine Min corrected entity length
 -min_entity_len <MIN_E_LEN>         LeadMine Min entity length
 -o <OFILE>                          Output file
 -spellcorrect                       LeadMine spelling correction
 -textcol <TEXTCOL>                  # of text/document input column
 -unquote                            unquote quoted column
 -v,--verbose                        Verbose.
```

### JensenLab Tagger

```
$ tagcorpus
Usage: tagcorpus [OPTIONS]
Required Arguments
	--types=filename
	--entities=filename
	--names=filename
Optional Arguments
	--documents=filename	Read input from file instead of from STDIN
	--groups=filename
	--type-pairs=filename	Types of pairs that are allowed
	--stopwords=filename
	--local-stopwords=filename
	--autodetect Turn autodetect on
	--tokenize-characters Turn single-character tokenization on
	--document-weight=1.00
	--paragraph-weight=2.00
	--sentence-weight=0.20
	--normalization-factor=0.60
	--threads=1
	--out-matches=filename
	--out-pairs=filename
	--out-segments=filename
```

# Clinicaltrials.gov analytics
Includes cheminformatics and medical terms text mining.

---

### About AACT:
* [AACT-CTTI](https://aact.ctti-clinicaltrials.org/) database from Duke.
* CTTI = Clinical Trials Transformation Initiative
* AACT = Aggregate Analysis of ClinicalTrials.gov
* According to website (July 2018), data is refreshed monthly.
* Identify drugs by intervention ID, since may be multiple drugs per trial (NCT\_ID).

### References:
* <http://clinicaltrials.gov>
* <https://aact.ctti-clinicaltrials.org/>
* [AACT Data Dictionary](https://aact.ctti-clinicaltrials.org/data_dictionary), which references <https://prsinfo.clinicaltrials.gov/definitions.html> and <https://prsinfo.clinicaltrials.gov/results_definitions.html>.
* [The Database for Aggregate Analysis of ClinicalTrials.gov (AACT) and Subsequent Regrouping by Clinical Specialty](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0033677), Tasneem et al., March 16, * 2012https://doi.org/10.1371/journal.pone.0033677.
* [How to avoid common problems when using ClinicalTrials.gov in research: 10 issues to consider](https://www.bmj.com/content/361/bmj.k1452), Tse et al., BMJ 2018; 361 doi: https://doi.org/10.1136/bmj.k1452 (Published 25 May 2018.
* See also: <https://www.ctti-clinicaltrials.org/briefing-room/publications>

### About NextMove LeadMine:
* Text mining performed with [NextMove LeadMine](http://nextmovesoftware.com).

### Purpose:
* Associate drugs with diseases/phenotypes.
* Associate protein targets with diseases/phenotypes.
* Associate drugs with protein targets.
* Predict and score disease-target associations.

### AACT tables of interest:
| *Table* | *Notes* |
| ---: | :--- |
| **studies** | (titles) |
| **keywords** | (reported) |
| **brief\_summaries** | (max 5000 chars) |
| **detailed\_descriptions** | (max 32000 chars) |
| **conditions** | |
| **browse\_conditions** | (NCT-MeSH links) |
| **interventions** | (various; our focus is drugs only) |
| **browse\_interventions** | (NCT-MeSH links) |
| **intervention\_other\_names** | (synonyms) |
| **study\_references** | (including type results\_reference) |

### Overall workflow:
* `Go_ct_GetData.sh` - Fetch selected data from AACT db.
* `Go_xref_drugs.sh` - PubChem and ChEMBL IDs via APIs.
* `Go_BuildDicts.sh` - Build NextMove LeadMine dicts for MeSH etc. NER.
* `Go_NER.sh` - LeadMine NER.
* `Go_NER_pubmed.sh` - LeadMine NER, selected referenced PMIDs.
* `leadmine_utils.sh` - Runs LeadMine API custom app on TSVs.
* Results analyzed for associations via R codes.

### Association semantics:
* **keywords**, **conditions**, **studies** and **summaries**: reported terms and free text which may be text mined for intended associations.
* **descriptions**:  may be text mined for both the intended and other conditions, symptoms and phenotypic traits, which may be non-obvious from the study design.
* **study\_references**: via PubMed, text mining of titles, abstracts can associate disease/phenotypes, protein targets, chemical entities and more.  The "results\_reference" type may include findings not anticipated in the design/protocol.
* **interventions** include drug names which can be recognized and mapped to standard IDs, a task for which NextMove LeadMine is particularly suited.

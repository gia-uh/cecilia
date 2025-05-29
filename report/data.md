# Cecilia v1 Dataset - Comprehensive Technical Report

**Report Generated:** 2025-05-27 16:32:47 UTC
**Model Repository:** gia-uh/cecilia-tiny
**Dataset Location:** /workspace/data/maria-silvia-dataset
**Analysis Framework:** Continual Pretraining Framework

---

## Executive Summary

This comprehensive technical report analyzes the Cecilia v1 dataset used for continual pretraining of the Cecilia-Tiny model. The analysis provides critical insights into dataset composition, quality metrics, tokenization efficiency, and training implications essential for understanding model performance and potential improvements.

### Key Findings

- **Dataset Scale:** 296,311 files across 3026 domains
- **Corpus Size:** 2,631,691,355 characters (~3.45 GB)
- **Vocabulary Richness:** 384,963,687 total words
- **Average Document Length:** 8,881 characters per file


---

## 1. Dataset Architecture & Composition

### 1.1 Structural Overview

The Maria Silvia dataset comprises **3026 distinct domains** containing **296,311 text files**. This multi-domain architecture enables robust continual learning across diverse Cuban cultural and linguistic contexts.

#### Domain Distribution Analysis

| Domain | Files | Percentage | Description |
|--------|-------|------------|-------------|
| ecured/ecured/c/a | 9,249 | 3.1% | Specialized Cuban content domain |
| ecured/ecured/m/a | 8,621 | 2.9% | Specialized Cuban content domain |
| Enciclopedia Digital del Audiovisual Cubano/curated | 8,126 | 2.7% | Specialized Cuban content domain |
| ecured/ecured/l/a | 7,769 | 2.6% | Specialized Cuban content domain |
| ecured/ecured/e/l | 6,590 | 2.2% | Specialized Cuban content domain |
| ecured/ecured/c/o | 5,961 | 2.0% | Specialized Cuban content domain |
| ecured/ecured/j/o | 5,935 | 2.0% | Specialized Cuban content domain |
| ecured/ecured/a/n | 5,635 | 1.9% | Specialized Cuban content domain |
| ecured/ecured/p/a | 5,096 | 1.7% | Specialized Cuban content domain |
| ecured/ecured/s/a | 4,995 | 1.7% | Specialized Cuban content domain |

*Note: 3016 additional domains not shown above. Complete listing available in JSON summary.*


### 1.2 Content Metrics & Statistics

#### Overall Corpus Statistics
- **Total Characters:** 2,631,691,355
- **Total Words:** 384,963,687
- **Total Lines:** 34,505,341
- **Character Density:** 76.3 chars/line
- **Lexical Density:** 6.8 chars/word

#### Domain-wise Content Analysis

| Domain | Files | Characters | Words | Avg File Size | Content Density |
|--------|-------|------------|-------|---------------|-----------------|
| literature/cleaned | 428 | 249,387,066 | 32,186,005 | 582680 | 7.75 |
| ecured/ecured/c/a | 9,240 | 58,862,866 | 8,327,218 | 6370 | 7.07 |
| ecured/ecured/m/a | 8,615 | 53,938,133 | 7,632,028 | 6261 | 7.07 |
| ecured/ecured/a/n | 5,626 | 44,563,297 | 6,029,040 | 7921 | 7.39 |
| ecured/ecured/l/a | 7,758 | 40,132,264 | 5,866,290 | 5173 | 6.84 |
| ecured/ecured/c/o | 5,959 | 39,237,300 | 5,594,457 | 6585 | 7.01 |
| ecured/ecured/j/o | 5,929 | 38,789,753 | 5,398,647 | 6542 | 7.19 |
| ecured/ecured/e/l | 6,585 | 33,675,988 | 4,895,093 | 5114 | 6.88 |
| ecured/ecured/p/a | 5,093 | 33,260,044 | 4,697,844 | 6531 | 7.08 |
| ecured/ecured/s/a | 4,991 | 32,086,489 | 4,581,110 | 6429 | 7.00 |

*Note: 3016 additional domains not shown above. Complete data available in JSON summary.*


#### Content Quality Insights

**Document Length Distribution:**
- Files range from small snippets to substantial documents
- Average document length: 8,881 characters
- This distribution suggests good diversity in content granularity

**Lexical Richness:**
- Character-to-word ratio: 6.84
- Indicates higher complexity with longer words (formal/academic content)


---

## 3. Language Analysis & Cuban Spanish Characteristics

### 3.1 Language Distribution

**Overall Language Detection Results:**
- **Files Analyzed:** 3017
- **Primary Languages Detected:**

| Language | Count | Percentage |
|----------|-------|------------|
| Spanish | 2893 | 95.9% |
| English | 67 | 2.2% |
| SO | 39 | 1.3% |
| Catalan | 7 | 0.2% |
| French | 7 | 0.2% |


**Detection Confidence:** 0.989 (avg) - High confidence

### 3.2 Cuban Spanish Characteristics

#### Cultural and Geographic Indicators
**Most Frequent Cuban Terms Found:**

- **Ño:** 802,590 occurrences
- **Río:** 177,809 occurrences
- **Ron:** 98,923 occurrences
- **Cuba:** 88,287 occurrences
- **Son:** 56,030 occurrences
- **Revolución:** 40,569 occurrences
- **Habana:** 32,779 occurrences
- **Che:** 30,144 occurrences
- **La Habana:** 25,006 occurrences
- **Caña:** 18,473 occurrences


#### Language Register Analysis
- **Formal Language Indicators:** 15,365 (28.8%)
- **Informal Language Indicators:** 38,074 (71.2%)
- **Register Assessment:** Predominantly informal

- **Average Sentence Length:** 17.0 words
- **Complexity Assessment:** Moderate complexity (standard prose)
### 3.3 Most Common Words

Top words found in the dataset (excluding common stop words):

| Rank | Word | Frequency |
|------|------|-----------|
| 1 | entre | 68,210 |
| 2 | telefono | 63,332 |
| 3 | cuba | 53,956 |
| 4 | calle | 49,388 |
| 5 | hijos | 44,206 |
| 6 | maria | 41,725 |
| 7 | html | 35,688 |
| 8 | vedado | 34,642 |
| 9 | habana | 32,430 |
| 10 | cid | 31,334 |


*Complete word frequency data available in the detailed JSON report.*


### 3.4 Text Quality Assessment

- **Encoding Issues:** 0 files
- **Non-Latin Characters:** 588,657 occurrences
- **Special Characters Ratio:** 0.0756

#### Quality Indicators
- **Language Consistency:** Excellent (Spanish dominance)
- **Cultural Relevance:** High Cuban content
- **Text Integrity:** Excellent

---

## 4. Tokenization Analysis & Efficiency

### 4.1 Model Tokenization Performance

Analysis performed using the actual pre-tokenized dataset from `gia-uh/cecilia-tiny` tokenizer.

#### Pre-tokenized Dataset Metrics
- **Total Samples:** 1,104,532
- **Total Tokens (no padding):** 982,024,795
- **Total Tokens (with padding):** 1,131,040,768
- **Total Padding Tokens:** 0
- **Average Sequence Length:** 889.3 tokens (without padding)
- **Max Sequence Length:** 1024 tokens
- **Min Sequence Length:** 1 tokens
- **Padding Ratio:** 13.2%
- **Context Windows:** 959,008 chunks (1024 tokens each)

#### Dataset Utilization
This analysis uses the actual tokenized dataset that was used for training, providing accurate token counts and padding analysis. The padding detection helps understand sequence efficiency and model training behavior.

**Training Implications:**
- **Effective Token Count:** 982,024,795 tokens will contribute to loss computation
- **Padding Overhead:** 13.2% of compute cycles spent on padded positions
- **Memory Efficiency:** High (lower padding ratio is better)

---

## 3. Training Configuration

```yaml

# Model
model_name: "BSC-LT/salamandra-2b"

# Model precision
precision: "bf16-true"
static_graph: false

# Training parameters
number_epochs: 2
batch_size: 4

# Validation parameters
validate_on_end: true
validate_after_epoch: true
validate_after_k_steps: 640

# Gradient parameters
gradient_accumulation: true
gradient_accumulation_steps: 16
grad_clip: 1.0

# Optimizer parameters
lr: 0.00002
lr_decay: true
weight_decay: 0.01
beta1: 0.9
beta2: 0.999

# Scheduler parameters
lr_scheduler: "warmup_linear"
warmup_proportion: 0.06

# Distributed_strategy
parallelization_strategy: "fsdp"

# FSDP specific parameters
sharding_strategy: "FULL_SHARD"
state_dict_type: "sharded"
limit_all_gathers: true
cpu_offload: false
num_workers: 4
gradient_checkpointing: true
```

---

## 5. Dataset Quality Assessment

### 5.1 Strengths
✅ **Domain Diversity:** Comprehensive coverage of Cuban cultural content
✅ **Scale:** Substantial corpus size suitable for continual pretraining
✅ **Consistency:** Uniform UTF-8 encoding across all files
✅ **Organization:** Well-structured domain-based organization
✅ **Linguistic Relevance:** Focused on Cuban Spanish variants and cultural context

### 5.2 Quality Indicators

- **Document Length Consistency:** Good (avg: 8,881 chars)
- **Domain Balance:** Imbalanced (ratio: 9249.0:1)

### 5.3 Potential Considerations
⚠️ **Domain Representation:** Monitor for potential bias toward specific content types
⚠️ **Temporal Distribution:** Consider content recency and historical balance
⚠️ **Language Variants:** Ensure representation of different Cuban Spanish registers

---

## 6. Recommendations & Next Steps

### 6.1 Training Optimization
1. **Validation Strategy:** Implement domain-stratified validation sets
2. **Learning Rate:** Current conservative approach is appropriate for continual learning
3. **Monitoring:** Track perplexity across different domains during training
4. **Early Stopping:** Implement based on validation metrics to prevent overfitting

### 6.2 Dataset Enhancement
1. **Quality Control:** Implement automated content quality checks
2. **Deduplication:** Run similarity analysis to identify potential duplicates
3. **Domain Augmentation:** Consider balancing underrepresented domains
4. **Metadata Enrichment:** Add domain and source metadata for better tracking

### 6.3 Evaluation Framework
1. **Intrinsic Evaluation:** Perplexity and loss tracking across domains
2. **Extrinsic Evaluation:** Task-specific benchmarks for Cuban Spanish
3. **Human Evaluation:** Cultural relevance and linguistic quality assessment
4. **Comparative Analysis:** Performance vs. base model on domain-specific tasks

---

## 7. Methodology & Data Extraction

### 7.1 Metric Calculation Methods

#### Text Statistics Extraction
- **Character Count:** `len(text)` - Raw Unicode character count including spaces and punctuation
- **Word Count:** `len(text.split())` - Space-separated token count, basic but consistent across domains
- **Line Count:** `text.count('\n') + 1` - Newline-based line counting for document structure analysis
- **File Size Distribution:** Character count per file for corpus composition analysis

#### Language Detection Methodology
- **Primary Tool:** `langdetect` library (Google's language detection algorithm)
- **Confidence Scoring:** Probabilistic confidence values (0.0-1.0) for detection reliability
- **Fallback Handling:** Files with detection failures classified as 'unknown'
- **Sample Size:** First 5,000 characters per file for efficiency and consistency

#### Tokenization Analysis Approach
**Pre-tokenized Dataset (Primary Method):**
- **Source:** Actual tokenized training data from `gia-uh/cecilia-tiny`
- **Token Counting:** Excludes padding tokens for accurate training metrics
- **Sequence Analysis:** Real sequence lengths used during model training
- **Padding Detection:** Multi-method approach using attention masks and token ID analysis
- **Padding Analysis:** Comprehensive distribution patterns and sequence efficiency metrics

**Enhanced Padding Detection Algorithm:**
1. **Primary Method:** Use attention_mask values (1=content, 0=padding) when available
2. **Fallback Method:** Analyze token ID frequencies to identify actual padding token
3. **Validation:** Test multiple potential padding tokens (0, 1, most frequent token)
4. **Selection:** Choose padding detection method with most reasonable ratio (5-60%)
5. **Statistics:** Calculate per-sequence and aggregate padding distributions

**Raw Text Analysis (Fallback):**
- **Tokenizer:** HuggingFace AutoTokenizer from base model repository
- **Encoding Method:** `tokenizer.encode()` with truncation and special tokens
- **Efficiency Metrics:** Tokens per character and tokens per word ratios
- **Context Windows:** 1024-token chunks for memory requirement estimation

#### Text Quality Assessment
**Corruption Detection Algorithm:**
1. **Empty File Check:** `len(text.strip()) == 0`
2. **Alphabetic Ratio:** `alpha_chars / total_chars < 0.3` for texts > 50 characters
3. **Encoding Issues:** Non-ASCII character ratio > 20% for texts > 100 characters
4. **Corruption Indicators:** Special character patterns suggesting encoding problems

**Spanish Language Characteristics:**
- **Cuban Indicators:** Predefined lexicon of Cuban-specific terms, places, and cultural references
- **Register Analysis:** Formal vs. informal language markers using linguistic indicator lists
- **Sentence Segmentation:** Regex-based splitting on `[.!?]+` with minimum 10-character sentences

#### Domain Analysis Methodology
- **Directory Mapping:** File system structure used as domain proxy
- **Sampling Strategy:** Stratified sampling across domains for balanced analysis
- **Statistical Aggregation:** Per-domain metrics calculated independently then combined
- **File Path Processing:** Relative paths from dataset root for consistent domain identification

### 7.2 Data Quality Assurance

#### Validation Procedures
- **Division by Zero Protection:** All ratio calculations include denominator validation
- **Error Logging:** Systematic logging of analysis failures with diagnostic information
- **Sample Size Control:** Configurable sampling to balance accuracy and computational efficiency
- **Memory Management:** Chunked processing and text truncation for large dataset handling

#### Reliability Measures
- **Confidence Intervals:** Language detection confidence scores reported
- **Coverage Metrics:** Percentage of successfully analyzed files per domain
- **Error Categorization:** Systematic classification of problematic files by issue type
- **Reproducibility:** Fixed random seeds and deterministic processing order

### 7.3 Statistical Analysis Framework

#### Aggregation Methods
- **Domain-Level Statistics:** Independent calculation then weighted aggregation
- **Global Metrics:** Cross-domain summation with proper normalization
- **Distribution Analysis:** Percentile-based analysis for file size and content length
- **Efficiency Calculations:** Harmonic and arithmetic means for different metric types

#### Reporting Standards
- **Precision Control:** Appropriate decimal places for different metric types
- **Scientific Notation:** Large numbers formatted with comma separators
- **Error Handling:** Graceful degradation when analysis components fail
- **Completeness Tracking:** Explicit reporting of analysis coverage and limitations

---

## 8. Technical Specifications

### 8.1 Analysis Environment
- **Framework:** Continual Pretraining Framework
- **Model Loading:** HuggingFace Transformers AutoModel/AutoTokenizer
- **Analysis Tools:** Custom dataset utilities with statistical analysis
- **Tokenizer:** Model-specific tokenizer from `gia-uh/cecilia-tiny`

### 8.2 Data Sources
The dataset encompasses the following top domains (showing top 10 by file count):

- **Ecured/Ecured/C/A:** Specialized Cuban content domain (9,249 files)
- **Ecured/Ecured/M/A:** Specialized Cuban content domain (8,621 files)
- **Enciclopedia Digital Del Audiovisual Cubano/Curated:** Specialized Cuban content domain (8,126 files)
- **Ecured/Ecured/L/A:** Specialized Cuban content domain (7,769 files)
- **Ecured/Ecured/E/L:** Specialized Cuban content domain (6,590 files)
- **Ecured/Ecured/C/O:** Specialized Cuban content domain (5,961 files)
- **Ecured/Ecured/J/O:** Specialized Cuban content domain (5,935 files)
- **Ecured/Ecured/A/N:** Specialized Cuban content domain (5,635 files)
- **Ecured/Ecured/P/A:** Specialized Cuban content domain (5,096 files)
- **Ecured/Ecured/S/A:** Specialized Cuban content domain (4,995 files)

*Note: 3016 additional domains not shown. Complete listing available in JSON summary.*


### 8.3 Reproducibility Information
- **Analysis Date:** 2025-05-27 16:32:47
- **Model Version:** gia-uh/cecilia-tiny
- **Dataset Path:** `/workspace/data/maria-silvia-dataset`
- **Configuration:** `config/experiments/salamandra-2b-maria-silvia`

---

## Appendices

### Appendix A: Statistical Distributions
Detailed statistical distributions and visualizations are available in the accompanying plots:
- **Main Analysis:** `dataset_analysis_plots.png` - Overview charts including domain distribution, file sizes, language distribution, and content statistics
- **Specialized Analysis:** `dataset_specialized_analysis.png` - Cuban cultural indicators, tokenization metrics, language register analysis, and data quality overview

### Appendix B: Raw Data Summary
Complete numerical data is available in the JSON summary file (`dataset_analysis_summary.json`).

### Appendix C: Configuration Files
Training configurations are stored in:
- Continual training: `config/experiments/salamandra-2b-maria-silvia/continual.yaml`
- Tokenization: `config/experiments/salamandra-2b-maria-silvia/tokenizer.yaml`

---

*This technical report was automatically generated by the Maria Silvia Dataset Analysis Pipeline on 2025-05-27.*

**Report Status:** ✅ Complete
**Quality Assurance:** Automated analysis with manual review recommended
**Next Review:** Recommended after training completion

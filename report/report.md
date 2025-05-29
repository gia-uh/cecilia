---
title: "Cecilia: The Cuban Language Model"
subtitle: Technical Report
format:
  pdf:
    template-partials:
      - before-body.tex
    number-sections: true
    citation-style: ieee
affiliations:
  - id: uh
    name: University of Havana
  - id: ua
    name: University of Alicante
author:
  - name: Ernesto L. Estevanell¹²
    affiliation:
      - ref: uh
      - ref: ua
  - name: Suilan Estévez¹
    affiliation:
      - ref: uh
  - name: Alejandro Piad¹
    affiliation:
      - ref: uh
  - name: Yudivián Almeida¹
    affiliation:
      - ref: uh
  - name: Daniel A. Valdés¹
    affiliation:
      - ref: uh
  - name: Roberto Marti¹
    affiliation:
      - ref: uh
  - name: Deborah Famadas¹
    affiliation:
      - ref: uh
  - name: Roberto García¹
    affiliation:
      - ref: uh
  - name: Gabriel Hernández¹
    affiliation:
      - ref: uh
  - name: Elena Rodríguez¹
    affiliation:
      - ref: uh
  - name: Niley González¹
    affiliation:
      - ref: uh
  - name: Carla Pérez¹
    affiliation:
      - ref: uh
  - name: Alejandro Beltrán¹
    affiliation:
      - ref: uh
  - name: Juan Pablo Consuegra¹²
    affiliation:
      - ref: uh
      - ref: ua
  - name: Robiert Sepúlveda²
    affiliation:
      - ref: ua
  - name: Yoan Gutiérrez²
    affiliation:
      - ref: ua
  - name: Rafael Muñoz²
    affiliation:
      - ref: ua
  - name: Andrés Montoyo²
    affiliation:
      - ref: ua
  - name: Manuel Palomar²
    affiliation:
      - ref: ua
bibliography: references.bib
abstract: Cecilia 2B is a 2-billion-parameter language model continually pretrained on a large, diverse corpus of Cuban Spanish text to capture the unique linguistic and cultural features of Cuban Spanish. Built on the Salamandra 2B architecture, Cecilia 2B adapts a robust multilingual base model through continual pretraining on approximately 1 billion tokens from Cuban newspapers, encyclopedias, legal documents, literature, and song lyrics. This approach enables efficient deployment in resource-constrained environments and provides a foundational resource for Cuban Spanish NLP tasks such as text generation, sentiment analysis, and named entity recognition. This report details the model’s design, training methodology, dataset, and potential applications, highlighting its significance for Cuban Spanish language technology and future research directions.
---

## Introduction

Cecilia-2B-v0.1 (hereafter Cecilia 2B) is a compact language model continual pretrained [@ke2023continual] on a diverse and extensive corpus of Cuban written text, designed to capture the unique linguistic, cultural, and social nuances of Cuban Spanish.

The motivation behind Cecilia stems from the need to develop language technologies that accurately reflect regional language variations and cultural contexts, which are often underrepresented or inadequately modeled by large, generic language models. Cuban Spanish exhibits distinct lexical, syntactic, and pragmatic features, as well as culturally specific references, that necessitate specialized modeling to improve natural language processing (NLP) performance on Cuban-specific tasks [@blodgett2020language].

Cecilia 2B is the first iteration of what the authors expect to be a comprehensive project aimed at creating pretrained and fine-tunes language models in the Cuban Spanish variant for several model sizes, architectures, and domains.

By focusing first on a relatively small model size of 2 billion parameters, Cecilia 2B balances computational efficiency with linguistic specialization, enabling deployment in resource-constrained environments common in Cuba and similar settings. This approach allows us to explore the optimal strategies for creating this type of resources, as well as facilitating broader accessibility and practical usage from the beginning of the project. The experienced obtained in this iteration of Cecilia will directly inform the development of future, larger models.

The Cecilia 2B model is based on the Salamandra 2B [@gonzalez2025salamandra] architecture and was continual pretrained for two full epochs on a private corpus comprising approximately 1 billion tokens, including Cuban newspapers spanning a decade, the Cuban Online Encyclopedia, a comprehensive collection of Cuban laws, hundreds of Cuban literary works, local encyclopedias documenting Cubanisms, and song lyrics from prominent Cuban artists. This varied and culturally grounded dataset aims to guarantee Cecilia 2B internalizes both language patterns and cultural knowledge essential for Cuban Spanish NLP applications.

Cecilia 2B is aimed at a range of NLP tasks such as text generation, sentiment analysis, named entity recognition, and machine translation, all tailored to Cuban Spanish. The model’s development reflects a growing trend in NLP research emphasizing the creation of smaller, domain- and dialect-specific models to democratize access to language technologies, preserve linguistic diversity, and provide more accurate and contextually relevant tools for speakers of underrepresented language varieties [@bommasani2021opportunities; @bender2021dangers].

This technical report presents the design, training methodology, dataset composition, and potential applications of Cecilia 2B, highlighting its role as a foundational resource for Cuban Spanish NLP research and applications.

The remainder of this report is organized as follows: Section 2 describes the model architecture and design. Section 3 presents the training corpus and procedure. Section 4 presents some briefs notes on ongoing evaluation efforts. Section 5 discusses practical applications and potential use cases. Section 6 addresses ethical considerations, including bias and responsible deployment. Finally, Section 7 outlines future work and directions for further improving the model.

## Model Architecture and Design

Cecilia 2B is built upon the Salamandra 2B model [@gonzalez2025salamandra], a transformer-based decoder-only language model developed by the Barcelona Supercomputing Center’s Language Technologies Unit. Salamandra 2B comprises approximately 2.25 billion parameters and employs a standard Transformer architecture with 24 layers, a hidden size of 2048, and 16 attention heads. It uses rotary positional embeddings (RoPE), SwiGLU activation functions, RMS normalization, and flash attention to optimize training stability and computational efficiency. The model supports a large context window of 8,192 tokens and a vocabulary size of 256K tokens, enabling it to handle diverse multilingual inputs effectively.

Salamandra 2B was chosen as the base model for Cecilia 2B due to its strong multilingual capabilities, efficient architecture, and open-source availability under an Apache 2.0 license, which facilitates fine-tuning and adaptation for specific language varieties. Its design balances model capacity and computational resource requirements, making it suitable for deployment in resource-constrained environments typical of Cuban NLP applications.

Importantly, the architecture of Salamandra 2B was left unmodified in the development of Cecilia 2B, including the tokenizer and vocabulary. The adaptation to Cuban Spanish was applied exclusively through continual pretraining on a curated Cuban text corpus, ensuring that the model’s original structural and hyperparameter configurations remain intact. This approach aims to preserve the robustness and generalization properties of the base Salamandra 2B model while specializing its linguistic knowledge to the Cuban Spanish variant. However, it must be considered that words outside the original vocabulary (cubanisms and transliterated words, for example) will be harder to learn due to the nature of tokenization [@gururangan2020dont].

## Training Data and Procedure

The training corpus for Cecilia 2B comprises approximately 1 billion tokens of Cuban Spanish text, including digitized Cuban newspapers from the last decade, the Cuban Encyclopedia, a comprehensive collection of Cuban laws, hundreds of literary works by Cuban authors, local encyclopedias documenting Cubanisms, and song lyrics from prominent Cuban artists. This diverse dataset was curated to capture the linguistic and cultural richness of Cuban Spanish.

All data was collected via web scraping under a fair use assumption and is intended solely for academic and research purposes. To respect copyright and intellectual property rights, the raw training data is not publicly available at the moment.

A full report of the dataset composition is available [here](https://github.com/syalia-srl/cecilia/blob/main/report/data.md).

### Dataset Composition

The Cecilia 2B training corpus is extensive, as shown in [@tbl-corpus-stats], comprising nearly 300,000 text files with a total of approximately 2.6 billion characters and an estimated 385 million words. This large volume of data ensures comprehensive linguistic coverage, enabling the model to learn a wide range of lexical and syntactic patterns specific to Cuban Spanish.

::: {#tbl-corpus-stats}

| Metric                  | Value               |
|-------------------------|---------------------|
| Total Files             | 296,311             |
| Total Characters        | 2,631,691,355       |
| Total Words             | 384,963,687         |
| Total Lines             | 34,505,341          |
| Average Document Length | 8,881 characters    |
| Average Sentence Length | 17.0 words          |
| Lexical Density         | 6.8 characters/word |
:
Basic corpus statistics.
:::

The average document length of 8,881 characters indicates the dataset includes a balanced mix of short and long texts, which is beneficial for training a model capable of understanding various discourse structures, from brief statements to extended narratives. An average sentence length of 17 words reflects moderately complex sentence constructions typical of formal written language, supporting the model’s ability to handle nuanced linguistic phenomena.

The lexical density of 6.8 characters per word suggests a rich vocabulary with a diversity of word lengths, which contributes to the model’s capacity to represent the Cuban Spanish lexicon effectively. Overall, these statistics demonstrate that the dataset provides a robust foundation for continual pretraining, enabling Cecilia 2B to internalize the distinctive linguistic and cultural characteristics of Cuban Spanish.

::: {#tbl-corpus-metrics}
| Metric                               | Value         |
| ------------------------------------ | ------------- |
| Total Samples                        | 1,104,532     |
| Total Tokens (no padding)            | 982,024,795   |
| Total Tokens (with padding)          | 1,131,040,768 |
| Average Sequence Length (no padding) | 889.3 tokens  |
| Padding Ratio                        | 13.2%         |
:
Tokenized corpus metrics.
:::

After tokenization, as shown in [@tbl-corpus-metrics], the dataset consists of over 1.1 million samples, with nearly one billion tokens excluding padding. The average sequence length is approximately 889 tokens, with sequences ranging from a single token up to the maximum context window size of 1024 tokens. The padding ratio of 13.2% indicates that a moderate portion of sequences required padding to reach the fixed length, which is typical for datasets with variable-length texts. The data was segmented into 959,008 context windows, each containing 1024 tokens, enabling the model to process long-range dependencies effectively during training.

### Training Procedure

The training of Cecilia 2B was conducted over two full epochs with a batch size of 4, combined with gradient accumulation over 16 steps to effectively simulate a larger batch size of 64. This approach balances the constraints of available GPU memory with the need for stable gradient estimates during optimization. Gradient clipping with a maximum norm of 1.0 was applied to prevent exploding gradients and improve training stability.

Optimization was performed using the AdamW optimizer with a learning rate of 2e-5, incorporating weight decay of 0.01 to regularize the model and reduce overfitting. The learning rate followed a warmup linear decay schedule, with a warmup phase covering 6% of the total training steps, allowing the model to gradually adapt to the data before reaching the peak learning rate. The AdamW hyperparameters beta1 and beta2 were set to 0.9 and 0.999, respectively, consistent with best practices for transformer training.

Mixed precision training using bfloat16 (bf16) precision was employed to accelerate computation and reduce memory consumption without sacrificing numerical stability. The training leveraged Fully Sharded Data Parallel (FSDP) parallelization with full sharding and sharded state dictionaries to optimize memory usage across multiple GPUs. Gradient checkpointing was enabled to further reduce memory footprint by trading compute for storage during backpropagation.

Validation was performed both after each epoch and periodically every 640 training steps, ensuring continuous monitoring of model performance and early detection of potential overfitting or training instability. Overall, these design choices reflect a careful balance between computational efficiency, training stability, and effective convergence on the specialized Cuban Spanish corpus, enabling Cecilia 2B to internalize linguistic nuances while operating within the constraints of available hardware resources.

Training was conducted over approximately 48 hours on a high-performance compute setup consisting of 2 NVIDIA A100 GPUs (40 GB each), an AMD EPYC CPU with 128 cores and 256 threads, and 1 TB of RAM.

@tbl-training-params summarizes the training hyperparameters used for Cecilia 2B.

::: {#tbl-training-params}
| Parameter                   | Value         |
| --------------------------- | ------------- |
| Number of epochs            | 2             |
| Batch size                  | 4             |
| Gradient accumulation steps | 16            |
| Effective batch size        | 64            |
| Learning rate               | 2e-5          |
| Learning rate scheduler     | Warmup linear |
| Warmup proportion           | 6%            |
| Optimizer                   | AdamW         |
| Weight decay                | 0.01          |
| Beta1, Beta2                | 0.9, 0.999    |
| Gradient clipping norm      | 1.0           |
| Precision                   | bfloat16      |
:
Training Hyperparameters.
:::

## Evaluation and Benchmarking

:::{#tbl-eval-results}
| Task                     | Metric      | Salamandra    | Cecila    | Rel Err       |
|--------------------------|-------------|--------------:|----------:|--------------:|
| `arc_challenge`          | acc         | 0.37031       | 0.38225   | 3.13%         |
| `arc_easy`               | acc         | 0.72264       | 0.73401   | 1.55%         |
| `belebele_en`            | acc         | 0.21556       | 0.24778   | 13.00%        |
| `belebele_es`            | acc         | 0.22778       | 0.24444   | 6.82%         |
| `escola`                 | acc         | 0.59259       | 0.55461   | -6.41%        |
| `openbookqa`             | acc         | 0.30000       | 0.28200   | -6.00%        |
| `openbookqa_es`          | acc         | 0.30800       | 0.29400   | -4.55%        |
| `paws_en`                | acc         | 0.56100       | 0.57350   | 2.18%         |
| `paws_es`                | acc         | 0.56050       | 0.55550   | -0.89%        |
| `piqa`                   | acc         | 0.73721       | 0.73667   | -0.07%        |
| `social_iqa`             | acc         | 0.45394       | 0.44626   | -1.69%        |
| `teca`                   | acc         | 0.46481       | 0.43174   | -7.11%        |
| `wnli`                   | acc         | 0.46479       | 0.42254   | -9.09%        |
| `wnli_es`                | acc         | 0.56338       | 0.59155   | 4.76%         |
| `xnli_en`                | acc         | 0.46225       | 0.47671   | 3.03%         |
| `xnli_va`                | acc         | 0.47505       | 0.48523   | 2.10%         |
| `xstorycloze_en`         | acc         | 0.71145       | 0.70483   | -0.93%        |
| `xstorycloze_es`         | acc         | 0.65255       | 0.65189   | -0.10%        |
| `arc_challenge`          | acc_norm    | 0.40700       | 0.41809   | 2.65%         |
| `arc_easy`               | acc_norm    | 0.72559       | 0.73990   | 1.93%         |
| `belebele_en`            | acc_norm    | 0.21556       | 0.24778   | 13.00%        |
| `belebele_es`            | acc_norm    | 0.22778       | 0.24444   | 6.82%         |
| `openbookqa`             | acc_norm    | 0.39600       | 0.40000   | 1.00%         |
| `openbookqa_es`          | acc_norm    | 0.40800       | 0.40400   | -0.98%        |
| `piqa`                   | acc_norm    | 0.74701       | 0.74701   | 0.00%         |
| `cocoteros_es`           | bleu        | 8.46507       | 6.72269   | -20.58%       |
| `xlsum_es`               | bleu        | 0.80082       | 0.59723   | -25.42%       |
| `triviaqa`               | exact_match | 0.37595       | 0.35432   | -5.75%        |
| `xquad_es`               | exact_match | 0.37731       | 0.36050   | -4.45%        |
| `xquad_es`               | f1          | 0.58413       | 0.56911   | -2.57%        |
| `cocoteros_es`           | rouge1      | 0.33887       | 0.31209   | -7.90%        |
| `xlsum_es`               | rouge1      | 0.13464       | 0.08705   | -35.35%       |
|                          |             |               |           |               |
| **Mean Diff**            |             |               |           | **-2.43%**    |
:
Evaluation results in selected NLP tasks in English and Spanish, in comparison with Salamandra 2B.
:::

Evaluation of Cecilia 2B is still ongoing. At this stage, we present partial results focused on comparing Cecilia 2B to its base model, Salamandra 2B, across a broad suite of standard NLP benchmarks. These tasks include multiple-choice question answering, reading comprehension, paraphrase identification, natural language inference, summarization, translation, and open-domain question answering, in both English and Spanish. @tbl-eval-results summarizes the results of this comparison.

The results show a nuanced picture. Cecilia 2B demonstrates improvements mainly in Spanish and multilingual understanding tasks (e.g., BELEBELE [@belebele], XNLI [@xnli], PAWS [@paws], and some science QA benchmarks [@arc]), reflecting the benefits of continual pretraining on a Cuban Spanish corpus.

However, there are notable decreases in performance on general-purpose and English-centric tasks, as well as summarization and translation benchmarks (e.g., XSUM, Cocoteros, XQuAD [@xquad], and some QA tasks [@openbookqa; @triviaqa]). This is an expected trade-off when adapting a model to a novel language variant using continual pretraining, as some general capabilities may be partially sacrificed for increased in-domain specialization [@goodfellow2013empirical].

It is important to emphasize that these benchmarks are largely general-purpose and not specifically tailored to the Cuban Spanish variant for which Cecilia is intended. The observed average difference is a modest decrease of about 2.4% relative to Salamandra 2B across all tasks, with the largest drops in summarization and translation. This is consistent with expectations, as the model has not yet been fine-tuned for instruction following or for downstream tasks.

Crucially, we do not yet have results on new or custom tasks that target the unique linguistic and cultural phenomena of Cuban Spanish--the primary motivation for Cecilia’s development. As Cecilia 2B is presently only pretrained and has not undergone instruction tuning or task-specific fine-tuning, comprehensive evaluations on downstream tasks such as question answering, dialogue generation, or other domain-specific applications remain pending. These more specialized assessments will be addressed in future work, following the development of an instruction-tuned version of Cecilia that can better support interactive and task-oriented use cases.

## Applications and Use Cases

Cecilia 2B remains a work in progress and is currently most suitable for research purposes. As the model has not yet been fine-tuned for instruction following or specific downstream tasks, its direct applicability in production environments or interactive applications is limited at this stage. However, its foundational capabilities as a Cuban Spanish-pretrained language model open promising avenues for future development.

Once fine-tuned, Cecilia’s relatively small size—approximately 2 billion parameters—combined with its specialized training on Cuban Spanish, positions it as a valuable resource for a range of natural language processing tasks tailored to this linguistic variant. Potential use cases include text generation that respects Cuban cultural and linguistic nuances, sentiment analysis for Cuban social media and news, named entity recognition in local contexts, machine translation with improved handling of Cubanisms, and domain-specific question answering.

Currently, the model is not quantized and requires approximately 14 GB of GPU memory for full loading and inference, which may exceed the hardware capabilities of smaller research teams or institutions with limited computational resources. To address this, quantized versions of Cecilia 2B are planned for release in the near future, which will significantly reduce memory requirements and enable broader accessibility and deployment on more modest hardware setups. This will facilitate wider adoption and experimentation within the Cuban and broader Spanish-speaking NLP research communities.

## Ethical Considerations

As with all large language models, Cecilia 2B is susceptible to issues such as biases and hallucinations. The model has not yet undergone comprehensive evaluation to determine the extent to which these problems persist or whether they are exacerbated relative to the original Salamandra 2B base model. Users should be aware that outputs may reflect unintended biases present in the training data or generate factually incorrect or misleading information.

Furthermore, the training corpus includes copyrighted materials collected under fair use assumptions strictly for academic research. Any use of Cecilia 2B must respect the intellectual property rights of the original content creators and copyright holders. Redistribution or commercial exploitation of the raw training data is prohibited.

Given these considerations and the fact that Cecilia 2B is not yet production-ready, access to the model on the Hugging Face platform is currently gated. Researchers interested in using the model must submit a request, which will be evaluated on a case-by-case basis. Approval is granted for use cases deemed ethical and aligned with responsible research practices. This controlled access aims to mitigate potential misuse and ensure that the model’s deployment aligns with community standards.

In due course, Cecilia 2B will be publicly released under a permissive license that allows broad use, including commercial applications, once further evaluations and refinements have been completed to ensure safety and reliability.

## Future Work

Future efforts will focus initially on further curating and expanding the Cuban Spanish corpus that underpins Cecilia 2B. Enhancing the dataset’s breadth and diversity will improve the model’s linguistic coverage and cultural representation, strengthening its foundation for downstream tasks.

For this particular model, the next key step is to fine-tune Cecilia 2B on general instruction-following tasks to enable more interactive and versatile applications. Subsequently, targeted fine-tuning on specific downstream Cuban Spanish NLP tasks—such as question answering, sentiment analysis, and named entity recognition—will be pursued to maximize its practical utility within the language processing domain.

In parallel, we plan to develop increasingly powerful models by leveraging larger versions of the Salamandra architecture or exploring alternative base models that demonstrate strong performance and suitability for Cuban Spanish. These efforts aim to balance model capacity, efficiency, and cultural specificity, ultimately providing the community with a range of high-quality language models tailored to Cuban Spanish and related linguistic variants.

One specific task that remains challenging is to retrain the tokenizer to better capture cubanisms and other terms that are split into distinct tokens by the Salamandra 2B tokenizer [@rust2021good]. Additionally, quantized versions of all Cecilia models will be published to enable efficient inference in production environments.

## Conclusions

The development of Cecilia 2B represents an initial but promising step toward creating high-quality language models tailored specifically for Cuban Spanish. This work aims not only to address the linguistic and cultural particularities of this variant but also to lay a foundation for future advancements in Cuban Spanish natural language processing.

We hope that this effort will inspire other communities across Latin America and similarly underserved language variants to build upon our experience, fostering a broader movement toward inclusive and diverse language technology development. We warmly invite researchers and practitioners interested in Cuban Spanish language modeling to collaborate, share insights, and contribute to the ongoing evolution of these resources, ultimately advancing the state of NLP for regional and minority language varieties.

## References{.unnumbered}
# Elementos que Necesitan Justificación en el Artículo "Cecilia: El Modelo de Lenguaje Cubano"

## Limitaciones de los Modelos Generalistas

- claim: "Los modelos generalistas, aunque poderosos, presentan limitaciones notables cuando se aplican a lenguas con pocos recursos o a variantes regionales, ya que suelen estar entrenados principalmente con datos de idiomas dominantes y no logran capturar los matices lingüísticos, culturales y contextuales propios de comunidades específicas."
  citation: "On Limitations of LLM as Annotator for Low Resource Languages"
  extract: "Low-resource languages face significant challenges due to the lack of sufficient linguistic data, resources, and tools for tasks such as supervised learning, annotation, and classification. This shortage hinders the development of accurate models and datasets, making it difficult to perform critical NLP tasks like sentiment analysis or hate speech detection."

- claim: "Incluso modelos avanzados como GPT-4o y Llama 3.1 (405B) tienen un rendimiento inferior en comparación con modelos BERT ajustados específicamente para idiomas como el marathi, con márgenes de precisión de 10.2% y 14.1% respectivamente."
  citation: "On Limitations of LLM as Annotator for Low Resource Languages"
  extract: "Even advanced models like GPT-4o and Llama 3.1 405B underperform compared to fine-tuned BERT-based baselines, with GPT-4o and Llama 3.1 405B trailing fine-tuned BERT by accuracy margins of 10.2% and 14.1%, respectively."

- claim: "Las evaluaciones existentes para lenguajes con pocos recursos contienen limitaciones que necesitan ser estudiadas más a fondo, ya que los marcos de evaluación actuales no capturan adecuadamente las inconsistencias culturales en los conjuntos de datos."
  citation: "Filipino Benchmarks for Measuring Sexist and Homophobic Bias in Multilingual Language Models from Southeast Asia"
  extract: "Bias studies on multilingual models confirm the presence of gender-related stereotypes in masked models processing languages with high NLP resources... We also find that for multilingual models, the extent of bias learned for a particular language is influenced by how much pretraining data in that language a model was exposed to."

## Ventajas de Modelos Pequeños para Lenguajes Regionales

- claim: "Los SLMs requieren significativamente menos memoria, almacenamiento y potencia de procesamiento en comparación con los modelos grandes, lo que los hace adecuados para dispositivos con capacidades de hardware limitadas, como smartphones, tablets y dispositivos IoT."
  citation: "InkubaLM: A small language model for low-resource African languages"
  extract: "High-resource language models often fall short in the African context, where there is a critical need for models that are efficient, accessible, and locally relevant, even amidst significant computing and data constraints. This paper introduces InkubaLM, a small language model with 0.4 billion parameters, which achieves performance comparable to models with significantly larger parameter counts and more extensive training data."

- claim: "Los modelos pequeños son más fáciles de ajustar para aplicaciones específicas y dominios lingüísticos particulares."
  citation: "Fox-1: Open Small Language Model for Cloud and Edge"
  extract: "We present Fox-1, a series of small language models (SLMs) consisting of Fox-1-1.6B and Fox-1-1.6B-Instruct-v0.1. These models are pre-trained on 3 trillion tokens of web-scraped document data and fine-tuned with 5 billion tokens of instruction-following and multi-turn conversation data... Fox-1 achieves better or on-par performance in various benchmarks compared to StableLM-2-1.6B, Gemma-2B, Qwen1.5-1.8B, and OpenELM1.1B, with competitive inference speed and throughput."

- claim: "Investigaciones recientes han demostrado que los SLMs pueden proporcionar una comprensión del lenguaje de alta calidad con un consumo de recursos significativamente menor, lo que los hace ideales para habilitar el trabajo digital en contextos lingüísticos específicos."
  citation: "Hymba: A Hybrid-head Architecture for Small Language Models"
  extract: "Notably, Hymba achieves state-of-the-art results for small LMs: Our Hymba-1.5B-Base model surpasses all sub-2B public models in performance and even outperforms Llama-3.2-3B with 1.32% higher average accuracy, an 11.67x cache size reduction, and 3.49x throughput."

## Estrategias para Construir Modelos de Lenguaje Pequeños con Pocos Recursos

- claim: "El preentrenamiento continuo (continual pretraining) ofrece un camino prometedor para la adaptación de dominio con recursos computacionales limitados."
  citation: "Continual Learning for Large Language Models: A Survey"
  extract: "Large language models (LLMs) are not amenable to frequent re-training, due to high training costs arising from their massive scale. However, updates are necessary to endow LLMs with new skills and keep them up-to-date with rapidly evolving human knowledge. This paper surveys recent works on continual learning for LLMs."

- claim: "Investigaciones recientes han demostrado mejoras significativas en el rendimiento a través del entrenamiento incremental en 400 millones de tokens, seguido de entrenamiento adicional para alcanzar mil millones de tokens. Los resultados muestran ganancias notables en tareas intensivas en conocimiento (MMLU +8.1%) y comprensión contextual (HellaSwag +7.6%), mientras revelan compensaciones en la especialización de dominio."
  citation: "Mining Hidden Thoughts from Texts: Evaluating Continual Pretraining with Synthetic Data for LLM Reasoning"
  extract: "Our analysis reveals that Reasoning CPT consistently improves performance across all evaluated domains. Notably, reasoning skills acquired in one domain transfer effectively to others; the performance gap with conventional methods widens as problem difficulty increases, with gains of up to 8 points on the most challenging problems."

- claim: "El preentrenamiento continuo de modelos de lenguaje pequeños en corpus específicos de dominio ha demostrado ser más efectivo que entrenar modelos desde cero. Por ejemplo, en el dominio biomédico, los modelos inicializados con MiniLM y continuamente preentrenados en textos específicos del dominio superaron a los modelos entrenados desde cero con el mismo vocabulario."
  citation: "AF Adapter: Continual Pretraining for Building Chinese Biomedical Language Model"
  extract: "Continual pretraining is a popular way of building a domain-specific pretrained language model from a general-domain language model. In spite of its high efficiency, continual pretraining suffers from catastrophic forgetting, which may harm the model's performance in downstream tasks... The results demonstrate that with only about 17% of model parameters trained, AF Adapter achieves 0.6%, 2% gain in performance on average, compared to strong baselines."

- claim: "El enfoque 'Adapt-and-Distill' representa una estrategia efectiva para desarrollar modelos pequeños, rápidos y efectivos para dominios específicos. Este método combina la adaptación de modelos preentrenados generales y la destilación de conocimiento específico del dominio, logrando un mejor rendimiento mientras se reduce significativamente el tamaño y se aumenta la velocidad del modelo."
  citation: "Adapt-and-Distill: Developing Small, Fast and Effective Pretrained Language Models for Domains"
  extract: "In this paper, we present a general approach to developing small, fast and effective pre-trained models for specific domains. This is achieved by adapting the off-the-shelf general pre-trained models and performing task-agnostic knowledge distillation in target domains... The experimental results demonstrate that our approach achieves better performance over the BERT BASE model in domain-specific tasks while 3.3x smaller and 5.1x faster than BERT BASE."

- claim: "La expansión de vocabulario específico del dominio durante la fase de adaptación y el empleo de la probabilidad de ocurrencia a nivel de corpus para elegir automáticamente el tamaño del vocabulario incremental son técnicas clave en este enfoque. Experimentos en los dominios biomédico e informático han demostrado que esta estrategia logra un mejor rendimiento en tareas específicas del dominio mientras el modelo es 3.3 veces más pequeño y 5.1 veces más rápido que los modelos originales."
  citation: "Adapt-and-Distill: Developing Small, Fast and Effective Pretrained Language Models for Domains"
  extract: "Specifically, we propose domain-specific vocabulary expansion in the adaptation stage and employ corpus level occurrence probability to choose the size of incremental vocabulary automatically... The experimental results demonstrate that our approach achieves better performance over the BERT BASE model in domain-specific tasks while 3.3x smaller and 5.1x faster than BERT BASE."

- claim: "Para lenguajes con recursos extremadamente limitados, el enfoque de 'datos pequeños' ha demostrado ser sorprendentemente efectivo. Investigaciones recientes han desafiado la suposición común de que las lenguas con pocos recursos se benefician del entrenamiento conjunto con lenguas de mayores recursos, demostrando que es posible entrenar modelos de lenguaje multilingües competitivos con menos de 1 GB de texto."
  citation: "Small Data? No Problem! Exploring the Viability of Pretrained Multilingual Language Models for Low-resourced Languages"
  extract: "In this work, we challenge this assumption and present the first attempt at training a multilingual language model on only low-resource languages. We show that it is possible to train competitive multilingual language models on less than 1 GB of text. Our model, named AfriBERTa, covers 11 African languages, including the first language model for 4 of these languages."

- claim: "La combinación de datos sintéticos generados tanto por traducción automática estadística como por modelos de traducción automática neuronal multilingües ha demostrado mejorar el rendimiento para lenguas con pocos recursos debido a la mayor diversidad de los datos sintéticos generados. Esta técnica es particularmente valiosa cuando los datos paralelos bilingües son escasos."
  citation: "Transcending Language Boundaries: Harnessing LLMs for Low-Resource Language Translation"
  extract: "To address this issue, this paper introduces a novel retrieval-based method that enhances translation quality for low-resource languages by focusing on key terms, which involves translating keywords and retrieving corresponding examples from existing data... Our retrieval-based method shows promise in improving both word-level accuracy and overall semantic understanding by leveraging existing resources more effectively."

- claim: "El uso de técnicas eficientes en parámetros como LoRA PEFT (Parameter-Efficient Fine-Tuning) minimiza el número de parámetros durante el ajuste fino, ofreciendo eficiencia computacional y manteniendo la robustez del modelo original al ajustar solo algunos de los parámetros."
  citation: "One-for-All: Generalized LoRA for Parameter-Efficient Fine-tuning"
  extract: "We present Generalized LoRA (GLoRA), an advanced approach for universal parameter-efficient fine-tuning tasks. Enhancing Low-Rank Adaptation (LoRA), GLoRA employs a generalized prompt module to optimize pre-trained model weights and adjust intermediate activations, providing more flexibility and capability across diverse tasks and datasets."

## Proyectos Regionales de Modelos de Lenguaje

- claim: "El proyecto SEALD (Southeast Asian Languages in One Network Data) constituye una de las iniciativas más ambiciosas para fortalecer la presencia digital de las lenguas del Sudeste Asiático. Mediante la colaboración entre AI Singapore y Google Research, se recopilaron y curaron grandes volúmenes de datos multilingües, abarcando idiomas como indonesio, malayo, tamil, birmano, filipino, vietnamita, tailandés, lao y jemer."
  citation: "SEA-LION: Southeast Asian Languages in One Network"
  extract: "Recently, Large Language Models (LLMs) have dominated much of the artificial intelligence scene with their ability to process and generate natural languages. However, the majority of LLM research and development remains English-centric, leaving low-resource languages such as those in the Southeast Asian (SEA) region under-represented. To address this representation gap, we introduce Llama-SEA-LION-v3-8B-IT and Gemma-SEA-LION-v3-9B-IT, two cutting-edge multilingual LLMs designed for SEA languages. The SEA-LION family of LLMs supports 11 SEA languages, namely English, Chinese, Indonesian, Vietnamese, Malay, Thai, Burmese, Lao, Filipino, Tamil, and Khmer."

- claim: "AfriBERTa representa un enfoque innovador para lenguas africanas con pocos recursos, desafiando la suposición de que el entrenamiento conjunto con idiomas de alto recurso es siempre beneficioso. Este modelo fue entrenado exclusivamente con menos de 1 GB de texto de 11 lenguas africanas, incluyendo el primer modelo de lenguaje para cuatro de ellas."
  citation: "Small Data? No Problem! Exploring the Viability of Pretrained Multilingual Language Models for Low-resourced Languages"
  extract: "In this work, we challenge this assumption and present the first attempt at training a multilingual language model on only low-resource languages. We show that it is possible to train competitive multilingual language models on less than 1 GB of text. Our model, named AfriBERTa, covers 11 African languages, including the first language model for 4 of these languages. Evaluations on named entity recognition and text classification spanning 10 languages show that our model outperforms mBERT and XLM-Rin several languages and is very competitive overall."

- claim: "Salamandra es un caso paradigmático de éxito en la construcción de modelos multilingües europeos, sirviendo también como base para adaptaciones regionales como Cecilia. La arquitectura de Salamandra abarca variantes de 2, 7 y 40 mil millones de parámetros, todas entrenadas desde cero sobre un corpus multilingüe cuidadosamente curado de 7.8 billones de tokens en 35 idiomas europeos y código de programación."
  citation: "Salamandra Technical Report"
  extract: "This work introduces Salamandra, a suite of open-source decoder-only large language models available in three different sizes: 2, 7, and 40 billion parameters. The models were trained from scratch on highly multilingual data that comprises text in 35 European languages and code."

- claim: "El modelo utiliza precisión bfloat16, embeddings RoPE, activación SwiGLU, normalización RMS, atención flash y una longitud de contexto de hasta 8,192 tokens, con un vocabulario de 256,000 tokens."
  citation: "Gemma 2: Improving Open Language Models at a Practical Size"
  extract: "In this work, we introduce Gemma 2, a new addition to the Gemma family of lightweight, state-of-the-art open models, ranging in scale from 2 billion to 27 billion parameters. In this new version, we apply several known technical modifications to the Transformer architecture, such as interleaving local-global attentions (Beltagy et al., 2020a) and group-query attention (Ainslie et al., 2023)."

## Arquitectura y Entrenamiento de Cecilia

- claim: "Para el proceso de entrenamiento, el corpus fue tokenizado en secuencias de hasta 1,024 tokens utilizando el tokenizador original de Salamandra 2B, sin modificaciones."
  citation: "RedWhale: An Adapted Korean LLM Through Efficient Continual Pretraining"
  extract: "RedWhale is developed using an efficient continual pretraining approach that includes a comprehensive Korean corpus preprocessing pipeline, a specialized tokenizer, an optimized model initialization technique, and a multistage pretraining strategy. These innovations collectively reduce training time and computational costs while maintaining high levels of accuracy and comprehension."

- claim: "Durante el entrenamiento se emplearon técnicas avanzadas como Fully Sharded Data Parallel (FSDP) y gradient checkpointing para maximizar el uso eficiente de memoria y recursos computacionales, además de validaciones periódicas y monitoreo de métricas para garantizar la robustez y generalización del modelo."
  citation: "Scaling Down to Scale Up: A Guide to Parameter-Efficient Fine-Tuning"
  extract: "This paper presents a systematic overview of parameter-efficient fine-tuning methods, covering over 50 papers published between early 2019 and mid-2024. These methods aim to address the challenges of fine-tuning large language models by training only a small subset of parameters."

## Evaluación

- claim: "En promedio, la reducción relativa de desempeño es de apenas 2.4% respecto al modelo base, una diferencia no significativa considerando la magnitud del cambio en los datos de entrenamiento y la especialización lograda."
  citation: "Continuous Training and Fine-tuning for Domain-Specific Language Models in Medical Question Answering"
  extract: "Large language models exhibit promising general capabilities but often lack specialized knowledge for domain-specific tasks. Developing domain experts from a base model enables a range of applications without prohibitive training costs. This work demonstrates a method using continuous training and instruction fine-tuning to rapidly adapt Llama 2 base models to the Chinese medical domain."

## Discusión

- claim: "El corpus utilizado, si bien diverso y representativo, podría inducir sesgos hacia los dominios más representados, como prensa y enciclopedias, en detrimento de registros menos frecuentes o más formales, lo que podría limitar la cobertura de ciertos contextos y estilos lingüísticos."
  citation: "Crowdsource, Crawl, or Generate? Creating SEA-VL, a Multicultural Vision-Language Dataset for Southeast Asia"
  extract: "Southeast Asia (SEA) is a region of extraordinary linguistic and cultural diversity, yet it remains significantly underrepresented in vision-language (VL) research. This often results in artificial intelligence (AI) models that fail to capture SEA cultural nuances. To fill this gap, we present SEA-VL, an open-source initiative dedicated to developing high-quality, culturally relevant data for SEA languages."

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/5928523/175a8840-18f3-47e0-8022-e323b2bd04f5/paper.pdf
[2] https://arxiv.org/abs/2402.17400
[3] https://aclanthology.org/2021.emnlp-main.436
[4] https://ieeexplore.ieee.org/document/10378115/
[5] https://arxiv.org/abs/2402.01364
[6] https://arxiv.org/abs/2408.11294
[7] https://arxiv.org/abs/2409.19854
[8] https://www.semanticscholar.org/paper/cda9ad68b474fd4735ac73e3557054ba737268d3
[9] https://ieeexplore.ieee.org/document/10385733/
[10] https://www.semanticscholar.org/paper/ed0689265c039a1e5adae8d2596b22b8833aac95
[11] https://aclanthology.org/2024.findings-emnlp.949
[12] https://aclanthology.org/2023.nlposs-1.26
[13] https://www.semanticscholar.org/paper/b9f9ab36de78257eb9800999512469dc1b5abf8e
[14] https://arxiv.org/abs/2312.00738
[15] https://arxiv.org/abs/2504.05747
[16] https://arxiv.org/abs/2503.07920
[17] https://www.tandfonline.com/doi/full/10.1080/01431161.2023.2297179
[18] https://arxiv.org/abs/2412.07303
[19] https://journals.bilpubgroup.com/index.php/jasr/article/view/6335
[20] https://link.springer.com/10.1007/s00382-023-06960-y
[21] https://gmd.copernicus.org/articles/17/7285/2024/
[22] https://dl.acm.org/doi/10.1145/3626772.3657952
[23] https://aclanthology.org/2021.mrl-1.11
[24] https://arxiv.org/abs/2410.08728
[25] https://aclanthology.org/2023.semeval-1.48
[26] https://www.ejmanager.com/fulltextpdf.php?mno=216117
[27] https://aclanthology.org/2023.semeval-1.297
[28] https://aclanthology.org/2023.semeval-1.165
[29] https://arxiv.org/abs/2408.17024
[30] https://ieeexplore.ieee.org/document/10292494/
[31] https://arxiv.org/abs/2211.03263
[32] https://arxiv.org/abs/2306.07967
[33] https://arxiv.org/abs/2405.15179
[34] https://arxiv.org/abs/2405.03003
[35] https://arxiv.org/abs/2401.04679
[36] https://arxiv.org/abs/2405.12130
[37] https://arxiv.org/abs/2405.19597
[38] https://www.semanticscholar.org/paper/6007263dd3d14373be5f84fb6ccb0be3f7fce903
[39] https://ieeexplore.ieee.org/document/10589847/
[40] https://arxiv.org/abs/2405.17357
[41] https://arxiv.org/abs/2402.12851
[42] https://arxiv.org/abs/2409.12191
[43] https://arxiv.org/abs/2404.04167
[44] https://arxiv.org/abs/2404.01549
[45] https://www.semanticscholar.org/paper/2dc8a283eab8e40ab4a4151bbbd827531811a486
[46] https://arxiv.org/abs/2404.01331
[47] https://aclanthology.org/2024.naacl-industry.1
[48] https://www.isca-archive.org/odyssey_2024/bellver24_odyssey.html
[49] https://aclanthology.org/2024.semeval-1.278
[50] https://www.semanticscholar.org/paper/dcdd353caa8c8b836986fc51c36e613999341d0b
[51] https://arxiv.org/abs/2501.05952
[52] https://www.nature.com/articles/s41698-025-00935-4
[53] https://www.nature.com/articles/s41598-025-97131-y
[54] https://arxiv.org/abs/2409.00084
[55] http://pubs.rsna.org/doi/10.1148/radiol.240895
[56] https://sol.sbc.org.br/index.php/stil/article/view/31116
[57] https://jai.in.ua/index.php/en/issues?paper_num=1648
[58] https://www.cureus.com/articles/305600-chatgpt-4-turbo-and-metas-llama-31-a-relative-analysis-of-answering-radiology-text-based-questions
[59] https://arxiv.org/abs/2408.02201
[60] https://arxiv.org/abs/2411.00622
[61] https://arxiv.org/abs/2411.17637
[62] https://www.semanticscholar.org/paper/a8b2c6bd0952066e61ff3a26cf98b5f13dbda1c6
[63] https://arxiv.org/abs/2411.11295
[64] https://ieeexplore.ieee.org/document/10825891/
[65] https://aclanthology.org/2024.nllp-1.30
[66] https://www.semanticscholar.org/paper/8731ad00e4c8050fcfc44fbfbd884ff6fb822594
[67] https://www.semanticscholar.org/paper/15e8671f3212f396280ad29c4814bdf9b990e1f4
[68] https://arxiv.org/abs/2411.13676
[69] https://www.semanticscholar.org/paper/4d8734b4445d875b4526b96162792605cb020e65
[70] https://arxiv.org/abs/2401.06066
[71] https://www.semanticscholar.org/paper/d670ac8d5fbef903c826643690c6a5d4392fde7f
[72] https://arxiv.org/abs/2408.00118
[73] https://arxiv.org/abs/2404.07839
[74] https://arxiv.org/abs/2403.20041
[75] https://arxiv.org/html/2502.08489v2
[76] https://arxiv.org/html/2503.10192v1
[77] https://arxiv.org/pdf/2408.00118.pdf
[78] https://arxiv.org/pdf/2402.17834.pdf
[79] https://aclanthology.org/2021.findings-acl.40
[80] https://arxiv.org/abs/2311.00204
[81] https://arxiv.org/abs/2409.03444
[82] https://arxiv.org/abs/2310.03328
[83] https://arxiv.org/abs/2403.18365
[84] https://academic.oup.com/jamia/article/31/9/1833/7645318
[85] https://arxiv.org/abs/2403.09296
[86] https://arxiv.org/abs/2411.19930
[87] https://www.semanticscholar.org/paper/81925c8d25944d17123fa05186993a2ef7ec63d7
[88] https://journals.uran.ua/itssi/article/view/308823
[89] https://arxiv.org/abs/2306.05406
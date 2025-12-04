# cliff_continual_learning_workflow - Complete PRD Documentation

## Overview
PRDs for nodes in the 'cliff_continual_learning_workflow' module.

## Table of Contents

- [collect_new_material_datasets](#collect_new_material_datasets)

- [collect_reference_material_dataset](#collect_reference_material_dataset)

- [compute_accuracy_and_forgetting_metrics](#compute_accuracy_and_forgetting_metrics)

- [configure_training_hyperparameters](#configure_training_hyperparameters)

- [define_knowledge_distillation_loss](#define_knowledge_distillation_loss)

- [define_project_scope](#define_project_scope)

- [design_backbone_and_base_head](#design_backbone_and_base_head)

- [evaluate_cliff_performance](#evaluate_cliff_performance)

- [freeze_backbone_and_base_head](#freeze_backbone_and_base_head)

- [generate_comparative_results_table](#generate_comparative_results_table)

- [implement_cosine_similarity_gate](#implement_cosine_similarity_gate)

- [implement_delta_head](#implement_delta_head)

- [implement_prompt_pool_structure](#implement_prompt_pool_structure)

- [incremental_train_material_specific_components](#incremental_train_material_specific_components)

- [preprocess_images](#preprocess_images)

- [produce_visualizations](#produce_visualizations)

- [set_up_memory_replay_buffer](#set_up_memory_replay_buffer)

- [split_datasets](#split_datasets)

- [train_base_model_on_reference](#train_base_model_on_reference)

- [train_naive_fine_tuning_baseline](#train_naive_fine_tuning_baseline)

- [train_prompt_based_baseline](#train_prompt_based_baseline)

- [write_summary_report](#write_summary_report)



---

## collect_new_material_datasets

### Description
Gather labeled optical‑microscopy datasets for each additional 2D material that will be introduced sequentially.

### Implementation Plan

#### 1. Select three target 2D materials (MoS2, WS2, h‑BN) based on literature prevalence and availability of exfoliation sources.

| Category | Details |
| --- | --- |
| **Reason** | Choosing well‑studied materials ensures that reference data exists and that downstream models have meaningful class diversity. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Consult recent 2D‑material review papers; create a table mapping material → typical flake thickness range; confirm substrate compatibility (SiO2/Si). |

#### 2. Define standard substrate preparation protocol for each material (clean SiO2 wafer, spin‑coat PMMA optional, annealing temperature).

| Category | Details |
| --- | --- |
| **Reason** | Consistent substrate preparation reduces systematic imaging variance across materials, facilitating fair model comparison. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write SOP document; include cleaning steps (piranha, acetone, IPA), bake temperature (150 °C, 5 min), and storage conditions; store SOP as markdown in repo. |

#### 3. Specify optical‑microscope configuration: illumination type (bright‑field), objective magnification (50×), numerical aperture (0.8), exposure time (10 ms), pixel resolution (0.2 µm/pixel).

| Category | Details |
| --- | --- |
| **Reason** | Uniform imaging settings enable direct pixel‑wise comparison and reduce domain shift when training the backbone. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a calibration checklist; capture a reference grid image before each acquisition session; log settings in a CSV file per session. |

#### 4. Create a data‑capture schedule: for each material, acquire at least 5,000 raw images covering different flake sizes, orientations, and defect types.

| Category | Details |
| --- | --- |
| **Reason** | A minimum sample size guarantees statistical significance for class‑balance during stratified splitting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a spreadsheet tracker with columns: material, session_id, image_id, flake_id, target_layer_count; aim for ~1,000 images per layer class (1‑5 L). |

#### 5. Develop annotation guidelines: define label taxonomy (layer_count ∈ {1,2,3,4,5}, defect_type ∈ {none, tear, wrinkle, contamination}), image_quality thresholds (SNR > 10 dB, no motion blur).

| Category | Details |
| --- | --- |
| **Reason** | Clear, reproducible annotation rules ensure high inter‑annotator agreement and reliable downstream training. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Write a 2‑page protocol, include example annotated images; integrate into labeling tool (e.g., Labelbox) with mandatory fields; enforce validation scripts to reject out‑of‑range values. |

#### 6. Execute labeling workflow: assign two independent annotators per image, resolve conflicts via a senior reviewer, and export consolidated CSV per material.

| Category | Details |
| --- | --- |
| **Reason** | Dual‑annotation plus arbitration reduces labeling errors and provides a reliability metric (Cohen’s κ). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Automate assignment using a Python script that pulls image paths from the capture directory; schedule weekly review meetings; store final CSV in <project_root>/metadata/<material>_labels.csv. |

#### 7. Store each material’s labeled dataset in a version‑controlled cloud bucket (e.g., gs://cliff-datasets/<material>/) using a directory layout: raw/, annotated/, splits/. Include a manifest JSON summarizing counts and hash values.

| Category | Details |
| --- | --- |
| **Reason** | Centralized, immutable storage simplifies reproducibility and enables downstream pipeline access across compute nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use gsutil to sync local folders; generate manifest via a Bash/Python one‑liner that computes SHA256 for each file; commit manifest to Git. |

#### 8. Perform stratified train/validation/test split per material with a 70/15/15 ratio, ensuring each layer class is proportionally represented in each split.

| Category | Details |
| --- | --- |
| **Reason** | Stratification preserves class distribution, preventing skewed performance metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a Python function using sklearn.model_selection.StratifiedShuffleSplit; output three JSON files (train_<material>.json, val_<material>.json, test_<material>.json) containing file paths and label metadata. |

#### 9. Populate the output fields: list of material names, collection method strings, annotation guideline summaries, storage paths, split ratio strings, total image counts after QC, and set is_dataset_ready = true only if all previous steps succeeded without errors.

| Category | Details |
| --- | --- |
| **Reason** | Fulfilling the defined output structure is required for downstream nodes to consume the data correctly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Write a final aggregation script that reads the manifest, counts images per material, validates existence of split JSONs, and writes a single JSON payload matching the Output Structure schema. |


---

## collect_reference_material_dataset

### Description
Gather a labeled optical‑microscopy dataset for the reference 2D material that will be used to pre‑train the backbone and base head.

### Implementation Plan

#### 1. Define the reference material (e.g., graphene) and assign a concise dataset identifier such as "graphene_optical_dataset".

| Category | Details |
| --- | --- |
| **Reason** | A clear identifier ensures downstream nodes can reference the dataset unambiguously and avoids naming collisions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a constant string variable; embed the material name; store in the output field `dataset_name`. |

#### 2. Compile a comprehensive list of publicly available and in‑house sources that contain high‑resolution optical‑microscopy images of the reference material.

| Category | Details |
| --- | --- |
| **Reason** | Using multiple sources maximizes dataset diversity, improves model generalisation, and satisfies reproducibility requirements. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Search repositories (e.g., Materials Cloud, NanoHUB, university data portals), query literature for supplementary datasets, and record URLs or lab inventory IDs in `source_list`. |

#### 3. For each source, document the acquisition protocol: microscope type, objective magnification, illumination wavelength, exposure time, pixel resolution, and any preprocessing performed by the source.

| Category | Details |
| --- | --- |
| **Reason** | Explicit acquisition metadata enables reproducible reconstruction of raw image conditions and supports later quality‑control steps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a step‑by‑step bullet list per source and concatenate them into the `acquisition_steps` array; use a templated format: "[Source] – Set XYZ, capture 2048×2048 PNG at 100× magnification". |

#### 4. Download or request the raw image files, preserving original filenames and metadata (EXIF, TIFF tags). Store them in a temporary staging directory organized by source.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining original structure prevents loss of provenance and facilitates checksum verification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a shell script (or Python `requests`/`gdown`) that iterates over `source_list`, saves files to `<staging_dir>/<source_name>/`, and logs MD5 hashes. |

#### 5. Define the annotation schema required for each image: at minimum `layer_count` (integer), optional `flake_id` (string), and optional `defect_label` (enumerated). Record this schema in `annotation_requirements`.

| Category | Details |
| --- | --- |
| **Reason** | A standardized annotation format ensures consistency across sources and downstream training pipelines. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a JSON schema file and list its field names in the output list. |

#### 6. Perform manual or semi‑automated annotation of each image according to the schema. Use tools such as LabelImg, CVAT, or custom Python scripts that overlay layer‑count tables from source papers.

| Category | Details |
| --- | --- |
| **Reason** | Accurate labeling is crucial for supervised pre‑training; semi‑automated methods speed up the process while preserving quality. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Assign a trained annotator, generate a CSV `annotations.csv` with columns `filename,layer_count,flake_id,defect_label`; store alongside images. |

#### 7. Execute verification steps: (a) compute and record checksums for each image, (b) run a visual inspection checklist (focus, illumination uniformity, artefacts), (c) validate that every image has a matching annotation entry, (d) ensure `layer_count` values are within expected physical limits (1‑10 layers for graphene). Append each step description to `verification_steps`.

| Category | Details |
| --- | --- |
| **Reason** | Verification guarantees dataset integrity, prevents garbage‑in‑garbage‑out during model training, and satisfies reproducibility audits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a Python validation script that reads the staging directory, checks MD5 against recorded values, cross‑references the CSV, and logs any inconsistencies; failures raise exceptions. |

#### 8. Select a storage format that is both efficient for large‑scale training and easy to stream: choose TFRecord for TensorFlow pipelines or HDF5 for PyTorch, and also keep a human‑readable CSV manifest.

| Category | Details |
| --- | --- |
| **Reason** | Optimised storage reduces I/O bottlenecks, enables sharding, and ensures compatibility with downstream training code. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write a conversion script that reads images and annotations, writes them into TFRecord files (one file per 1,000 samples) and concurrently writes a `manifest.csv`; set `storage_format` accordingly. |

#### 9. Persist the finalized dataset to a permanent location: e.g., `gs://my‑project-data/datasets/graphene_optical_dataset/` or `/mnt/data/datasets/graphene_optical_dataset/`. Record the absolute URI in `dataset_path`.

| Category | Details |
| --- | --- |
| **Reason** | A fixed, versioned location enables downstream nodes to reliably locate the dataset without ambiguity. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Copy TFRecord shards and manifest CSV to the chosen bucket using `gsutil` or `rsync`; verify copy via checksum. |

#### 10. Calculate `total_samples` by counting the number of image‑annotation pairs stored; set `is_ready_for_pretraining` to `true` only if all verification steps passed without errors.

| Category | Details |
| --- | --- |
| **Reason** | Providing explicit counts and a ready flag allows downstream training nodes to make conditional decisions (e.g., abort if dataset incomplete). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run `len(annotations.csv)`; set boolean based on exit status of verification script. |


---

## compute_accuracy_and_forgetting_metrics

### Description
Aggregate performance numbers for CLIFF, naive fine‑tuning, and prompt‑only baselines, computing both accuracy and forgetting.

### Implementation Plan

#### 1. Define a deterministic file‑naming convention for each model’s test‑result artefact (e.g., `results/<model_id>/test_metrics.json`) and store the path in a constant dictionary for lookup.

| Category | Details |
| --- | --- |
| **Reason** | A uniform naming scheme eliminates ambiguity when loading data from disparate training pipelines and enables reproducible aggregation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a Python dict: `RESULT_PATHS = {'CLIFF': 'results/CLIFF/test_metrics.json', 'NaiveFineTuning': 'results/NaiveFineTuning/test_metrics.json', 'PromptBaseline': 'results/PromptBaseline/test_metrics.json'}`. Validate existence with `os.path.exists` and raise a clear error if missing. |

#### 2. Load per‑material test accuracies from each JSON file; each file must contain a mapping `material_name -> top1_accuracy` and a list `ordered_materials` that reflects the chronological learning order.

| Category | Details |
| --- | --- |
| **Reason** | Both the per‑material accuracy and the order of learning are required to compute forgetting correctly. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper `load_metrics(path)` that returns `(ordered_materials, acc_dict)`. Use `json.load` and assert that all expected materials from `split_datasets.material_names` are present. |

#### 3. Validate that the material order is identical across all three models; if not, re‑order each model’s accuracy list to match the canonical order from `split_datasets.material_names`.

| Category | Details |
| --- | --- |
| **Reason** | Consistent ordering guarantees that per‑material lists line up when constructing the final output structure. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the canonical material list and build ordered accuracy lists: `cliff_acc = [cliff_dict[m] for m in canonical]` etc. Log a warning if any model is missing a material and insert `None` (later handled as `nan`). |

#### 4. Compute mean accuracy for each model by averaging over the ordered per‑material accuracies, ignoring `nan` entries.

| Category | Details |
| --- | --- |
| **Reason** | Mean accuracy is a primary evaluation metric required by downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `np.nanmean(np.array(acc_list, dtype=float))` from NumPy for robust handling of missing values. |

#### 5. Implement the forgetting calculation: for a given model, iterate over the learning sequence; for each material *i* compute the drop `acc_i_before - acc_i_after` where `acc_i_before` is the accuracy recorded immediately after material *i* was first learned, and `acc_i_after` is the accuracy after the final material has been learned. Average these drops across all *i* to obtain the forgetting metric.

| Category | Details |
| --- | --- |
| **Reason** | Forgetting measures catastrophic loss of knowledge; the definition matches that of `evaluate_cliff_performance` and ensures comparability across baselines. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Assume each model’s JSON contains a list `cumulative_accuracies` where entry *k* is the accuracy on material *k* after training up to material *k*. Compute `drops = [cum_acc[i] - final_acc[i] for i in range(num_materials-1)]` and take the mean. If `cumulative_accuracies` is absent, fallback to the simple definition `mean(initial_accuracy - final_accuracy)`. |

#### 6. Assemble the final output dictionary with keys matching the declared `output_structure` (models, materials, per‑material lists, means, forgettings). Convert the entire dict to a JSON string with `json.dumps(..., indent=2, sort_keys=True)` and store under `summary_json`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a single JSON‑formatted string; sorting keys improves readability and deterministic output for testing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
output = {
    "models": ["CLIFF", "NaiveFineTuning", "PromptBaseline"],
    "materials": canonical,
    "cliff_per_material_accuracy": cliff_acc,
    "naive_fine_tuning_per_material_accuracy": naive_acc,
    "prompt_baseline_per_material_accuracy": prompt_acc,
    "cliff_mean_accuracy": cliff_mean,
    "naive_fine_tuning_mean_accuracy": naive_mean,
    "prompt_baseline_mean_accuracy": prompt_mean,
    "cliff_forgetting": cliff_forget,
    "naive_fine_tuning_forgetting": naive_forget,
    "prompt_baseline_forgetting": prompt_forget,
    "summary_json": json.dumps(...)
}
``` |

#### 7. Add robust error handling: wrap each I/O operation in try/except blocks, log missing files, malformed JSON, or mismatched material sets, and raise a custom `MetricsAggregationError` with a clear message.

| Category | Details |
| --- | --- |
| **Reason** | Early failure detection simplifies debugging of upstream pipelines and prevents silent propagation of incorrect metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a small utility module `utils.py` with `load_json(path)` and `assert_materials_match(list1, list2)` functions. Use Python's `logging` module at INFO level for normal operation and ERROR level for failures. |

#### 8. Write unit tests covering: (a) correct loading and ordering, (b) mean calculation with NaNs, (c) forgetting computation on a synthetic cumulative‑accuracy series, and (d) JSON output schema compliance.

| Category | Details |
| --- | --- |
| **Reason** | Automated testing guarantees that future changes to parent nodes or data formats do not break this aggregation step. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `pytest` with fixtures that generate temporary result JSON files. Validate that `compute_accuracy_and_forgetting_metrics()` returns a dict whose fields match the `output_structure` types. |

#### 9. Document the function in a docstring that mirrors the node’s prompt, includes parameter descriptions (`result_paths`), return type (`dict`), and an example of the produced `summary_json`.

| Category | Details |
| --- | --- |
| **Reason** | Clear documentation aids downstream developers and ensures the function can be called programmatically without re‑reading the prompt. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Follow Google Python style guide for docstrings. |


---

## configure_training_hyperparameters

### Description
Set learning rates, batch sizes, optimizer types, and schedule for both base pre‑training and incremental material training.

### Implementation Plan

#### 1. Extract dimensionality and parameter count from `design_backbone_and_base_head` (backbone_layers, base_head_input_dimension, base_head_output_dimension) to guide optimizer and learning‑rate scaling decisions.

| Category | Details |
| --- | --- |
| **Reason** | Backbone size directly affects stable training regimes; larger models typically need smaller LR to avoid divergence. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the JSON output of the parent node, compute total parameter count, and apply a rule‑based scaling: base_lr = 1e‑4 * (100M / total_params). |

#### 2. Select AdamW as `base_optimizer` because it decouples weight decay from the gradient update, which is beneficial for transformer‑style prompt vectors and ResNet backbones.

| Category | Details |
| --- | --- |
| **Reason** | AdamW provides robust convergence on mixed‑precision training and is widely used in CL literature. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Hard‑code optimizer name "AdamW" and expose weight_decay (e.g., 0.01) as a constant that can be overridden via config. |

#### 3. Set `base_learning_rate` to 1e‑4, `base_batch_size` to 64, and `base_epochs` to 30 based on empirical studies for ResNet‑50 on optical‑microscopy datasets.

| Category | Details |
| --- | --- |
| **Reason** | These values balance convergence speed and generalization; batch size 64 fits typical GPU memory for 224×224 images. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign static values; annotate that they can be tuned via a hyper‑parameter sweep if GPU resources allow. |

#### 4. Derive incremental learning rates (`incremental_prompt_learning_rate` and `incremental_delta_learning_rate`) from the base LR using a decay factor of 0.5 for prompts and 0.3 for delta head (e.g., 5e‑5 and 3e‑5 respectively).

| Category | Details |
| --- | --- |
| **Reason** | Prompts are lightweight and benefit from a slightly higher LR than the delta head, which is deeper and more prone to over‑fitting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute: incremental_prompt_lr = base_lr * 0.5; incremental_delta_lr = base_lr * 0.3; round to 5e‑5 and 3e‑5. |

#### 5. Choose `incremental_batch_size` = 32 and `incremental_epochs` = 15 for each new material, reflecting the smaller data volume per material and the need for faster convergence during continual learning.

| Category | Details |
| --- | --- |
| **Reason** | Smaller batches reduce memory pressure when mixing replay samples; fewer epochs avoid catastrophic forgetting while still allowing prompt/delta adaptation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set constants; document that batch size can be scaled with GPU memory availability. |

#### 6. Define `replay_ratio` as "1:3" (one replay sample per three new material samples) to maintain a balanced proportion of historic knowledge while focusing on new data.

| Category | Details |
| --- | --- |
| **Reason** | Empirical CL studies show a 1:3 ratio mitigates forgetting without overwhelming the optimizer with old data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Hard‑code string "1:3"; expose as a tunable parameter in the configuration file. |

#### 7. Compose a concise `rationale` field that succinctly explains each hyper‑parameter choice, linking back to model size, dataset characteristics, and continual‑learning theory.

| Category | Details |
| --- | --- |
| **Reason** | Providing rationale improves reproducibility and aids future hyper‑parameter tuning. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template‑based string generation: concatenate explanations from previous bullets into a single paragraph. |

#### 8. Validate that all output fields conform to the declared PrimitiveTypes and serialize them into a JSON object for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect strict type adherence; early validation prevents runtime errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a schema validator (e.g., using jsonschema) that checks type and presence of each key before returning the final output. |


---

## define_knowledge_distillation_loss

### Description
Formulate a loss that distills knowledge from the frozen base model into the evolving CLIFF model using replay samples.

### Implementation Plan

#### 1. Load replay buffer metadata from the parent node `set_up_memory_replay_buffer` (buffer_directory, exemplar_file_paths, class_ids) and deserialize the stored base logits for each exemplar into a tensor `Z_base` of shape [N_replay, C] where C is the number of classes.

| Category | Details |
| --- | --- |
| **Reason** | The distillation term requires the frozen base model's logits for the exact replay samples; loading them once at the start avoids repeated forward passes through the frozen model. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a lightweight JSON/YAML parser to read a manifest file located in `buffer_directory` that maps each exemplar path to its stored logits; then stack logits into a PyTorch tensor on the same device as the training model. |

#### 2. Define the classification loss function `L_{cls}` as standard categorical cross‑entropy (CE) between the current model logits `Z_curr` for the *new* material batch and the one‑hot ground‑truth labels `y`.

| Category | Details |
| --- | --- |
| **Reason** | Cross‑entropy is the de‑facto loss for multi‑class classification and aligns with the evaluation metric (top‑1 accuracy). |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement `torch.nn.CrossEntropyLoss(reduction='mean')` and expose its string name as `classification_loss_type = "cross_entropy"`. |

#### 3. Define the distillation loss function `L_{kd}` as the Kullback‑Leibler divergence between the current model logits `Z_curr^{replay}` (softmax temperature‑scaled) and the stored base logits `Z_base` (also temperature‑scaled). Use PyTorch's `KLDivLoss` with `log_target=False` and `reduction='batchmean'`.

| Category | Details |
| --- | --- |
| **Reason** | KL‑divergence measures how well the student (current CLIFF model) mimics the teacher (frozen base) on replayed exemplars, encouraging retention of previously learned knowledge. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply temperature `T` (commonly T=2) to both logits: `p = softmax(Z_curr^{replay} / T)`, `q = softmax(Z_base / T)`. Compute `L_{kd} = KLDivLoss(log(p), q) * (T^2)` to correct gradient scaling. |

#### 4. Introduce a weighting hyper‑parameter `λ_{kd}` (named `distillation_weight`) to balance the two objectives: `L = L_{cls} + λ_{kd} * L_{kd}`.

| Category | Details |
| --- | --- |
| **Reason** | A scalar weight lets practitioners tune the trade‑off between learning new material and preserving old knowledge; typical values lie in [0.1, 1.0]. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set `weighting_hyperparameter_name = "distillation_weight"` and propose a default `weighting_hyperparameter_value = 0.5`. Document that this value can be overridden via the training‑hyperparameter config. |

#### 5. Compose the final loss expression string `loss_expression` in LaTeX‑compatible notation, e.g.:

```
L = \underbrace{\text{CE}(Z_{curr}^{new}, y)}_{\text{classification}} + \lambda_{kd}\,\underbrace{\text{KL}\big(\text{softmax}(Z_{curr}^{replay}/T) \| \text{softmax}(Z_{base}/T)\big)}_{\text{distillation}}
```

| Category | Details |
| --- | --- |
| **Reason** | Providing a clear mathematical formula is required by downstream documentation and ensures reproducibility across implementations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | String‑format the expression using the variable names defined above; embed LaTeX delimiters for readability. |

#### 6. Validate shape compatibility: assert that `Z_curr^{replay}` and `Z_base` share the same class dimension `C`, and that the batch size of replay samples matches the number of stored logits.

| Category | Details |
| --- | --- |
| **Reason** | Mismatched dimensions would cause runtime errors during loss computation and break the training loop. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Insert a runtime check `assert Z_curr_replay.shape == Z_base.shape` with an informative error message. |

#### 7. Export the five required output fields (`loss_expression`, `classification_loss_type`, `distillation_loss_type`, `weighting_hyperparameter_name`, `weighting_hyperparameter_value`) as plain strings/floats according to the node's output schema.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (`incremental_train_material_specific_components`) consume these fields to construct the actual training step; strict type adherence avoids serialization issues. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Populate a Python dict with the keys and cast values to `str` or `float` as required; serialize to JSON if needed. |


---

## define_project_scope

### Description
State the precise research goals, performance metrics, and constraints for the CLIFF framework.

### Implementation Plan

#### 1. Gather domain‑specific requirements by reviewing recent literature on optical‑microscopy flake‑layer classification and consulting project stakeholders to capture the overarching research intent.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the scope reflects both state‑of‑the‑art capabilities and the actual needs of the research team. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conduct a brief literature survey (e.g., 5‑7 recent papers), hold a 30‑minute stakeholder interview, and summarize key goals in a bullet list. |

#### 2. Formulate a single‑sentence primary objective that explicitly mentions (a) continual learning, (b) classification of flake layers, and (c) the use of optical microscopy images.

| Category | Details |
| --- | --- |
| **Reason** | A concise, well‑crafted objective provides a clear north‑star for all downstream development. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Combine the three required elements using the template: "Develop a continual‑learning framework that accurately classifies the number of layers in 2D material flakes from optical‑microscopy images while preserving knowledge of previously learned materials." |

#### 3. Enumerate evaluation metrics that will quantitatively measure both instantaneous performance and knowledge retention, such as top‑1 accuracy per material, mean accuracy across all materials, forgetting (accuracy drop on earlier materials), and optional secondary metrics like macro‑F1 or inference latency.

| Category | Details |
| --- | --- |
| **Reason** | A comprehensive metric set enables rigorous assessment of the continual‑learning trade‑off between plasticity and stability. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a list of strings: ["top‑1 accuracy", "mean accuracy", "forgetting", "macro‑F1 (optional)", "inference latency (optional)"] and justify each choice in a comment. |

#### 4. Identify high‑level system constraints that must be respected throughout the project, including: (1) backbone network weights are frozen after pre‑training, (2) prompt vectors and delta head are the only trainable components during incremental phases, (3) memory replay buffer size ≤ 5 % of total training samples, (4) maximum GPU memory footprint ≤ 12 GB, and (5) data privacy compliance (no external data sharing).

| Category | Details |
| --- | --- |
| **Reason** | Explicit constraints prevent scope creep and guide architectural decisions such as model size and replay strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Write each constraint as a concise string and optionally prefix with a category tag (e.g., "[Model] frozen backbone"). |

#### 5. Populate the three output fields (primary_objective, evaluation_metrics, high_level_constraints) using the strings and lists created in the previous steps, ensuring they conform to the declared PrimitiveTypes.

| Category | Details |
| --- | --- |
| **Reason** | Transforms the narrative scope into the machine‑readable JSON structure required by downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign: primary_objective = <sentence from bullet 2>; evaluation_metrics = <list from bullet 3>; high_level_constraints = <list from bullet 4>. |

#### 6. Validate the constructed output against the schema: check that primary_objective is a non‑empty string, evaluation_metrics is a non‑empty list of strings, and high_level_constraints is a non‑empty list of strings; raise a clear error if any check fails.

| Category | Details |
| --- | --- |
| **Reason** | Automatic validation catches formatting bugs early, avoiding downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a simple assert‑style function or use a JSON schema validator (e.g., jsonschema.validate) with the defined output_structure. |

#### 7. Return the final JSON object containing the three fields, ready to be consumed by the downstream node `design_backbone_and_base_head`.

| Category | Details |
| --- | --- |
| **Reason** | Completes the node’s responsibility and provides a clean hand‑off to the next stage of the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the Python dict to JSON (or directly output the dict in the system) and ensure no extra fields are present. |


---

## design_backbone_and_base_head

### Description
Specify the CNN backbone architecture and the classification head that will be initially trained on the reference material.

### Implementation Plan

#### 1. Extract high‑level constraints from the parent node `define_project_scope` (e.g., frozen backbone, target accuracy) to bound the design space for the backbone and head.

| Category | Details |
| --- | --- |
| **Reason** | Using the explicit constraints guarantees that the chosen architecture aligns with the project’s primary objective and evaluation metrics. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `high_level_constraints` list from the parent output, parse entries such as "frozen backbone" and "limited parameter budget", and store them in a local configuration object. |

#### 2. Select ResNet‑50 as the backbone because it offers a good trade‑off between representational power and computational cost, and its architecture is well‑studied for transfer learning in microscopy domains.

| Category | Details |
| --- | --- |
| **Reason** | ResNet‑50 provides pretrained weights on ImageNet, which can be fine‑tuned or frozen as required, and its block structure simplifies layer‑wise inspection. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Set `backbone_architecture` = "ResNet-50". Enumerate each stage (conv1, bn1, relu, maxpool, layer1‑layer4, avgpool, flatten) with output channel dimensions (e.g., conv1: 7×7×64, layer1: 256, …) and store as strings in `backbone_layers`. |

#### 3. Determine the dimensionality of the backbone’s final feature vector (2048 for ResNet‑50 after global average pooling) and define the base head as a single fully‑connected layer mapping to the number of flake‑layer classes.

| Category | Details |
| --- | --- |
| **Reason** | A simple linear head is sufficient for the initial reference‑material pre‑training and keeps the parameter count low, respecting the frozen‑backbone constraint. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `base_head_architecture` = "Fully‑Connected (Linear) layer". Set `base_head_input_dimension` = 2048. Compute `base_head_output_dimension` by counting unique `layer_count` labels in the reference dataset (e.g., 5 classes) and assign the integer. |

#### 4. Specify the weight‑initialization strategy: use Kaiming He normal initialization for all convolutional layers in ResNet‑50 and Xavier uniform initialization for the fully‑connected head.

| Category | Details |
| --- | --- |
| **Reason** | Kaiming initialization is optimal for ReLU‑based convolutional nets, while Xavier works well for linear layers, ensuring stable gradient flow at the start of pre‑training. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a string `initialization_strategy` = "Kaiming He for conv layers, Xavier uniform for FC head". Document the exact PyTorch calls (torch.nn.init.kaiming_normal_ and torch.nn.init.xavier_uniform_). |

#### 5. Run a sanity‑check forward pass using a dummy tensor of shape (1, 3, 224, 224) through the backbone and base head to verify dimensional consistency and that the output shape matches `base_head_output_dimension`.

| Category | Details |
| --- | --- |
| **Reason** | Early shape validation prevents runtime errors during the subsequent pre‑training phase. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Instantiate the selected backbone (torchvision.models.resnet50(pretrained=False)), replace the final fully‑connected layer with the defined head, feed a torch.randn tensor, and assert output.shape == (1, base_head_output_dimension). Log any mismatches. |

#### 6. Serialize all six output fields into the required JSON structure so downstream nodes can consume them without further transformation.

| Category | Details |
| --- | --- |
| **Reason** | Consistent, typed output is essential for the typed DAG execution engine. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching `output_structure`, convert to JSON, and ensure types match PrimitiveType definitions (e.g., list of strings for `backbone_layers`). |


---

## evaluate_cliff_performance

### Description
Run inference on test splits of all materials and record per‑material accuracy and overall forgetting metric.

### Implementation Plan

#### 1. Parse the `split_datasets` output JSON files to obtain `material_names` and the corresponding list of test‑split file‑path JSONs (`test_split_json_paths`). Load each JSON and deserialize the list of absolute image file paths for every material.

| Category | Details |
| --- | --- |
| **Reason** | The evaluation routine needs a deterministic, reproducible mapping from material identifier to its test images; using the exact splits produced during dataset preparation guarantees consistency between training and evaluation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python's `json` module; iterate over `test_split_json_paths`, validate that each path exists, and raise a descriptive error if any file is missing. Store results in a dict `test_paths[material_name] = [list_of_paths]`. |

#### 2. Instantiate the CLIFF model by loading the checkpoint files generated by `incremental_train_material_specific_components` (e.g., `model_weights.pth`). Ensure that the backbone and base head are set to `requires_grad=False` and that the learned prompt pool and delta head weights are correctly injected.

| Category | Details |
| --- | --- |
| **Reason** | Accurate inference requires the exact model state after incremental training; loading the checkpoint also guarantees that the frozen components remain non‑trainable during evaluation. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a `load_cliff_model(checkpoint_path, device)` helper that:
- Calls `torch.load` with `map_location=device`.
- Restores backbone, base head, prompt pool, and delta head.
- Explicitly sets `requires_grad=False` for all backbone and base‑head parameters.
- Returns a ready‑to‑evaluate `nn.Module`. |

#### 3. Define a deterministic image preprocessing pipeline identical to the one used in `preprocess_images` and training (resize to target dimensions, normalize with the recorded mean/std, optional center‑crop). Wrap it in a `torchvision.transforms.Compose` object.

| Category | Details |
| --- | --- |
| **Reason** | Evaluation must use the same preprocessing as training to avoid distribution shift; mismatched preprocessing would artificially deflate accuracy. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read `image_width`, `image_height`, `normalization_mean`, and `normalization_std` from the `preprocess_images` output (if stored) or from a config file. Construct: `transforms = T.Compose([T.Resize((height, width)), T.ToTensor(), T.Normalize(mean, std)])`. |

#### 4. For each material in `material_names`, iterate over its test image paths in mini‑batches (batch size derived from `incremental_train_material_specific_components` hyper‑parameters or a default of 64). Load images with `PIL.Image.open`, apply the preprocessing pipeline, and move tensors to the evaluation device (GPU if available).

| Category | Details |
| --- | --- |
| **Reason** | Batch processing maximizes GPU utilization and ensures that memory constraints are respected; consistent batch size also mirrors training conditions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a generator `batch_loader(paths, batch_size)` that yields `(batch_tensor, batch_labels)`. Labels are extracted from the filename convention or an auxiliary CSV that maps each image to its ground‑truth layer count. |

#### 5. Run a forward pass through the loaded CLIFF model: first obtain backbone features, then compute cosine‑similarity gating scores against each material‑specific prompt (using the `implement_cosine_similarity_gate` logic), aggregate the gated prompt vector, pass the combined representation through the delta head, and finally add the base‑head logits to obtain final class scores.

| Category | Details |
| --- | --- |
| **Reason** | The full CLIFF inference pipeline (backbone → gated prompts → delta head → residual addition) must be executed to faithfully reproduce the model's predictions. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Within a `torch.no_grad()` context:
```python
features = backbone(images)
cos_sims = cosine_similarity(features, prompt_pool)
weights = torch.softmax(cos_sims, dim=1)
prompt_agg = torch.einsum('bn, n d -> bd', weights, prompt_pool)
combined = torch.cat([features, prompt_agg], dim=1)
delta_logits = delta_head(combined)
logits = base_head(features) + delta_logits
``` |

#### 6. Compute top‑1 predictions by taking `torch.argmax(logits, dim=1)`. Compare predictions with ground‑truth labels to accumulate `correct_cnt` and `total_cnt` for the current material.

| Category | Details |
| --- | --- |
| **Reason** | Top‑1 accuracy is the primary metric required by the node specification; accumulating counts per material enables later per‑material accuracy computation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain dictionaries `correct[material]` and `total[material]`. After each batch: `correct[mat] += (preds == labels).sum().item(); total[mat] += labels.size(0)`. |

#### 7. After processing all test images for a material, compute its accuracy as `material_accuracies[i] = correct[material] / total[material]`. Store the value in a list preserving the order of `material_names`.

| Category | Details |
| --- | --- |
| **Reason** | Converting raw counts to a normalized accuracy metric yields the required `material_accuracies` output field. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Loop over `material_names` and compute `accuracy = correct[name] / total[name]` with a guard against division‑by‑zero (return 0.0 if total is 0). |

#### 8. Calculate `average_accuracy` as the arithmetic mean of `material_accuracies` using `np.mean(material_accuracies)`.

| Category | Details |
| --- | --- |
| **Reason** | The overall average provides a single scalar summarising performance across all materials, as required by the output schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Import `numpy as np` and compute `average_accuracy = float(np.mean(material_accuracies))`. |

#### 9. Derive the forgetting metric: retrieve the per‑material accuracy *after* each incremental training step from the logs produced by `incremental_train_material_specific_components` (e.g., a JSON `material_accuracy_history.json` where each entry records the accuracy of every previously learned material after the current material is trained). For material *i*, compute `forget_i = max_{j>i}(acc_i^{(j-1)}) - acc_i^{(final)}`; then average `forget_i` across all i < N to obtain `forgetting_metric`.

| Category | Details |
| --- | --- |
| **Reason** | Forgetting quantifies catastrophic loss of knowledge; the definition matches the description in the node prompt and is consistent with downstream `compute_accuracy_and_forgetting_metrics` expectations. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Pseudo‑code:
```python
history = json.load(open('material_accuracy_history.json'))
forget_vals = []
for i, mat in enumerate(material_names[:-1]):
    best_before = max([history[step][mat] for step in range(i, len(material_names)-1)])
    final_acc = material_accuracies[i]
    forget_vals.append(best_before - final_acc)
forgetting_metric = float(np.mean(forget_vals))
``` |

#### 10. Compose `summary_report` as a multi‑line string: include a markdown table listing each material and its top‑1 accuracy, a line for `Average Accuracy`, and a line for `Forgetting Metric`. Add a brief narrative explaining the trends (e.g., which materials are hardest, magnitude of forgetting).

| Category | Details |
| --- | --- |
| **Reason** | Human‑readable reporting is required for downstream documentation and for the `write_summary_report` node; a structured markdown table eases visual inspection. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python f‑strings:
```python
rows = "\n".join([f"| {m} | {a:.2%} |" for m, a in zip(material_names, material_accuracies)])
summary_report = f"## CLIFF Evaluation Summary\n\n| Material | Top‑1 Accuracy |\n|---|---|\n{rows}\n\n**Average Accuracy:** {average_accuracy:.2%}\n**Forgetting Metric:** {forgetting_metric:.2%}\n"
``` |

#### 11. Return a dictionary containing all five output fields (`material_names`, `material_accuracies`, `average_accuracy`, `forgetting_metric`, `summary_report`) ensuring type compliance (list of strings, list of floats, floats, string).

| Category | Details |
| --- | --- |
| **Reason** | The workflow orchestration expects a concrete JSON‑serialisable object matching the declared output schema; strict type adherence prevents downstream runtime errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
output = {
    "material_names": material_names,
    "material_accuracies": material_accuracies,
    "average_accuracy": average_accuracy,
    "forgetting_metric": forgetting_metric,
    "summary_report": summary_report,
}
print(json.dumps(output, indent=2))
``` |

#### 12. Add robust logging (Python `logging` module) at INFO level for major milestones (model load, start/end of each material evaluation, computed metrics) and at DEBUG level for batch‑level statistics. Include exception handling that captures I/O errors, GPU OOM, and mismatched label counts, re‑raising with a clear message.

| Category | Details |
| --- | --- |
| **Reason** | Traceability and debuggability are crucial for reproducible scientific experiments; clear logs help diagnose failures without rerunning the entire pipeline. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Configure a logger: `logger = logging.getLogger('evaluate_cliff')`; set `logger.setLevel(logging.INFO)`. Wrap major sections in `try/except` blocks and log `logger.exception('...')` on failure. |


---

## freeze_backbone_and_base_head

### Description
Mark backbone and base head parameters as non‑trainable for subsequent continual learning phases.

### Implementation Plan

#### 1. Load the checkpoint produced by `train_base_model_on_reference` (field `base_model_weights_path`) into the same model class used for design_backbone_and_base_head.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we are freezing the exact parameter tensors that were trained on the reference dataset. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.load(path, map_location='cpu')` (or equivalent for TensorFlow/Keras) to obtain `state_dict`; instantiate the model architecture (backbone + base_head) and call `model.load_state_dict(state_dict, strict=True)`. |

#### 2. Iterate over all parameters belonging to the backbone module (e.g., `model.backbone.parameters()`) and set `param.requires_grad = False` for each.

| Category | Details |
| --- | --- |
| **Reason** | Marks the backbone as non‑trainable so that subsequent optimizer steps do not update its weights. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
frozen_names = []
for name, param in model.backbone.named_parameters():
    param.requires_grad = False
    frozen_names.append(name)
``` |

#### 3. Iterate over all parameters of the base classification head (e.g., `model.base_head.parameters()`) and set `param.requires_grad = False` similarly, appending their names to the frozen list.

| Category | Details |
| --- | --- |
| **Reason** | Completes the freezing of the entire base model while leaving downstream components mutable. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
for name, param in model.base_head.named_parameters():
    param.requires_grad = False
    frozen_names.append(name)
``` |

#### 4. Collect the names of all parameters that remain trainable after the above steps. These should correspond to the prompt pool (e.g., `model.material_prompts`) and the delta head (e.g., `model.delta_head`).

| Category | Details |
| --- | --- |
| **Reason** | Provides the `trainable_parameters` output and is required for verification that only intended modules are still updating. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
trainable_names = [name for name, p in model.named_parameters() if p.requires_grad]
``` |

#### 5. Perform a verification pass: assert that every name in `frozen_names` has `requires_grad == False` and every name in `trainable_names` belongs to either the prompt pool or delta head.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that accidental un‑freezing of backbone/base‑head parameters is caught early, preventing downstream training bugs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```python
expected_trainable_prefixes = ('material_prompts', 'delta_head')
verification_passed = all(
    any(name.startswith(pref) for pref in expected_trainable_prefixes) for name in trainable_names
) and all(
    not param.requires_grad for name, param in model.named_parameters() if name in frozen_names
)
``` |

#### 6. Serialize the results into the defined output structure: set `operation_status` to "success" if `verification_passed` is True, otherwise include an error description; output `frozen_parameters` = frozen_names, `trainable_parameters` = trainable_names, and `verification_passed` flag.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic, schema‑compliant response for downstream nodes (e.g., incremental_train_material_specific_components). |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dict matching the output schema and return/print it; in a production pipeline, wrap in a JSON encoder. |

#### 7. Save the now‑frozen model weights back to disk (optional but recommended) so that future stages can reload without recomputing the freeze step.

| Category | Details |
| --- | --- |
| **Reason** | Ensures reproducibility and reduces the risk of re‑freezing inconsistently if the pipeline is rerun. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
torch.save(model.state_dict(), path_to_frozen_weights)
``` (or `model.save_weights` for TF/Keras). |

#### 8. Add comprehensive logging: log the count of frozen parameters, count of trainable parameters, and any mismatches detected during verification.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and audit trails for experiments involving many materials and incremental steps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use the `logging` module with `INFO` level messages; e.g., `logging.info(f"Frozen {len(frozen_names)} params; trainable {len(trainable_names)} params")`. |


---

## generate_comparative_results_table

### Description
Create a markdown table comparing CLIFF, naive fine‑tuning, and prompt‑only baselines across all metrics.

### Implementation Plan

#### 1. Load the JSON summary produced by the parent node `compute_accuracy_and_forgetting_metrics` (field `summary_json`) and deserialize it into a native Python dictionary.

| Category | Details |
| --- | --- |
| **Reason** | Deserialization is required to access individual numeric fields (mean accuracies, forgetting values, per‑material lists) for further processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.loads()`; add error handling for malformed JSON; raise a clear exception if required keys are missing. |

#### 2. Extract the ordered list of model identifiers from the parent output field `models` and map them to the canonical display names required for the table (e.g., replace "CLIFF" → "CLIFF", "NaiveFineTuning" → "Naive Fine‑Tuning", "PromptBaseline" → "Prompt‑Only").

| Category | Details |
| --- | --- |
| **Reason** | The downstream consumer expects human‑readable model names, not internal identifiers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a static mapping dictionary; apply it with a list comprehension; validate that all three expected models are present. |

#### 3. Collect overall accuracies: read `cliff_mean_accuracy`, `naive_fine_tuning_mean_accuracy`, and `prompt_baseline_mean_accuracy` from the deserialized dict and assemble them into the list `overall_accuracies` ordered according to `model_names`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the `overall_accuracies` output aligns with the row order of the markdown table. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map each model name to its corresponding mean field; cast to `float` with rounding to 4 decimal places for readability. |

#### 4. Collect average forgetting values: read `cliff_forgetting`, `naive_fine_tuning_forgetting`, and `prompt_baseline_forgetting` and assemble them into `average_forgettings` in the same order as `model_names`.

| Category | Details |
| --- | --- |
| **Reason** | Forgetting is a key comparative metric; consistent ordering is essential for downstream analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Same approach as the previous bullet; ensure values are non‑negative; if a value is missing, insert `None` and later replace with "N/A" in the markdown. |

#### 5. Extract per‑material accuracy lists (`cliff_per_material_accuracy`, `naive_fine_tuning_per_material_accuracy`, `prompt_baseline_per_material_accuracy`) and the global `materials` list; truncate each per‑material list to at most three entries (as required by the prompt).

| Category | Details |
| --- | --- |
| **Reason** | The markdown table column must list up to three material accuracies; truncation prevents overflow and keeps the table readable. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Slice each list with `[:3]`; keep the same ordering of materials as provided; if fewer than three materials exist, fill missing slots with `"-"` placeholders. |

#### 6. Flatten the truncated per‑material accuracies into a single list `per_material_accuracies` ordered by model then by material.

| Category | Details |
| --- | --- |
| **Reason** | Matches the output schema definition and allows downstream nodes to index accuracies without needing nested structures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the three model‑specific lists and extend a master list; ensure each entry is a `float` rounded to 2‑3 decimal places. |

#### 7. Construct the markdown table string:
```
| Model | Overall Accuracy | Avg. Forgetting | Material‑1 | Material‑2 | Material‑3 |
|-------|------------------|----------------|-----------|-----------|-----------|
| CLIFF | 0.92 | 0.03 | 0.94 | 0.91 | 0.92 |
| Naive Fine‑Tuning | 0.85 | 0.15 | 0.88 | 0.83 | 0.84 |
| Prompt‑Only | 0.88 | 0.10 | 0.90 | 0.86 | 0.88 |
```
Populate each cell using the previously assembled lists, inserting "-" where a material slot is empty.

| Category | Details |
| --- | --- |
| **Reason** | A well‑formatted markdown table is the primary deliverable for human readers and for inclusion in the final report. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python string templating (e.g., f‑strings or `str.format`); loop over `model_names` to generate rows; ensure proper escaping of pipe characters; validate that each row has exactly six columns. |

#### 8. Validate the final outputs:
- `markdown_table` must be a non‑empty string containing at least three rows (header + separator + data rows).
- `model_names`, `overall_accuracies`, and `average_forgettings` must each have length 3.
- `per_material_accuracies` length must be ≤ 9 (3 models × 3 materials).
If any validation fails, raise an informative exception.

| Category | Details |
| --- | --- |
| **Reason** | Early detection of mismatched data prevents downstream failures and ensures contract compliance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper `assert` block; log the mismatched dimensions; include a fallback that inserts placeholder values rather than crashing for production robustness. |

#### 9. Return a dictionary matching the declared `output_structure` with keys: `markdown_table`, `model_names`, `overall_accuracies`, `average_forgettings`, `per_material_accuracies`.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the typed node contract; downstream nodes (`write_summary_report`) will consume these fields directly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a plain Python dict; ensure each value adheres to its PrimitiveType (e.g., cast lists to `list`, floats to `float`). |

#### 10. Add logging statements at DEBUG level before and after each major transformation (loading JSON, extracting metrics, building table) to aid troubleshooting and reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Transparent logs simplify debugging in complex DAG executions and satisfy audit requirements. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python `logging` module; include node name in log messages; optionally expose a `verbose` flag. |


---

## implement_cosine_similarity_gate

### Description
Build a gate that selects and weights prompts based on cosine similarity between input features and prompt embeddings.

### Implementation Plan

#### 1. Load the prompt pool metadata produced by `implement_prompt_pool_structure` (variable name, dimensionality D, list of material IDs, and the learnable tensor containing all prompt embeddings).

| Category | Details |
| --- | --- |
| **Reason** | The gate must have direct access to the raw prompt embeddings to compute similarity with the backbone output. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Import the prompt pool variable (e.g., `material_prompts`) from the model's state dictionary; ensure it is a tensor of shape (num_materials, D). |

#### 2. During the forward pass, retrieve the backbone feature vector `f` for the current input image (shape: [D]), ensuring it is L2‑normalized before similarity computation.

| Category | Details |
| --- | --- |
| **Reason** | Cosine similarity requires both vectors to be unit‑norm; normalizing the backbone output eliminates scale bias. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply `f_norm = f / (torch.norm(f, p=2) + 1e-8)` using the same precision as the prompt embeddings. |

#### 3. L2‑normalize each prompt embedding in the pool to obtain `P_norm` (shape: [num_materials, D]).

| Category | Details |
| --- | --- |
| **Reason** | Consistent normalization across prompts guarantees that the dot product equals cosine similarity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute `P_norm = material_prompts / (torch.norm(material_prompts, dim=1, keepdim=True) + 1e-8)` once per training step or cache if static. |

#### 4. Compute cosine similarity scores by taking the matrix‑vector product between `P_norm` and the normalized backbone vector `f_norm`: `scores = torch.matmul(P_norm, f_norm)` resulting in a 1‑D tensor of length `num_materials`.

| Category | Details |
| --- | --- |
| **Reason** | Matrix‑vector multiplication is highly efficient on GPUs and yields the exact cosine similarity for each prompt. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use PyTorch/TF tensor ops; ensure dtype consistency (float32). Store the result as `similarity_scores`. |

#### 5. Apply a temperature‑scaled softmax to the similarity scores to obtain attention weights: `weights = torch.softmax(scores / temperature, dim=0)`. Choose a default temperature of 0.1 to sharpen the distribution.

| Category | Details |
| --- | --- |
| **Reason** | Softmax converts raw similarities into a probability distribution that can be used for weighted aggregation; temperature controls sharpness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement as a separate function `softmax_weights(scores, temperature=0.1)`. Store the output as `softmax_weights`. |

#### 6. Compute the weighted prompt aggregation by performing a weighted sum of the original (non‑normalized) prompt embeddings: `weighted_prompt = torch.sum(weights.unsqueeze(1) * material_prompts, dim=0)`.

| Category | Details |
| --- | --- |
| **Reason** | Using the original embeddings preserves their learned magnitude while still being guided by similarity‑based attention. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Broadcast `weights` to shape `[num_materials, 1]`, multiply with `material_prompts`, then sum over the material dimension. Store as `weighted_prompt_vector`. |

#### 7. Package the four outputs (`pseudo_code`, `similarity_scores`, `softmax_weights`, `weighted_prompt_vector`) into the node's result structure. The `pseudo_code` field should contain a language‑agnostic, step‑by‑step script reflecting the operations above.

| Category | Details |
| --- | --- |
| **Reason** | The node contract requires both concrete numeric outputs for downstream computation and a human‑readable pseudo‑code description for documentation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a multi‑line string with clear comments, variable names matching the steps, and include optional type hints. Example provided in the pseudo‑code field. |

#### 8. Add sanity‑check assertions: verify that `similarity_scores` length equals `number_of_materials`, that `softmax_weights` sum to 1 (within tolerance), and that `weighted_prompt_vector` shape matches `prompt_dimension` D.

| Category | Details |
| --- | --- |
| **Reason** | Early detection of shape or numerical errors prevents downstream crashes in incremental training loops. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `assert torch.allclose(weights.sum(), torch.tensor(1.0), atol=1e-5)` and shape checks; raise informative errors if violated. |


---

## implement_delta_head

### Description
Define a lightweight residual head that learns material‑specific corrections on top of the frozen base head.

### Implementation Plan

#### 1. Extract the dimensionality of the frozen backbone's final feature vector from the parent node `design_backbone_and_base_head` (use `base_head_input_dimension` if the base head directly consumes the backbone output, otherwise compute from the last convolutional block, e.g., 2048 for ResNet‑50).

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the delta head receives exactly the same sized gated features that the base head expects, preventing shape mismatches during forward passes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the JSON output of `design_backbone_and_base_head`; if `base_head_input_dimension` is present, assign it to `delta_head_input_size`. Otherwise, map the known backbone architecture (e.g., ResNet‑50) to its standard output dimension. |

#### 2. Set `delta_head_output_size` equal to `base_head_output_dimension` obtained from `design_backbone_and_base_head`.

| Category | Details |
| --- | --- |
| **Reason** | The delta head must output a correction vector that can be added element‑wise to the base head logits; matching dimensions are mandatory. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read `base_head_output_dimension` from the parent node and assign it directly to `delta_head_output_size`. |

#### 3. Define the delta head as a two‑layer MLP (the simplest yet expressive residual head). Choose a hidden dimension `H` (e.g., 256) that is small relative to the input size to keep the head lightweight.

| Category | Details |
| --- | --- |
| **Reason** | A shallow MLP provides enough capacity to learn material‑specific bias/correction while keeping parameter count low, preserving the continual‑learning efficiency. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dictionary: `delta_head_layer_sizes = [delta_head_input_size, H, delta_head_output_size]`. Store `H` as a configurable hyper‑parameter in `configure_training_hyperparameters`. |

#### 4. Select activation functions: use ReLU after the first linear layer and a linear (identity) activation after the second layer so that the output can be added directly to the base logits.

| Category | Details |
| --- | --- |
| **Reason** | ReLU introduces non‑linearity for expressive corrections; a linear output prevents unwanted scaling of logits. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set `delta_head_activation_functions = ["ReLU", "Linear"]`. |

#### 5. Specify the full architecture string for `delta_head_architecture` – e.g., "Two‑layer MLP with hidden size 256, ReLU activation after first layer, linear output".

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable summary for documentation and downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Concatenate the chosen hyper‑parameters into a formatted description. |

#### 6. Initialize the first linear layer with Kaiming‑He (He) initialization (mode=‘fan_in’, nonlinearity=‘relu’) and the second linear layer with zeros (so initial correction is zero).

| Category | Details |
| --- | --- |
| **Reason** | Kaiming init stabilizes training for ReLU layers; zero init for the final layer guarantees that at the start of incremental training the delta head does not alter the base logits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | In PyTorch: `nn.init.kaiming_normal_(layer1.weight, nonlinearity='relu')`; `nn.init.zeros_(layer2.weight)`; bias terms can be zero‑initialized. |

#### 7. Implement the delta head as a reusable module (e.g., `class DeltaHead(nn.Module)`) exposing a `forward(gated_features)` method that returns the correction logits.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulation simplifies integration with the larger CLIFF model and allows easy swapping of hidden dimension `H` later. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write a small class inheriting from `torch.nn.Module`, construct `nn.Sequential` with the two linear layers and activation, and store layer sizes as class attributes for later introspection. |

#### 8. Document how the delta head is combined with the frozen base head during inference: `final_logits = base_logits + delta_head(gated_features)`.

| Category | Details |
| --- | --- |
| **Reason** | Clarifies the residual nature of the head for downstream developers and for the `incremental_train_material_specific_components` node which expects a residual correction. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Add a comment block in the module and include the equation in the `delta_head_architecture` description. |

#### 9. Create a unit‑test script that feeds a dummy tensor of shape `(batch, delta_head_input_size)` through the delta head and asserts that the output shape equals `(batch, delta_head_output_size)` and that the initial output is all zeros (due to zero initialization of the second layer).

| Category | Details |
| --- | --- |
| **Reason** | Automated sanity check prevents shape bugs early and guarantees the zero‑correction property before training begins. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `torch.randn(4, delta_head_input_size)` as input, run the forward pass, and compare `output.detach().abs().max()` to a small epsilon. |

#### 10. Expose the delta head configuration (layer sizes, activation list, hidden dimension) as entries in the output JSON fields `delta_head_layer_sizes` and `delta_head_activation_functions` so that downstream nodes (e.g., `configure_training_hyperparameters`) can reference them programmatically.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates downstream automation, logging, and reproducibility of experiments. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Populate the output fields directly from the variables defined in earlier bullets. |


---

## implement_prompt_pool_structure

### Description
Create the data structure and embedding logic for a pool of learnable material‑specific prompts.

### Implementation Plan

#### 1. Define a dedicated PyTorch nn.Module named `MaterialPromptPool` that internally registers a Parameter tensor of shape `(N, D)` where `N = number_of_materials` and `D = prompt_dimension`.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulating the prompt pool in a module ensures seamless integration with the autograd engine and provides a clean API for indexing by material ID. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.nn.Parameter(torch.empty(N, D))` and initialize it in `__init__` via `torch.nn.init.normal_(self.prompts, mean=0.0, std=0.02)` (or the chosen `initialization_method`). |

#### 2. Create a Python dictionary `material_id_to_index` mapping each string identifier in `material_ids` to its integer position in the prompt matrix.

| Category | Details |
| --- | --- |
| **Reason** | Fast lookup (O(1)) is required during training/inference to fetch the correct prompt vector for a given sample's material label. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `self.id2idx = {mid: idx for idx, mid in enumerate(material_ids)}` stored as a member of the module. |

#### 3. Implement a method `get_prompt(material_id: str) -> torch.Tensor` that returns the prompt vector `self.prompts[self.id2idx[material_id]]` and adds a batch dimension if needed.

| Category | Details |
| --- | --- |
| **Reason** | Abstracts the indexing logic away from downstream code, allowing batch‑wise retrieval by passing a list of material IDs and using `torch.index_select`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If a list of IDs is provided, convert them to indices via list comprehension, then `torch.index_select(self.prompts, 0, torch.tensor(indices, device=self.prompts.device))`. |

#### 4. Choose an integration strategy: prepend the prompt vector to the token sequence produced by the backbone's patch embedding (ViT‑style) or concatenate it to the global feature map (CNN‑style). Store this choice in `integration_method`.

| Category | Details |
| --- | --- |
| **Reason** | The integration method determines how the prompt influences downstream layers; prepending aligns with transformer prompt‑tuning literature, while concatenation works for classic CNNs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For a ResNet‑based backbone, after the final spatial pooling produce a feature vector `f`. Compute `f_aug = torch.cat([prompt, f], dim=-1)` where `prompt` is broadcasted across the batch. For a ViT, insert `prompt` as additional tokens before the class token. |

#### 5. Set `requires_grad=True` for the prompt Parameter and ensure all other backbone and base‑head parameters have `requires_grad=False` (handled later by `freeze_backbone_and_base_head`).

| Category | Details |
| --- | --- |
| **Reason** | Only the prompt vectors should be learnable during incremental phases; this flag guarantees gradients flow correctly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | When creating the Parameter, pass `requires_grad=True`. Verify via `assert self.prompts.requires_grad`. |

#### 6. Expose the module in the model's forward pass: modify the main `CLIFFModel` forward method to accept an extra argument `material_id` and retrieve the prompt via `prompt = self.prompt_pool.get_prompt(material_id)` before merging with backbone output.

| Category | Details |
| --- | --- |
| **Reason** | The forward signature must allow the training loop to supply the correct material label for each batch. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Add `def forward(self, x, material_id):` → `prompt = self.prompt_pool.get_prompt(material_id)` → integrate as per chosen `integration_method`. |

#### 7. Provide an `example_code_snippet` string illustrating instantiation and a single forward call, e.g.,
```python
prompt_pool = MaterialPromptPool(
    num_materials=3,
    prompt_dim=128,
    material_ids=["graphene", "MoS2", "WS2"],
    init_method="normal_std_0.02"
)
model = CLIFFModel(backbone=resnet50, base_head=fc, prompt_pool=prompt_pool)
logits = model(images, material_id="MoS2")
```

| Category | Details |
| --- | --- |
| **Reason** | Concrete code helps downstream developers quickly copy‑paste and adapt the implementation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Compose the snippet as a raw string and assign to the `example_code_snippet` output field. |


---

## incremental_train_material_specific_components

### Description
For each new material, jointly train the material‑specific prompt, delta head, and replay/distillation mechanisms while keeping backbone frozen.

### Implementation Plan

#### 1. Validate that the backbone and base head are frozen by checking `requires_grad=False` for all their parameters (output from `freeze_backbone_and_base_head`).

| Category | Details |
| --- | --- |
| **Reason** | Ensures no accidental gradient updates leak into the frozen components during incremental training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `model.backbone.parameters()` and `model.base_head.parameters()`; raise an error if any `requires_grad` is True. |

#### 2. Load the hyper‑parameter configuration generated by `configure_training_hyperparameters` (learning rates, batch size, replay ratio, epochs, optimizer types).

| Category | Details |
| --- | --- |
| **Reason** | All subsequent training loops must obey the same schedule and optimizer settings to guarantee reproducibility. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the JSON or Python dict returned by the parent node; instantiate AdamW for prompts and delta head with `incremental_prompt_learning_rate` and `incremental_delta_learning_rate` respectively. |

#### 3. Initialize the prompt pool for all new materials using the schema from `implement_prompt_pool_structure` (prompt dimension, number of materials). For each material, create a separate learnable prompt vector and register it as a `torch.nn.Parameter` attached to the optimizer for prompts.

| Category | Details |
| --- | --- |
| **Reason** | Material‑specific prompts must exist before training begins; they provide the conditioning signal for the gated features. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a `torch.nn.Embedding(num_materials, prompt_dim)` with `requires_grad=True`; map material IDs to embedding indices. |

#### 4. Instantiate the delta head according to the architecture specified by `implement_delta_head` (e.g., two‑layer MLP with defined input/output sizes and activations). Register its parameters with the delta‑head optimizer.

| Category | Details |
| --- | --- |
| **Reason** | The delta head is the only trainable component that learns residual corrections for each material. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.nn.Sequential` to build the MLP; ensure its output dimension matches the base head output dimension. |

#### 5. Set up the memory replay buffer using the artifact from `set_up_memory_replay_buffer` (directory path, exemplars per class). Load any pre‑existing exemplars into an in‑memory index for fast sampling.

| Category | Details |
| --- | --- |
| **Reason** | Replay buffer must be ready to supply past exemplars during each incremental epoch. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Read `exemplar_file_paths`; store a mapping `{class_id: [tensor, label]}`; implement a `sample(num_samples)` method that returns a balanced batch. |

#### 6. Iterate over the list of new materials returned by `collect_new_material_datasets.materials` in the order they will be introduced.

| Category | Details |
| --- | --- |
| **Reason** | Continual learning requires a deterministic material ordering for reproducibility and for correct forgetting measurement later. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | For `material_idx, material_name in enumerate(materials):` execute the training loop described in subsequent bullets. |

#### 7. For the current material, load its training split JSON file (path from `split_datasets.train_split_json_paths` matched by material name) into a PyTorch `Dataset` that yields `(image, label)` pairs.

| Category | Details |
| --- | --- |
| **Reason** | Provides the fresh data on which the prompt and delta head will be optimized. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `torch.utils.data.Dataset` subclass that reads image paths, applies the preprocessing pipeline, and returns tensors. |

#### 8. Create a `DataLoader` that mixes new‑material samples with replay exemplars according to the `replay_ratio` (e.g., "1:3" → 1 replay sample for every 3 new samples). Shuffle within each epoch.

| Category | Details |
| --- | --- |
| **Reason** | Balancing new and old data mitigates catastrophic forgetting while respecting the configured replay schedule. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute `num_new = batch_size * (replay_ratio_denominator/(replay_ratio_numerator+replay_ratio_denominator))`; sample `num_replay = batch_size - num_new` from the buffer each iteration. |

#### 9. During each batch forward pass:
   a. Pass images through the frozen backbone to obtain feature vectors `F`.
   b. Retrieve the current material's prompt embedding `P` from the prompt pool.
   c. Compute cosine‑similarity scores between `F` and all prompt embeddings using the gate from `implement_cosine_similarity_gate`.
   d. Apply softmax to obtain weights and compute the weighted prompt vector `P_weighted`.
   e. Concatenate or add `P_weighted` to `F` to produce gated features `G`.
   f. Feed `G` into the delta head to obtain correction logits `Δlogits`.
   g. Add `Δlogits` to the frozen base head logits (computed once from `F` and cached) to get final logits `logits`.

| Category | Details |
| --- | --- |
| **Reason** | This sequence implements the core forward computation defined by the model architecture, ensuring that only prompts and delta head affect the output. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a `forward()` method in a wrapper module that calls `self.backbone(image)`, `self.cosine_gate(F)`, merges prompts, and then `self.delta_head(G)`. Cache base head output with `torch.no_grad()`. |

#### 10. Compute the combined loss for the batch:
   - Classification loss: cross‑entropy between `logits` and true labels for both new and replay samples.
   - Distillation loss: KL‑divergence between `logits` (student) and stored base‑model logits for replay samples, weighted by `weighting_hyperparameter` from `define_knowledge_distillation_loss`.
   - Total loss = `classification_loss + λ * distillation_loss`.

| Category | Details |
| --- | --- |
| **Reason** | The loss formulation enforces correct predictions on new data while preserving knowledge from earlier materials. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.nn.CrossEntropyLoss` for classification; for distillation, retrieve stored base logits from the replay buffer (saved during earlier phases) and compute `torch.nn.KLDivLoss(reduction='batchmean')` with `log_softmax`/`softmax` as needed. |

#### 11. Back‑propagate the total loss **only** through prompt parameters and delta head parameters (optimizers created earlier). Ensure that the backbone and base head gradients are disabled (they remain `requires_grad=False`).

| Category | Details |
| --- | --- |
| **Reason** | Maintains the frozen‑backbone constraint while updating only the intended components. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Call `optimizer_prompt.zero_grad(); optimizer_delta.zero_grad(); total_loss.backward(); optimizer_prompt.step(); optimizer_delta.step();`. |

#### 12. After each epoch, update the replay buffer:
   - For each class in the current material, select the top‑k exemplars (e.g., highest loss or most diverse embeddings) up to `exemplars_per_class`.
   - Replace older exemplars of the same class if buffer usage exceeds capacity.
   - Store the corresponding base‑model logits for future distillation.
   - Record buffer usage percentage for the output field `replay_buffer_usage`.

| Category | Details |
| --- | --- |
| **Reason** | Keeps the replay buffer representative of all learned materials and provides the necessary teacher logits for distillation. |
| **Impact** | MEDIUM |
| **Complexity** | HIGH |
| **Method** | Implement a FIFO or herding strategy; compute embeddings for candidate exemplars using the frozen backbone, then select via k‑means centroids or loss‑based ranking. |

#### 13. At the end of training for the current material, evaluate its validation split (provided by `split_datasets.validation_split_json_paths`). Compute top‑1 accuracy and store it as `last_material_accuracy` for the final material, while also logging per‑material accuracies for later analysis.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantitative checkpoint to confirm that the material was learned successfully and supplies the required output metric. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run inference with `torch.no_grad()`, compare predicted class argmax with ground‑truth, compute `correct / total`. |

#### 14. Save checkpoints after each material: serialize prompt pool embeddings, delta head weights, optimizer states, and current replay buffer metadata to disk. Append checkpoint paths to a log for possible resume.

| Category | Details |
| --- | --- |
| **Reason** | Allows recovery from interruptions and enables later analysis of intermediate models. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `torch.save({'prompt_state_dict': prompt_pool.state_dict(), 'delta_state_dict': delta_head.state_dict(), 'optimizer_prompt': optimizer_prompt.state_dict(), 'optimizer_delta': optimizer_delta.state_dict(), 'buffer_meta': buffer_meta}, checkpoint_path)`. |

#### 15. After the loop over all new materials finishes, set `training_completed` to `True`, assemble the final `prompt_embeddings` by flattening all prompt vectors, collect `delta_head_weights` by flattening all MLP parameters, and compute the final `replay_buffer_usage` as `(total_exemplars / (exemplars_per_class * num_classes_total)) * 100`.

| Category | Details |
| --- | --- |
| **Reason** | Produces the exact output fields defined in the node's schema, ready for downstream nodes such as `evaluate_cliff_performance`. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `prompt_pool.parameters()` and `delta_head.parameters()`, convert tensors to Python lists via `.detach().cpu().flatten().tolist()`. Compute usage percentage using values from `set_up_memory_replay_buffer`. |

#### 16. Log a concise summary (JSON or plain text) containing:
   - `training_completed`
   - `last_material_accuracy`
   - `replay_buffer_usage`
   - Paths to saved checkpoints
   - Any warnings or anomalies encountered during training.
   Return this summary as part of the node's output for transparency and debugging.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates downstream auditing, reproducibility, and quick inspection of training health. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dictionary, dump with `json.dumps(..., indent=2)`, and attach to the node's return payload. |


---

## preprocess_images

### Description
Standardize all images (normalization, resizing, augmentation) and store them ready for training.

### Implementation Plan

#### 1. Extract source image directories from the parent nodes: read `dataset_path` from `collect_reference_material_dataset` and each entry of `storage_paths` from `collect_new_material_datasets`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the preprocessing script knows exactly where the raw images reside for every material, avoiding hard‑coded paths. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the JSON or Python objects returned by the parent nodes; store paths in a dict `material -> raw_dir`. |

#### 2. Define preprocessing hyper‑parameters: set `image_width` and `image_height` (e.g., 224×224), `normalization_mean` = 0.5, `normalization_std` = 0.5, and a boolean `augmentation_enabled` (configurable via a command‑line flag or config file).

| Category | Details |
| --- | --- |
| **Reason** | These parameters are required by downstream training code and must be recorded for reproducibility. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python `argparse.Namespace` or a YAML config file; validate that values are positive integers/floats. |

#### 3. Create the root output directory `processed_images_dir` (e.g., `data/processed/`) and, for each material, sub‑directories `{material}/train`, `{material}/val`, `{material}/test`.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic folder hierarchy makes later splitting and data loading straightforward and matches the expectations of the `split_datasets` node. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs(path, exist_ok=True)` in a loop over materials and splits. |

#### 4. Initialize an empty list `processed_image_paths` and a counter `total_images_processed = 0`.

| Category | Details |
| --- | --- |
| **Reason** | Collecting these values during the loop allows immediate population of the required output fields without a second pass. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Python list and integer variables. |

#### 5. Iterate over each material and over every image file (`.png`, `.jpg`, `.tif`) in its raw directory. For each image:

| Category | Details |
| --- | --- |
| **Reason** | Core processing loop – must handle all files robustly. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `glob.glob(os.path.join(raw_dir, "*.[pj][pn]g"))` and `tifffile.imread` for TIFFs. |

#### 6. Load the image with Pillow (or OpenCV), convert to RGB, cast to `float32`, and scale pixel values to the range [0, 1].

| Category | Details |
| --- | --- |
| **Reason** | Standardizes input format for downstream deep‑learning frameworks that expect float tensors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `img = Image.open(path).convert('RGB'); img = np.asarray(img).astype(np.float32) / 255.0`. |

#### 7. Apply normalization: `img = (img - normalization_mean) / normalization_std` element‑wise.

| Category | Details |
| --- | --- |
| **Reason** | Centers the data distribution, which improves training stability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | NumPy broadcasting or torch transforms. |

#### 8. Resize the normalized image to `(image_width, image_height)` using bilinear interpolation (`Image.BILINEAR`).

| Category | Details |
| --- | --- |
| **Reason** | All models expect a fixed input size; bilinear interpolation preserves visual quality. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `img_resized = Image.fromarray((img*255).astype(np.uint8)).resize((image_width, image_height), Image.BILINEAR)`. |

#### 9. If `augmentation_enabled` is True and the current split is `train`, generate augmented variants using a deterministic pipeline: random rotation (±15°), horizontal/vertical flip, and brightness jitter (±0.2). Append each augmented image to the same material `train` folder with suffixes `_rot`, `_flip`, `_bright`.

| Category | Details |
| --- | --- |
| **Reason** | Data augmentation increases robustness for the first training stage while keeping validation/test untouched. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Leverage `torchvision.transforms.Compose([RandomRotation(15), RandomHorizontalFlip(), ColorJitter(brightness=0.2)])`; apply to the PIL image before saving. |

#### 10. Save the (possibly augmented) image as a lossless PNG (`cv2.imwrite` or `Image.save`) in the appropriate `{material}/{split}` folder. Record the absolute file path in `processed_image_paths` and increment `total_images_processed`.

| Category | Details |
| --- | --- |
| **Reason** | Persists the standardized data and builds the required output list for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `save_path = os.path.join(processed_images_dir, material, split, filename); Image.fromarray((img_resized*255).astype(np.uint8)).save(save_path)`. |

#### 11. After processing all images, write a small `metadata.json` inside `processed_images_dir` containing the hyper‑parameters (`image_width`, `image_height`, `normalization_mean`, `normalization_std`, `augmentation_enabled`).

| Category | Details |
| --- | --- |
| **Reason** | Provides a self‑contained record for reproducibility and for any downstream audit. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `json.dump({...}, open(os.path.join(processed_images_dir, 'metadata.json'), 'w'))`. |

#### 12. Return the populated output fields: `processed_images_dir`, `processed_image_paths`, `total_images_processed`, `image_width`, `image_height`, `normalization_mean`, `normalization_std`, `augmentation_enabled`.

| Category | Details |
| --- | --- |
| **Reason** | Fulfills the node contract so that `split_datasets` can consume the standardized images. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict matching the output schema and output it via the workflow engine. |


---

## produce_visualizations

### Description
Generate plots (e.g., accuracy vs. material order, forgetting curve) to visually illustrate CLIFF’s advantages.

### Implementation Plan

#### 1. Load the JSON summary produced by `compute_accuracy_and_forgetting_metrics` and deserialize it into a Python dict.

| Category | Details |
| --- | --- |
| **Reason** | All required numeric data (per‑material accuracies and forgetting metrics for each model) are stored in this JSON; parsing it is the first step toward any visualisation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.load(open(summary_path))`; validate that keys `materials`, `cliff_per_material_accuracy`, `naive_fine_tuning_per_material_accuracy`, `prompt_baseline_per_material_accuracy`, `cliff_forgetting`, `naive_fine_tuning_forgetting`, `prompt_baseline_forgetting` exist; raise a descriptive error if any are missing. |

#### 2. Prepare a unified pandas DataFrame where each row corresponds to a material and columns contain the three methods' accuracies and forgetting values.

| Category | Details |
| --- | --- |
| **Reason** | A DataFrame provides convenient indexing for matplotlib plotting and ensures the material order is consistent across both figures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
import pandas as pd
materials = data['materials']
df = pd.DataFrame({
    'Material': materials,
    'CLIFF': data['cliff_per_material_accuracy'],
    'NaiveFineTuning': data['naive_fine_tuning_per_material_accuracy'],
    'PromptBaseline': data['prompt_baseline_per_material_accuracy'],
    'CLIFF_Forgetting': [data['cliff_forgetting']]*len(materials),
    'Naive_Forgetting': [data['naive_fine_tuning_forgetting']]*len(materials),
    'Prompt_Forgetting': [data['prompt_baseline_forgetting']]*len(materials),
})
``` |

#### 3. Create the *accuracy‑over‑material‑order* line plot using Matplotlib: X‑axis = material index (preserve the order from `materials`), Y‑axis = top‑1 accuracy, one line per method, with markers and a legend.

| Category | Details |
| --- | --- |
| **Reason** | A line plot directly shows how each method’s performance evolves as new materials are added, highlighting CLIFF’s stability and improvement. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```python
import matplotlib.pyplot as plt
plt.figure(figsize=(8,5))
for method, color in zip(['CLIFF','NaiveFineTuning','PromptBaseline'], ['tab:blue','tab:orange','tab:green']):
    plt.plot(df['Material'], df[method], marker='o', color=color, label=method)
plt.xlabel('Material (learning order)')
plt.ylabel('Top‑1 Accuracy (%)')
plt.title('Accuracy vs. Material Order for CLIFF and Baselines')
plt.ylim(0,100)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
accuracy_plot_path = 'figures/accuracy_vs_material.png'
plt.tight_layout()
plt.savefig(accuracy_plot_path, dpi=300)
plt.close()
``` |

#### 4. Create the *forgetting magnitude* bar plot: X‑axis = material name, Y‑axis = forgetting value, three grouped bars per material for the three methods.

| Category | Details |
| --- | --- |
| **Reason** | Bar charts make it easy to compare the amount of performance degradation (forgetting) each method suffers on previously learned materials. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```python
import numpy as np
x = np.arange(len(df['Material']))
width = 0.25
plt.figure(figsize=(9,5))
plt.bar(x - width, df['CLIFF_Forgetting'], width, label='CLIFF', color='tab:blue')
plt.bar(x, df['Naive_Forgetting'], width, label='Naive Fine‑Tuning', color='tab:orange')
plt.bar(x + width, df['Prompt_Forgetting'], width, label='Prompt‑Only', color='tab:green')
plt.xlabel('Material')
plt.ylabel('Forgetting (Δ Accuracy %)')
plt.title('Forgetting Magnitude per Material')
plt.xticks(x, df['Material'], rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
forgetting_plot_path = 'figures/forgetting_per_material.png'
plt.tight_layout()
plt.savefig(forgetting_plot_path, dpi=300)
plt.close()
``` |

#### 5. Return the four output fields as a JSON‑compatible dict, ensuring absolute or project‑relative file paths are used.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (e.g., `write_summary_report`) expect explicit file locations and human‑readable captions to embed the figures into the final manuscript. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
output = {
    'accuracy_plot_filepath': accuracy_plot_path,
    'forgetting_curve_filepath': forgetting_plot_path,
    'accuracy_plot_caption': 'Figure X: Accuracy progression as materials are introduced sequentially. CLIFF maintains higher and more stable accuracy compared to naive fine‑tuning and prompt‑only baselines.',
    'forgetting_curve_caption': 'Figure Y: Forgetting magnitude for each material. CLIFF exhibits substantially lower forgetting than the baselines, confirming its continual‑learning capability.'
}
print(json.dumps(output, indent=2))
``` |

#### 6. Add robust error handling: if the metrics JSON is missing any required key, raise a `KeyError` with a clear message; if the `figures/` directory does not exist, create it before saving.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node fails gracefully and produces reproducible artefacts even when upstream steps change. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs('figures', exist_ok=True)`; wrap the plotting code in a `try/except` block that logs the exception and re‑raises it. |


---

## set_up_memory_replay_buffer

### Description
Create a buffer that stores exemplar samples from previously learned materials for replay during continual training.

### Implementation Plan

#### 1. Load the JSON split files produced by the `split_datasets` node (train_split_json_paths, validation_split_json_paths, test_split_json_paths) to retrieve the full list of image file paths and their associated class (layer count) labels for each material.

| Category | Details |
| --- | --- |
| **Reason** | The split files are the authoritative source of which images belong to which class; using them guarantees reproducibility and alignment with downstream training splits. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read each JSON with Python's `json.load`, iterate over entries to build a mapping `material -> {class_id -> [file_path, ...]}`. |

#### 2. Define a global memory budget (e.g., 2,000 exemplars) and compute `exemplars_per_class` as `budget // (total_number_of_classes_across_all_materials)`. If the budget is insufficient for a uniform allocation, fall back to a minimum of 5 exemplars per class and adjust the budget accordingly.

| Category | Details |
| --- | --- |
| **Reason** | A fixed budget controls RAM/disk usage and ensures the replay buffer remains scalable as more materials are added. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Calculate `total_number_of_classes_across_all_materials` by counting unique layer IDs across all materials; use integer division; enforce a lower bound via `max(min_per_class, computed_value)`. |

#### 3. Implement a stratified sampling strategy per class: for each `class_id` within each material, select `exemplars_per_class` images using the "herding" algorithm (choose samples whose feature embeddings are closest to the class centroid) if pre‑computed features exist, otherwise fall back to random uniform sampling with a fixed random seed for reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Herding preserves the distributional characteristics of each class better than pure random sampling, which improves knowledge‑distillation performance. |
| **Impact** | MEDIUM |
| **Complexity** | HIGH |
| **Method** | If feature vectors are stored in `features/<material>/<image_id>.npy`, load them, compute class centroid, rank images by Euclidean distance to centroid, pick top‑k; otherwise use `random.sample` with `np.random.seed(42)`. |

#### 4. Create a dedicated buffer directory (`buffer_directory`) on the filesystem, e.g., `./replay_buffer/`. Within it, create sub‑folders for each material (`graphene/`, `MoS2/`, …) and further sub‑folders for each class ID (`class_0/`, `class_1/`, …). Copy or hard‑link the selected exemplar image files into the appropriate sub‑folder.

| Category | Details |
| --- | --- |
| **Reason** | A hierarchical directory layout mirrors the logical organization (material → class) and simplifies path‑based retrieval without requiring a database. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs` with `exist_ok=True`; copy with `shutil.copy2` or create hard links via `os.link` to avoid duplicating data. |

#### 5. Populate the `exemplar_file_paths` list with the absolute (or project‑relative) paths of all copied exemplar files, preserving the order `material -> class_id -> file` for deterministic indexing.

| Category | Details |
| --- | --- |
| **Reason** | Downstream components (loss definition, training loops) need a flat list of paths to load images on‑the‑fly. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Walk the buffer directory with `os.walk`, filter by image extensions, sort paths lexicographically, and append to the list. |

#### 6. Generate the `class_ids` list by enumerating all unique class identifiers present in the buffer (e.g., `[0,1,2,3]` for layer counts). Store them in ascending order to align with the ordering used in the loss function and prompt indexing.

| Category | Details |
| --- | --- |
| **Reason** | A canonical ordering prevents mismatches between class‑specific exemplars and model outputs during distillation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Collect class IDs while sampling; use `sorted(set(collected_ids))`. |

#### 7. Compute `total_exemplars` as `len(exemplar_file_paths)` and verify that `total_exemplars == exemplars_per_class * len(class_ids) * number_of_materials`. Raise an exception if the equality does not hold.

| Category | Details |
| --- | --- |
| **Reason** | Integrity check catches bugs in the sampling or file‑copy stages early, avoiding silent downstream errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple arithmetic comparison; raise `ValueError` with a descriptive message if mismatched. |

#### 8. Design a lightweight retrieval API called `get_replay_batch(class_ids: Optional[List[int]] = None, batch_size: int = 32, shuffle: bool = True) -> Tuple[torch.Tensor, List[int]]`. The function loads images from `exemplar_file_paths` (using Pillow or OpenCV), applies the same preprocessing pipeline as training data, returns a tensor batch and the corresponding class IDs.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulating the loading logic behind a well‑documented function keeps training loops clean and enables easy swapping of storage back‑ends later. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement the function in `replay_buffer.py`; use `torch.utils.data.Dataset` subclass for lazy loading; support optional filtering by `class_ids` and optional shuffling via `torch.utils.data.DataLoader`. |

#### 9. Write a concise `retrieval_api_description` string summarizing the function signature, input arguments, return types, and any side‑effects (e.g., on‑the‑fly augmentation). Example: `"def get_replay_batch(class_ids: List[int] = None, batch_size: int = 32, shuffle: bool = True) -> (Tensor[batch, C, H, W], List[int])"`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (e.g., `define_knowledge_distillation_loss` and `incremental_train_material_specific_components`) need a human‑readable contract to invoke the buffer correctly. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a one‑line docstring and store it in the output field. |

#### 10. Serialize a metadata JSON file (`metadata.json`) inside `buffer_directory` containing all output fields (`buffer_directory`, `exemplars_per_class`, `total_exemplars`, `class_ids`, `exemplar_file_paths`). This file serves as a checkpoint for reproducibility and debugging.

| Category | Details |
| --- | --- |
| **Reason** | Persisting metadata enables other pipeline stages to reload the buffer without recomputing it, saving time on repeated experiments. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `json.dump` with `indent=2`; ensure paths are stored relative to the project root for portability. |


---

## split_datasets

### Description
Create train/validation/test splits for the reference and each new material while preserving class balance.

### Implementation Plan

#### 1. Collect the list of material directories from the `processed_images_dir` output of `preprocess_images` and infer `material_names` by parsing directory names.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the splitting procedure automatically adapts to any number of materials without hard‑coding identifiers. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `os.listdir` on the root processed images directory; filter out non‑folder entries; sort alphabetically for deterministic ordering. |

#### 2. For each material, read a manifest CSV (or generate one on‑the‑fly) that maps every image file path to its class label (layer count).

| Category | Details |
| --- | --- |
| **Reason** | Accurate class labels are required to perform stratified sampling that preserves class balance across splits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If a `metadata.csv` exists in the material folder, load with `pandas.read_csv`; otherwise, infer label from filename convention using regex; store in a DataFrame with columns `["filepath", "label"]`. |

#### 3. Validate that each material has at least a minimum number of samples per class (e.g., 5) to allow a meaningful 70/15/15 split; raise a warning or fallback to a simple random split if the condition is not met.

| Category | Details |
| --- | --- |
| **Reason** | Stratified splitting fails when a class has too few instances; early detection prevents downstream errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Group by `label` and count; compare counts to a threshold; log results with Python's `logging` module. |

#### 4. Perform a stratified split for each material using `sklearn.model_selection.StratifiedShuffleSplit` with `test_size=0.30` and `train_size=0.70`, then further split the 30% into validation and test (15% each) using a second `StratifiedShuffleSplit` on the held‑out set.

| Category | Details |
| --- | --- |
| **Reason** | StratifiedShuffleSplit guarantees that each split mirrors the original class distribution while the fixed `random_state` ensures reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Set `random_state=42` (or configurable seed). First split: `train_idx, holdout_idx = sss.split(filepaths, labels)`. Second split on holdout: `val_idx, test_idx = sss2.split(holdout_filepaths, holdout_labels)`. |

#### 5. Create dedicated output directories for each split: `<split_root>/<material>/train/`, `<split_root>/<material>/val/`, `<split_root>/<material>/test/` and copy (or symlink) the selected image files into these folders.

| Category | Details |
| --- | --- |
| **Reason** | Physical separation of splits simplifies downstream data loaders and prevents accidental leakage between training and evaluation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `os.makedirs(..., exist_ok=True)`. For large datasets, prefer `os.symlink` to avoid duplication; fallback to `shutil.copy2` if symlinks are unsupported. |

#### 6. Serialize the absolute file paths of each split into JSON files named `<material>_train.json`, `<material>_val.json`, and `<material>_test.json` stored under a central `splits/` directory.

| Category | Details |
| --- | --- |
| **Reason** | JSON files are lightweight, language‑agnostic, and can be directly consumed by downstream training scripts. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dict `{ "paths": [list_of_paths] }` and write with `json.dump(..., indent=2)`. Collect the generated JSON filepaths into the respective output lists. |

#### 7. Generate a human‑readable `split_ratio_description` string (e.g., "70% train / 15% validation / 15% test") and attach it to the node output.

| Category | Details |
| --- | --- |
| **Reason** | Provides downstream nodes with a concise summary for logging and reporting purposes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Hard‑code the description based on the ratios used; make it configurable via a constant at the top of the script. |

#### 8. Run a post‑split verification: compute class distribution for each generated split and assert that the deviation from the original distribution is ≤ 2% per class; log any violations as warnings.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the stratification succeeded and that downstream evaluation will be fair. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Re‑load each JSON, map paths back to labels using the earlier manifest, compute histograms with `numpy.bincount`, compare percentages, and use `assert` or `logging.warning`. |

#### 9. Return the five output fields (`material_names`, `train_split_json_paths`, `validation_split_json_paths`, `test_split_json_paths`, `split_ratio_description`) in the order defined by the node schema.

| Category | Details |
| --- | --- |
| **Reason** | Ensures strict compliance with the DAG contract and enables downstream nodes to consume the splits without additional parsing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assemble a dictionary matching the schema and `return` it from the node's execution function. |


---

## train_base_model_on_reference

### Description
Train the backbone and base head on the reference material dataset, then freeze them.

### Implementation Plan

#### 1. Parse the split_datasets output to locate the JSON file that lists file‑paths for the reference material's training split (identified by the material name matching the ‘material’ field of the reference dataset).

| Category | Details |
| --- | --- |
| **Reason** | Accurate loading of the correct training data is fundamental; the split JSON guarantees class‑balanced, reproducible splits. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `train_split_json_paths` list; match the index of the reference material name in `material_names`; load the JSON array of image paths using Python's `json` module. |

#### 2. Similarly parse split_datasets to obtain the reference material's validation split JSON for monitoring validation accuracy each epoch.

| Category | Details |
| --- | --- |
| **Reason** | Validation data is required to decide early‑stopping or to record the final validation metric. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the same index as above on `validation_split_json_paths`; load file paths into a validation dataset object. |

#### 3. Extract the backbone and base‑head architectural specifications from design_backbone_and_base_head (e.g., `backbone_architecture`, `backbone_layers`, `base_head_architecture`, `base_head_input_dimension`, `base_head_output_dimension`, `initialization_strategy`).

| Category | Details |
| --- | --- |
| **Reason** | The model must be instantiated exactly as designed to ensure downstream components (prompt pool, delta head) align with dimensions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map `backbone_architecture` to a PyTorch model class (e.g., torchvision.models.resnet50); rebuild the head as a `nn.Linear(base_head_input_dimension, base_head_output_dimension)`; apply the specified `initialization_strategy` (Xavier for linear layers, Kaiming for conv layers) via custom weight‑initialization functions. |

#### 4. Create a PyTorch `Dataset` class that reads image files from the training split, applies the same preprocessing pipeline used in `preprocess_images` (resize, normalize with the stored `normalization_mean` and `normalization_std`), and returns (image_tensor, label).

| Category | Details |
| --- | --- |
| **Reason** | Ensuring preprocessing consistency between pre‑training and later stages prevents distribution shift. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Subclass `torch.utils.data.Dataset`; inside `__getitem__` load image via PIL, resize to target dimensions (from `preprocess_images` output), convert to tensor, normalize, and fetch label from accompanying metadata CSV. |

#### 5. Instantiate DataLoaders for training and validation using the batch size `base_batch_size` from configure_training_hyperparameters, with `shuffle=True` for training and `shuffle=False` for validation.

| Category | Details |
| --- | --- |
| **Reason** | Efficient batching and shuffling are required for stable gradient updates and reproducible validation scores. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `torch.utils.data.DataLoader(train_dataset, batch_size=base_batch_size, shuffle=True, num_workers=4)`; similarly for validation with `shuffle=False`. |

#### 6. Configure the optimizer as `base_optimizer` (e.g., AdamW) with learning rate `base_learning_rate`; optionally add weight decay as per best practices for CNN pre‑training.

| Category | Details |
| --- | --- |
| **Reason** | Hyper‑parameter alignment guarantees that the base model is trained under the same regime expected by downstream incremental training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `optimizer = torch.optim.AdamW(model.parameters(), lr=base_learning_rate, weight_decay=1e-4)` if `base_optimizer` == "AdamW"; otherwise map string to appropriate torch optimizer class. |

#### 7. Implement the training loop for exactly `base_epochs` iterations: for each epoch, iterate over the training DataLoader, forward‑pass through backbone → base head, compute cross‑entropy loss, back‑propagate, and step the optimizer.

| Category | Details |
| --- | --- |
| **Reason** | The core learning process; must be deterministic and record metrics for reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Pseudo‑code: `for epoch in range(base_epochs): model.train(); for imgs, lbls in train_loader: optimizer.zero_grad(); logits = model(imgs); loss = criterion(logits, lbls); loss.backward(); optimizer.step();` |

#### 8. After each epoch, evaluate the model on the validation DataLoader, compute top‑1 accuracy, and log `epoch`, `train_loss`, `val_accuracy` to a JSON or CSV logger for later inspection.

| Category | Details |
| --- | --- |
| **Reason** | Monitoring validation accuracy enables reporting `base_model_validation_accuracy` and early detection of divergence. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Set `model.eval()`, disable grad, compute predictions, compare with labels, accumulate correct/total counts; store `val_accuracy` in a dict keyed by epoch. |

#### 9. Upon completion of all epochs, record the final validation accuracy (the accuracy from the last epoch) as `base_model_validation_accuracy`.

| Category | Details |
| --- | --- |
| **Reason** | This scalar is part of the node's required output and serves as a baseline metric for later continual‑learning phases. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Extract the last entry from the validation logger; assign to output variable. |

#### 10. Save the entire model state dict to a deterministic file path, e.g., `models/base_model_epoch{base_epochs}.pth`; assign this path to `base_model_weights_path`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (freeze_backbone_and_base_head, incremental training) need to load the exact trained weights. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `torch.save(model.state_dict(), base_model_weights_path)`; ensure the directory exists. |

#### 11. Freeze the backbone and base head by iterating over `model.backbone.parameters()` and `model.base_head.parameters()` and setting `param.requires_grad = False`.

| Category | Details |
| --- | --- |
| **Reason** | The specification demands a frozen backbone for continual‑learning; freezing prevents accidental gradient updates later. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
for param in model.backbone.parameters():
    param.requires_grad = False
for param in model.base_head.parameters():
    param.requires_grad = False
``` |

#### 12. Verify freezing by checking that `any(p.requires_grad for p in model.backbone.parameters())` and similarly for the base head returns `False`; set `backbone_frozen_status` and `base_head_frozen_status` accordingly.

| Category | Details |
| --- | --- |
| **Reason** | A verification step ensures correctness before downstream nodes consume the frozen model. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `backbone_frozen_status = not any(p.requires_grad for p in model.backbone.parameters())` and similarly for `base_head_frozen_status`. |

#### 13. Populate the final output dictionary with all required fields (`base_model_weights_path`, `base_model_training_epochs`, `base_model_validation_accuracy`, `backbone_frozen_status`, `base_head_frozen_status`) and return it from the node execution function.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract; enables downstream nodes to consume structured outputs. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dict matching `output_structure` and serialize to JSON if the workflow engine expects file‑based outputs. |


---

## train_naive_fine_tuning_baseline

### Description
Fine‑tune the entire backbone and head on each new material sequentially without any continual‑learning safeguards, to serve as a baseline.

### Implementation Plan

#### 1. Instantiate the model architecture using the backbone_architecture, backbone_layers, base_head_architecture, base_head_input_dimension, and base_head_output_dimension values emitted by the design_backbone_and_base_head node; load any pre‑trained weights from the most recent checkpoint (or random init if first material).

| Category | Details |
| --- | --- |
| **Reason** | Ensures the training script builds exactly the same network topology that downstream nodes expect, preserving reproducibility across experiments. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the JSON output of design_backbone_and_base_head, map layer names to PyTorch (or TensorFlow) modules, construct the model class, and implement a helper `load_weights(path)` that restores state_dict if a checkpoint exists. |

#### 2. Set all model parameters to `requires_grad=True` (unfreeze) before training each material, overriding any previous freezing that may have been applied during base pre‑training.

| Category | Details |
| --- | --- |
| **Reason** | The baseline deliberately fine‑tunes the entire network, so every weight must be learnable for each incremental step. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `model.parameters()` and set `.requires_grad = True`; verify with a diagnostic print of the number of trainable parameters. |

#### 3. Read the split_datasets node output to obtain `material_names`, `train_split_json_paths`, and `validation_split_json_paths`. Ensure the ordering of these three lists is identical, establishing a deterministic material sequence.

| Category | Details |
| --- | --- |
| **Reason** | The script must know exactly which JSON file corresponds to which material to load the correct image file paths for training and validation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Load each JSON file (list of image file paths) using `json.load()`. Store in a dict `{material: {'train': [...], 'val': [...]}}` for fast lookup. |

#### 4. Extract hyper‑parameters from configure_training_hyperparameters: use `base_optimizer`, `base_learning_rate`, `base_batch_size`, and `base_epochs` as the training schedule for the naive fine‑tuning baseline (these values are appropriate because no replay or prompt learning is involved).

| Category | Details |
| --- | --- |
| **Reason** | The baseline must share the same optimizer and learning‑rate regime as the base model to make a fair comparison; the incremental_* hyper‑parameters are specific to CL‑based methods and should not be used here. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a mapping `optimizer_cls = getattr(torch.optim, base_optimizer)`; instantiate `optimizer = optimizer_cls(model.parameters(), lr=base_learning_rate)`. |

#### 5. For each material in `material_names` (loop order preserved from split_datasets):
   a. Build a training `DataLoader` from the material's train split using `base_batch_size` and standard augmentations (random flip, rotation) that were applied during preprocessing.
   b. Build a validation `DataLoader` from the material's validation split (no augmentation, deterministic transforms).
   c. Reset the optimizer state at the start of each material to avoid cross‑material momentum leakage.
   d. Run a training epoch loop for `base_epochs` iterations:
      i.   Forward pass, compute cross‑entropy loss against ground‑truth labels.
      ii.  Back‑propagation (`loss.backward()`), optimizer step, and zero gradients.
      iii. Optionally log training loss and accuracy to a CSV/logger.
   e. After each epoch, evaluate on the validation set; keep the checkpoint with the highest validation accuracy for that material.
   f. Save the selected checkpoint to `checkpoints/{material}_epoch{best_epoch}.pth` and record the path in `trained_checkpoints`.
   g. Append `material` to `materials_fine_tuned` and `base_epochs` to `epochs_per_material`.
   h. Store the best validation accuracy for the material; if the material is the last in the sequence, also assign it to `final_validation_accuracy`.


| Category | Details |
| --- | --- |
| **Reason** | These steps constitute the core naive fine‑tuning loop: fully unfreeze, train on the new material, checkpoint the best model, and move on without any memory replay or prompt updates. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a reusable function `train_one_material(model, train_loader, val_loader, optimizer, epochs)` that returns `best_checkpoint_path` and `best_val_accuracy`. Use `torch.save(model.state_dict(), path)`. Ensure deterministic seeding (`torch.manual_seed(42)`) for reproducibility. |

#### 6. Wrap the entire material‑wise training loop in a try/except block; on any exception set `training_success = False` and break, otherwise after the loop set `training_success = True`.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear boolean flag required by downstream evaluation nodes and guarantees graceful failure handling. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python's `try: ... except Exception as e: logging.error(e); training_success = False` pattern. |

#### 7. After all materials have been processed, verify that the lengths of `trained_checkpoints`, `materials_fine_tuned`, and `epochs_per_material` are identical and match the number of materials; raise an assertion error if mismatched.

| Category | Details |
| --- | --- |
| **Reason** | Ensures output consistency with the schema and prevents downstream nodes from encountering shape mismatches. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `assert len(trained_checkpoints) == len(materials_fine_tuned) == len(epochs_per_material) == len(material_names)`. |

#### 8. Log a summary JSON file (`baseline_fine_tuning_summary.json`) containing all output fields for provenance, and optionally upload the file to the experiment tracking system (e.g., MLflow, Weights & Biases).

| Category | Details |
| --- | --- |
| **Reason** | Facilitates reproducibility, auditability, and easy consumption by `compute_accuracy_and_forgetting_metrics` which expects the checkpoint list and material order. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Create a dictionary with keys matching the output_structure, `json.dump` it with indent=2, and store under `outputs/` directory. |


---

## train_prompt_based_baseline

### Description
Train only material prompts (no delta head, no replay) on each new material to serve as a prompt‑only baseline.

### Implementation Plan

#### 1. Load hyper‑parameter configuration from the output of `configure_training_hyperparameters` (base_optimizer, incremental_prompt_learning_rate, incremental_batch_size, incremental_epochs).

| Category | Details |
| --- | --- |
| **Reason** | Centralising hyper‑parameters ensures consistency across all training scripts and makes future tuning straightforward. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read a JSON/YAML file produced by the parent node; map fields to local variables; assert required keys exist. |

#### 2. Instantiate the frozen backbone and base head using the architecture specifications from `design_backbone_and_base_head`; load pre‑trained weights if available.

| Category | Details |
| --- | --- |
| **Reason** | The backbone must remain frozen during prompt‑only training; using the same architecture guarantees compatibility with the prompt pool. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create PyTorch model objects (e.g., torchvision.models.resnet50); call `model.load_state_dict(torch.load(path))`; set `requires_grad=False` for all parameters of backbone and base head. |

#### 3. Create the prompt pool according to `implement_prompt_pool_structure` output (prompt_pool_variable_name, prompt_dimension, number_of_materials, material_ids, initialization_method).

| Category | Details |
| --- | --- |
| **Reason** | A deterministic prompt pool allows each material to have its own learnable vector that will be updated independently. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Initialize a `nn.Parameter` tensor of shape `(number_of_materials, prompt_dimension)` using the specified method (e.g., torch.randn * 0.02); store in a `nn.Module` named as per `prompt_pool_variable_name`. |

#### 4. Freeze all parameters except the prompt pool: verify that only the prompt parameters have `requires_grad=True`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that no accidental gradient updates affect the backbone or base head, matching the baseline specification. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `model.parameters()` and assert `requires_grad` is False; iterate over prompt pool parameters and assert True; raise error if mismatch. |

#### 5. For each material listed in the `split_datasets` output, load its training and validation JSON split files, build `torch.utils.data.Dataset` objects that return (image_tensor, label) pairs, and wrap them in `DataLoader`s using `incremental_batch_size`.

| Category | Details |
| --- | --- |
| **Reason** | Material‑specific DataLoaders provide the correct data stream for isolated prompt training while keeping the code reusable. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a custom `FlakeDataset` that reads image paths from the JSON, applies the same preprocessing pipeline used for the base model, and returns tensors; create `DataLoader(train_dataset, batch_size, shuffle=True)` and `DataLoader(val_dataset, batch_size, shuffle=False)`. |

#### 6. Create an optimizer (e.g., AdamW) that only receives the prompt pool parameters and uses `incremental_prompt_learning_rate` as learning rate.

| Category | Details |
| --- | --- |
| **Reason** | Separate optimizer prevents accidental updates to frozen components and respects the learning‑rate schedule defined for prompts. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | optimizer = torch.optim.AdamW(prompt_pool.parameters(), lr=incremental_prompt_learning_rate, weight_decay=0.01). |

#### 7. Implement the training loop: for `epoch` in range(`incremental_epochs`): iterate over the material's training DataLoader, for each batch retrieve the prompt vector corresponding to the current material ID, prepend/concatenate it to the backbone feature map as defined by `integration_method`, forward through the frozen backbone and base head, compute cross‑entropy loss against labels, back‑propagate (`loss.backward()`), and call `optimizer.step()` followed by `optimizer.zero_grad()`.

| Category | Details |
| --- | --- |
| **Reason** | This loop isolates gradient flow to the prompt vectors only, fulfilling the prompt‑only baseline requirement. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Pseudo‑code: 
```
for epoch in range(num_epochs):
    for images, labels in train_loader:
        prompt_vec = prompt_pool[material_index].unsqueeze(0).expand(images.size(0), -1)
        features = backbone(images)
        gated = torch.cat([prompt_vec, features], dim=1)  # or per integration_method
        logits = base_head(gated)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
```
 |

#### 8. After each epoch, evaluate on the material's validation DataLoader using the same forward path (no gradient), compute top‑1 accuracy, and store the best‑validation‑accuracy checkpoint of the prompt vectors.

| Category | Details |
| --- | --- |
| **Reason** | Validation monitoring is essential to detect over‑fitting and to select the final prompt vector for each material. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Set `model.eval()`, disable gradient with `torch.no_grad()`, compute predictions, compare with labels, calculate accuracy; if current accuracy > best, save `prompt_pool[material_index].cpu().detach()` to a file path like `prompts/{material_id}_prompt.pt`. |

#### 9. After finishing all epochs for a material, append the saved prompt file path to `prompt_vectors_trained` and the best validation accuracy to `validation_accuracy_per_material`.

| Category | Details |
| --- | --- |
| **Reason** | Aggregating these values fulfills the required output schema and provides downstream nodes with ready‑to‑load prompt vectors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain Python lists; after each material loop, `prompt_vectors_trained.append(prompt_path)` and `validation_accuracy_per_material.append(best_acc)`. |

#### 10. Repeat the material‑wise training loop for every material listed in the split‑datasets output, keeping the same optimizer (which will continue updating the prompt pool for new indices) and resetting epoch counters per material.

| Category | Details |
| --- | --- |
| **Reason** | Sequential training mirrors the continual‑learning order while still adhering to the baseline constraint of no replay or delta head. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop over `material_ids`; for each, call the per‑material training routine; ensure the optimizer’s state is not cleared between materials so learning rate schedule remains consistent. |

#### 11. Set `prompt_training_status` to `True` if all material loops complete without exception; otherwise catch exceptions, log error details, and set the flag to `False`.

| Category | Details |
| --- | --- |
| **Reason** | A binary status flag provides a clear success/failure signal for downstream evaluation nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Wrap the outermost material loop in a try/except block; on success, `prompt_training_status = True`; on failure, `prompt_training_status = False` and write the exception to a log file. |

#### 12. Assign `training_epochs_completed` the value of `incremental_epochs` (or the actual number of epochs run if early stopping was implemented).

| Category | Details |
| --- | --- |
| **Reason** | Outputs the exact training budget used, which is needed for reproducibility and for the `compute_accuracy_and_forgetting_metrics` node. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | If early stopping is added, store the epoch index at which training stopped; otherwise copy `incremental_epochs`. |

#### 13. Serialize the final JSON output containing all four fields (`prompt_training_status`, `prompt_vectors_trained`, `validation_accuracy_per_material`, `training_epochs_completed`) to the path expected by downstream nodes (e.g., `artifacts/prompt_baseline_output.json`).

| Category | Details |
| --- | --- |
| **Reason** | Standardised artifact storage enables downstream nodes to read the outputs without custom parsing logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python `json.dump` with `indent=2`; ensure the file path is communicated via a known environment variable or a config entry. |


---

## write_summary_report

### Description
Compose a concise report summarizing methodology, experiments, results, and key conclusions about CLIFF.

### Implementation Plan

#### 1. Load the markdown table output (`markdown_table`) from the `generate_comparative_results_table` node and store it as a raw string for later insertion into the Results section.

| Category | Details |
| --- | --- |
| **Reason** | The comparative table is the core quantitative evidence for CLIFF's superiority and must be reproduced verbatim in the report. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `markdown_table` field from the parent node's JSON payload, verify that it contains a valid markdown table (e.g., starts with `|`), and assign it to a variable `comparative_table`. |

#### 2. Load the filepaths (`accuracy_plot_filepath` and `forgetting_curve_filepath`) and captions (`accuracy_plot_caption`, `forgetting_curve_caption`) from the `produce_visualizations` node.

| Category | Details |
| --- | --- |
| **Reason** | Figures provide visual reinforcement of the numerical trends and are required for the Results section. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Extract the four string fields, check that the paths exist on the filesystem, and copy the images into a `figures/` sub‑directory of the report output folder. |

#### 3. Compose the Abstract by summarizing (i) the problem of continual learning for 2‑D material classification, (ii) the CLIFF framework, (iii) key quantitative gains (e.g., +X% overall accuracy, -Y% forgetting), and (iv) the broader impact.

| Category | Details |
| --- | --- |
| **Reason** | The abstract must be self‑contained and give readers a rapid understanding of contributions. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use template strings with placeholders filled from the metrics in `overall_accuracies` and `average_forgettings` (parent node outputs) and concise language. |

#### 4. Write the Introduction by reviewing prior work on continual learning and prompt‑based adaptation, stating the research gap, and motivating CLIFF's design choices (frozen backbone + prompt pool + delta head).

| Category | Details |
| --- | --- |
| **Reason** | Sets the context and justifies why the proposed method matters. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Combine domain‑specific literature references (hard‑coded or configurable) with bullet‑point rationale; no external data needed. |

#### 5. Generate the Method section using the design specifications from `design_backbone_and_base_head`, `implement_prompt_pool_structure`, `implement_cosine_similarity_gate`, `implement_delta_head`, and `configure_training_hyperparameters` nodes. Enumerate architecture, training schedule, replay buffer, and distillation loss.

| Category | Details |
| --- | --- |
| **Reason** | Readers need a reproducible description of the full CLIFF pipeline. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Iterate over each referenced node, extract key fields (e.g., `backbone_architecture`, `prompt_dimension`, `loss_expression`), and format them into subsections with code snippets where appropriate. |

#### 6. Create the Experiments section describing dataset collection (`collect_reference_material_dataset`, `collect_new_material_datasets`), preprocessing (`preprocess_images`), splitting (`split_datasets`), and evaluation metrics (accuracy, forgetting). Include a concise table summarizing dataset sizes and split ratios.

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency on experimental rigor and reproducibility. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Pull dataset statistics from `collect_*` nodes if available, otherwise synthesize a summary based on typical values; embed a markdown table manually. |

#### 7. Populate the Results section with: (a) the `comparative_table` markdown, (b) the two figures inserted via standard Markdown image syntax (`![](figures/accuracy_plot.png)`), using the captions from the visualization node, and (c) a narrative interpretation of the numbers (e.g., percentage improvements, statistical significance if available).

| Category | Details |
| --- | --- |
| **Reason** | Directly presents the empirical evidence and ties it back to the research questions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | String‑concatenate the table, then add newline, then embed images with captions; parse numeric values from `overall_accuracies` and `average_forgettings` arrays to compute delta values for the narrative. |

#### 8. Draft the Discussion by analyzing why CLIFF outperforms baselines: effect of prompt pool gating, reduced forgetting via replay‑distillation, trade‑offs of frozen backbone, and potential failure modes. Cite specific rows of the comparative table to back claims.

| Category | Details |
| --- | --- |
| **Reason** | Critical reflection demonstrates deep understanding and guides future work. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over each model row, compare per‑material accuracies, and articulate observations; add bullet points for limitations and open questions. |

#### 9. Write the Conclusion summarizing the main achievements (e.g., X% accuracy gain, Y% forgetting reduction), reiterating the significance for continual learning in materials science, and outlining concrete next steps (e.g., scaling to more materials, exploring alternative prompt encodings).

| Category | Details |
| --- | --- |
| **Reason** | Ends the report with a clear take‑away and roadmap. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Reuse key numbers already mentioned; keep the paragraph concise (3‑4 sentences). |

#### 10. Assemble all section strings (`abstract`, `introduction`, `method`, `experiments`, `results`, `discussion`, `conclusion`) into a single JSON object matching the defined output structure and return it from the node.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract and makes downstream consumption trivial. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dictionary with keys exactly as listed in `output_structure` and serialize it; ensure no stray newline characters break the JSON formatting. |

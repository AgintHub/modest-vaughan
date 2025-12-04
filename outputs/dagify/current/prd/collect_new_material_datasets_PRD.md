# collect_new_material_datasets PRD

## Description
Gather labeled optical‑microscopy datasets for each additional 2D material that will be introduced sequentially.


## Implementation Plan

### 1. Select three target 2D materials (MoS2, WS2, h‑BN) based on literature prevalence and availability of exfoliation sources.

| Category | Details |
| --- | --- |
| **Reason** | Choosing well‑studied materials ensures that reference data exists and that downstream models have meaningful class diversity. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Consult recent 2D‑material review papers; create a table mapping material → typical flake thickness range; confirm substrate compatibility (SiO2/Si). |

### 2. Define standard substrate preparation protocol for each material (clean SiO2 wafer, spin‑coat PMMA optional, annealing temperature).

| Category | Details |
| --- | --- |
| **Reason** | Consistent substrate preparation reduces systematic imaging variance across materials, facilitating fair model comparison. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write SOP document; include cleaning steps (piranha, acetone, IPA), bake temperature (150 °C, 5 min), and storage conditions; store SOP as markdown in repo. |

### 3. Specify optical‑microscope configuration: illumination type (bright‑field), objective magnification (50×), numerical aperture (0.8), exposure time (10 ms), pixel resolution (0.2 µm/pixel).

| Category | Details |
| --- | --- |
| **Reason** | Uniform imaging settings enable direct pixel‑wise comparison and reduce domain shift when training the backbone. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a calibration checklist; capture a reference grid image before each acquisition session; log settings in a CSV file per session. |

### 4. Create a data‑capture schedule: for each material, acquire at least 5,000 raw images covering different flake sizes, orientations, and defect types.

| Category | Details |
| --- | --- |
| **Reason** | A minimum sample size guarantees statistical significance for class‑balance during stratified splitting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a spreadsheet tracker with columns: material, session_id, image_id, flake_id, target_layer_count; aim for ~1,000 images per layer class (1‑5 L). |

### 5. Develop annotation guidelines: define label taxonomy (layer_count ∈ {1,2,3,4,5}, defect_type ∈ {none, tear, wrinkle, contamination}), image_quality thresholds (SNR > 10 dB, no motion blur).

| Category | Details |
| --- | --- |
| **Reason** | Clear, reproducible annotation rules ensure high inter‑annotator agreement and reliable downstream training. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Write a 2‑page protocol, include example annotated images; integrate into labeling tool (e.g., Labelbox) with mandatory fields; enforce validation scripts to reject out‑of‑range values. |

### 6. Execute labeling workflow: assign two independent annotators per image, resolve conflicts via a senior reviewer, and export consolidated CSV per material.

| Category | Details |
| --- | --- |
| **Reason** | Dual‑annotation plus arbitration reduces labeling errors and provides a reliability metric (Cohen’s κ). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Automate assignment using a Python script that pulls image paths from the capture directory; schedule weekly review meetings; store final CSV in <project_root>/metadata/<material>_labels.csv. |

### 7. Store each material’s labeled dataset in a version‑controlled cloud bucket (e.g., gs://cliff-datasets/<material>/) using a directory layout: raw/, annotated/, splits/. Include a manifest JSON summarizing counts and hash values.

| Category | Details |
| --- | --- |
| **Reason** | Centralized, immutable storage simplifies reproducibility and enables downstream pipeline access across compute nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use gsutil to sync local folders; generate manifest via a Bash/Python one‑liner that computes SHA256 for each file; commit manifest to Git. |

### 8. Perform stratified train/validation/test split per material with a 70/15/15 ratio, ensuring each layer class is proportionally represented in each split.

| Category | Details |
| --- | --- |
| **Reason** | Stratification preserves class distribution, preventing skewed performance metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a Python function using sklearn.model_selection.StratifiedShuffleSplit; output three JSON files (train_<material>.json, val_<material>.json, test_<material>.json) containing file paths and label metadata. |

### 9. Populate the output fields: list of material names, collection method strings, annotation guideline summaries, storage paths, split ratio strings, total image counts after QC, and set is_dataset_ready = true only if all previous steps succeeded without errors.

| Category | Details |
| --- | --- |
| **Reason** | Fulfilling the defined output structure is required for downstream nodes to consume the data correctly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Write a final aggregation script that reads the manifest, counts images per material, validates existence of split JSONs, and writes a single JSON payload matching the Output Structure schema. |

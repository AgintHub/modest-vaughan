# split_datasets PRD

## Description
Create train/validation/test splits for the reference and each new material while preserving class balance.


## Implementation Plan

### 1. Collect the list of material directories from the `processed_images_dir` output of `preprocess_images` and infer `material_names` by parsing directory names.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the splitting procedure automatically adapts to any number of materials without hard‑coding identifiers. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `os.listdir` on the root processed images directory; filter out non‑folder entries; sort alphabetically for deterministic ordering. |

### 2. For each material, read a manifest CSV (or generate one on‑the‑fly) that maps every image file path to its class label (layer count).

| Category | Details |
| --- | --- |
| **Reason** | Accurate class labels are required to perform stratified sampling that preserves class balance across splits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If a `metadata.csv` exists in the material folder, load with `pandas.read_csv`; otherwise, infer label from filename convention using regex; store in a DataFrame with columns `["filepath", "label"]`. |

### 3. Validate that each material has at least a minimum number of samples per class (e.g., 5) to allow a meaningful 70/15/15 split; raise a warning or fallback to a simple random split if the condition is not met.

| Category | Details |
| --- | --- |
| **Reason** | Stratified splitting fails when a class has too few instances; early detection prevents downstream errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Group by `label` and count; compare counts to a threshold; log results with Python's `logging` module. |

### 4. Perform a stratified split for each material using `sklearn.model_selection.StratifiedShuffleSplit` with `test_size=0.30` and `train_size=0.70`, then further split the 30% into validation and test (15% each) using a second `StratifiedShuffleSplit` on the held‑out set.

| Category | Details |
| --- | --- |
| **Reason** | StratifiedShuffleSplit guarantees that each split mirrors the original class distribution while the fixed `random_state` ensures reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Set `random_state=42` (or configurable seed). First split: `train_idx, holdout_idx = sss.split(filepaths, labels)`. Second split on holdout: `val_idx, test_idx = sss2.split(holdout_filepaths, holdout_labels)`. |

### 5. Create dedicated output directories for each split: `<split_root>/<material>/train/`, `<split_root>/<material>/val/`, `<split_root>/<material>/test/` and copy (or symlink) the selected image files into these folders.

| Category | Details |
| --- | --- |
| **Reason** | Physical separation of splits simplifies downstream data loaders and prevents accidental leakage between training and evaluation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `os.makedirs(..., exist_ok=True)`. For large datasets, prefer `os.symlink` to avoid duplication; fallback to `shutil.copy2` if symlinks are unsupported. |

### 6. Serialize the absolute file paths of each split into JSON files named `<material>_train.json`, `<material>_val.json`, and `<material>_test.json` stored under a central `splits/` directory.

| Category | Details |
| --- | --- |
| **Reason** | JSON files are lightweight, language‑agnostic, and can be directly consumed by downstream training scripts. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dict `{ "paths": [list_of_paths] }` and write with `json.dump(..., indent=2)`. Collect the generated JSON filepaths into the respective output lists. |

### 7. Generate a human‑readable `split_ratio_description` string (e.g., "70% train / 15% validation / 15% test") and attach it to the node output.

| Category | Details |
| --- | --- |
| **Reason** | Provides downstream nodes with a concise summary for logging and reporting purposes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Hard‑code the description based on the ratios used; make it configurable via a constant at the top of the script. |

### 8. Run a post‑split verification: compute class distribution for each generated split and assert that the deviation from the original distribution is ≤ 2% per class; log any violations as warnings.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the stratification succeeded and that downstream evaluation will be fair. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Re‑load each JSON, map paths back to labels using the earlier manifest, compute histograms with `numpy.bincount`, compare percentages, and use `assert` or `logging.warning`. |

### 9. Return the five output fields (`material_names`, `train_split_json_paths`, `validation_split_json_paths`, `test_split_json_paths`, `split_ratio_description`) in the order defined by the node schema.

| Category | Details |
| --- | --- |
| **Reason** | Ensures strict compliance with the DAG contract and enables downstream nodes to consume the splits without additional parsing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assemble a dictionary matching the schema and `return` it from the node's execution function. |

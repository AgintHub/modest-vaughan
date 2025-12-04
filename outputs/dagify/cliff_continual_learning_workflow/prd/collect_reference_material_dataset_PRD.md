# collect_reference_material_dataset PRD

## Description
Gather a labeled optical‑microscopy dataset for the reference 2D material that will be used to pre‑train the backbone and base head.


## Implementation Plan

### 1. Define the reference material (e.g., graphene) and assign a concise dataset identifier such as "graphene_optical_dataset".

| Category | Details |
| --- | --- |
| **Reason** | A clear identifier ensures downstream nodes can reference the dataset unambiguously and avoids naming collisions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a constant string variable; embed the material name; store in the output field `dataset_name`. |

### 2. Compile a comprehensive list of publicly available and in‑house sources that contain high‑resolution optical‑microscopy images of the reference material.

| Category | Details |
| --- | --- |
| **Reason** | Using multiple sources maximizes dataset diversity, improves model generalisation, and satisfies reproducibility requirements. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Search repositories (e.g., Materials Cloud, NanoHUB, university data portals), query literature for supplementary datasets, and record URLs or lab inventory IDs in `source_list`. |

### 3. For each source, document the acquisition protocol: microscope type, objective magnification, illumination wavelength, exposure time, pixel resolution, and any preprocessing performed by the source.

| Category | Details |
| --- | --- |
| **Reason** | Explicit acquisition metadata enables reproducible reconstruction of raw image conditions and supports later quality‑control steps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a step‑by‑step bullet list per source and concatenate them into the `acquisition_steps` array; use a templated format: "[Source] – Set XYZ, capture 2048×2048 PNG at 100× magnification". |

### 4. Download or request the raw image files, preserving original filenames and metadata (EXIF, TIFF tags). Store them in a temporary staging directory organized by source.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining original structure prevents loss of provenance and facilitates checksum verification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a shell script (or Python `requests`/`gdown`) that iterates over `source_list`, saves files to `<staging_dir>/<source_name>/`, and logs MD5 hashes. |

### 5. Define the annotation schema required for each image: at minimum `layer_count` (integer), optional `flake_id` (string), and optional `defect_label` (enumerated). Record this schema in `annotation_requirements`.

| Category | Details |
| --- | --- |
| **Reason** | A standardized annotation format ensures consistency across sources and downstream training pipelines. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a JSON schema file and list its field names in the output list. |

### 6. Perform manual or semi‑automated annotation of each image according to the schema. Use tools such as LabelImg, CVAT, or custom Python scripts that overlay layer‑count tables from source papers.

| Category | Details |
| --- | --- |
| **Reason** | Accurate labeling is crucial for supervised pre‑training; semi‑automated methods speed up the process while preserving quality. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Assign a trained annotator, generate a CSV `annotations.csv` with columns `filename,layer_count,flake_id,defect_label`; store alongside images. |

### 7. Execute verification steps: (a) compute and record checksums for each image, (b) run a visual inspection checklist (focus, illumination uniformity, artefacts), (c) validate that every image has a matching annotation entry, (d) ensure `layer_count` values are within expected physical limits (1‑10 layers for graphene). Append each step description to `verification_steps`.

| Category | Details |
| --- | --- |
| **Reason** | Verification guarantees dataset integrity, prevents garbage‑in‑garbage‑out during model training, and satisfies reproducibility audits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a Python validation script that reads the staging directory, checks MD5 against recorded values, cross‑references the CSV, and logs any inconsistencies; failures raise exceptions. |

### 8. Select a storage format that is both efficient for large‑scale training and easy to stream: choose TFRecord for TensorFlow pipelines or HDF5 for PyTorch, and also keep a human‑readable CSV manifest.

| Category | Details |
| --- | --- |
| **Reason** | Optimised storage reduces I/O bottlenecks, enables sharding, and ensures compatibility with downstream training code. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write a conversion script that reads images and annotations, writes them into TFRecord files (one file per 1,000 samples) and concurrently writes a `manifest.csv`; set `storage_format` accordingly. |

### 9. Persist the finalized dataset to a permanent location: e.g., `gs://my‑project-data/datasets/graphene_optical_dataset/` or `/mnt/data/datasets/graphene_optical_dataset/`. Record the absolute URI in `dataset_path`.

| Category | Details |
| --- | --- |
| **Reason** | A fixed, versioned location enables downstream nodes to reliably locate the dataset without ambiguity. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Copy TFRecord shards and manifest CSV to the chosen bucket using `gsutil` or `rsync`; verify copy via checksum. |

### 10. Calculate `total_samples` by counting the number of image‑annotation pairs stored; set `is_ready_for_pretraining` to `true` only if all verification steps passed without errors.

| Category | Details |
| --- | --- |
| **Reason** | Providing explicit counts and a ready flag allows downstream training nodes to make conditional decisions (e.g., abort if dataset incomplete). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run `len(annotations.csv)`; set boolean based on exit status of verification script. |

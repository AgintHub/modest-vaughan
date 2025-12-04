# set_up_memory_replay_buffer PRD

## Description
Create a buffer that stores exemplar samples from previously learned materials for replay during continual training.


## Implementation Plan

### 1. Load the JSON split files produced by the `split_datasets` node (train_split_json_paths, validation_split_json_paths, test_split_json_paths) to retrieve the full list of image file paths and their associated class (layer count) labels for each material.

| Category | Details |
| --- | --- |
| **Reason** | The split files are the authoritative source of which images belong to which class; using them guarantees reproducibility and alignment with downstream training splits. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read each JSON with Python's `json.load`, iterate over entries to build a mapping `material -> {class_id -> [file_path, ...]}`. |

### 2. Define a global memory budget (e.g., 2,000 exemplars) and compute `exemplars_per_class` as `budget // (total_number_of_classes_across_all_materials)`. If the budget is insufficient for a uniform allocation, fall back to a minimum of 5 exemplars per class and adjust the budget accordingly.

| Category | Details |
| --- | --- |
| **Reason** | A fixed budget controls RAM/disk usage and ensures the replay buffer remains scalable as more materials are added. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Calculate `total_number_of_classes_across_all_materials` by counting unique layer IDs across all materials; use integer division; enforce a lower bound via `max(min_per_class, computed_value)`. |

### 3. Implement a stratified sampling strategy per class: for each `class_id` within each material, select `exemplars_per_class` images using the "herding" algorithm (choose samples whose feature embeddings are closest to the class centroid) if pre‑computed features exist, otherwise fall back to random uniform sampling with a fixed random seed for reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Herding preserves the distributional characteristics of each class better than pure random sampling, which improves knowledge‑distillation performance. |
| **Impact** | MEDIUM |
| **Complexity** | HIGH |
| **Method** | If feature vectors are stored in `features/<material>/<image_id>.npy`, load them, compute class centroid, rank images by Euclidean distance to centroid, pick top‑k; otherwise use `random.sample` with `np.random.seed(42)`. |

### 4. Create a dedicated buffer directory (`buffer_directory`) on the filesystem, e.g., `./replay_buffer/`. Within it, create sub‑folders for each material (`graphene/`, `MoS2/`, …) and further sub‑folders for each class ID (`class_0/`, `class_1/`, …). Copy or hard‑link the selected exemplar image files into the appropriate sub‑folder.

| Category | Details |
| --- | --- |
| **Reason** | A hierarchical directory layout mirrors the logical organization (material → class) and simplifies path‑based retrieval without requiring a database. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs` with `exist_ok=True`; copy with `shutil.copy2` or create hard links via `os.link` to avoid duplicating data. |

### 5. Populate the `exemplar_file_paths` list with the absolute (or project‑relative) paths of all copied exemplar files, preserving the order `material -> class_id -> file` for deterministic indexing.

| Category | Details |
| --- | --- |
| **Reason** | Downstream components (loss definition, training loops) need a flat list of paths to load images on‑the‑fly. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Walk the buffer directory with `os.walk`, filter by image extensions, sort paths lexicographically, and append to the list. |

### 6. Generate the `class_ids` list by enumerating all unique class identifiers present in the buffer (e.g., `[0,1,2,3]` for layer counts). Store them in ascending order to align with the ordering used in the loss function and prompt indexing.

| Category | Details |
| --- | --- |
| **Reason** | A canonical ordering prevents mismatches between class‑specific exemplars and model outputs during distillation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Collect class IDs while sampling; use `sorted(set(collected_ids))`. |

### 7. Compute `total_exemplars` as `len(exemplar_file_paths)` and verify that `total_exemplars == exemplars_per_class * len(class_ids) * number_of_materials`. Raise an exception if the equality does not hold.

| Category | Details |
| --- | --- |
| **Reason** | Integrity check catches bugs in the sampling or file‑copy stages early, avoiding silent downstream errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple arithmetic comparison; raise `ValueError` with a descriptive message if mismatched. |

### 8. Design a lightweight retrieval API called `get_replay_batch(class_ids: Optional[List[int]] = None, batch_size: int = 32, shuffle: bool = True) -> Tuple[torch.Tensor, List[int]]`. The function loads images from `exemplar_file_paths` (using Pillow or OpenCV), applies the same preprocessing pipeline as training data, returns a tensor batch and the corresponding class IDs.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulating the loading logic behind a well‑documented function keeps training loops clean and enables easy swapping of storage back‑ends later. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement the function in `replay_buffer.py`; use `torch.utils.data.Dataset` subclass for lazy loading; support optional filtering by `class_ids` and optional shuffling via `torch.utils.data.DataLoader`. |

### 9. Write a concise `retrieval_api_description` string summarizing the function signature, input arguments, return types, and any side‑effects (e.g., on‑the‑fly augmentation). Example: `"def get_replay_batch(class_ids: List[int] = None, batch_size: int = 32, shuffle: bool = True) -> (Tensor[batch, C, H, W], List[int])"`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (e.g., `define_knowledge_distillation_loss` and `incremental_train_material_specific_components`) need a human‑readable contract to invoke the buffer correctly. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a one‑line docstring and store it in the output field. |

### 10. Serialize a metadata JSON file (`metadata.json`) inside `buffer_directory` containing all output fields (`buffer_directory`, `exemplars_per_class`, `total_exemplars`, `class_ids`, `exemplar_file_paths`). This file serves as a checkpoint for reproducibility and debugging.

| Category | Details |
| --- | --- |
| **Reason** | Persisting metadata enables other pipeline stages to reload the buffer without recomputing it, saving time on repeated experiments. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `json.dump` with `indent=2`; ensure paths are stored relative to the project root for portability. |

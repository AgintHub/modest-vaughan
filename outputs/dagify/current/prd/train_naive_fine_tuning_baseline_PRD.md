# train_naive_fine_tuning_baseline PRD

## Description
Fine‑tune the entire backbone and head on each new material sequentially without any continual‑learning safeguards, to serve as a baseline.


## Implementation Plan

### 1. Instantiate the model architecture using the backbone_architecture, backbone_layers, base_head_architecture, base_head_input_dimension, and base_head_output_dimension values emitted by the design_backbone_and_base_head node; load any pre‑trained weights from the most recent checkpoint (or random init if first material).

| Category | Details |
| --- | --- |
| **Reason** | Ensures the training script builds exactly the same network topology that downstream nodes expect, preserving reproducibility across experiments. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the JSON output of design_backbone_and_base_head, map layer names to PyTorch (or TensorFlow) modules, construct the model class, and implement a helper `load_weights(path)` that restores state_dict if a checkpoint exists. |

### 2. Set all model parameters to `requires_grad=True` (unfreeze) before training each material, overriding any previous freezing that may have been applied during base pre‑training.

| Category | Details |
| --- | --- |
| **Reason** | The baseline deliberately fine‑tunes the entire network, so every weight must be learnable for each incremental step. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `model.parameters()` and set `.requires_grad = True`; verify with a diagnostic print of the number of trainable parameters. |

### 3. Read the split_datasets node output to obtain `material_names`, `train_split_json_paths`, and `validation_split_json_paths`. Ensure the ordering of these three lists is identical, establishing a deterministic material sequence.

| Category | Details |
| --- | --- |
| **Reason** | The script must know exactly which JSON file corresponds to which material to load the correct image file paths for training and validation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Load each JSON file (list of image file paths) using `json.load()`. Store in a dict `{material: {'train': [...], 'val': [...]}}` for fast lookup. |

### 4. Extract hyper‑parameters from configure_training_hyperparameters: use `base_optimizer`, `base_learning_rate`, `base_batch_size`, and `base_epochs` as the training schedule for the naive fine‑tuning baseline (these values are appropriate because no replay or prompt learning is involved).

| Category | Details |
| --- | --- |
| **Reason** | The baseline must share the same optimizer and learning‑rate regime as the base model to make a fair comparison; the incremental_* hyper‑parameters are specific to CL‑based methods and should not be used here. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a mapping `optimizer_cls = getattr(torch.optim, base_optimizer)`; instantiate `optimizer = optimizer_cls(model.parameters(), lr=base_learning_rate)`. |

### 5. For each material in `material_names` (loop order preserved from split_datasets):
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

### 6. Wrap the entire material‑wise training loop in a try/except block; on any exception set `training_success = False` and break, otherwise after the loop set `training_success = True`.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear boolean flag required by downstream evaluation nodes and guarantees graceful failure handling. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python's `try: ... except Exception as e: logging.error(e); training_success = False` pattern. |

### 7. After all materials have been processed, verify that the lengths of `trained_checkpoints`, `materials_fine_tuned`, and `epochs_per_material` are identical and match the number of materials; raise an assertion error if mismatched.

| Category | Details |
| --- | --- |
| **Reason** | Ensures output consistency with the schema and prevents downstream nodes from encountering shape mismatches. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `assert len(trained_checkpoints) == len(materials_fine_tuned) == len(epochs_per_material) == len(material_names)`. |

### 8. Log a summary JSON file (`baseline_fine_tuning_summary.json`) containing all output fields for provenance, and optionally upload the file to the experiment tracking system (e.g., MLflow, Weights & Biases).

| Category | Details |
| --- | --- |
| **Reason** | Facilitates reproducibility, auditability, and easy consumption by `compute_accuracy_and_forgetting_metrics` which expects the checkpoint list and material order. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Create a dictionary with keys matching the output_structure, `json.dump` it with indent=2, and store under `outputs/` directory. |

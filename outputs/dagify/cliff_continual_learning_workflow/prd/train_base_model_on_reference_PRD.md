# train_base_model_on_reference PRD

## Description
Train the backbone and base head on the reference material dataset, then freeze them.


## Implementation Plan

### 1. Parse the split_datasets output to locate the JSON file that lists file‑paths for the reference material's training split (identified by the material name matching the ‘material’ field of the reference dataset).

| Category | Details |
| --- | --- |
| **Reason** | Accurate loading of the correct training data is fundamental; the split JSON guarantees class‑balanced, reproducible splits. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `train_split_json_paths` list; match the index of the reference material name in `material_names`; load the JSON array of image paths using Python's `json` module. |

### 2. Similarly parse split_datasets to obtain the reference material's validation split JSON for monitoring validation accuracy each epoch.

| Category | Details |
| --- | --- |
| **Reason** | Validation data is required to decide early‑stopping or to record the final validation metric. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the same index as above on `validation_split_json_paths`; load file paths into a validation dataset object. |

### 3. Extract the backbone and base‑head architectural specifications from design_backbone_and_base_head (e.g., `backbone_architecture`, `backbone_layers`, `base_head_architecture`, `base_head_input_dimension`, `base_head_output_dimension`, `initialization_strategy`).

| Category | Details |
| --- | --- |
| **Reason** | The model must be instantiated exactly as designed to ensure downstream components (prompt pool, delta head) align with dimensions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map `backbone_architecture` to a PyTorch model class (e.g., torchvision.models.resnet50); rebuild the head as a `nn.Linear(base_head_input_dimension, base_head_output_dimension)`; apply the specified `initialization_strategy` (Xavier for linear layers, Kaiming for conv layers) via custom weight‑initialization functions. |

### 4. Create a PyTorch `Dataset` class that reads image files from the training split, applies the same preprocessing pipeline used in `preprocess_images` (resize, normalize with the stored `normalization_mean` and `normalization_std`), and returns (image_tensor, label).

| Category | Details |
| --- | --- |
| **Reason** | Ensuring preprocessing consistency between pre‑training and later stages prevents distribution shift. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Subclass `torch.utils.data.Dataset`; inside `__getitem__` load image via PIL, resize to target dimensions (from `preprocess_images` output), convert to tensor, normalize, and fetch label from accompanying metadata CSV. |

### 5. Instantiate DataLoaders for training and validation using the batch size `base_batch_size` from configure_training_hyperparameters, with `shuffle=True` for training and `shuffle=False` for validation.

| Category | Details |
| --- | --- |
| **Reason** | Efficient batching and shuffling are required for stable gradient updates and reproducible validation scores. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `torch.utils.data.DataLoader(train_dataset, batch_size=base_batch_size, shuffle=True, num_workers=4)`; similarly for validation with `shuffle=False`. |

### 6. Configure the optimizer as `base_optimizer` (e.g., AdamW) with learning rate `base_learning_rate`; optionally add weight decay as per best practices for CNN pre‑training.

| Category | Details |
| --- | --- |
| **Reason** | Hyper‑parameter alignment guarantees that the base model is trained under the same regime expected by downstream incremental training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `optimizer = torch.optim.AdamW(model.parameters(), lr=base_learning_rate, weight_decay=1e-4)` if `base_optimizer` == "AdamW"; otherwise map string to appropriate torch optimizer class. |

### 7. Implement the training loop for exactly `base_epochs` iterations: for each epoch, iterate over the training DataLoader, forward‑pass through backbone → base head, compute cross‑entropy loss, back‑propagate, and step the optimizer.

| Category | Details |
| --- | --- |
| **Reason** | The core learning process; must be deterministic and record metrics for reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Pseudo‑code: `for epoch in range(base_epochs): model.train(); for imgs, lbls in train_loader: optimizer.zero_grad(); logits = model(imgs); loss = criterion(logits, lbls); loss.backward(); optimizer.step();` |

### 8. After each epoch, evaluate the model on the validation DataLoader, compute top‑1 accuracy, and log `epoch`, `train_loss`, `val_accuracy` to a JSON or CSV logger for later inspection.

| Category | Details |
| --- | --- |
| **Reason** | Monitoring validation accuracy enables reporting `base_model_validation_accuracy` and early detection of divergence. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Set `model.eval()`, disable grad, compute predictions, compare with labels, accumulate correct/total counts; store `val_accuracy` in a dict keyed by epoch. |

### 9. Upon completion of all epochs, record the final validation accuracy (the accuracy from the last epoch) as `base_model_validation_accuracy`.

| Category | Details |
| --- | --- |
| **Reason** | This scalar is part of the node's required output and serves as a baseline metric for later continual‑learning phases. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Extract the last entry from the validation logger; assign to output variable. |

### 10. Save the entire model state dict to a deterministic file path, e.g., `models/base_model_epoch{base_epochs}.pth`; assign this path to `base_model_weights_path`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (freeze_backbone_and_base_head, incremental training) need to load the exact trained weights. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `torch.save(model.state_dict(), base_model_weights_path)`; ensure the directory exists. |

### 11. Freeze the backbone and base head by iterating over `model.backbone.parameters()` and `model.base_head.parameters()` and setting `param.requires_grad = False`.

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

### 12. Verify freezing by checking that `any(p.requires_grad for p in model.backbone.parameters())` and similarly for the base head returns `False`; set `backbone_frozen_status` and `base_head_frozen_status` accordingly.

| Category | Details |
| --- | --- |
| **Reason** | A verification step ensures correctness before downstream nodes consume the frozen model. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `backbone_frozen_status = not any(p.requires_grad for p in model.backbone.parameters())` and similarly for `base_head_frozen_status`. |

### 13. Populate the final output dictionary with all required fields (`base_model_weights_path`, `base_model_training_epochs`, `base_model_validation_accuracy`, `backbone_frozen_status`, `base_head_frozen_status`) and return it from the node execution function.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract; enables downstream nodes to consume structured outputs. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dict matching `output_structure` and serialize to JSON if the workflow engine expects file‑based outputs. |

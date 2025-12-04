# train_prompt_based_baseline PRD

## Description
Train only material prompts (no delta head, no replay) on each new material to serve as a prompt‑only baseline.


## Implementation Plan

### 1. Load hyper‑parameter configuration from the output of `configure_training_hyperparameters` (base_optimizer, incremental_prompt_learning_rate, incremental_batch_size, incremental_epochs).

| Category | Details |
| --- | --- |
| **Reason** | Centralising hyper‑parameters ensures consistency across all training scripts and makes future tuning straightforward. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read a JSON/YAML file produced by the parent node; map fields to local variables; assert required keys exist. |

### 2. Instantiate the frozen backbone and base head using the architecture specifications from `design_backbone_and_base_head`; load pre‑trained weights if available.

| Category | Details |
| --- | --- |
| **Reason** | The backbone must remain frozen during prompt‑only training; using the same architecture guarantees compatibility with the prompt pool. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create PyTorch model objects (e.g., torchvision.models.resnet50); call `model.load_state_dict(torch.load(path))`; set `requires_grad=False` for all parameters of backbone and base head. |

### 3. Create the prompt pool according to `implement_prompt_pool_structure` output (prompt_pool_variable_name, prompt_dimension, number_of_materials, material_ids, initialization_method).

| Category | Details |
| --- | --- |
| **Reason** | A deterministic prompt pool allows each material to have its own learnable vector that will be updated independently. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Initialize a `nn.Parameter` tensor of shape `(number_of_materials, prompt_dimension)` using the specified method (e.g., torch.randn * 0.02); store in a `nn.Module` named as per `prompt_pool_variable_name`. |

### 4. Freeze all parameters except the prompt pool: verify that only the prompt parameters have `requires_grad=True`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that no accidental gradient updates affect the backbone or base head, matching the baseline specification. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over `model.parameters()` and assert `requires_grad` is False; iterate over prompt pool parameters and assert True; raise error if mismatch. |

### 5. For each material listed in the `split_datasets` output, load its training and validation JSON split files, build `torch.utils.data.Dataset` objects that return (image_tensor, label) pairs, and wrap them in `DataLoader`s using `incremental_batch_size`.

| Category | Details |
| --- | --- |
| **Reason** | Material‑specific DataLoaders provide the correct data stream for isolated prompt training while keeping the code reusable. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a custom `FlakeDataset` that reads image paths from the JSON, applies the same preprocessing pipeline used for the base model, and returns tensors; create `DataLoader(train_dataset, batch_size, shuffle=True)` and `DataLoader(val_dataset, batch_size, shuffle=False)`. |

### 6. Create an optimizer (e.g., AdamW) that only receives the prompt pool parameters and uses `incremental_prompt_learning_rate` as learning rate.

| Category | Details |
| --- | --- |
| **Reason** | Separate optimizer prevents accidental updates to frozen components and respects the learning‑rate schedule defined for prompts. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | optimizer = torch.optim.AdamW(prompt_pool.parameters(), lr=incremental_prompt_learning_rate, weight_decay=0.01). |

### 7. Implement the training loop: for `epoch` in range(`incremental_epochs`): iterate over the material's training DataLoader, for each batch retrieve the prompt vector corresponding to the current material ID, prepend/concatenate it to the backbone feature map as defined by `integration_method`, forward through the frozen backbone and base head, compute cross‑entropy loss against labels, back‑propagate (`loss.backward()`), and call `optimizer.step()` followed by `optimizer.zero_grad()`.

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

### 8. After each epoch, evaluate on the material's validation DataLoader using the same forward path (no gradient), compute top‑1 accuracy, and store the best‑validation‑accuracy checkpoint of the prompt vectors.

| Category | Details |
| --- | --- |
| **Reason** | Validation monitoring is essential to detect over‑fitting and to select the final prompt vector for each material. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Set `model.eval()`, disable gradient with `torch.no_grad()`, compute predictions, compare with labels, calculate accuracy; if current accuracy > best, save `prompt_pool[material_index].cpu().detach()` to a file path like `prompts/{material_id}_prompt.pt`. |

### 9. After finishing all epochs for a material, append the saved prompt file path to `prompt_vectors_trained` and the best validation accuracy to `validation_accuracy_per_material`.

| Category | Details |
| --- | --- |
| **Reason** | Aggregating these values fulfills the required output schema and provides downstream nodes with ready‑to‑load prompt vectors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain Python lists; after each material loop, `prompt_vectors_trained.append(prompt_path)` and `validation_accuracy_per_material.append(best_acc)`. |

### 10. Repeat the material‑wise training loop for every material listed in the split‑datasets output, keeping the same optimizer (which will continue updating the prompt pool for new indices) and resetting epoch counters per material.

| Category | Details |
| --- | --- |
| **Reason** | Sequential training mirrors the continual‑learning order while still adhering to the baseline constraint of no replay or delta head. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop over `material_ids`; for each, call the per‑material training routine; ensure the optimizer’s state is not cleared between materials so learning rate schedule remains consistent. |

### 11. Set `prompt_training_status` to `True` if all material loops complete without exception; otherwise catch exceptions, log error details, and set the flag to `False`.

| Category | Details |
| --- | --- |
| **Reason** | A binary status flag provides a clear success/failure signal for downstream evaluation nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Wrap the outermost material loop in a try/except block; on success, `prompt_training_status = True`; on failure, `prompt_training_status = False` and write the exception to a log file. |

### 12. Assign `training_epochs_completed` the value of `incremental_epochs` (or the actual number of epochs run if early stopping was implemented).

| Category | Details |
| --- | --- |
| **Reason** | Outputs the exact training budget used, which is needed for reproducibility and for the `compute_accuracy_and_forgetting_metrics` node. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | If early stopping is added, store the epoch index at which training stopped; otherwise copy `incremental_epochs`. |

### 13. Serialize the final JSON output containing all four fields (`prompt_training_status`, `prompt_vectors_trained`, `validation_accuracy_per_material`, `training_epochs_completed`) to the path expected by downstream nodes (e.g., `artifacts/prompt_baseline_output.json`).

| Category | Details |
| --- | --- |
| **Reason** | Standardised artifact storage enables downstream nodes to read the outputs without custom parsing logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python `json.dump` with `indent=2`; ensure the file path is communicated via a known environment variable or a config entry. |

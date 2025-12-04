# define_knowledge_distillation_loss PRD

## Description
Formulate a loss that distills knowledge from the frozen base model into the evolving CLIFF model using replay samples.


## Implementation Plan

### 1. Load replay buffer metadata from the parent node `set_up_memory_replay_buffer` (buffer_directory, exemplar_file_paths, class_ids) and deserialize the stored base logits for each exemplar into a tensor `Z_base` of shape [N_replay, C] where C is the number of classes.

| Category | Details |
| --- | --- |
| **Reason** | The distillation term requires the frozen base model's logits for the exact replay samples; loading them once at the start avoids repeated forward passes through the frozen model. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a lightweight JSON/YAML parser to read a manifest file located in `buffer_directory` that maps each exemplar path to its stored logits; then stack logits into a PyTorch tensor on the same device as the training model. |

### 2. Define the classification loss function `L_{cls}` as standard categorical cross‑entropy (CE) between the current model logits `Z_curr` for the *new* material batch and the one‑hot ground‑truth labels `y`.

| Category | Details |
| --- | --- |
| **Reason** | Cross‑entropy is the de‑facto loss for multi‑class classification and aligns with the evaluation metric (top‑1 accuracy). |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement `torch.nn.CrossEntropyLoss(reduction='mean')` and expose its string name as `classification_loss_type = "cross_entropy"`. |

### 3. Define the distillation loss function `L_{kd}` as the Kullback‑Leibler divergence between the current model logits `Z_curr^{replay}` (softmax temperature‑scaled) and the stored base logits `Z_base` (also temperature‑scaled). Use PyTorch's `KLDivLoss` with `log_target=False` and `reduction='batchmean'`.

| Category | Details |
| --- | --- |
| **Reason** | KL‑divergence measures how well the student (current CLIFF model) mimics the teacher (frozen base) on replayed exemplars, encouraging retention of previously learned knowledge. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply temperature `T` (commonly T=2) to both logits: `p = softmax(Z_curr^{replay} / T)`, `q = softmax(Z_base / T)`. Compute `L_{kd} = KLDivLoss(log(p), q) * (T^2)` to correct gradient scaling. |

### 4. Introduce a weighting hyper‑parameter `λ_{kd}` (named `distillation_weight`) to balance the two objectives: `L = L_{cls} + λ_{kd} * L_{kd}`.

| Category | Details |
| --- | --- |
| **Reason** | A scalar weight lets practitioners tune the trade‑off between learning new material and preserving old knowledge; typical values lie in [0.1, 1.0]. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set `weighting_hyperparameter_name = "distillation_weight"` and propose a default `weighting_hyperparameter_value = 0.5`. Document that this value can be overridden via the training‑hyperparameter config. |

### 5. Compose the final loss expression string `loss_expression` in LaTeX‑compatible notation, e.g.:

```
L = \underbrace{\text{CE}(Z_{curr}^{new}, y)}_{\text{classification}} + \lambda_{kd}\,\underbrace{\text{KL}\big(\text{softmax}(Z_{curr}^{replay}/T) \| \text{softmax}(Z_{base}/T)\big)}_{\text{distillation}}
```

| Category | Details |
| --- | --- |
| **Reason** | Providing a clear mathematical formula is required by downstream documentation and ensures reproducibility across implementations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | String‑format the expression using the variable names defined above; embed LaTeX delimiters for readability. |

### 6. Validate shape compatibility: assert that `Z_curr^{replay}` and `Z_base` share the same class dimension `C`, and that the batch size of replay samples matches the number of stored logits.

| Category | Details |
| --- | --- |
| **Reason** | Mismatched dimensions would cause runtime errors during loss computation and break the training loop. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Insert a runtime check `assert Z_curr_replay.shape == Z_base.shape` with an informative error message. |

### 7. Export the five required output fields (`loss_expression`, `classification_loss_type`, `distillation_loss_type`, `weighting_hyperparameter_name`, `weighting_hyperparameter_value`) as plain strings/floats according to the node's output schema.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (`incremental_train_material_specific_components`) consume these fields to construct the actual training step; strict type adherence avoids serialization issues. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Populate a Python dict with the keys and cast values to `str` or `float` as required; serialize to JSON if needed. |

# freeze_backbone_and_base_head PRD

## Description
Mark backbone and base head parameters as non‑trainable for subsequent continual learning phases.


## Implementation Plan

### 1. Load the checkpoint produced by `train_base_model_on_reference` (field `base_model_weights_path`) into the same model class used for design_backbone_and_base_head.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we are freezing the exact parameter tensors that were trained on the reference dataset. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.load(path, map_location='cpu')` (or equivalent for TensorFlow/Keras) to obtain `state_dict`; instantiate the model architecture (backbone + base_head) and call `model.load_state_dict(state_dict, strict=True)`. |

### 2. Iterate over all parameters belonging to the backbone module (e.g., `model.backbone.parameters()`) and set `param.requires_grad = False` for each.

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

### 3. Iterate over all parameters of the base classification head (e.g., `model.base_head.parameters()`) and set `param.requires_grad = False` similarly, appending their names to the frozen list.

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

### 4. Collect the names of all parameters that remain trainable after the above steps. These should correspond to the prompt pool (e.g., `model.material_prompts`) and the delta head (e.g., `model.delta_head`).

| Category | Details |
| --- | --- |
| **Reason** | Provides the `trainable_parameters` output and is required for verification that only intended modules are still updating. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
trainable_names = [name for name, p in model.named_parameters() if p.requires_grad]
``` |

### 5. Perform a verification pass: assert that every name in `frozen_names` has `requires_grad == False` and every name in `trainable_names` belongs to either the prompt pool or delta head.

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

### 6. Serialize the results into the defined output structure: set `operation_status` to "success" if `verification_passed` is True, otherwise include an error description; output `frozen_parameters` = frozen_names, `trainable_parameters` = trainable_names, and `verification_passed` flag.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic, schema‑compliant response for downstream nodes (e.g., incremental_train_material_specific_components). |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dict matching the output schema and return/print it; in a production pipeline, wrap in a JSON encoder. |

### 7. Save the now‑frozen model weights back to disk (optional but recommended) so that future stages can reload without recomputing the freeze step.

| Category | Details |
| --- | --- |
| **Reason** | Ensures reproducibility and reduces the risk of re‑freezing inconsistently if the pipeline is rerun. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
torch.save(model.state_dict(), path_to_frozen_weights)
``` (or `model.save_weights` for TF/Keras). |

### 8. Add comprehensive logging: log the count of frozen parameters, count of trainable parameters, and any mismatches detected during verification.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and audit trails for experiments involving many materials and incremental steps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use the `logging` module with `INFO` level messages; e.g., `logging.info(f"Frozen {len(frozen_names)} params; trainable {len(trainable_names)} params")`. |

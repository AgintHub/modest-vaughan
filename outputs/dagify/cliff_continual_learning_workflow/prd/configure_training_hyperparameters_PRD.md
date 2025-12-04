# configure_training_hyperparameters PRD

## Description
Set learning rates, batch sizes, optimizer types, and schedule for both base pre‑training and incremental material training.


## Implementation Plan

### 1. Extract dimensionality and parameter count from `design_backbone_and_base_head` (backbone_layers, base_head_input_dimension, base_head_output_dimension) to guide optimizer and learning‑rate scaling decisions.

| Category | Details |
| --- | --- |
| **Reason** | Backbone size directly affects stable training regimes; larger models typically need smaller LR to avoid divergence. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the JSON output of the parent node, compute total parameter count, and apply a rule‑based scaling: base_lr = 1e‑4 * (100M / total_params). |

### 2. Select AdamW as `base_optimizer` because it decouples weight decay from the gradient update, which is beneficial for transformer‑style prompt vectors and ResNet backbones.

| Category | Details |
| --- | --- |
| **Reason** | AdamW provides robust convergence on mixed‑precision training and is widely used in CL literature. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Hard‑code optimizer name "AdamW" and expose weight_decay (e.g., 0.01) as a constant that can be overridden via config. |

### 3. Set `base_learning_rate` to 1e‑4, `base_batch_size` to 64, and `base_epochs` to 30 based on empirical studies for ResNet‑50 on optical‑microscopy datasets.

| Category | Details |
| --- | --- |
| **Reason** | These values balance convergence speed and generalization; batch size 64 fits typical GPU memory for 224×224 images. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign static values; annotate that they can be tuned via a hyper‑parameter sweep if GPU resources allow. |

### 4. Derive incremental learning rates (`incremental_prompt_learning_rate` and `incremental_delta_learning_rate`) from the base LR using a decay factor of 0.5 for prompts and 0.3 for delta head (e.g., 5e‑5 and 3e‑5 respectively).

| Category | Details |
| --- | --- |
| **Reason** | Prompts are lightweight and benefit from a slightly higher LR than the delta head, which is deeper and more prone to over‑fitting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute: incremental_prompt_lr = base_lr * 0.5; incremental_delta_lr = base_lr * 0.3; round to 5e‑5 and 3e‑5. |

### 5. Choose `incremental_batch_size` = 32 and `incremental_epochs` = 15 for each new material, reflecting the smaller data volume per material and the need for faster convergence during continual learning.

| Category | Details |
| --- | --- |
| **Reason** | Smaller batches reduce memory pressure when mixing replay samples; fewer epochs avoid catastrophic forgetting while still allowing prompt/delta adaptation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set constants; document that batch size can be scaled with GPU memory availability. |

### 6. Define `replay_ratio` as "1:3" (one replay sample per three new material samples) to maintain a balanced proportion of historic knowledge while focusing on new data.

| Category | Details |
| --- | --- |
| **Reason** | Empirical CL studies show a 1:3 ratio mitigates forgetting without overwhelming the optimizer with old data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Hard‑code string "1:3"; expose as a tunable parameter in the configuration file. |

### 7. Compose a concise `rationale` field that succinctly explains each hyper‑parameter choice, linking back to model size, dataset characteristics, and continual‑learning theory.

| Category | Details |
| --- | --- |
| **Reason** | Providing rationale improves reproducibility and aids future hyper‑parameter tuning. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template‑based string generation: concatenate explanations from previous bullets into a single paragraph. |

### 8. Validate that all output fields conform to the declared PrimitiveTypes and serialize them into a JSON object for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect strict type adherence; early validation prevents runtime errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a schema validator (e.g., using jsonschema) that checks type and presence of each key before returning the final output. |

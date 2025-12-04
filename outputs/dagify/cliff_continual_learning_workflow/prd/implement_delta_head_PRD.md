# implement_delta_head PRD

## Description
Define a lightweight residual head that learns material‑specific corrections on top of the frozen base head.


## Implementation Plan

### 1. Extract the dimensionality of the frozen backbone's final feature vector from the parent node `design_backbone_and_base_head` (use `base_head_input_dimension` if the base head directly consumes the backbone output, otherwise compute from the last convolutional block, e.g., 2048 for ResNet‑50).

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the delta head receives exactly the same sized gated features that the base head expects, preventing shape mismatches during forward passes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the JSON output of `design_backbone_and_base_head`; if `base_head_input_dimension` is present, assign it to `delta_head_input_size`. Otherwise, map the known backbone architecture (e.g., ResNet‑50) to its standard output dimension. |

### 2. Set `delta_head_output_size` equal to `base_head_output_dimension` obtained from `design_backbone_and_base_head`.

| Category | Details |
| --- | --- |
| **Reason** | The delta head must output a correction vector that can be added element‑wise to the base head logits; matching dimensions are mandatory. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read `base_head_output_dimension` from the parent node and assign it directly to `delta_head_output_size`. |

### 3. Define the delta head as a two‑layer MLP (the simplest yet expressive residual head). Choose a hidden dimension `H` (e.g., 256) that is small relative to the input size to keep the head lightweight.

| Category | Details |
| --- | --- |
| **Reason** | A shallow MLP provides enough capacity to learn material‑specific bias/correction while keeping parameter count low, preserving the continual‑learning efficiency. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dictionary: `delta_head_layer_sizes = [delta_head_input_size, H, delta_head_output_size]`. Store `H` as a configurable hyper‑parameter in `configure_training_hyperparameters`. |

### 4. Select activation functions: use ReLU after the first linear layer and a linear (identity) activation after the second layer so that the output can be added directly to the base logits.

| Category | Details |
| --- | --- |
| **Reason** | ReLU introduces non‑linearity for expressive corrections; a linear output prevents unwanted scaling of logits. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set `delta_head_activation_functions = ["ReLU", "Linear"]`. |

### 5. Specify the full architecture string for `delta_head_architecture` – e.g., "Two‑layer MLP with hidden size 256, ReLU activation after first layer, linear output".

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable summary for documentation and downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Concatenate the chosen hyper‑parameters into a formatted description. |

### 6. Initialize the first linear layer with Kaiming‑He (He) initialization (mode=‘fan_in’, nonlinearity=‘relu’) and the second linear layer with zeros (so initial correction is zero).

| Category | Details |
| --- | --- |
| **Reason** | Kaiming init stabilizes training for ReLU layers; zero init for the final layer guarantees that at the start of incremental training the delta head does not alter the base logits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | In PyTorch: `nn.init.kaiming_normal_(layer1.weight, nonlinearity='relu')`; `nn.init.zeros_(layer2.weight)`; bias terms can be zero‑initialized. |

### 7. Implement the delta head as a reusable module (e.g., `class DeltaHead(nn.Module)`) exposing a `forward(gated_features)` method that returns the correction logits.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulation simplifies integration with the larger CLIFF model and allows easy swapping of hidden dimension `H` later. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write a small class inheriting from `torch.nn.Module`, construct `nn.Sequential` with the two linear layers and activation, and store layer sizes as class attributes for later introspection. |

### 8. Document how the delta head is combined with the frozen base head during inference: `final_logits = base_logits + delta_head(gated_features)`.

| Category | Details |
| --- | --- |
| **Reason** | Clarifies the residual nature of the head for downstream developers and for the `incremental_train_material_specific_components` node which expects a residual correction. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Add a comment block in the module and include the equation in the `delta_head_architecture` description. |

### 9. Create a unit‑test script that feeds a dummy tensor of shape `(batch, delta_head_input_size)` through the delta head and asserts that the output shape equals `(batch, delta_head_output_size)` and that the initial output is all zeros (due to zero initialization of the second layer).

| Category | Details |
| --- | --- |
| **Reason** | Automated sanity check prevents shape bugs early and guarantees the zero‑correction property before training begins. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `torch.randn(4, delta_head_input_size)` as input, run the forward pass, and compare `output.detach().abs().max()` to a small epsilon. |

### 10. Expose the delta head configuration (layer sizes, activation list, hidden dimension) as entries in the output JSON fields `delta_head_layer_sizes` and `delta_head_activation_functions` so that downstream nodes (e.g., `configure_training_hyperparameters`) can reference them programmatically.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates downstream automation, logging, and reproducibility of experiments. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Populate the output fields directly from the variables defined in earlier bullets. |

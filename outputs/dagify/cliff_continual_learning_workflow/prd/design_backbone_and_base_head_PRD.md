# design_backbone_and_base_head PRD

## Description
Specify the CNN backbone architecture and the classification head that will be initially trained on the reference material.


## Implementation Plan

### 1. Extract high‑level constraints from the parent node `define_project_scope` (e.g., frozen backbone, target accuracy) to bound the design space for the backbone and head.

| Category | Details |
| --- | --- |
| **Reason** | Using the explicit constraints guarantees that the chosen architecture aligns with the project’s primary objective and evaluation metrics. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `high_level_constraints` list from the parent output, parse entries such as "frozen backbone" and "limited parameter budget", and store them in a local configuration object. |

### 2. Select ResNet‑50 as the backbone because it offers a good trade‑off between representational power and computational cost, and its architecture is well‑studied for transfer learning in microscopy domains.

| Category | Details |
| --- | --- |
| **Reason** | ResNet‑50 provides pretrained weights on ImageNet, which can be fine‑tuned or frozen as required, and its block structure simplifies layer‑wise inspection. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Set `backbone_architecture` = "ResNet-50". Enumerate each stage (conv1, bn1, relu, maxpool, layer1‑layer4, avgpool, flatten) with output channel dimensions (e.g., conv1: 7×7×64, layer1: 256, …) and store as strings in `backbone_layers`. |

### 3. Determine the dimensionality of the backbone’s final feature vector (2048 for ResNet‑50 after global average pooling) and define the base head as a single fully‑connected layer mapping to the number of flake‑layer classes.

| Category | Details |
| --- | --- |
| **Reason** | A simple linear head is sufficient for the initial reference‑material pre‑training and keeps the parameter count low, respecting the frozen‑backbone constraint. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `base_head_architecture` = "Fully‑Connected (Linear) layer". Set `base_head_input_dimension` = 2048. Compute `base_head_output_dimension` by counting unique `layer_count` labels in the reference dataset (e.g., 5 classes) and assign the integer. |

### 4. Specify the weight‑initialization strategy: use Kaiming He normal initialization for all convolutional layers in ResNet‑50 and Xavier uniform initialization for the fully‑connected head.

| Category | Details |
| --- | --- |
| **Reason** | Kaiming initialization is optimal for ReLU‑based convolutional nets, while Xavier works well for linear layers, ensuring stable gradient flow at the start of pre‑training. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a string `initialization_strategy` = "Kaiming He for conv layers, Xavier uniform for FC head". Document the exact PyTorch calls (torch.nn.init.kaiming_normal_ and torch.nn.init.xavier_uniform_). |

### 5. Run a sanity‑check forward pass using a dummy tensor of shape (1, 3, 224, 224) through the backbone and base head to verify dimensional consistency and that the output shape matches `base_head_output_dimension`.

| Category | Details |
| --- | --- |
| **Reason** | Early shape validation prevents runtime errors during the subsequent pre‑training phase. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Instantiate the selected backbone (torchvision.models.resnet50(pretrained=False)), replace the final fully‑connected layer with the defined head, feed a torch.randn tensor, and assert output.shape == (1, base_head_output_dimension). Log any mismatches. |

### 6. Serialize all six output fields into the required JSON structure so downstream nodes can consume them without further transformation.

| Category | Details |
| --- | --- |
| **Reason** | Consistent, typed output is essential for the typed DAG execution engine. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching `output_structure`, convert to JSON, and ensure types match PrimitiveType definitions (e.g., list of strings for `backbone_layers`). |

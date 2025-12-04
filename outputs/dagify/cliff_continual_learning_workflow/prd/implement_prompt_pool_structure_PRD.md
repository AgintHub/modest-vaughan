# implement_prompt_pool_structure PRD

## Description
Create the data structure and embedding logic for a pool of learnable material‑specific prompts.


## Implementation Plan

### 1. Define a dedicated PyTorch nn.Module named `MaterialPromptPool` that internally registers a Parameter tensor of shape `(N, D)` where `N = number_of_materials` and `D = prompt_dimension`.

| Category | Details |
| --- | --- |
| **Reason** | Encapsulating the prompt pool in a module ensures seamless integration with the autograd engine and provides a clean API for indexing by material ID. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.nn.Parameter(torch.empty(N, D))` and initialize it in `__init__` via `torch.nn.init.normal_(self.prompts, mean=0.0, std=0.02)` (or the chosen `initialization_method`). |

### 2. Create a Python dictionary `material_id_to_index` mapping each string identifier in `material_ids` to its integer position in the prompt matrix.

| Category | Details |
| --- | --- |
| **Reason** | Fast lookup (O(1)) is required during training/inference to fetch the correct prompt vector for a given sample's material label. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `self.id2idx = {mid: idx for idx, mid in enumerate(material_ids)}` stored as a member of the module. |

### 3. Implement a method `get_prompt(material_id: str) -> torch.Tensor` that returns the prompt vector `self.prompts[self.id2idx[material_id]]` and adds a batch dimension if needed.

| Category | Details |
| --- | --- |
| **Reason** | Abstracts the indexing logic away from downstream code, allowing batch‑wise retrieval by passing a list of material IDs and using `torch.index_select`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If a list of IDs is provided, convert them to indices via list comprehension, then `torch.index_select(self.prompts, 0, torch.tensor(indices, device=self.prompts.device))`. |

### 4. Choose an integration strategy: prepend the prompt vector to the token sequence produced by the backbone's patch embedding (ViT‑style) or concatenate it to the global feature map (CNN‑style). Store this choice in `integration_method`.

| Category | Details |
| --- | --- |
| **Reason** | The integration method determines how the prompt influences downstream layers; prepending aligns with transformer prompt‑tuning literature, while concatenation works for classic CNNs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For a ResNet‑based backbone, after the final spatial pooling produce a feature vector `f`. Compute `f_aug = torch.cat([prompt, f], dim=-1)` where `prompt` is broadcasted across the batch. For a ViT, insert `prompt` as additional tokens before the class token. |

### 5. Set `requires_grad=True` for the prompt Parameter and ensure all other backbone and base‑head parameters have `requires_grad=False` (handled later by `freeze_backbone_and_base_head`).

| Category | Details |
| --- | --- |
| **Reason** | Only the prompt vectors should be learnable during incremental phases; this flag guarantees gradients flow correctly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | When creating the Parameter, pass `requires_grad=True`. Verify via `assert self.prompts.requires_grad`. |

### 6. Expose the module in the model's forward pass: modify the main `CLIFFModel` forward method to accept an extra argument `material_id` and retrieve the prompt via `prompt = self.prompt_pool.get_prompt(material_id)` before merging with backbone output.

| Category | Details |
| --- | --- |
| **Reason** | The forward signature must allow the training loop to supply the correct material label for each batch. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Add `def forward(self, x, material_id):` → `prompt = self.prompt_pool.get_prompt(material_id)` → integrate as per chosen `integration_method`. |

### 7. Provide an `example_code_snippet` string illustrating instantiation and a single forward call, e.g.,
```python
prompt_pool = MaterialPromptPool(
    num_materials=3,
    prompt_dim=128,
    material_ids=["graphene", "MoS2", "WS2"],
    init_method="normal_std_0.02"
)
model = CLIFFModel(backbone=resnet50, base_head=fc, prompt_pool=prompt_pool)
logits = model(images, material_id="MoS2")
```

| Category | Details |
| --- | --- |
| **Reason** | Concrete code helps downstream developers quickly copy‑paste and adapt the implementation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Compose the snippet as a raw string and assign to the `example_code_snippet` output field. |

<div align="center">

<h1>ModelMirage Catalog</h1>
<hr>

**Item model catalog for ModelMirage: JSON index, schema, validator and sample model**

![Minecraft](https://img.shields.io/badge/MINECRAFT-26.2-62B47A?style=flat-square&logo=minecraft&logoColor=white)
![Python](https://img.shields.io/badge/PYTHON-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/hhhhhffd/ModelMirage-catolog/validate.yml?style=flat-square&label=VALIDATE)
![License](https://img.shields.io/github/license/hhhhhffd/ModelMirage-catolog?style=flat-square)

[Format](#catalog-format) · [Add a model](#adding-a-model) · [License](#license)

</div>

> [!NOTE]
> Archived — no longer maintained.

## What it is

The data repository behind the [ModelMirage](https://github.com/hhhhhffd/ModelMirage) client mod (Fabric, Minecraft 26.2). The mod downloads `index.json` from this repository and lets the player put any listed model on any item. The repository holds the index, a JSON schema, a dependency-free validator and one model, Blood Axe Mace.

Client index URL: `https://raw.githubusercontent.com/hhhhhffd/ModelMirage-catolog/main/index.json`

## Catalog format

`index.json` (schema version 1) lists models. Each entry has an ID, a display name, a JSON model and its textures. There is no binding to an item: any `java-item` model can be applied to any item in the client.

- Supported: regular Java item models with `elements` and `display`, static PNG textures, `minecraft:item/generated` and `minecraft:item/handheld`.
- Not supported in version 1: animated PNG, armor, blocks, OptiFine CIT, Bedrock geometry.
- All paths are relative to the repository root. The validator checks sizes, SHA-256, PNG files, dependencies and cycles between custom parent models.

## Adding a model

1. Create `models/<id>/model.json` and put PNG files into `models/<id>/textures/`.
2. Add an entry to `index.json`: `model` and every texture carry a relative `path`, `sha256` and size in `bytes`.
3. `textures` keys must match the identifiers in the JSON model; references like `#0` resolve from its `textures`.
4. For custom parent models add a `parents` map (identifier to the same file object). `minecraft:*` parents may come from the client resources.
5. Add the permission/license and credits next to the model (`NOTICE.txt`).
6. Run the checks:

```bash
python scripts/validate_catalog.py
python -m unittest discover -s tests
```

GitHub Actions (`.github/workflows/validate.yml`) runs both on every push and pull request.

## Contents

| Path | Purpose |
| --- | --- |
| `index.json` | the catalog index |
| `schema.json` | JSON schema of the index |
| `models/blood-axe-mace/` | sample model with texture and `NOTICE.txt` |
| `scripts/validate_catalog.py` | catalog validator |
| `tests/test_catalog.py` | validator tests |

## License

MIT, see [LICENSE](LICENSE). The license covers the index, schema and tooling. Models and textures carry their own terms: see the `NOTICE.txt` next to each model (the Blood Axe Mace assets are excluded from the MIT license).

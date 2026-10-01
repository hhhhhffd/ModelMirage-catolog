import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.validate_catalog import validate


class CatalogValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source / "models", self.root / "models")
        self.index = json.loads((source / "index.json").read_text())

    def run_catalog(self):
        (self.root / "index.json").write_text(json.dumps(self.index))
        return validate(self.root)

    def test_valid_catalog(self):
        self.assertEqual(self.run_catalog(), 1)

    def test_path_traversal_rejected(self):
        self.index["models"][0]["model"]["path"] = "../index.json"
        with self.assertRaisesRegex(ValueError, "Unsafe asset path"):
            self.run_catalog()

    def test_corrupt_download_rejected(self):
        self.index["models"][0]["model"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.run_catalog()

    def test_missing_texture_rejected(self):
        entry = self.index["models"][0]
        entry["textures"]["other:missing"] = entry["textures"].pop("modelmirage:item/blood_axe_mace")
        with self.assertRaisesRegex(ValueError, "Missing dependent texture"):
            self.run_catalog()

    def test_duplicate_model_rejected(self):
        self.index["models"].append(copy.deepcopy(self.index["models"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate model"):
            self.run_catalog()


if __name__ == "__main__":
    unittest.main()

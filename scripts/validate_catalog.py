"""Validate the version 1 catalog without third-party dependencies."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys

ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
RESOURCE = re.compile(r"[a-z0-9_.-]+:[a-z0-9_./-]+\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root):
    root = Path(root).resolve()
    index = json.loads((root / "index.json").read_text())
    require(index.get("schema") == 1, "Unsupported schema")
    require(isinstance(index.get("models"), list), "models must be a list")
    require(len(index["models"]) <= 4096, "Too many models")
    ids = set()

    def read_asset(asset, maximum):
        path = asset["path"]
        pure = PurePosixPath(path)
        require(isinstance(path, str) and not pure.is_absolute() and
                all(part not in ("", ".", "..") for part in path.split("/")) and
                "\\" not in path and "%" not in path and ":" not in path,
                "Unsafe asset path: " + path)
        file = (root / path).resolve()
        require(file.is_relative_to(root), "Asset escapes catalog")
        require(type(asset["bytes"]) is int and 0 < asset["bytes"] <= maximum,
                "Invalid asset size: " + path)
        require(file.stat().st_size == asset["bytes"], "Size mismatch: " + path)
        data = file.read_bytes()
        require(hashlib.sha256(data).hexdigest() == asset["sha256"], "SHA-256 mismatch: " + path)
        return data

    for entry in index["models"]:
        require(ID.fullmatch(entry["id"]), "Invalid model id")
        require(entry["id"] not in ids, "Duplicate model id")
        ids.add(entry["id"])
        require(entry.get("format") == "java-item", "Unsupported format")
        require(isinstance(entry["name"], str) and 0 < len(entry["name"]) <= 128, "Invalid name")
        textures = entry["textures"]
        require(0 < len(textures) <= 32, "Invalid texture count")
        for name, asset in textures.items():
            require(RESOURCE.fullmatch(name), "Invalid texture id")
            png = read_asset(asset, 16 * 1024 * 1024)
            require(len(png) >= 33 and png[:8] == b"\x89PNG\r\n\x1a\n" and png[12:16] == b"IHDR", "Invalid PNG")
            width, height = struct.unpack(">II", png[16:24])
            require(0 < width <= 2048 and 0 < height <= 2048, "PNG dimensions exceed limits")

        def read_model(asset):
            data = json.loads(read_asset(asset, 4 * 1024 * 1024))
            require(isinstance(data, dict), "Model must be an object")
            require(len(data.get("elements", [])) <= 4096, "Too many elements")
            return data

        parents = {name: read_model(asset) for name, asset in entry.get("parents", {}).items()}
        require(len(parents) <= 32, "Too many parents")
        for name in parents:
            require(RESOURCE.fullmatch(name), "Invalid parent id")
        model = read_model(entry["model"])
        chain = [model]
        seen = set()
        parent = model.get("parent")
        while parent:
            require(RESOURCE.fullmatch(parent), "Invalid parent reference")
            require(parent not in seen, "Cyclic model parents")
            seen.add(parent)
            require(len(seen) <= 32, "Model parent chain too long")
            if parent not in parents:
                require(parent.startswith("minecraft:"), "Missing parent: " + parent)
                break
            chain.append(parents[parent])
            parent = parents[parent].get("parent")

        slots = {}
        for item in reversed(chain):
            slots.update(item.get("textures", {}))
        for slot in slots:
            value = slots[slot]
            seen_slots = {slot}
            while isinstance(value, str) and value.startswith("#"):
                key = value[1:]
                require(key in slots and key not in seen_slots, "Invalid texture alias: " + value)
                seen_slots.add(key)
                value = slots[key]
            if isinstance(value, dict):
                value = value["sprite"]
            require(isinstance(value, str) and value in textures, "Missing dependent texture: " + str(value))
        for item in chain:
            for element in item.get("elements", []):
                for face in element.get("faces", {}).values():
                    reference = face["texture"]
                    require(reference.startswith("#") and reference[1:] in slots, "Missing face texture: " + reference)
    return len(ids)


if __name__ == "__main__":
    try:
        root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
        print(f"Catalog valid: {validate(root)} model(s)")
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Catalog invalid: {error}", file=sys.stderr)
        sys.exit(1)

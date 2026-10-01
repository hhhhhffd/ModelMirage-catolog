# ModelMirage Catalog

Каталог моделей предметов для ModelMirage / Fabric 26.2.

Источник для клиента: `https://raw.githubusercontent.com/hhhhhffd/ModelMirage-catolog/main/index.json`.

`index.json` содержит список моделей. Каждая запись описывает ID, отображаемое имя, JSON-модель и текстуры. Привязки к предмету нет: любую модель формата `java-item` можно поставить на любой выбранный предмет в клиенте.

## Добавление модели

1. Создай `models/<id>/model.json` и положи PNG в `models/<id>/textures/`.
2. Добавь запись в `index.json`: `model` и каждая текстура содержат относительный `path`, `sha256` и размер `bytes`.
3. Ключи `textures` должны совпадать с идентификаторами в JSON-модели. Ссылки вида `#0` разрешаются из её `textures`.
4. Для собственных родительских моделей добавь карту `parents`: идентификатор → такой же объект файла. Родители `minecraft:*` могут браться из ресурсов клиента.
5. Добавь разрешение/лицензию и авторство в каталог модели.
6. Запусти `python scripts/validate_catalog.py` и `python -m unittest discover -s tests`.

Поддерживаются обычные Java item models с `elements`, `display` и статические PNG, а также `minecraft:item/generated` / `minecraft:item/handheld`. Анимированные PNG, armor, блоки, OptiFine CIT и Bedrock geometry не входят в формат версии 1.

Все пути относительны корню каталога. Проверяются размеры, SHA-256, PNG, зависимости и циклы собственных родителей. GitHub Actions запускает эти проверки при каждом push и pull request.

Метаданные и инструменты — CC0. Модели и текстуры имеют отдельные условия; смотри `NOTICE.txt` рядом с ними.

# FHD_Wormhole 0.7.4 NATIVE NODLL TEST — sources for Nexus review

**All 11 uploaded runtime files rebuild byte for byte from editable source.** The build is self-contained: no 0.7.3 base release, original DAT/GI files, game installation, Windows tools or downloads are required. Six automated tests passed, including 106 checks of statements recovered from rebuilt Rus/Eng DATs against controlled game API fixtures.

The supplied **TEST** status, author **Prolog_D**, version 0.7.4 and all runtime behavior are preserved. There is no DLL, EXE, SCR, ScriptLibs entry or ImportedFunction call in this mod. No RSON recovery project is needed: all executable statements are embedded in the recovered configuration source.

## What is included

| Path | Purpose |
| --- | --- |
| `source/CFG/Main.json` | Complete UI, button action, OnStart and OnLoad initialization |
| `source/CFG/Rus/Lang.json` | Russian strings, hull series, engine offers and equipped-item event handler |
| `source/CFG/Eng/Lang.json` | English equivalents and the same native generation definitions |
| `source/CFG/CacheData.json` | All six local image aliases |
| `source/graphics/*.json` | Complete editable sources for six single-layer ARGB8888 GI images |
| `source/ModuleInfo.txt` | UTF-8 metadata, emitted as original CP1251 bytes and line endings |
| `scripts/` | Full builder and lossless DAT/GI codecs |
| `tests/` | Source-only reconstruction, definition checks and game-API fixtures |
| `original-file-sha256.json`, `build-verification.json` | Uploaded runtime hashes and completed verification |
| `.github/workflows/build.yml` | GitHub build/check workflow |

The original archive's build script modified an unpacked full 0.7.3 release. This package replaces that dependency with complete current source. Older 0.7.2/0.7.3/0.7.4 patch scripts, duplicate text exports, historical reports and the BMP screenshot are excluded. Nothing requires manual decompilation or recovery on the user's PC.

## Original behavior retained

The mod registers the ordinary Wormhole hull series with `Probability=7` and paired special-engine definitions at priorities 0, 41 and 82. Each additional engine definition matches its corresponding original definition except for CustomTag. Native game generation supplies items; the mod does not periodically scan or refill shops.

OnStart/OnLoad initialize hidden service-info caches for definition IDs. The event handler runs for entering/reentering Ship, changing hull and equipping/unequipping items. It examines equipped hull/engine objects and cached IDs. The recovered callback contains no OnStep event, inventory/world loop or definition lookup. Legacy core/module/extra-special recognition and the newer hull-series/tier/extra-engine recognition remain present.

The button opens Galaxy after confirmation. A newly selected jump order triggers the original handoff, records a shared cooldown ending at current turn + 30, and advances the day. Installed ordinary breakable equipment is reduced to durability 1; the installed engine and fuel tank are capped at 10. Already lower durability is not raised. The original exclusions for the hull, artifacts, unused and unbreakable items remain in the code. Exact in-game object classification and jump behavior were not validated in a running game.

Cancelled selection, an unchanged existing jump target, missing WH capability, use outside normal space and an active cooldown exit without applying the jump penalty in the tested fixtures. Changing from a WH hull to a WH engine does not bypass the shared cooldown.

## Build and tests

Building requires **Python 3.10+ and its standard library only**. Behavior tests additionally require Node.js. Verified on 28 October 2026 with Python 3.12.14, zlib 1.3.2 and Node.js 24.22.1.

```sh
python3 scripts/build.py --strict-original
python3 -m unittest discover -s tests -v
```

Output: `dist/FHD_Wormhole_v0.7.4_FROM_SOURCE.zip` and `dist/build-report.json`. The installable ZIP contains all 11 runtime files at `Mods/FHD_MODS/FHD_Wormhole`. The delivered GitHub review archive itself contains source files, not a prebuilt installed mod. For deliberate source changes, omit `--strict-original`; changed hashes are reported.

Tests verify all original hashes, all six CacheData references, DAT/GI roundtrips, editable ARGB pixels, actual config edits, paired engine properties, bootstrap equivalence, event restrictions and a complete isolated rebuild without any previous release or binaries. The behavior fixture executes JS-adapted statements extracted from rebuilt DATs, making 53 checks for each localization: initialization, recognition, visibility, rejection paths, cooldown boundaries, equipment wear and jump handoff. These API fixtures are not the game's script compiler, RNG, renderer or executable.

The JSON preserves every string, block, stored entry order, sorting record, seed and image header/layer field. Graphics contain explicit raw pixel samples, including alpha and hidden color bytes, rather than opaque original GI payloads. The original flattened images are fully recovered; original layered artwork was not supplied.

## Generation limits and installation notes

The supplied NoDLL version explicitly does **not** implement a quota of three items per sector or a percentage table based on discovered sectors. Generation is left to the engine's native competition, technology, shop and restocking rules. `Probability=7` is not a statement that one seventh of all generated hulls will be Wormhole hulls, and duplicate engine entries do not guarantee twice as many items per year.

The uploaded 60,000-draw generation model and its historical check counts were not rerun here. They required additional vanilla and old-release configuration inputs. They are not counted among the new tests, and no fresh probability or whole-galaxy stock estimate is claimed.

The supplied README states that ordinary planets do not generate WH engines; station shops and the main pirate planet use their respective native rules. Existing stock is not immediately regenerated by installation. The original metadata cautions against disabling the mod mid-playthrough. Only one FHD_Wormhole variant should be active; removing the previous complete folder avoids leftovers from DLL-based variants. No changes to a user's installed game were performed here.

## Provenance and limits

Input: `FHD_Wormhole-v0.7.4 nativ NoDLL.rar` (ZIP container), SHA-256 `81b23df1aaae1ba8c9a2d2987408e8f304abe263fc961e3389b10ed9bb6cbd67`. All 11 runtime files are reproduced. Existing authorship, translations, TEST labeling and runtime values are unchanged.

No live Windows game, actual game-script compilation, shop generation/restocking, save compatibility, full mixed-mod installation, antivirus verdict or Nexus moderation approval is claimed. The hosted GitHub workflow was supplied but not executed on GitHub during preparation. Byte identity establishes preservation of the supplied version.

The independent DAT codec follows format conventions studied in the previously supplied MIT-licensed [rangers-utils](https://github.com/murgesku/rangers-utils). GI handling reuses the lossless typed source codec developed for the preceding mod preparations, with conventions checked against the previously supplied [SRHD-XenoModKit](https://github.com/Xenomorphchyma/SRHD-XenoModKit) materials. No third-party executable is bundled, and no new license or redistribution permission is inferred.

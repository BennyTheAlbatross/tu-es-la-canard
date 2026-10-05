"""Stage a game-only allowlist and publish a complete static release atomically."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

import soundfile

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
RELEASES = BUILD / "releases"
RELEASES.mkdir(exist_ok=True)
RUNTIME_CACHE = BUILD / "runtime-cache"


def runtime_file(entry):
    path = RUNTIME_CACHE / entry["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        pending = path.with_name(path.name + ".download")
        subprocess.run(["curl", "--compressed", "--retry", "5", "--retry-all-errors",
                        "-fsS", "https://pygame-web.github.io/cdn/" + entry["path"],
                        "-o", str(pending)], check=True)
        if hashlib.sha256(pending.read_bytes()).hexdigest() != entry["sha256"]:
            raise RuntimeError(f"Runtime checksum changed: {entry['path']}")
        os.replace(pending, path)
    return path


def copy_file(relative, destination):
    source = ROOT / relative
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


with tempfile.TemporaryDirectory(prefix="canard-", dir=BUILD) as temporary:
    stage = Path(temporary) / "game"
    stage.mkdir()
    modules = ["main.py", "runtime/main_menu.py", "runtime/gameplay.py",
               "tuer_le_canard/tuer_le_canard.py", "tuer_le_canard/game_data.py",
               "rules/objects.csv"]
    modules += [f"rules/{name}.py" for name in
                ("browser", "sprits", "movments", "interactions", "gates",
                 "hazards", "shaders", "music")]
    assets = json.loads((ROOT / "scripts/game-assets.json").read_text())
    for relative in modules + assets:
        copy_file(relative, stage)
    for source in sorted((ROOT / "maps/game").glob("*.csv")):
        copy_file(str(source.relative_to(ROOT)), stage)
    music, rate = soundfile.read(ROOT / "assets/music/hellfeather_march.wav")
    audio_out = stage / "assets/music/hellfeather_march.ogg"
    audio_out.parent.mkdir(parents=True, exist_ok=True)
    soundfile.write(audio_out, music, rate, format="OGG", subtype="VORBIS")

    subprocess.run([sys.executable, "-m", "pygbag", "--build", "--no_opt",
                    "--title", "Tu es la Canard", str(stage)], check=True)
    generated = stage / "build/web"
    if not (generated / "index.html").is_file() or not list(generated.glob("*.apk")):
        raise RuntimeError("Pygbag did not produce a complete game package")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    release = RELEASES / stamp
    release.mkdir()
    shutil.copytree(generated, release / "game")
    shutil.copytree(ROOT / "web", release, dirs_exist_ok=True)
    runtime_manifest = json.loads((ROOT / "scripts/runtime-assets.json").read_text())
    for entry in runtime_manifest:
        target = release / "runtime" / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_file(entry), target)
    game_index = release / "game/index.html"
    html = game_index.read_text()
    html = html.replace('https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js', '../vendor/browserfs.min.js')
    html = html.replace('https://pygame-web.github.io/cdn/0.9.3/', '../runtime/0.9.3/')
    html = html.replace('    cdn : "../runtime/0.9.3/",', '    cdn : location.origin + "/runtime/0.9.3/",')
    bridge = '<script src="../game-bridge.js"></script><link rel="stylesheet" href="../game.css">'
    if "</head>" not in html:
        raise RuntimeError("Generated page has no head; cannot install input bridge")
    game_index.write_text(html.replace("</head>", bridge + "\n</head>", 1))
    # Our Caddy-hosted site loads game.tar.gz; .apk is only used on itch.io.
    for redundant in (release / "game").glob("*.apk"):
        redundant.unlink()
    # Keep interpreter imports and the package index on this same static site.
    for relative in ("0.9.3/pythons.js", "vtx.js"):
        path = release / "runtime" / relative
        text = path.read_text().replace("https://pygame-web.github.io/cdn/", "/runtime/")
        path.write_text(text)
    index = release / "runtime/index-0.9.3-cp312.json"
    packages = json.loads(index.read_text())
    packages["-CDN-"] = "/runtime/"
    index.write_text(json.dumps(packages))
    # Configure the wheel index before the interpreter's initial repo preload.
    # Resetting it in the game template happens too late and loses that preload.
    pyrc = release / "runtime/0.9.3/cpythonrc.py"
    text = pyrc.read_text().replace(
        "import aio.cross\n",
        'import aio.cross\nimport platform as _canard_platform\nos.environ["PYGPI"] = str(_canard_platform.window.location.origin) + "/runtime/"\n', 1)
    pyrc.write_text(text)

    forbidden = {".git", ".env", "map_editor.py", "NOTES.md", "DECISIONS.md"}
    for path in release.rglob("*"):
        if path.name in forbidden:
            raise RuntimeError(f"Forbidden file in public build: {path.name}")
    report = {"pygbag": "0.9.3", "public_bytes": sum(p.stat().st_size for p in release.rglob("*") if p.is_file()),
              "game_images": len(assets), "music_bytes": audio_out.stat().st_size,
              "game_package_bytes": sum(p.stat().st_size for p in (release / "game").glob("*.tar.gz"))}
    (release / "build-info.json").write_text(json.dumps(report, indent=2) + "\n")
    pending = BUILD / (".web-" + stamp)
    pending.symlink_to(release.relative_to(BUILD), target_is_directory=True)
    os.replace(pending, BUILD / "web")
    print(json.dumps(report, indent=2))
    print(f"Static website: {BUILD / 'web'}")

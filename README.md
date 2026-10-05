# Tu es la Canard — browser port

A static Pygame/Pygbag port of [BennyTheAlbatross/tu-es-la-canard](https://github.com/BennyTheAlbatross/tu-es-la-canard).
Desktop browsers offer 2D and ray-cast gameplay. Touch devices with a coarse
pointer offer 2D with an on-screen directional pad and action buttons.
The public build contains existing game levels, without the map editor.

## Native development

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-web.txt
.venv/bin/python runtime/main_menu.py
```

Native gameplay keeps both modes and the existing editor. Browser loops yield
to the browser; browser ray-cast runs in-process instead of launching a child
process. Native ray-cast retains its subprocess launch. The port also fixes
an existing ray-cast quit event being overwritten by the next update.

## Browser development

```sh
.venv/bin/python -m pygbag .
```

Open http://localhost:8000 and click the game to start audio and focus input.
This development command packages the checkout broadly; use the production
build below for the game-only asset allowlist and complete wrapper.

## Building for web

```sh
./scripts/build-web.sh
```

If the virtual environment lives elsewhere:

```sh
CANARD_PYTHON=/path/to/venv/bin/python ./scripts/build-web.sh
```

The build requires curl and the pinned requirements. It stages only required
modules, CSV levels and 53 actively loaded images. Original WAV music is
converted to OGG in staging; original assets remain unchanged.
Runtime files are downloaded once, verified against committed SHA-256 hashes,
and served locally with the site. Output is `build/web`, an atomic symlink to
a complete release in `build/releases`. A failed build leaves the prior
release selected. Generated files and caches are ignored by Git.

The build uses Pygbag 0.9.3. Its browser interpreter is CPython 3.12 with
pygame-ce 2.5.7; native development uses pygame-ce 2.5.8. Runtime updates need
new reviewed checksums and browser verification.

For a local production-style preview, use Caddy with `deploy/Caddyfile`,
changing its root and loopback port for the development machine. Verify
Chromium and Firefox, controls, levels, return/restart, audio after interaction,
touch input and console errors before publishing.

Optional automated browser checks (development machine only):

```sh
.venv/bin/pip install playwright==1.63.0
.venv/bin/python -m playwright install chromium firefox
CANARD_URL=http://127.0.0.1:18000 .venv/bin/python scripts/test-browser.py
```

The checks exercise menus, both desktop modes, all six level loads, movement,
torch, return controls, and emulated touch 2D. Evidence is saved under
`build/browser-evidence`. Real device/audio checks remain necessary.

## Deploying to canard-web

Build and verify on the development machine, then upload static files:

```sh
git pull --ff-only
./scripts/build-web.sh
./scripts/deploy-web.sh canard@canard-web
```

The deployment script creates a new release, switches `/srv/canard/build`
atomically, checks local HTTP, and restores the previous release if that check
fails. The serving VM does not need GitHub credentials, a Python build
environment, or a checkout. Full provisioning, isolation checks, recovery and
emergency commands are in [deploy/OPERATIONS.md](deploy/OPERATIONS.md).

## Architecture

Internet → Tailscale Funnel HTTPS → isolated Debian `canard-web` VM →
Caddy on loopback → `/srv/canard/build` → visitor's WebAssembly game.

The visitor's browser runs the game. The server serves static files and keeps
no game sessions, accounts, database, upload endpoint or analytics. Game
runtime dependencies are also served by Caddy rather than a third-party CDN.
The VM must have no NAS mounts or homelab credentials, and both LAN and tailnet
isolation must be verified before enabling Funnel. Deployment configuration
is prepared; provisioning and public verification are separate required steps.

Emergency shutdown on the serving VM:

```sh
sudo tailscale funnel reset
sudo systemctl stop caddy
```

## Upstream game notes

#tu es la canard 

## Run the game

```bash
python3 runtime/main_menu.py
```

Choose a level, then play the same CSV map in either the 2D or ray-cast mode.

### Controls

- Arrow keys: move in 2D
- WASD / arrows / mouse: move and turn in ray-cast mode
- Space: toggle the player's torch
- M: toggle music
- Enter: select menu item
- Escape: return or quit

Raising the torch increases visibility, slows the duck, and makes every demon
1.5x faster. Nearby hidden doors are permanently opened when revealed. One-way
gate arrows show the direction the duck may travel. Map 5 is a complete puzzle
level demonstrating gates, a hidden torch door, demons, and collapsing floors.

## Map editor

Run the visual CSV editor with:

```bash
python3 map_editor.py
```

It opens `map1.csv` by default. Pass another map path to open it directly:

```bash
python3 map_editor.py maps/game/map4.csv
```

Blank CSV cells remain blank and are distinct from background object `0`. Hold the arrows, WASD, or Vim-style H/J/K/L keys to move continuously; moving beyond the right or bottom edge expands the map. Shift-H/J/K/L and the mouse wheel pan larger maps. Horizontal wheel gestures pan sideways, and Shift+vertical wheel is the fallback. Left-click and drag to paint continuously. Right-click and drag or press Delete to make cells blank. Q/E changes the catalogue selection.

Press `:` for Vim-style commands: `:w`, `:q`, `:wq`, `:q!`, and `:e`. Press `?` to show or hide the complete controls overlay. The palette is loaded from `rules/objects.csv`, so new catalogue entries appear automatically.

'''
a dungon puzzle explorere, where you the duck enter hell and battle deamons. 
a map and level build framework implimented in python & and clickly clickly excel. 
'''


## dir structure and plan 

home/ 
|---maps/
|   |--- map1.csv       #containers raw level configuration WORLD STATE
|
|---rules/ 
|   |--- objects.csv   # containes and describes objects in maps. OBJECT DEFINIATION
|   |--- movement.py   # describes movement of player and enemies. 
|   |--- colsion_ruels.py # rules for interaction between objects and players. 
|   |--- level_loader.py   # cordinates level choice and maps loaded. 
|
|---Source/ 
|   |--- map1.ods      # map editor source file.
| 
|---Assets/ 
|   |---sprits/        #png images 
|   |--- audio/        #sound affects music
|
|---Scripts
|   |--- main_menu.py       # menu screen/ death screen/ level picker. 
|   |--- score_timer.py     # clock timer, some kind of higher score per level. 
|   |--- scores.csv         # saves highscore data
|   |--- main.py            # Master script.  
|
|---launcher.py             # Main urnnng script
|---README.MD               # repo instructions/ plan / this doc 

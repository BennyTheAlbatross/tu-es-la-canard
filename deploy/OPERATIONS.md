# Static serving and recovery

This is a deployment runbook, not a claim that the VM has been provisioned.
Record completed host/network checks separately before enabling Funnel.

## Architecture

Internet → Tailscale Funnel HTTPS → Caddy on 127.0.0.1:8080 →
/srv/canard/build (atomic release symlink).

The browser runs Pygame/WebAssembly. This machine runs no Python game
processes, development server, database, session backend, or Docker stack.
Required interpreter/wheel files are included in the static build.

## Serving VM

Dedicated Debian VM canard-web; start at 1 vCPU, 1 GB RAM, 16 GB disk.
Create the deployment user canard with a locked password and an explicitly
chosen administrator public SSH key. Do not copy any private key into it.
Install Caddy, Tailscale, curl, SSH server, and unattended-upgrades through
their supported repositories. Apply Debian updates.

Keep /srv/canard owned by canard, directories 755 and files 644. Caddy runs
under its normal caddy account and cannot write the deployments. Install
deploy/Caddyfile at /etc/caddy/Caddyfile and validate before starting:

```sh
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl enable --now caddy
```

The config disables Caddy's administration endpoint, binds HTTP to loopback,
disables directory browsing, blocks repository paths, and sets a CSP suitable
for the Pygbag template. Test that policy in Chromium and Firefox. It permits
inline scripts and eval because the interpreter/template requires them.

## Isolation gate

Apply firewall policy outside the guest at the Proxmox VM interface. Block
guest-initiated private LAN, management, link-local, and IPv6 ULA destinations
except narrowly required DHCP/DNS. Choose a resolver without giving the VM
router-management access. Account for both IPv4 and IPv6 and keep established
responses to administrator connections working.

Also restrict the tagged VM in the tailnet policy: allow administrator
connections to its SSH/web services, and no guest-initiated connections to
other tailnet machines. A broad allow-all source rule can defeat this policy.
Do not overwrite an existing tailnet policy without checking current rules.

No NAS mounts, private documents, Proxmox tokens, other-machine credentials,
private SSH keys, subnet routing, exit-node role, or SSH exposure via Funnel.

Verify from the guest that management/NAS/private VM connections fail.
Verify approved updates, time, DNS, and Tailscale transport still work.
Inspect `ss -tulpn`, `findmnt`, and `systemctl --type=service --state=running`.

## Manual deployment

From the development checkout:

```sh
git pull --ff-only
./scripts/build-web.sh
# Browser checks before publishing the resulting release.
./scripts/deploy-web.sh canard@canard-web
```

No build environment or GitHub credential is needed on the serving VM.
The script uploads into a new release directory and atomically changes
/srv/canard/build. It restores the prior symlink if its HTTP check fails.
Retain a previous verified release for rollback; clean old releases deliberately.

## Tailscale and public access

Join using a dedicated tag and the tailnet administrator-approved policy.
Verify private administration and static serving first:

```sh
sudo tailscale serve --bg http://127.0.0.1:8080
tailscale serve status
```

After browser, filesystem, network-isolation, and private-access checks pass,
switch that service to public Funnel:

```sh
sudo tailscale serve reset
sudo tailscale funnel --bg http://127.0.0.1:8080
tailscale funnel status
```

Funnel may need administrator approval of HTTPS/Funnel capabilities. Publish
only this static HTTP service. Use the reported HTTPS URL; do not expose SSH.
Verify play from an unrelated Internet connection and record the result.

## Emergency shutdown

```sh
sudo tailscale funnel reset
sudo systemctl stop caddy
```

To revoke this machine entirely, remove it in the Tailscale administration
console; `sudo tailscale logout` also disconnects it locally. Keep Proxmox
console access for recovery. Stop the VM from Proxmox if compromise is suspected.

## Updates and rollback

Debian: `sudo apt update && sudo apt upgrade`; review reboot requirements.
Enable unattended security updates and monitor their status.
Pygbag: update requirements-web.txt, regenerate the pinned runtime manifest,
then repeat browser, audio, mobile, download-size, and public checks. Do not
silently accept changed runtime checksums.

Rollback: point /srv/canard/build to a previous release using a temporary
symlink and `mv -T` while logged in as canard, then check HTTP and public play.

## Recreate from scratch

Create a clean Debian VM with the same minimal resources and independent
firewall policy. Install only serving/admin packages, recreate canard and
authorized public keys, install/validate Caddyfile, join with the restricted
tailnet tag, deploy a verified static release, test isolation/private access,
then enable Funnel and repeat the unrelated-Internet play test. Never restore
personal credentials, mounts, or the compromised machine's Tailscale state.

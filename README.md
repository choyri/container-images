# container-images

Lightly re-packaged upstream container images — an official base plus the one
thing it is missing — built and published by GitHub Actions to Docker Hub and
GHCR.

## Images

| Directory                          | Image             | What it adds                                |
| ---------------------------------- | ----------------- | ------------------------------------------- |
| [`opensearch-ik/`](opensearch-ik/) | `opensearch-ik`   | OpenSearch + INFINI `analysis-ik` plugin    |
| [`warp/`](warp/) | `warp` | Cloudflare WARP + 3proxy HTTP / SOCKS5 proxies |

## Repository setup

One-time configuration, under **Settings → Secrets and variables → Actions**:

| Kind     | Name                 | Value                                              |
| -------- | -------------------- | -------------------------------------------------- |
| Variable | `DOCKERHUB_USERNAME` | Docker Hub account or org that owns the repos       |
| Secret   | `DOCKERHUB_TOKEN`    | Docker Hub access token with read/write scope       |

GHCR needs no secret — the workflows push with the built-in `GITHUB_TOKEN` and a
`packages: write` permission. To publish to GHCR only, delete the `docker.io`
lines from a workflow's `meta-images` and `registry-auths`.

Install the [Renovate GitHub App](https://github.com/apps/renovate) and grant it
access to this repository. [`.github/renovate.json`](.github/renovate.json)
configures updates for Dockerfile image versions and GitHub Actions
dependencies. The hosted app opens pull requests when updates are available.
Changes to the contents of an existing Docker image tag do not trigger update
pull requests.

## Layout

One workflow file per image, named after its directory. Each is a thin caller of
[`docker/github-builder`](https://github.com/docker/github-builder), Docker's
maintained reusable build workflow, which handles per-platform runners, manifest
assembly, caching and signed SLSA provenance.

## Conventions

- Keep exact upstream version tags in each Dockerfile.
  Workflows read version metadata from it instead of maintaining duplicate pins.
- Build on relevant file changes or manual dispatch; pull requests build without
  publishing. Publish only from `master`, then smoke-test the resulting digest.
- Keep image-specific tag and update policies in each image's README.

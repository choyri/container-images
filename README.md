# container-images

Lightly re-packaged upstream container images — an official base plus the one
thing it is missing — built and published by GitHub Actions to Docker Hub and
GHCR.

## Images

| Directory                          | Image             | What it adds                                |
| ---------------------------------- | ----------------- | ------------------------------------------- |
| [`opensearch-ik/`](opensearch-ik/) | `opensearch-ik`   | OpenSearch + INFINI `analysis-ik` plugin    |

## Repository setup

One-time configuration, under **Settings → Secrets and variables → Actions**:

| Kind     | Name                 | Value                                              |
| -------- | -------------------- | -------------------------------------------------- |
| Variable | `DOCKERHUB_USERNAME` | Docker Hub account or org that owns the repos       |
| Secret   | `DOCKERHUB_TOKEN`    | Docker Hub access token with read/write scope       |

GHCR needs no secret — the workflows push with the built-in `GITHUB_TOKEN` and a
`packages: write` permission. To publish to GHCR only, delete the `docker.io`
lines from a workflow's `meta-images` and `registry-auths`.

## Layout

One workflow file per image, named after its directory. Each is a thin caller of
[`docker/github-builder`](https://github.com/docker/github-builder), Docker's
maintained reusable build workflow, which handles per-platform runners, manifest
assembly, caching and signed SLSA provenance.

## Conventions

- Pin an exact upstream version via a build arg; never build `FROM` a floating
  tag, so a rebuild of a given tag is reproducible.
- Every image is rebuilt weekly on a schedule to pick up base-image patches.
- Every workflow ends with a smoke test that starts the published image and
  asserts the added functionality actually works.

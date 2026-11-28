# opensearch-ik

[OpenSearch](https://github.com/opensearch-project/OpenSearch) with the
[INFINI analysis-ik](https://github.com/infinilabs/analysis-ik) Chinese analysis
plugin preinstalled.

## Tags

`OPENSEARCH_VERSION` in the [Dockerfile](Dockerfile) is the only version pin.
The workflow automatically generates these tags:

| Tag | Contents |
| --- | --- |
| `X.Y.Z` | The matching OpenSearch and analysis-ik versions |
| `X.Y` | The last published patch in that minor series |
| `X` | The last published version in that major series |
| `latest` | The latest maintained version |

Platforms: `linux/amd64`, `linux/arm64`.

Only the current version is built. Historical images remain available without
automatic backports. Use an exact version tag in production, or an image digest
when its contents must stay fixed.

## Usage

```yaml
services:
  opensearch:
    image: ghcr.io/choyri/opensearch-ik:3
    environment:
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
      - DISABLE_SECURITY_PLUGIN=true
      - DISABLE_PERFORMANCE_ANALYZER_AGENT_CLI=true
    ports:
      - 127.0.0.1:9200:9200
    volumes:
      - opensearch-data:/usr/share/opensearch/data

volumes:
  opensearch-data:
```

This example disables the security plugin and binds the port to localhost.
Check plugin loading and Chinese tokenization:

```sh
curl -fsS 'http://localhost:9200/_cat/plugins?v' | grep analysis-ik
curl -fsS -X POST http://localhost:9200/_analyze \
    -H 'Content-Type: application/json' \
    -d '{"analyzer":"ik_smart","text":"计算机汉字输入方法"}'
```

## Building locally

From the repository root, without repeating the version:

```sh
docker build -t opensearch-ik:local ./opensearch-ik
```

## Updates and publishing

[Renovate](../.github/renovate.json) monitors the official image for new version
tags and updates `OPENSEARCH_VERSION` in the Dockerfile through pull requests.
For a manual upgrade, change that argument's default value.

Pull requests build both platforms without publishing. The matching plugin must
exist at `https://get.infini.cloud/opensearch/analysis-ik/<version>`, or plugin
installation fails. If the plugin is not available yet, leave the upgrade PR
open and rerun CI after its release before merging.

Changes merged to `master` publish the image and smoke-test the resulting digest
on both architectures. Smoke tests run after publishing, so a failure means the
tags already exist and require investigation. There is no scheduled rebuild;
manual publishing is available from `master`.

See [repository setup](../README.md#repository-setup) for the one-time Renovate
GitHub App connection.

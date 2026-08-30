# opensearch-ik

[OpenSearch](https://github.com/opensearch-project/opensearch) with the
[INFINI analysis-ik](https://github.com/infinilabs/analysis-ik) Chinese analysis
plugin preinstalled.

## Tags

| Tag                    | Contents                                      |
| ---------------------- | --------------------------------------------- |
| `3.8.0`                | OpenSearch 3.8.0 + analysis-ik 3.8.0          |
| `3.8`, `3`, `latest`   | Moving aliases for the newest 3.x build       |

Platforms: `linux/amd64`, `linux/arm64`.

## Usage

```yaml
services:
  opensearch:
    image: ghcr.io/choyri/opensearch-ik:3.8.0
    environment:
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
      # - OPENSEARCH_INITIAL_ADMIN_PASSWORD=<a-strong-password>
      - DISABLE_SECURITY_PLUGIN=true
      - DISABLE_PERFORMANCE_ANALYZER_AGENT_CLI=true
    ports:
      - 127.0.0.1:9200:9200
    volumes:
      - opensearch-data:/usr/share/opensearch/data

volumes:
  opensearch-data:
```

Check the plugin is live:

```console
$ curl -sk -u admin:<password> 'https://localhost:9200/_cat/plugins?v' | grep analysis-ik
$ curl -sk -u admin:<password> -X POST https://localhost:9200/_analyze \
    -H 'Content-Type: application/json' \
    -d '{"analyzer":"ik_smart","text":"计算机汉字输入方法"}'
```

## Building locally

```console
$ docker build --build-arg OPENSEARCH_VERSION=3.8.0 -t opensearch-ik:3.8.0 ./opensearch-ik
```

## Publishing a new version

Add an entry to the `build` matrix in
[`.github/workflows/opensearch-ik.yml`](../.github/workflows/opensearch-ik.yml)
and move the `3` / `latest` aliases onto it. The plugin must already exist at
`https://release.infinilabs.com/analysis-ik/stable/`.

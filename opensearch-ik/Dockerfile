# syntax=docker/dockerfile:1

ARG OPENSEARCH_VERSION=3.10.1

FROM opensearchproject/opensearch:${OPENSEARCH_VERSION}

ARG OPENSEARCH_VERSION

# The plugin must match the base image version.
RUN set -eux; \
    opensearch-plugin install --batch \
      "https://get.infini.cloud/opensearch/analysis-ik/${OPENSEARCH_VERSION}"; \
    opensearch-plugin list | grep -qx analysis-ik

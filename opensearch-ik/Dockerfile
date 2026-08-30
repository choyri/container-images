# syntax=docker/dockerfile:1

ARG OPENSEARCH_VERSION=3.8.0

FROM opensearchproject/opensearch:${OPENSEARCH_VERSION}

ARG OPENSEARCH_VERSION

# analysis-ik is version-locked: its plugin-descriptor.properties pins
# opensearch.version, so `opensearch-plugin install` itself fails on a mismatch
# between this ARG and the base image tag. Always pin an exact base version
# here -- never a floating tag such as `3` or `latest`.
RUN set -eux; \
    opensearch-plugin install --batch \
      "https://get.infini.cloud/opensearch/analysis-ik/${OPENSEARCH_VERSION}"; \
    opensearch-plugin list | grep -qx analysis-ik

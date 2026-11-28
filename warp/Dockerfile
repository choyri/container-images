# syntax=docker/dockerfile:1

ARG THREEPROXY_VERSION=1.0.4
ARG MESH_VERSION=2026.10.0

FROM 3proxy/3proxy:${THREEPROXY_VERSION} AS threeproxy

FROM cloudflare/mesh:${MESH_VERSION}

COPY --from=threeproxy /bin/3proxy /usr/local/bin/3proxy
COPY 3proxy.cfg /etc/3proxy/3proxy.cfg
COPY 3proxy-LICENSE /usr/local/share/licenses/3proxy/LICENSE

COPY --chmod=755 entrypoint.sh healthcheck.sh /usr/local/bin/

ENV SRCNAT_ENABLED=false

EXPOSE 1080/tcp 3128/tcp

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD ["/usr/local/bin/healthcheck.sh"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []

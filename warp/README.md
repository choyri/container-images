# warp

[Cloudflare WARP](https://developers.cloudflare.com/warp-client/) with HTTP and
SOCKS5 proxies powered by [3proxy](https://github.com/3proxy/3proxy).

## Tags

| Tags | Contents |
| --- | --- |
| `2026.10.0`, `latest` | Cloudflare Mesh 2026.10.0 + 3proxy 1.0.3 |

Platforms: `linux/amd64`, `linux/arm64`.

## Usage

Requires a Linux TUN device (`/dev/net/tun`) and the `NET_ADMIN` capabilities.

```yaml
services:
  warp:
    image: ghcr.io/choyri/warp:latest
    restart: unless-stopped
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    # SOCKS5 UDP requires a shared Docker network.
    ports:
      - 127.0.0.1:3128:3128
      - 127.0.0.1:1080:1080
    volumes:
      - warp-data:/var/lib/cloudflare-warp

volumes:
  warp-data:
```

The first start registers a personal WARP client and accepts Cloudflare's service
terms. Registration is saved in the `warp-data` volume. Keep this volume when
recreating the container; do not reuse a Mesh or Zero Trust registration.

Applications on the same Compose network can use `http://warp:3128` for HTTP and
HTTPS, or `socks5h://warp:1080` for SOCKS5 with proxy-side DNS resolution. Set the
proxy in the application; joining the network alone does not route its traffic.

The default configuration has no authentication. Use a trusted network only.

Check the connection after enabling host access:

```console
$ curl --proxy http://127.0.0.1:3128 https://www.cloudflare.com/cdn-cgi/trace
$ curl --proxy socks5h://127.0.0.1:1080 https://www.cloudflare.com/cdn-cgi/trace
```

Both requests should return `warp=on`.

## Configuration

- Mount a named volume or writable host directory at `/var/lib/cloudflare-warp`.
  The container refuses to start without this mount.
- To configure authentication, mount a custom file at `/etc/3proxy/3proxy.cfg`.
  Keep the process in the foreground (no `daemon`).
- SOCKS5 UDP requires a client with `UDP ASSOCIATE` support on the same Docker
  network. Publishing port `1080` alone does not expose its dynamic UDP ports.

## Building locally

From the repository root:

```console
$ docker build --pull -t warp:local ./warp
```

## Publishing a new version

Update the versions in `Dockerfile` and the build arguments, tags, cache scope,
and version metadata in [the workflow](../.github/workflows/warp.yml).
Keep the tags and usage example above in sync.

## License

The image includes the [3proxy license](3proxy-LICENSE) at
`/usr/local/share/licenses/3proxy/LICENSE`.

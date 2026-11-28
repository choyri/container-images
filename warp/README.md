# warp

[Cloudflare WARP](https://developers.cloudflare.com/warp-client/) with HTTP and
SOCKS5 proxies powered by [3proxy](https://github.com/3proxy/3proxy).

## Tags

Tags follow `MESH_VERSION` in the [Dockerfile](Dockerfile):

| Tag | Contents |
| --- | --- |
| `YYYY.M.P` | That Cloudflare Mesh version with the pinned 3proxy dependency |
| `latest` | The latest published build |

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

## Updates and publishing

Renovate monitors both `cloudflare/mesh` and `3proxy/3proxy` for new version tags
and updates the version arguments in the Dockerfile through pull requests.

The workflow reads `MESH_VERSION` from the Dockerfile to generate the version
tag, cache scope and version metadata. Both dependency versions are maintained
only in the Dockerfile; no workflow or documentation version edits are needed.

Pull requests build both platforms without publishing. Changes merged to
`master` publish the image and run the proxy smoke tests against the resulting
digest. These tests cover HTTP and SOCKS5 proxies without registering a WARP
device in CI. Manual publishing is also available from `master`.

A 3proxy update republishes the current Mesh version tag.
Pin the output image digest when its contents must stay fixed.
Historical tags remain available and are not rebuilt automatically.

See [repository setup](../README.md#repository-setup) for the one-time Renovate
GitHub App connection.

## License

The image includes the [3proxy license](3proxy-LICENSE) at
`/usr/local/share/licenses/3proxy/LICENSE`.

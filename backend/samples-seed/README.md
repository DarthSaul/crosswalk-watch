# Bundled sample clips

Drop short `.mp4` files here before building the Docker image and they'll be
baked into `/app/data/samples/` so the home-page picker has content out of the
box on a fresh persistent volume.

Keep these small (a few MB each, ~10-second trims) — they ship inside every
container layer. Trim full-length samples with:

```sh
ffmpeg -i input.mp4 -t 10 -c copy seed_short.mp4
```

This directory's `.mp4` contents are gitignored; only this README and
`.gitkeep` are tracked. To include a clip in the build, just `cp` it here and
run `fly deploy`.

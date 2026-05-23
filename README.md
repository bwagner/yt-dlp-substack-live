# yt-dlp-substack-live

A [yt-dlp](https://github.com/yt-dlp/yt-dlp) extractor plugin for Substack live
streams (`*.substack.com/live-stream/<id>` URLs).

yt-dlp's built-in `SubstackIE` covers Substack posts, podcasts, and on-demand
videos (`*.substack.com/p/<slug>`), but not live streams or their replays.
This plugin fills that gap.

The gap is tracked upstream as
[yt-dlp/yt-dlp#16784](https://github.com/yt-dlp/yt-dlp/issues/16784); if yt-dlp
adds native support, this plugin becomes unnecessary.

## What it extracts

- Signed Mux HLS playback URL (all renditions: 270p / 360p / 540p typical)
- Title, description, host, publication, scheduled / start / end timestamps
- Duration (for replays)
- English subtitles (when present)
- Thumbnail
- Replay-eligibility check (clear error if a stream is not replay-eligible)

`is_live` / `was_live` are set correctly based on stream state.

## Install

### Manual (recommended)

```bash
mkdir -p ~/.config/yt-dlp/plugins/yt-dlp-substack-live
cp -r yt_dlp_plugins ~/.config/yt-dlp/plugins/yt-dlp-substack-live/
```

Or symlink for live updates:

```bash
mkdir -p ~/.config/yt-dlp/plugins/yt-dlp-substack-live
ln -s "$PWD/yt_dlp_plugins" ~/.config/yt-dlp/plugins/yt-dlp-substack-live/yt_dlp_plugins
```

Verify yt-dlp picks it up:

```bash
yt-dlp -v --skip-download https://open.substack.com/live-stream/212607 2>&1 | grep -E 'Extractor Plugins|Plugin directories'
```

You should see `Extractor Plugins: SubstackLiveIE` and the plugin directory
listed.

### Other install locations

yt-dlp searches several directories for plugins; `~/.config/yt-dlp/plugins/`
is the standard user location on Linux/macOS. See [yt-dlp's plugin
documentation](https://github.com/yt-dlp/yt-dlp/wiki/Plugins) for alternatives.

## Usage

```bash
# Best-quality video
yt-dlp https://open.substack.com/live-stream/<id>

# Video + English subtitles as SRT
yt-dlp --write-subs --sub-langs en --convert-subs srt \
       https://open.substack.com/live-stream/<id>

# Subtitles only
yt-dlp --write-subs --sub-langs en --convert-subs srt --skip-download \
       https://open.substack.com/live-stream/<id>

# List what's available
yt-dlp --list-subs --skip-download https://open.substack.com/live-stream/<id>
```

Any `*.substack.com/live-stream/<digits>` URL is matched, including
`open.substack.com/...` and publication subdomains.

## Caveats

- **Mux JWT expiration.** The signed playback URL is valid for ~8 hours after
  extraction. Extract and download in the same session; long-paused resumes
  past that window will fail and require re-running yt-dlp.
- **Substack HTML changes.** The plugin reads stream metadata from the
  `window._preloads` JSON blob Substack inlines into the page. If Substack
  restructures that blob, the plugin breaks. File an issue.
- **Scheduled streams.** Streams that haven't started yet have no playback URL
  and will fail with a clear error.

## License

MIT. See [LICENSE](LICENSE).

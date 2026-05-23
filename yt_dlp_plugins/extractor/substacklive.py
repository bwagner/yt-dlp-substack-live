from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
    ExtractorError,
    int_or_none,
    js_to_json,
    parse_iso8601,
    str_or_none,
)
from yt_dlp.utils.traversal import traverse_obj


class SubstackLiveIE(InfoExtractor):
    IE_NAME = 'substack:live'
    _VALID_URL = r'https?://(?:[\w-]+\.)?substack\.com/live-stream/(?P<id>\d+)'
    _TESTS = [{
        'url': 'https://open.substack.com/live-stream/212607',
        'info_dict': {
            'id': '212607',
            'ext': 'mp4',
            'title': 'Live with Kent Beck',
            'uploader': 'Kent Beck',
            'uploader_id': 'kentbeck',
            'channel': 'Software Design: Tidy First?',
            'was_live': True,
        },
        'params': {'skip_download': True},
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # The signed Mux JWT in playbackUrl expires ~8h after page render;
        # resumes past that point require re-running yt-dlp.
        preloads = self._parse_json(self._search_json(
            r'window\._preloads\s*=\s*JSON\.parse\(', webpage, 'preloads',
            video_id, transform_source=js_to_json,
            contains_pattern=r'"{(?s:.+)}"'), video_id)

        live = traverse_obj(preloads, ('activeLiveStream', 'liveStream', {dict}))
        info = traverse_obj(preloads, ('activeLiveStream', 'liveStreamInformation', {dict}))
        if not live or not info:
            raise ExtractorError('Could not locate live stream data', expected=True)

        playback_url = info.get('desktopPlaybackUrl') or info.get('playbackUrl')
        if not playback_url:
            if info.get('isReplayEligible') is False:
                raise ExtractorError('Replay is not available for this stream', expected=True)
            raise ExtractorError(
                'No playback URL found (stream may not have started yet)', expected=True)

        formats, subtitles = self._extract_m3u8_formats_and_subtitles(
            playback_url, video_id, 'mp4', m3u8_id='hls')

        started = parse_iso8601(live.get('started_streaming_at'))
        ended = parse_iso8601(live.get('ended_streaming_at'))

        return {
            'id': video_id,
            'title': live.get('title'),
            'description': live.get('description') or None,
            'formats': formats,
            'subtitles': subtitles,
            'timestamp': started,
            'release_timestamp': parse_iso8601(live.get('scheduled_at')),
            'duration': int_or_none(ended - started) if (started and ended) else None,
            'thumbnail': (info.get('desktopThumbnailPhotoUrl')
                          or info.get('thumbnailPhotoUrl')),
            'uploader': traverse_obj(preloads, ('activeLiveStream', 'user', 'name', {str})),
            'uploader_id': traverse_obj(preloads, ('activeLiveStream', 'user', 'handle', {str})),
            'channel': traverse_obj(preloads, ('activeLiveStream', 'pub', 'name', {str})),
            'channel_id': str_or_none(traverse_obj(preloads, ('activeLiveStream', 'pub', 'id'))),
            'is_live': bool(started) and not ended,
            'was_live': bool(ended),
        }

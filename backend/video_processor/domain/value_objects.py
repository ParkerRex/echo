"""
Value objects for the video processing domain.

Value objects are immutable objects that represent domain concepts
without identity. They are compared by their attributes rather than
by identity.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class VideoResolution:
    """
    Video resolution as width and height in pixels.

    This is a frozen (immutable) dataclass representing the resolution
    of a video, which can be compared for equality with other resolutions.
    """

    width: int
    height: int

    def __str__(self) -> str:
        """Return string representation as 'WIDTHxHEIGHT'."""
        return f"{self.width}x{self.height}"

    @classmethod
    def from_string(cls, resolution_str: str) -> "VideoResolution":
        """
        Create resolution from string format 'WIDTHxHEIGHT'.

        Args:
            resolution_str: String in format '1920x1080' or similar

        Returns:
            VideoResolution object

        Raises:
            ValueError: If the string cannot be parsed
        """
        try:
            width, height = resolution_str.lower().split("x")
            return cls(width=int(width), height=int(height))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid resolution format: {resolution_str}")

    @property
    def aspect_ratio(self) -> float:
        """Calculate the aspect ratio (width / height)."""
        if self.height == 0:
            return 0
        return self.width / self.height

    @property
    def is_hd(self) -> bool:
        """Check if resolution is HD (720p or higher)."""
        return self.height >= 720

    @property
    def is_4k(self) -> bool:
        """Check if resolution is 4K (2160p or higher)."""
        return self.height >= 2160


@dataclass(frozen=True)
class VideoFormat:
    """
    Video format with name and codec information.

    This is a frozen (immutable) dataclass representing the format
    of a video, including the container format and codec.
    """

    name: str  # Container format (mp4, mov, avi, etc.)
    codec: Optional[str] = None  # Video codec (h264, vp9, etc.)
    audio_codec: Optional[str] = None  # Audio codec (aac, mp3, etc.)

    def __str__(self) -> str:
        """Return string representation with format and codec if available."""
        if self.codec:
            return f"{self.name} ({self.codec})"
        return self.name

    @property
    def is_web_compatible(self) -> bool:
        """Check if the format is web-compatible (suitable for browsers)."""
        web_formats = {
            "mp4": ["h264", "h265"],
            "webm": ["vp8", "vp9", "av1"],
            "ogg": ["theora"],
        }

        if self.name not in web_formats:
            return False

        if self.codec is None:
            return self.name in web_formats

        return self.codec in web_formats.get(self.name, [])


@dataclass(frozen=True)
class TimestampedText:
    """
    Text with start and end timestamps.

    This is a frozen (immutable) dataclass representing text with
    associated start and end times, useful for subtitles, chapters, etc.
    """

    text: str
    start_time: float  # Timestamp in seconds
    end_time: float  # Timestamp in seconds

    def __post_init__(self):
        """Validate that end_time is not before start_time."""
        if self.end_time < self.start_time:
            raise ValueError(
                f"End time ({self.end_time}) cannot be before start time ({self.start_time})"
            )

    @property
    def duration(self) -> float:
        """Calculate the duration in seconds."""
        return self.end_time - self.start_time

    def format_timestamps(self, format_type: str = "srt") -> str:
        """
        Format timestamps according to the specified format.

        Args:
            format_type: Format type ('srt', 'vtt', or 'plain')

        Returns:
            Formatted timestamp string
        """
        if format_type == "srt":
            return f"{self._format_srt_time(self.start_time)} --> {self._format_srt_time(self.end_time)}"
        elif format_type == "vtt":
            return f"{self._format_vtt_time(self.start_time)} --> {self._format_vtt_time(self.end_time)}"
        elif format_type == "plain":
            return f"{int(self.start_time)}s - {int(self.end_time)}s"
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{int(seconds % 1 * 1000):03d}"

    @staticmethod
    def _format_vtt_time(seconds: float) -> str:
        """Format time in WebVTT format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{int(seconds % 1 * 1000):03d}"


@dataclass(frozen=True)
class Chapter(TimestampedText):
    """
    Video chapter with title and timestamps.

    This is a frozen (immutable) dataclass representing a chapter in a video,
    inheriting from TimestampedText with the text field used as the chapter title.
    """

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage and serialization."""
        return {
            "title": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Chapter":
        """Create from dictionary."""
        return cls(
            text=data["title"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )


@dataclass(frozen=True)
class Subtitle(TimestampedText):
    """
    Video subtitle with text and timestamps.

    This is a frozen (immutable) dataclass representing a subtitle in a video,
    inheriting from TimestampedText.
    """

    index: int = 0  # Subtitle index for SRT format

    def to_srt(self) -> str:
        """Format subtitle as SRT format entry."""
        return f"{self.index}\n{self.format_timestamps('srt')}\n{self.text}\n"

    def to_vtt(self) -> str:
        """Format subtitle as WebVTT format entry."""
        return f"{self.format_timestamps('vtt')}\n{self.text}\n"

    @classmethod
    def from_dict(cls, data: Dict) -> "Subtitle":
        """Create from dictionary."""
        return cls(
            text=data["text"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            index=data.get("index", 0),
        )


@dataclass(frozen=True)
class SubtitleCollection:
    """
    Collection of subtitles for a video.

    This is a frozen (immutable) dataclass representing all subtitles for a video.
    It provides methods to export to different subtitle formats.
    """

    subtitles: List[Subtitle]
    language: str = "en"

    def to_srt(self) -> str:
        """Convert subtitles to SRT format."""
        # Ensure subtitles are sorted by start time
        sorted_subs = sorted(self.subtitles, key=lambda s: s.start_time)

        # Assign sequential indices
        indexed_subs = [
            Subtitle(s.text, s.start_time, s.end_time, i + 1)
            for i, s in enumerate(sorted_subs)
        ]

        return "\n".join(sub.to_srt() for sub in indexed_subs)

    def to_vtt(self) -> str:
        """Convert subtitles to WebVTT format."""
        # Ensure subtitles are sorted by start time
        sorted_subs = sorted(self.subtitles, key=lambda s: s.start_time)

        # Build VTT file
        header = f"WEBVTT\nKind: subtitles\nLanguage: {self.language}\n"
        body = "\n".join(sub.to_vtt() for sub in sorted_subs)

        return f"{header}\n{body}"

"""Picture widget for GeekMagic displays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Widget, WidgetConfig
from .camera import CameraImage, _camera_placeholder
from .components import THEME_TEXT_PRIMARY

if TYPE_CHECKING:
    from ..render_context import RenderContext
    from .components import Component
    from .state import WidgetState


class PictureWidget(Widget):
    """Widget that displays images with optional cycling.

    Supports up to 32 sources per mode:
    - ``entity_ids``: HA image.* / camera.* entity IDs
    - ``media_source_items``: individual media-source:// URIs
    - ``media_source_folder``: a single media-source:// folder URI whose
      contents are auto-discovered and cycled through

    The coordinator combines all configured sources and advances through them
    on each update cycle so each image is shown in turn.
    """

    def __init__(self, config: WidgetConfig) -> None:
        super().__init__(config)
        raw: list[str] = config.options.get("entity_ids", [])
        self.entity_ids: list[str] = [e for e in raw if e]

        raw_ms: list[str] = config.options.get("media_source_items", [])
        self.media_source_items: list[str] = [m for m in raw_ms if m]

        self.media_source_folder: str | None = config.options.get("media_source_folder") or None

        self.fit: str = config.options.get("fit", "contain")
        self.show_label: bool = config.options.get("show_label", False)

    def get_entities(self) -> list[str]:
        """Return HA entity IDs so HA state tracking works."""
        return list(self.entity_ids)

    def render(self, ctx: RenderContext, state: WidgetState) -> Component:
        """Render the picture widget."""
        if state.image is None:
            return _camera_placeholder(label=self.config.label or "No Image")

        label = None
        if self.show_label:
            label = self.config.label
            if not label and state.entity:
                label = state.entity.friendly_name
            label = label or "Image"

        img = state.image
        return CameraImage(
            image=img.convert("RGB") if img.mode != "RGB" else img,
            label=label,
            color=self.config.color or THEME_TEXT_PRIMARY,
            fit=self.fit,
        )

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

    Supports up to 32 sources which are cycled on each update:
    - ``entity_ids``: HA image.* / camera.* entity IDs
    - ``image_paths``: image URLs or media-source:// paths (as used in the
      HA Picture Card image path selector)

    All configured sources are combined and cycled through in order.
    """

    def __init__(self, config: WidgetConfig) -> None:
        super().__init__(config)
        raw: list = config.options.get("entity_ids", [])
        self.entity_ids: list[str] = [e for e in raw if isinstance(e, str) and e]

        raw_paths: list = config.options.get("image_paths", [])
        self.image_paths: list[str] = []
        for p in raw_paths:
            if isinstance(p, str) and p:
                self.image_paths.append(p)
            elif isinstance(p, dict):
                # Older configs may have stored the ha-selector[media] return value
                # ({url, entity}) directly instead of extracting the URL string.
                url = str(p.get("url") or p.get("media_content_id") or "")
                if url:
                    self.image_paths.append(url)

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

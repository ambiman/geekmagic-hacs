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
    """Widget that displays HA image entities with optional cycling.

    Supports 1-32 image entities. When multiple entities are configured the
    coordinator advances through them on each update cycle so each image is
    shown in turn.
    """

    def __init__(self, config: WidgetConfig) -> None:
        super().__init__(config)
        raw: list[str] = config.options.get("entity_ids", [])
        # Filter out blank entries that the UI may produce while editing
        self.entity_ids: list[str] = [e for e in raw if e]
        self.fit: str = config.options.get("fit", "contain")
        self.show_label: bool = config.options.get("show_label", False)

    def get_entities(self) -> list[str]:
        """Return all configured entity IDs so HA state tracking works."""
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

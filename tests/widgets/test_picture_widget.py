"""Tests for the PictureWidget."""

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from PIL import Image

from custom_components.geekmagic.render_context import RenderContext
from custom_components.geekmagic.renderer import Renderer
from custom_components.geekmagic.widgets.base import WidgetConfig
from custom_components.geekmagic.widgets.camera import CameraImage
from custom_components.geekmagic.widgets.picture import PictureWidget
from custom_components.geekmagic.widgets.state import EntityState, WidgetState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(entity_ids: list[str], **options) -> WidgetConfig:
    return WidgetConfig(
        widget_type="picture",
        slot=0,
        options={"entity_ids": entity_ids, **options},
    )


def _make_state(image: Image.Image | None = None, entity_id: str | None = None) -> WidgetState:
    entity = None
    if entity_id:
        entity = EntityState(
            entity_id=entity_id,
            state="ok",
            attributes={"friendly_name": "My Photo"},
        )
    return WidgetState(
        entity=entity,
        entities={},
        history=[],
        forecast=[],
        image=image,
        now=datetime.now(tz=UTC),
    )


def _solid_image(
    color: tuple[int, int, int] = (255, 0, 0), size: tuple[int, int] = (50, 50)
) -> Image.Image:
    return Image.new("RGB", size, color)


@pytest.fixture
def renderer():
    return Renderer()


@pytest.fixture
def render_context(renderer):
    _img, draw = renderer.create_canvas()
    rect = (0, 0, 120, 120)
    return RenderContext(draw, rect, renderer)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class TestPictureWidgetConfig:
    def test_entity_ids_loaded_from_options(self):
        w = PictureWidget(_make_config(["image.photo1", "image.photo2"]))
        assert w.entity_ids == ["image.photo1", "image.photo2"]

    def test_blank_entity_ids_filtered_out(self):
        w = PictureWidget(_make_config(["image.photo1", "", "image.photo2"]))
        assert w.entity_ids == ["image.photo1", "image.photo2"]

    def test_empty_entity_ids(self):
        w = PictureWidget(_make_config([]))
        assert w.entity_ids == []

    def test_default_fit_is_contain(self):
        w = PictureWidget(_make_config(["image.photo1"]))
        assert w.fit == "contain"

    def test_custom_fit(self):
        w = PictureWidget(_make_config(["image.photo1"], fit="cover"))
        assert w.fit == "cover"

    def test_default_show_label_is_false(self):
        w = PictureWidget(_make_config(["image.photo1"]))
        assert w.show_label is False

    def test_show_label_option(self):
        w = PictureWidget(_make_config(["image.photo1"], show_label=True))
        assert w.show_label is True

    def test_max_32_entities(self):
        ids = [f"image.photo{i}" for i in range(32)]
        w = PictureWidget(_make_config(ids))
        assert len(w.entity_ids) == 32


# ---------------------------------------------------------------------------
# get_entities
# ---------------------------------------------------------------------------


class TestGetEntities:
    def test_returns_all_entity_ids(self):
        w = PictureWidget(_make_config(["image.a", "image.b", "image.c"]))
        assert w.get_entities() == ["image.a", "image.b", "image.c"]

    def test_returns_empty_list_when_no_entities(self):
        w = PictureWidget(_make_config([]))
        assert w.get_entities() == []

    def test_single_entity(self):
        w = PictureWidget(_make_config(["image.only"]))
        assert w.get_entities() == ["image.only"]


# ---------------------------------------------------------------------------
# Rendering — no image
# ---------------------------------------------------------------------------


class TestPictureWidgetNoImage:
    def test_placeholder_when_no_image(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        component = w.render(render_context, _make_state(image=None))
        # Should NOT be a CameraImage — it should be the placeholder Column
        assert not isinstance(component, CameraImage)

    def test_placeholder_when_no_entities(self, render_context):
        w = PictureWidget(_make_config([]))
        component = w.render(render_context, _make_state(image=None))
        assert not isinstance(component, CameraImage)

    def test_placeholder_renders_without_error(self, renderer, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        component = w.render(render_context, _make_state(image=None))
        # Component must be renderable
        component.render(render_context, 0, 0, render_context.width, render_context.height)


# ---------------------------------------------------------------------------
# Rendering — with image
# ---------------------------------------------------------------------------


class TestPictureWidgetWithImage:
    def test_returns_camera_image_when_image_provided(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        img = _solid_image()
        component = w.render(render_context, _make_state(image=img))
        assert isinstance(component, CameraImage)

    def test_fit_contain_propagated(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"], fit="contain"))
        component = w.render(render_context, _make_state(image=_solid_image()))
        assert isinstance(component, CameraImage)
        assert component.fit == "contain"

    def test_fit_cover_propagated(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"], fit="cover"))
        component = w.render(render_context, _make_state(image=_solid_image()))
        assert isinstance(component, CameraImage)
        assert component.fit == "cover"

    def test_no_label_by_default(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        component = w.render(render_context, _make_state(image=_solid_image()))
        assert isinstance(component, CameraImage)
        assert component.label is None

    def test_label_shown_when_show_label_true_and_config_label_set(self, render_context):
        cfg = _make_config(["image.photo1"], show_label=True)
        cfg.label = "Holiday"
        w = PictureWidget(cfg)
        component = w.render(render_context, _make_state(image=_solid_image()))
        assert isinstance(component, CameraImage)
        assert component.label == "Holiday"

    def test_label_falls_back_to_entity_friendly_name(self, render_context):
        cfg = _make_config(["image.photo1"], show_label=True)
        w = PictureWidget(cfg)
        state = _make_state(image=_solid_image(), entity_id="image.photo1")
        component = w.render(render_context, state)
        assert isinstance(component, CameraImage)
        assert component.label == "My Photo"

    def test_label_falls_back_to_image_when_no_entity(self, render_context):
        cfg = _make_config(["image.photo1"], show_label=True)
        w = PictureWidget(cfg)
        component = w.render(render_context, _make_state(image=_solid_image()))
        assert isinstance(component, CameraImage)
        assert component.label == "Image"

    def test_rgba_image_converted_to_rgb(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        rgba_img = Image.new("RGBA", (50, 50), (255, 0, 0, 128))
        component = w.render(render_context, _make_state(image=rgba_img))
        assert isinstance(component, CameraImage)
        assert component.image.mode == "RGB"

    def test_rgb_image_not_converted(self, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        rgb_img = _solid_image()
        component = w.render(render_context, _make_state(image=rgb_img))
        assert isinstance(component, CameraImage)
        assert component.image.mode == "RGB"

    def test_renders_without_error(self, renderer, render_context):
        w = PictureWidget(_make_config(["image.photo1"]))
        component = w.render(render_context, _make_state(image=_solid_image()))
        component.render(render_context, 0, 0, render_context.width, render_context.height)


# ---------------------------------------------------------------------------
# Cycle logic (coordinator side)
# ---------------------------------------------------------------------------


class TestPictureCycleIndex:
    """Verify the cycle-index arithmetic used by the coordinator."""

    def test_cycle_advances_per_update(self):
        """Simulate the coordinator advancing the cycle index each update."""
        entity_ids = ["image.a", "image.b", "image.c"]
        cycle_indices: dict[int, int] = {}

        def next_entity(slot: int) -> str:
            idx = cycle_indices.get(slot, 0) % len(entity_ids)
            cycle_indices[slot] = (idx + 1) % len(entity_ids)
            return entity_ids[idx]

        assert next_entity(0) == "image.a"
        assert next_entity(0) == "image.b"
        assert next_entity(0) == "image.c"
        assert next_entity(0) == "image.a"  # wraps around

    def test_single_entity_always_returns_same(self):
        entity_ids = ["image.only"]
        cycle_indices: dict[int, int] = {}

        def next_entity(slot: int) -> str:
            idx = cycle_indices.get(slot, 0) % len(entity_ids)
            cycle_indices[slot] = (idx + 1) % len(entity_ids)
            return entity_ids[idx]

        for _ in range(5):
            assert next_entity(0) == "image.only"

    def test_slots_are_independent(self):
        ids = ["image.x", "image.y"]
        cycle_indices: dict[int, int] = {}

        def next_entity(slot: int) -> str:
            idx = cycle_indices.get(slot, 0) % len(ids)
            cycle_indices[slot] = (idx + 1) % len(ids)
            return ids[idx]

        assert next_entity(0) == "image.x"
        assert next_entity(1) == "image.x"  # slot 1 is independent
        assert next_entity(0) == "image.y"
        assert next_entity(1) == "image.y"

    def test_32_entities_wraps_correctly(self):
        entity_ids = [f"image.photo{i}" for i in range(32)]
        cycle_indices: dict[int, int] = {}

        def next_entity(slot: int) -> str:
            idx = cycle_indices.get(slot, 0) % len(entity_ids)
            cycle_indices[slot] = (idx + 1) % len(entity_ids)
            return entity_ids[idx]

        for i in range(32):
            assert next_entity(0) == f"image.photo{i}"
        assert next_entity(0) == "image.photo0"  # wraps back to start

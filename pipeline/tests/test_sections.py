import numpy as np

from atlas_pipeline import sections


def test_label_ids_survive_the_png_packing_including_ids_above_255():
    slab = np.zeros((5, 7), np.uint16)
    slab[0, 0], slab[4, 6], slab[2, 3] = 7, 2035, 256
    rgb = sections.slice_to_png_array(slab)
    assert rgb.shape == (7, 5, 3) and rgb.dtype == np.uint8
    assert np.array_equal(sections.decode_png_array(rgb), slab)


def test_image_layout_puts_anterior_on_top_and_lateral_on_the_left():
    slab = np.zeros((4, 6), np.uint16)
    slab[0, 5] = 9  # x index 0 = most lateral, y index 5 = most anterior
    rgb = sections.slice_to_png_array(slab)
    assert rgb[0, 0, 0] == 9  # top-left pixel

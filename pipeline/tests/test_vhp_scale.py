import numpy as np

import vhp_stack_register as vsr


def small_grey(nz=12):
    # the real in-plane size (2048x1216 photos -> 682x405 voxels), a few slices
    return vsr.grey_volume(np.zeros((nz, 1216 // vsr.F, 2048 // vsr.F, 3), dtype=np.uint8))


def test_grey_spacing_is_the_block_size():
    grey = small_grey()
    assert np.allclose(grey.GetSpacing(), (vsr.F * vsr.PX, vsr.F * vsr.PX, vsr.SLICE_MM))


def test_photo_lps_round_trip():
    grey = small_grey()
    for p in ([0.0, 0.0, 0.0], [-120.3, 87.1, 4.2], [250.0, -150.5, -3.7], [12.34, 56.78, 1.0]):
        back = vsr.photo_to_lps(grey, *vsr.lps_to_photo(grey, p, exact=True))
        assert np.allclose(back, p, atol=1e-6)
    for s, x, y in ((vsr.FIRST, 0, 0), (vsr.FIRST + 5, 919, 807), (vsr.FIRST + 11, 2045, 1214)):
        assert vsr.lps_to_photo(grey, vsr.photo_to_lps(grey, s, x, y)) == (s, x, y)


def test_block_centre_pixel_lands_on_its_voxel():
    # voxel i is the mean of pixels i*F .. i*F + F-1, so its centre pixel i*F + (F-1)/2 maps to index i
    grey = small_grey()
    nx, ny, nz = grey.GetSize()
    for i, j in ((0, 0), (300, 200), (nx - 1, ny - 1)):
        p = vsr.photo_to_lps(grey, vsr.FIRST, i * vsr.F + (vsr.F - 1) / 2, j * vsr.F + (vsr.F - 1) / 2)
        ix, iy, iz = grey.TransformPhysicalPointToContinuousIndex(tuple(p))
        assert np.allclose((ix, iy, iz), (i, ny - 1 - j, nz - 1), atol=1e-6)  # y and z are flipped into LPS

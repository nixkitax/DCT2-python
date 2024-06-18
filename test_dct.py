import unittest
import numpy as np
from dct_module import dct2_manual, idct2_manual, dct2, idct2

class TestDCT(unittest.TestCase):

    def setUp(self):
        self.matrix = np.random.rand(8, 8).astype(np.float32)

    def test_dct2_manual(self):
        dct_manual = dct2_manual(self.matrix)
        self.assertEqual(dct_manual.shape, self.matrix.shape)

    def test_idct2_manual(self):
        dct_manual = dct2_manual(self.matrix)
        idct_manual = idct2_manual(dct_manual)
        np.testing.assert_almost_equal(self.matrix, idct_manual, decimal=5)

    def test_dct2(self):
        dct_lib = dct2(self.matrix)
        self.assertEqual(dct_lib.shape, self.matrix.shape)

    def test_idct2(self):
        dct_lib = dct2(self.matrix)
        idct_lib = idct2(dct_lib)
        np.testing.assert_almost_equal(self.matrix, idct_lib, decimal=5)

if __name__ == '__main__':
    unittest.main()

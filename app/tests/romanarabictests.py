import unittest

from app.extractor import decode_roman_numeral


class TestRomanArabic(unittest.TestCase):
    def test_correct_roman_to_arabic_convertion(self):
        self.assertEqual(decode_roman_numeral("ii"), 2)

    def test_correct_roman_to_arabic_convertion_with_caps(self):
        self.assertEqual(decode_roman_numeral("II"), 2)

    def test_wrong_roman_to_arabic_convertion(self):
        self.assertEqual(decode_roman_numeral("k"), 0)


if __name__ == '__main__':
    unittest.main()

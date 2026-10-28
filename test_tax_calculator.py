"""Regression checks for modeled rules and security helpers."""
import unittest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml.common import EntitiesForbidden
import tax_calculator as tax


class CalculatorTests(unittest.TestCase):
    """Check boundaries that static analysis cannot establish."""

    def test_new_tax(self):
        for salary, expected in [(0, 0), (1275000, 0), (1800000, 150800)]:
            with self.subTest(salary=salary):
                self.assertEqual(tax.new_regime_tax(salary), expected)

    def test_exemption_boundaries(self):
        for age, expected in [(59, 250000), (60, 300000),
                              (79, 300000), (80, 500000)]:
            self.assertEqual(tax.basic_exemption(age), expected)
        self.assertEqual(tax.old_regime_tax(550000, 80, {}), 0)

    def test_regime_comparison(self):
        deductions = {"80C": 200000, "80D": 30000}
        self.assertEqual(tax.old_regime_tax(1800000, 35, deductions), 279240)
        self.assertEqual(tax.better_regime(1800000, 35, deductions), "new")
        self.assertEqual(tax.better_regime(1800000, 35,
                                         {"deduction": 1700000}), "old")
        self.assertEqual(tax.better_regime(0, 35, {}), "new")

    def test_pan(self):
        self.assertTrue(tax.is_valid_pan("ABCDE1234F"))
        for value in [None, 123, "ABCDE1234FXYZ", "ABCDE1234F\n"]:
            self.assertFalse(tax.is_valid_pan(value))

    def test_encryption(self):
        key = AESGCM.generate_key(bit_length=256)
        first = bytes.fromhex(tax.encrypt_pan("ABCDE1234F", key))
        second = bytes.fromhex(tax.encrypt_pan("ABCDE1234F", key))
        self.assertNotEqual(first, second)
        self.assertEqual(AESGCM(key).decrypt(first[:12], first[12:], None),
                         b"ABCDE1234F")
        altered = first[:-1] + bytes([first[-1] ^ 1])
        with self.assertRaises(InvalidTag):
            AESGCM(key).decrypt(altered[:12], altered[12:], None)

    def test_xml_and_key(self):
        self.assertEqual(tax.parse_form16(
            "<form16><salary>1800000</salary><tds>150000</tds></form16>"),
            (1800000, 150000))
        with self.assertRaises(EntitiesForbidden):
            tax.parse_form16('<!DOCTYPE x [<!ENTITY e "123">]>'
                             '<form16><salary>&e;</salary>'
                             '<tds>0</tds></form16>')
        self.assertEqual(tax.signing_key().key_size, 2048)


if __name__ == "__main__":
    unittest.main()

"""Teaching tax calculator with validated inputs and secure PAN encryption."""

import re
import os
from defusedxml import minidom
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Slabs as configured for this program (modelled on FY 2025-26)
STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
CESS = 0.04
OLD_SLABS = [(250000, 0.0), (500000, 0.05),
             (1000000, 0.20), (float("inf"), 0.30)]

NEW_SLABS = [(400000, 0), (800000, 0.05), (1200000, 0.10),
             (1600000, 0.15), (2000000, 0.20), (2400000, 0.25),
             (float("inf"), 0.30)]


def new_regime_tax(salary):
    """Apply configured progressive slabs, inclusive rebate, then cess."""
    taxable = max(0, salary - STANDARD_DEDUCTION_NEW)
    if taxable <= REBATE_LIMIT_NEW:
        return 0
    tax_amount = 0
    lower_limit = 0
    for limit, rate in NEW_SLABS:
        tax_amount += max(0, min(taxable, limit) - lower_limit) * rate
        lower_limit = limit
    return int(tax_amount * (1 + CESS))


def basic_exemption(age):
    """Return the configured exemption for the supplied age."""
    if 60 <= age < 80:
        return 300000
    if age >= 80:
        return 500000
    return 250000


def old_regime_tax(salary, age, deductions):
    """Apply deductions, age exemption, progressive slabs and cess."""
    taxable = salary - STANDARD_DEDUCTION_OLD
    taxable = max(0, taxable - sum(deductions.values()))
    total_tax = 0
    lower_limit = basic_exemption(age)
    for limit, rate in OLD_SLABS:
        if taxable > lower_limit and rate > 0:
            total_tax = total_tax + (min(taxable, limit) - lower_limit) * rate
        lower_limit = max(lower_limit, limit)
    return int(total_tax * (1 + CESS))


def better_regime(salary, age, deductions):
    """Choose the lower tax; choose new on a tie."""
    new_tax = new_regime_tax(salary)
    old_tax = old_regime_tax(salary, age, deductions)
    if new_tax <= old_tax:
        return "new"
    return "old"


def is_valid_pan(pan):
    """Require a complete PAN pattern and a string input."""
    return isinstance(pan, str) and bool(
        re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


def encrypt_pan(pan, key):
    """Return hex nonce plus authenticated ciphertext using a caller key."""
    nonce = os.urandom(12)
    cipher_text = AESGCM(key).encrypt(nonce, pan.encode(), None)
    return (nonce + cipher_text).hex()


def signing_key():
    """Generate a 2048-bit RSA private signing key."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def parse_form16(xml_text):
    """Read salary and TDS with entity expansion blocked."""
    doc = minidom.parseString(xml_text)
    salary_text = doc.getElementsByTagName("salary")[0].firstChild.data
    tds_text = doc.getElementsByTagName("tds")[0].firstChild.data
    return int(salary_text), int(tds_text)


def main():
    """Demonstrate the teaching calculator and security helpers."""
    print("New regime, salary 12,75,000:", new_regime_tax(1275000))
    print("New regime, salary 18,00,000:", new_regime_tax(1800000))
    deductions = {"80C": 200000, "80D": 30000}
    print(
        "Old regime, salary 18,00,000:",
        old_regime_tax(
            1800000,
            35,
            deductions))
    print(f"Better regime: {better_regime(1800000, 35, deductions)}")
    print(f"Basic exemption at age 80: {basic_exemption(80)}")
    print("PAN 'ABCDE1234FXYZ' valid?", is_valid_pan("ABCDE1234FXYZ"))
    key = AESGCM.generate_key(bit_length=256)
    print(
        "Same PAN encrypts the same way twice?",
        encrypt_pan(
            "ABCDE1234F",
            key) == encrypt_pan(
            "ABCDE1234F",
            key))
    print("Form 16:", parse_form16(
        "<form16><salary>1800000</salary><tds>150000</tds></form16>"))
    print(f"Signing key size: {signing_key().key_size}")


if __name__ == "__main__":
    main()

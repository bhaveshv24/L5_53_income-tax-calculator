# Identified issues and fixes

Line numbers refer to the unchanged `before/tax_calculator.py`. Tool severity is preserved; Pylint/Flake8 categories are not security severity ratings.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Bandit B412 | High security | 6, 92 | CGIHandler exposes the legacy CGI/httpoxy attack surface. | Remove the unused CGI adapter and import. This teaching program remains a CLI; a web deployment would need a maintained server adapter. |
| Bandit B305 | Medium security | 77 | ECB reveals repeated plaintext patterns and lacks authentication. | Use AES-GCM with a fresh 12-byte random nonce, returning nonce plus authenticated ciphertext in hex. |
| Bandit B505 | Medium security | 83 | A 1024-bit RSA key is too weak. | Generate 2048-bit keys. |
| Bandit B318 | Medium security | 86 | Untrusted XML parser can process malicious entity definitions. | Use defusedxml.minidom and verify entity expansion is rejected. |
| Bandit B408 | Low security | 5 | Insecure standard-library XML parser import. | Replace with defusedxml. |
| Pylint W0702 / Flake8 E722 | Exception handling | 71-74 | Bare except hides unrelated failures. | Check input type explicitly and remove the broad exception. |
| Pylint W0612 / Flake8 F841 | Quality | 36 | bracket and checked are unused. | Remove both while rewriting progressive tax calculation. |
| Pylint W0611 / Flake8 F401 | Quality | 2-4 | Unused imports obscure dependencies. | Remove sys/json; os is now used for secure nonces. |
| Pylint W0613 | Quality | 85, 91 | strict/debug arguments have no effect. | Remove strict and the unused CGI helper. |
| Pylint C0103, C0114, C0116 | Maintainability | Throughout | Camel-case names and missing documentation. | Use snake_case and add module/function docstrings. |
| Pylint R1705, R0911, R1716 | Simplification | 18-32, 44 | Repetitive slab branching and verbose comparison. | Replace slab lookup with progressive table traversal; use chained age comparison. |
| Flake8 E302, E305, E501, E702 / Pylint C0301, C0321 | Style | Throughout; 36, 102-103 | Missing blank lines, overlong lines, semicolon statements. | Apply PEP 8 spacing and wrap expressions; remove compound statement. |
| Pylint C0209 | Style | 99-100, 104 | Old-style string formatting. | Use f-strings. |
| Manual review | Security design | 15, 76-80 | Embedded key and deterministic encryption. | Require a caller-supplied key; generate a temporary demo key, with no embedded production secret. |
| Manual review | Calculation | 35-41 | Whole income taxed at a single rate; rebate excludes boundary and cess survives rebate. | Apply progressive configured slabs, inclusive rebate, then cess. Clamp taxable income at zero. |
| Manual review | Boundary bug | 46 | Age exactly 80 gets the lowest exemption. | Use age >= 80 and test 59/60/79/80. |
| Manual review | Logic | 66 | Recommendation selects the more expensive regime. | Select the smaller tax; choose new on a tie. |
| Manual review | Validation | 72 | PAN prefix accepted with trailing characters. | Require re.fullmatch and reject nonstrings. |
| Manual review | Import side effect | 106 | Importing executes the demonstration. | Add a main guard. |

## Verified results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.57/10 | 10.00/10 |
| Bandit | 6 findings: 2 high, 3 medium, 1 low | 0 findings |
| Flake8 | See complete original report | 0 violations (empty report is expected) |

All three final tool exit codes are 0. No findings were suppressed. Six regression tests pass. Extra calculation fixes implement the repository's configured teaching rules; this does not add a complete statutory tax model, marginal relief, deduction caps, surcharge, or old-regime rebates. Renamed helpers, the explicit encryption key, and removal of the CGI wrapper change the original helper API intentionally.

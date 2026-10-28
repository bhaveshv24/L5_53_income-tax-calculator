# Reflections

The repository asks for four reflection answers, but the supplied handout does not contain the question text. The following four topic-based reflections address the stated learning outcomes and are not presented as verbatim handout questions.

## 1. What did each analysis tool contribute?

Pylint identified maintainability problems, unused values, broad exception handling and naming/documentation issues. Flake8 highlighted layout, whitespace, long lines, unused imports and the bare except. Bandit identified six security findings involving CGIHandler, ECB encryption, weak RSA and unsafe XML. Their overlap was useful, but each tool examined different aspects of the same script.

## 2. How were the findings prioritized and addressed?

The high-severity CGI findings came first, followed by medium-severity ECB, RSA and XML findings. I removed the unused CGI path, used authenticated AES-GCM with random nonces and a supplied key, increased RSA to 2048 bits, and replaced the XML parser with defusedxml. Then I resolved quality and style findings. Baseline reports were preserved so the final reports can be compared with the exact original file.

## 3. What did static analysis miss, and how were fixes verified?

The tools did not establish that the tax calculation or recommendation was correct. Manual review found a flat-rate calculation instead of progressive slabs, a rebate boundary/cess bug, the age-80 boundary, an inverted regime recommendation and partial PAN matching. Regression tests check those cases, encryption round trips and tamper detection, XML entity rejection, and RSA key size. The final Pylint score is 10.00/10; Bandit and Flake8 both report no findings. A clean scan does not prove complete correctness or security.

## 4. How would this change future development?

I would run all three tools early and in continuous integration, review security findings before cosmetic changes, and combine scans with focused behavior tests and code review. Clear names, docstrings and smaller responsibilities make later changes easier to assess. Secrets should come from caller-controlled storage rather than source code. For a real tax product, I would also validate legal rules and unsupported inputs separately; this lab deliberately retains a simplified teaching model.

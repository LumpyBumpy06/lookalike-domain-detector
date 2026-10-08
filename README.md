# lookalike-domain-detector

A small Python tool for finding domains that look like they are impersonating protected brands.

It currently uses three string-based detectors:

* `typosquat`
* `brand_token`
* `suffix_swap`

The tool only does string analysis. It does not check DNS, WHOIS, certificates, registration dates or page content. The expectation is that domains are collected elsewhere and passed into this tool.

## Detectors

| Detector      | Fires when                                                                                                                              | Example (`paypal.com`)                                                                    |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `typosquat`   | A candidate label is exactly one Damerau-Levenshtein edit from the brand label. The registrable label and subdomain labels are checked. | `paypa1.com`, `paypall.com`, `paypa.com`, `paypa1.evil.com`                               |
| `brand_token` | The brand label appears as a whole hyphen-delimited token in the registrable label or in a subdomain label.                             | `paypal-login.com`, `secure-paypal-login.com`, `paypal.evil.com`, `login-paypal.evil.com` |
| `suffix_swap` | The registrable label matches the brand label but the suffix is different.                                                              | `paypal.net`, `paypal.co.uk`, `paypal.xyz`                                                |

A candidate/brand pair can trigger more than one detector.

A candidate in the same registrable domain as the brand is not reported. For example, `login.paypal.com` is treated as part of `paypal.com`.

## Install and run

Requires Python 3.10+. There are no runtime dependencies.

```bash
make install
```

Run the CLI with:

```bash
lookalike --brands brands.txt --candidates candidates.txt
```

or:

```bash
python -m lookalike --brands brands.txt --candidates candidates.txt --format json
```

### Input

Input files are UTF-8, one domain per line.

Blank lines and whole-line `#` comments are ignored. Input is lower-cased, a trailing dot is removed, and duplicates are removed while keeping the first occurrence.

Anything that is not a valid supported ASCII hostname is skipped and counted.

For example:

```text
# brands.txt
paypal.com
bbc.co.uk
```

The tool expects hostnames rather than URLs or other DNS-related forms. The following are rejected:

```text
https://example.com
example.com:443
*.example.com
_dmarc.example.com
example.com # note
```

Output is sorted by candidate and then brand, so repeated runs are deterministic.

```text
$ lookalike --brands brands.txt --candidates candidates.txt

paypa1.com -> paypal.com [typosquat]
paypal-login.com -> paypal.com [brand_token]
paypal.evil.com -> paypal.com [brand_token]
login-paypal.evil.com -> paypal.com [brand_token]
paypa1.evil.com -> paypal.com [typosquat]
paypal.com.evil.com -> paypal.com [brand_token]
paypal.net -> paypal.com [suffix_swap]
```

`--format json` emits a single JSON array:

```json
[
  {
    "candidate": "paypa1.com",
    "brand": "paypal.com",
    "detectors": ["typosquat"]
  }
]
```

Diagnostics are written to stderr using `logging`, including the number of skipped input lines.

Exit codes:

* `0` on success, whether or not anything was found
* `2` for usage errors, unreadable files, or an empty brands file

## Repository layout

```text
src/lookalike/

  domain.py          domain parsing
  inputs.py          input parsing, de-duplication and skipped-line accounting
  detection.py       Detection / Finding result types
  pipeline.py        detector pipeline
  cli.py             command-line interface
  __main__.py

  detectors/
    detector.py      Detector Protocol
    typo_squat.py    TyposquatDetector and edit-distance implementation
    brand_token.py   BrandTokenDetector
    suffix_swap.py   SuffixSwapDetector
    factory.py       default detector set
```

Adding another detector means implementing the `Detector` protocol and registering it in `factory.py`.

The package includes a `py.typed` marker and is checked with `mypy --strict`.

## Design decisions

### Keep the core dependency-free

The project has no runtime dependencies. This keeps it easy to run and keeps the implementation relatively small.

The main trade-off is that some data, such as the public suffix list, has to be handled directly in the project.

### No risk scoring

The tool currently only reports which detectors matched rather than assigning a risk/confidence score.

This is deliberate: a domain-name match alone is not enough to determine whether a domain is malicious. For example, `paypal.de` may be a legitimate domain owned by the brand rather than an impersonation attempt.

## Development

Run:

```bash
make check
```

This runs formatting checks, linting, mypy and pytest.

To apply formatting and safe lint fixes:

```bash
make fmt
```

The test suite requires at least 90% branch coverage.

CI runs `make check` on Python 3.10.

## Limitations

### Parsing and input

**Skipped lines reporting.**

Skipped lines are counted, but the individual skipped lines are not currently reported.

**ASCII hostnames only.**

Domain labels must match `[a-z0-9-]`.

Unicode lookalikes are therefore rejected. For example:

```text
pаypal.com
```

where the `а` is Cyrillic rather than Latin, is treated as unsupported input.

Punycode labels such as:

```text
xn--pypal-4ve.com
```

are accepted as ordinary ASCII labels, but are not decoded.

Proper IDNA decoding and Unicode confusable analysis are not implemented.

**Public-suffix handling is incomplete.**

The parser currently recognises these multi-part suffixes:

```text
co.uk
org.uk
ac.uk
com.au
net.au
org.au
co.jp
```

Everything else is treated as a single suffix.

As a result, domains such as:

```text
paypal.com.br
paypal.co.nz
paypal.gov.uk
```

may be parsed incorrectly.

For example, `paypal.com.br` is currently treated as label `com` with suffix `br`, so `paypa1.com.br` will not be detected as a lookalike of `paypal.com`.

The long term fix is to use a maintained Public Suffix List.

**No TLD validation.**

Any syntactically valid final label is accepted as a suffix. IP-like input such as `192.168.1.1` can therefore be parsed as a hostname.

### Detection coverage

**`brand_token` does not handle concatenated forms.**

It looks for the brand label as a separate hyphen-delimited token.

These are detected:

```text
paypal-login.com
secure-paypal-login.com
paypal.evil.com
login-paypal.evil.com
paypal-secure-login.evil.com
```

but these are not:

```text
paypallogin.com
securepaypal.com
```

**`typosquat` only looks for one edit.**

The detector uses Damerau-Levenshtein distance and reports labels that are exactly one edit away from the brand label.

This catches:

```text
paypa1.com
paypall.com
paypa.com
paypa1.evil.com
```

but misses cases requiring two edits, such as:

```text
rnicrosoft.com
vvikipedia.com
g00gle.com
faceb00k.com
```

Keyboard adjacency, vowel substitutions and other specialised typo patterns are not modelled separately.

### Precision

The default `minimum_label_length` is 4, so brands shorter than four characters are ignored by the typosquat detector. This reduces some noise from very short labels, but is a simple heuristic rather than one based on measured false-positive rates.

Suffix swaps can also be legitimate. For example, `paypal.de` could simply be another domain owned by the brand. There is currently no allowlist for known legitimate domains.

### Output and evidence

A `Detection` currently stores only the detector name.

For example:

```text
paypal-login.com -> paypal.com [brand_token]
```

shows which rule fired, but not the matched token, edit, position or subdomain label.

There is also no ranking or confidence score.

Output is collected and sorted before it is printed, so the CLI is not streaming.

## Future work

### Scaling

* Index brands by label and suffix rather than comparing every candidate with every brand.
* Group typosquat comparisons by label length.
* Stream candidate input instead of keeping everything in memory.
* Concurrently process candidates

The current `Detector` interface is intentionally simple, so indexing would likely require a separate indexing/preparation layer or a change to the detector interface.

### Detection quality

* Replace the hand-maintained suffix list with a maintained Public Suffix List.
* Add IDNA and Unicode confusable handling.
* Add keyboard-based, multi-edit and concatenated-form detectors.

### Precision and evaluation

* Add per-brand allowlists for known legitimate domains.
* Evaluate detector precision and recall against a labelled set of benign and malicious domains.
* Use the results to tune heuristics such as `minimum_label_length`.
* Add richer evidence to findings i.e. for typosquat which character/s and where.
* Add property-based tests and fuzzing around domain parsing.

## Status

This is a first version of the detector rather than a complete phishing classifier.

The focus is on keeping the code small, testable and easy to extend, while being clear about what the current rules can and cannot detect.

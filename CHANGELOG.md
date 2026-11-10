# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/NNPDF/pineko/compare/v0.5.1...HEAD)

### Fixed
- For `Q0 < mc` with intrinsic charm, FK tables are now optimized with `Nf4Ind` instead of `Nf4Sym`, so they keep the V15 (c-) channel. ([#259](https://github.com/NNPDF/pineko/pull/259))

### Changed
- Drop Python 3.10 and add Python 3.14 ([#257](https://github.com/NNPDF/pineko/pull/257))

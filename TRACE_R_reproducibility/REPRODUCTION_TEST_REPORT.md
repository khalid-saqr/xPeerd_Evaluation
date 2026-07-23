# Reproduction test report

**Overall status:** PASS with the live Zenodo network path not executed in the build sandbox.

- Full Python test suite: 5 passed in 32.34 seconds.
- CLI end-to-end reproduction: PASS; 22/22 analytical quality gates and 10/10 figure files.
- CLI comparison against archived reference tables: 29/29 checks passed.
- Public notebook end-to-end execution: PASS in 33.11 seconds.
- Notebook comparison against archived reference tables: 29/29 checks passed.
- Notebook contract: exactly 10 processing cells and 5 figure cells.
- Source label contract: `xPeerd`; no deprecated `xPeerD` spelling in notebook source.
- Live Zenodo download: not executable from the build sandbox because outbound DNS was unavailable. The public acquisition path uses the Zenodo Records API plus two direct-download fallbacks and rejects any file that does not match both the pinned SHA-256 and MD5.

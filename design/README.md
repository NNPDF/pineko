# Preamble

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
[[RFC 2119]](https://tools.ietf.org/html/rfc2119).

## Used Abbreviations

TBD = to be determined

# Code specification

## Motivation

Replace the current APFELcomb code with a simpler and faster tool to generate FK
Tables for NNPDF fits.

## APFELcomb design and issues (Current status)

### Workflow

The apfelcomb project compiles a program which connects several tools and
databases from NNPDF and external providers in order to generate FK Tables,
where observables are stored into tables with a predefined input scale energy
value for PDFs evaluation.

The user/develop should include the custom implementation of the combination
operation for each specific process category. All operations involving DGLAP,
DIS and Fixed-target DY are performed at runtime. Operations involving the
generation of hadronic observables with or without electroweak corrections are
performed off-line and stored on git-lfs repositories.

The mapping between the requested FK table configuration, in terms of theory and
dataset choice, are controlled by the NNPDF theory sqlite database and by a
custom sqlite database build inside apfelcomb.

### Inputs

The apfelcomb program takes as input the:

- the theory database from NNPDF,
- a custom database with specifications for each dataset in NNPDF,
- CommonData files from NNPDF/buildmaster,
- APPLgrid grids,
- PineAPPL grids.

### External tools

The current apfelcomb implementation relies on third-party tools for:

- DGLAP evolution kernels (APFEL),
- DIS observables (APFEL),
- Fixed-target DY (APFEL)
- APPLgrids for hadronic processes (APPLgrid),
- PineAPPL grids for processes with EW corrections (PineAPPL).

### Problems to be avoided

Here a short summary of practical problems we would like to avoid:

- avoid different data input format, today we have to maintain parsers for APFEL
  (DIS/FTDY), APPLgrid and PineAPPL,
- avoid long runtime operations _Proposed Solution_: use caching and store the
  elements in a server a priori, e.g.: DGLAP evolution kernels, DIS and FTDY
  grids,
- reduce to minimum data input processing,

## Proposal

We propose to develop a code which performs the combination and provide tools to
prepare, store and update its requirements.

### Desired Features

- delegate the FK Table construction to a single code/function,
- provide tools to cache results and upload to server
- provide tools to optimize the quality of FK tables

### Input

The program should take as input:

1. the theory number identification number, using the NNPDF theory database.
   Note that in opposite to apfelcomb we should take the number and not the full
   sqlite string.
2. the dataset name following the NNPDF convention.

### Procedure

1. Retrieve the EKO
   1. Input: generate runcards
   2. depends on 1.1: Download: we compute the md5sum or whatever other
      algorithm on the runcard file and check for a corresponding file in the
      server, if it doesn't exit.
   3. depends on 1.1, fires if 1.2 fails: Create: invoke eko with the
      configuration from (1.1) and let it compute the operator
   4. depends on 1.3: Upload: uploads the operator from (1.3) (takes the md5sum
      of the runcard)
2. Retrieve PineAPPL grid
   1. **TBD** define an analog of 1.
3. Operator Application
   1. do the matrix multiplication
4. Delivery
   1. store the generated FKTables in the NNPDF repository
5. Quality Control
   1. the PineAPPL predictions
   2. the predictions using EKO with a reduced number of grid points (measures
      the compression penalty)
   3. the prediction of the FK table (measures the effect of the down-evolution)

### Requirements for external programs

#### eko

- the output MUST be provided in a self-contained format, i.e. the python
  library `eko` SHOULD NOT be required
- the current program design fulfills this specification

The current proposal for the `eko` output format is the following:

- for each pair of `(Q2_0, Q2)` there will be a rank 4 tensor `(fout, xout, fin, xin)`, saved in _numpy_
  binary format
  - it is possible to include binary in a `yaml` or to make an explicit
    `npy/npz` file instead
- since `numpy` it's loosing the information on the `dtype` and `shape` on save
  it should be shipped together in a metadata file
- since `eko` it's able to produce operators for multiple `Q2` at the same time
  it is possible to collect them in a single compressed archive

### Precomputed objects

In order to speed up the computations the code should provide an efficient
caching algorithm.

In especially the two main ingredients should be covered:

- EKO evolution kernels for NNPDF theories.
- PineAPPL grids predictions for all datasets in NNPDF

The caching will be managed by a NNPDF repository that can be interfaced via a
public server.

#### Server

The server is good because:

- easy & fast access
- public
- already implemented with backups

The server purpose is to storage any precomputed object that may be useful for
future usage.
The content will be publicly available for download through an API, while the
upload of generated objects will happen through authentication (reserved to
NNPDF members).

#### Git Repo

The repo is good because:

- we can check the revision if bugs are found
- is an extra source of backup

Since some of the objects requires some _handcrafting_ (in particular the
hadronic predictions obtained by Monte Carlo generators) it is useful to keep
them versioned, in order to track the process and help revision.
The _released_ version of this repo (i.e. _master_ branch) should be kept
automatically synced with the server, e.g. by a dedicated GitHub workflow.

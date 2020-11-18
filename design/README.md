# Code specification

## Motivation

Replace the current APFELcomb code with a simpler and faster tool to generate FK Tables for NNPDF fits.

## APFELcomb design and issues

### Workflow

The apfelcomb project compiles a program which connects several tools and
databases from NNPDF and external providers in order to generate FK Tables,
where observables are stored into tables with a predefined input scale energy value for PDFs evaluation.

The user/develop should include the custom implementation of the combination operation for each specific process category. All operations involving DGLAP, DIS and Fixed-target DY are performed at runtime. Operations involving the generation of hadronic observables with or without electroweak corrections are performed off-line and stored on git-lfs repositories.

The mapping between the requested FK table configuration, in terms of theory and dataset choice, are controlled by the NNPDF theory sqlite database and by a custom sqlite database build inside apfelcomb.

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
- avoid different data input format, today we have to maintain parsers for APFEL (DIS/FTDY), APPLgrid and PineAPPL,
- avoid long runtime operations that can be cached and stored in a server a priori, e.g.: DGLAP evolution kernels, DIS and FTDY grids,
- reduce to minimum data input processing,
- delegate the FK Table construction to a single code/function,
- provide tools to cache results and upload to server
- provide tools to optimize the quality of FK tables.

## Proposal

We propose to develop a code which performs the combination and provide tools to prepare, store and update its requirements.

### Input

The program should take as input:
1. the theory number identification number, using the NNPDF theory database. Note that in opposite to apfelcomb we should take the number and not the full sqlite string.
2. the dataset name following the NNPDF convention.

### Precomputed objects

The software suite should provide tools for the preparation of:
- EKO evolution kernels for NNPDF theories.
- PineAPPL grids predictions for all datasets in NNPDF.

Both objects must be stored in a NNPDF repository (server).

### Procedure

Starting from the previous two input values the algorithm should:
- download the precomputed EKO evolution kernel for the specific theory identification number from the NNPDF repositories. Preferably store the kernels in a format which does not require EKO at all.
- download the corresponding PineAPPL grid from the NNPDF repository.
- perform the combination and write the FK Table to disk
- store the generated FKTables in the NNPDF repository.



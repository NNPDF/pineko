# pineko

`pineko` combines coefficient function grids ("grids" for short) produced by [`runcards`](https://github.com/NNPDF/runcards)
in the form of [`PineAPPL` grids](https://github.com/N3PDF/pineappl)
and Evolution Kernel Operators by [`eko`](https://github.com/N3PDF/eko)
into FK tables. It is one part of the [`APFELcomb`](https://github.com/NNPDF/apfelcomb) replacement.

## Prerequisites

Since combines several ingredients into a new object one needs to provide a bunch of files first.

### pineko.toml

You need to provide a `pineko.toml`, that provides all necessary paths to the respective tools and output folders.
[DEBUG: Look at the debug example in this repo [1]].

### ymldb

You need all files of the `ymldb` [2].  [DEBUG: Look at the respective `load.sh` script to load from dom.]
This defines the mapping from datasets to FK tables.

### Theory Runcards

You need to provide the necessary theory runcards named with their respective theory ID inside the `theory_cards` paths [3].

### Default Operator Card

You need to provide a default operator card for `eko` [4].
[DEBUG: Look at the respective `load.sh` script to load from dom.]

### Coefficient Functions Grids

`pineko` is **NOT** computing grids, but is taking them as an input.
There are typically two ways to obtain grids: computing them from scratch with [`runcards`](https://github.com/NNPDF/runcards)
or reusing existing ones.

#### Generate new Grids with `rr`

You need to run `rr` with a given theory runcard and put the generated grid file with the same name
inside the `<paths.grids>/<theory_id>` folder. The name has to match the `ymldb` which is the case by default.

#### Inherit Grids from Existing Theory

You can reuse the grids from a different theory by using `pineko theory inherit-grids SOURCE_THEORY_ID TARGET_THEORY_ID DATASET1 DATASET2 ...`.
The relation between the source theory and the target theory is non-trivial [5].

## Running `pineko`

Running `pineko` consists of two steps - each of them being potentially computationally expensive:
computing the EKO and convoluting the EKO with the grid.

### Computing the EKO

Again this is a two step process:
1. Generate the necessary operator cards with `pineko theory opcards THEORY_ID DATASET1 DATASET2 ...`
2. Generate the actual EKOs with `pineko theory ekos THEORY_ID DATASET1 DATASET2 ...`

### Generating the FK Table

You need to have the EKO computed in the previous step.
Then you can convolute the EKO with the grid by `pineko theory fks THEORY_ID DATASET1 DATASET2 ...`

---

[1] Actually, instead we should provide a concise description here - but let's wait to be stable first

[2] this is to be replaced by the new CommonData format

[3] this is to be replaced by a binding to the true theory DB

[4] I'm thinking how to improve this, because how could we provide a study on the interpolation accuracy? at the moment there just equal

[5] examples being SV, different evolution settings, etc. - I'm thinking whether it might be worth to add an `inherit-eko` option

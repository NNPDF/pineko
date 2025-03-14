#!/bin/bash

set -euo pipefail

THEORY_ID=40008005 # NNLO QCD with EXA
PDF_NAME="NNPDF40_nnlo_as_01180"

POLARIZED_THEORY_ID=41100010  # NLO QCD⊗EWK with TRN
POLARIZED_POLPDF_NAME="NNPDFpol20_nlo_as_01180"
POLARIZED_UNPOLPDF_NAME="NNPDF40_nlo_pch_as_01180"

LIST_DIS_DATASETS=(
  "HERA_CC_318GEV_EP-SIGMARED"
  # "NNPDF_POS_2P24GEV_F2D"
)

LIST_HADRONIC_DATASETS=(
  "ATLAS_Z0_7TEV_36PB_ETA"
  "LHCB_WPWM_8TEV_MUON_Y"
  "ATLAS_SINGLETOP_8TEV_T-RAP-NORM"
)

LIST_POLARIZED_HADRONIC_DATASETS=(
  "STAR_WMWP_510GEV_WP-AL"
)

get_pdf_combinations() {
  OBJECTNAME=$1

  # Define the combination of PDF sets depending on the types
  if [[ "$OBJECTNAME" == *"-POL"* ]]; then
    PDFSETNAMES="$POLARIZED_POLPDF_NAME $POLARIZED_UNPOLPDF_NAME"
  elif [[ "$OBJECTNAME" == *"-UNPOL"* ]]; then
    PDFSETNAMES="$POLARIZED_UNPOLPDF_NAME"
  else
    PDFSETNAMES="$PDF_NAME"  # Fall to the NNPDF4.0 unpolarized set
  fi
  echo "$PDFSETNAMES"
}

compare_fks_with_grids() {
  THEORYID=$1

  # Compare the Hadronic FK tables with the Grids
  grids=(theory_productions/data/grids/"$THEORYID"/*.pineappl.lz4)
  for gridpath in "${grids[@]}"; do
    gridname=$(basename "$gridpath")
    PDFSETNAMES=$(get_pdf_combinations "$gridname")
    pineko compare ./theory_productions/data/fktables/"$THEORYID"/"$gridname" \
      ./theory_productions/data/grids/"$THEORYID"/"$gridname" 3 0 \
      $PDFSETNAMES --threshold 2 # set threshold to 2 permille
  done
}

compare_fktables() {
  REFERED_FK=$1
  CURRENT_FK=$2
  PDFSETNAMES=$3

  # Extract the predictions - the last column
  diffs=($(pineappl diff $REFERED_FK $CURRENT_FK "$PDFSETNAMES" | awk 'NR>2 {print $NF}'))

  preds_length=${#diffs[@]} # Get the length of the predictions
  for ((bin=0; bin<preds_length; bin++)); do
    pred_value=${diffs[bin]}
    value=$(printf "%.16f" "$pred_value") # Make sure it is in float representation
    # https://www.shell-tips.com/bash/math-arithmetic-calculation/#gsc.tab=0
    abs_diff=$(echo "scale=10; if ($value< 0) -($value) else $value" | bc)
    check_diff=$(echo "$abs_diff > 0.001" | bc) # Set threshold to 1 permille

    if [[ $check_diff -eq 1 ]]; then
      echo "Bin $bin: ($REFERED_FK) and ($CURRENT_FK) differ more than 1 permille."
      exit 1
    fi
  done
}

compare_fks_with_reference() {
  THEORYID=$1

  fktables=(./theory_productions/data/fktables/"$THEORYID"/*.pineappl.lz4)
  for fktable_path in "${fktables[@]}"; do
    fkname=$(basename "$fktable_path")
    PDFSETNAMES=$(get_pdf_combinations "$fkname")
    PDFSETNAMES=$(echo "$PDFSETNAMES" | sed 's/ /+p,/g')
    fkref="./theory_productions/data/fktables/$THEORYID/$fkname"
    fkcur="./theory_productions/reference_fks/$THEORYID/$fkname"
    compare_fktables "$fkref" "$fkcur" "$PDFSETNAMES"
  done
}

dis_predictions() {
  THEORYID=$1
  NFONLL_ID=$(($THEORYID*100))

  for dataset in "${LIST_DIS_DATASETS[@]}"; do
    pineko fonll -c pineko.ci.toml tcards $THEORYID
    pineko fonll -c pineko.ci.toml ekos --overwrite $THEORYID $dataset
    pineko fonll -c pineko.ci.toml fks --overwrite $THEORYID $dataset
    pineko fonll -c pineko.ci.toml combine --overwrite $THEORYID $dataset \
      --FFNS3 $NFONLL_ID \
      --FFN03 $(($NFONLL_ID+1)) \
      --FFNS4zeromass $(($NFONLL_ID+2)) \
      --FFNS4massive $(($NFONLL_ID+3)) \
      --FFN04 $(($NFONLL_ID+4)) \
      --FFNS5zeromass $(($NFONLL_ID+5)) \
      --FFNS5massive $(($NFONLL_ID+6))
  done
}

hadronic_predictions() {
  THEORYID=$1
  LIST_DATASETS=$2

  IFS='|' read -r -a ARRAY_DATASETS <<< "$LIST_DATASETS"
  for dataset in "${ARRAY_DATASETS[@]}"; do
    pineko theory -c pineko.ci.toml opcards --overwrite $THEORYID $dataset
    pineko theory -c pineko.ci.toml ekos --overwrite $THEORYID $dataset
    pineko theory -c pineko.ci.toml fks --overwrite $THEORYID $dataset
  done

  compare_fks_with_grids $THEORYID
}

# Expand the hadronic datasets
LIST_HADRONIC_DATA=$(IFS='|'; echo "${LIST_HADRONIC_DATASETS[*]}")
LIST_POLARIZED_DATA=$(IFS='|'; echo "${LIST_POLARIZED_HADRONIC_DATASETS[*]}")

# Unpolarized runs
dis_predictions $THEORY_ID
hadronic_predictions $THEORY_ID "$LIST_HADRONIC_DATA"
compare_fks_with_reference $THEORY_ID

# Polarized runs with multiple convolutions
hadronic_predictions $POLARIZED_THEORY_ID "$LIST_POLARIZED_DATA"
compare_fks_with_reference $POLARIZED_THEORY_ID

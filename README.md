# Installation

To install the latest version of miniconda and create a conda environment named `fvh-threeML` with threeML, astromodels, fermipy, and HAL installed, run the script `install_everything.sh`.

If you already have a recent version of conda installed, you can try to run `install_from_conda.sh` instead. Make sure that the conda executable you'd like to use is in your `$PATH` before running the script!

After installing, call `source ~/init_conda_fvh.sh` to activate your enviroment from a clean shell.

If you experience problems, try deleting/removing your `.rootrc` file.

# Testing the your setup

Inside your conda environment, call

    cd ~
    mkdir -p ${THREEML_TEST_DIR}
    cd ${THREEML_TEST_DIR}

    # Test astromodels
    pytest -vv -rs --pyargs astromodels
    
    # Test 3ML
    pytest -vv -rs --pyargs threeML
    
    cd ~


# Crab example

## Getting the data

## Example analysis

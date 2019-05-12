# Prerequisites

Installation instructions here should work on MacOS and linux.

To download this repository: `git clone https://github.com/henrikef/threeML-analysis-workshop.git`

## MacOS:

Before starting:

* Install Xcode from App Store.
* Run Xcode at least once (it does not fully install before it is run once). This step (and the following to be safe) need to be done after any (auto)update of Xcode.
* Execute the command line "xcode-select --install"
* Recent versions of XCode (current and previous) don't install the header files in /usr/include anymore. This breaks rootcint in root 5. You have to install the headers manually: `open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg`

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

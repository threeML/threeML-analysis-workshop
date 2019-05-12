#!/usr/bin/env python

from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np

import threeML
from astropy import units as u
from hawc_hal import HAL, HealpixConeROI

from VERITASLike import VERITASLike

import os

def find_and_delete(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
             os.remove(os.path.join(root, name))

def main(use_hal):
    ra, dec = 83.6292, 22.0144
    maptree = './data/maptree_fhit.root'
    response = './data/response_fhit.root'
    veritasdata = './data/threemlVEGAS20hr2p45.root'
    latdirectory = './data/lat_crab_data' # will put downloaded Fermi data there

    if use_hal:
        print('Use HAL plugin')
        data_radius = 3.0
        model_radius = 8.0

        roi = HealpixConeROI(data_radius=data_radius,
                            model_radius=model_radius,
                            ra=ra,
                            dec=dec)

        hawc = HAL("HAWC", maptree, response, roi)

    else:
        print('Use LiFF plugin')
        hawc = threeML.HAWCLike('hawc', maptree, response)

    hawc.set_active_measurements(1, 9) # Perform the fist only within the last nine bins

    hawc_data = {"name": "HAWC", "data":[hawc], "Emin":0.3*u.TeV, "Emax": 30 * u.TeV, "E0":7*u.TeV }

    with np.errstate(divide='ignore', invalid='ignore'):
        # This VERITASLike spits a lot of numpy errors. Silent them, I hope that's OK...
        # Udara told me that's normal.
        veritas = VERITASLike('veritas', veritasdata)

    veritas_data = { "name": "VERITAS", "data":[veritas], "Emin":0.1*u.TeV, "Emax":10*u.TeV, "E0":1*u.TeV } 

    # Fermi via Fermipy 
    tstart = '2017-01-01 00:00:00'
    tstop = '2017-03-01 00:00:00'
    evfile, scfile = threeML.download_LAT_data(ra, dec, 10.0, tstart, tstop, time_type='Gregorian', destination_directory=latdirectory)
    config = threeML.FermipyLike.get_basic_config(evfile=evfile, scfile=scfile, ra=ra, dec=dec)
    config['selection']['emax'] = 300000.0
    config['gtlike'] = {'edisp': False}
    fermi_lat = threeML.FermipyLike("LAT", config)

    lat_data = {"name":"Fermi_LAT", "data":[fermi_lat], "Emin":1e-4*u.TeV, "Emax":0.3*u.TeV, "E0":1*u.GeV }

    # Made up "Fermi-LAT" flux points
    # XYLike points are amsumed in base units of 3ML: keV, and keV s-1 cm-2 (bug: even if you provide something else...).
    x = [ 1.38e6, 2.57e6, 4.46e6, 7.76e6, 18.19e6, 58.88e6] # keV
    y = [5.92e-14, 1.81e-14, 6.39e-15, 1.62e-15, 2.41e-16, 1.87e-17] # keV s-1 cm-2
    yerr = [1.77e-15, 5.45e-16, 8.93e-17, 4.86e-17, 5.24e-18, 7.28e-19] # keV s-1 cm-2
    # Just save a copy for later use (plot points). Will redefine similar objects with other "source_name"
    xy_test = threeML.XYLike("xy_test", x, y, yerr,  poisson_data=False, quiet=False, source_name='XY_Test')

    joint_data = {"name":"Fermi_VERITAS_HAWC", "data":[fermi_lat, veritas, hawc], "Emin":1e-4*u.TeV, "Emax": 30*u.TeV, "E0":0.1*u.TeV}

    datasets = [hawc_data, veritas_data, lat_data, joint_data ]

    fig, ax = plt.subplots()

    #datasets = {
        #'FermiLAT': [fermi_lat, ],
        # For XYLike, source_name should be same as the one used in the best fit model loaded
        #'XYTest': [threeML.XYLike("xytest", x, y, yerr,  poisson_data=False, quiet=False, source_name='XYTest'), ],
        #'VERITAS': [veritas, ],
        #'HAWC': [hawc, ],
        #'LAT_VERITAS_HAWC': [hawc, veritas, fermi_lat],
        # For XYLike, source_name should be same as the one used in the best fit model loaded
        #'XY_HAWC': [threeML.XYLike("xy_hawc", x, y, yerr,  poisson_data=False, quiet=False, source_name='XY_HAWC'), hawc],
     #   }

    for dataset in datasets:

        find_and_delete("ccube.fits", "." )

        data = threeML.DataList(*dataset["data"])

        spectrum = threeML.Log_parabola()

        source = threeML.PointSource(dataset["name"], ra=ra, dec=dec, spectral_shape=spectrum)

        model = threeML.Model(source)
        model[dataset["name"]].spectrum.main.Log_parabola.alpha.bounds = (-4.0, -1.0)
        model[dataset["name"]].spectrum.main.Log_parabola.alpha.value = -2.653
        model[dataset["name"]].spectrum.main.Log_parabola.piv.value = dataset["E0"] 
        # model[key].spectrum.main.Log_parabola.piv.value = 1e7 # 10 GeV
        model[dataset["name"]].spectrum.main.Log_parabola.K.value = 3.15e-22
        #model[key].spectrum.main.Log_parabola.K.bounds = (1e-25, 1e-10)
        model[dataset["name"]].spectrum.main.Log_parabola.beta.value = 0.15
        model[dataset["name"]].spectrum.main.Log_parabola.beta.bounds = (0.0, 1.0)

        model.display()

        jl = threeML.JointLikelihood(model, data)
        jl.set_minimizer("ROOT")
        with np.errstate(divide='ignore', invalid='ignore'):
            # This VERITASLike spits a lot of numpy errors. Silent them, I hope that's OK...
            # Udara told me that's normal.
            best_fit_parameters, likelihood_values = jl.fit()

            jl.results.write_to("likelihoodresults_{0}.fits".format(dataset["name"]), overwrite=True)

        
        #plot results
        color = next(ax._get_lines.prop_cycler)['color']
        try:
            # Using a fixed version of model_plot.py
            threeML.plot_spectra(jl.results,
                ene_min=dataset["Emin"], ene_max=dataset["Emax"],
                energy_unit='TeV', flux_unit='TeV/(s cm2)',
                subplot=ax,
                fit_colors=color,
                contour_colors=color,
            )
        except:
            # Using a bugged version of model_plot.py
            print('Warning: fallback without colors... Use a fixed version of model_plot.py! (3ML PR #304)')
            threeML.plot_point_source_spectra(jl.results,
                ene_min=dataset["Emin"], ene_max=dataset["Emax"],
                energy_unit='TeV', flux_unit='TeV/(s cm2)',
                subplot=ax,
            )

    plotXYpoints = True
    if plotXYpoints:
        # Ad hoc plotting of the XYLike points. Something cleaner should be added to 3ML directly.
        xx = xy_test.x * 1e-9 # 1e-9 for keV to TeV
        yy = xy_test.y * 1e9 * xx * xx # 1e9 for the per keV to per TeV, xx*xx for E^2
        yyerr = xy_test.yerr * 1e9 * xx * xx
        #plt.errorbar(xx, yy, yerr=yyerr, fmt='o', label='XYTest points')
        plt.legend()

    plt.savefig("joint_spectrum.png" )


if __name__ == "__main__":

    main(use_hal=True)

# This file is part of ts_config_ocs.
#
# Developed for the Vera Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from rubin_scheduler.scheduler import basis_functions, detailers, example, features
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import BlobSurvey
from rubin_scheduler.scheduler.utils import CurrentAreaMap, Footprint
from rubin_scheduler.site_models import Almanac


def get_scheduler():
    nside = 32
    science_program = "BLOCK-T345"
    survey_start = 60653.5
    camera_rot_limits = [-80, 80]

    map_band_to_filtername = {
        "u": "u_02",
        "g": "g_01",
        "r": "r_03",
        "i": "i_06",
        "z": "z_03",
        "y": "y_04",
    }

    filtername = map_band_to_filtername["r"]
    filtername2 = map_band_to_filtername["g"]

    # Masks are fine - no band specific information.
    mask_basis_functions = example.standard_masks(
        nside=nside,
        # Let's avoid the moon by this many degrees
        moon_distance=30.0,
        # Erik says to make wind speed minor so set limit high
        wind_speed_maximum=50.0,
        # I think these are the values appropriate for alt limits now?
        min_alt=40,
        max_alt=70,
        min_az=220,
        max_az=360,
        # Avoid going into avoidance regions 30 minutes into the future
        shadow_minutes=30,
    )
    # Mask basis functions have zero weights.
    mask_basis_functions_weights = [0 for mask in mask_basis_functions]

    # Set up footprint stuff here instead of in rubin_scheduler.
    # Use the Almanac to find the position of the sun at the start of survey.
    almanac = Almanac(mjd_start=survey_start)
    sun_moon_info = almanac.get_sun_moon_positions(survey_start)
    sun_ra_start = sun_moon_info["sun_RA"].copy()
    # So this is a dictionary of filternames : int.
    filterdict = {}
    for i, f in enumerate(map_band_to_filtername.values()):
        filterdict[f] = i
    footprints = Footprint(
        filters=filterdict,
        mjd_start=survey_start,
        sun_ra_start=sun_ra_start,
        nside=nside,
    )
    # need to remap this to filtername not band
    footprint = CurrentAreaMap(nside=nside)
    footprint_hp, labels = footprint.return_maps()
    new_dtype = np.dtype([(map_band_to_filtername[f], "<f8") for f in "ugrizy"])
    footprint_hp_filter = footprint_hp.astype(new_dtype)
    for f in footprint_hp_filter.dtype.names:
        footprints.set_footprint(f, footprint_hp_filter[f])

    # Now set up basis functions
    m5_weight = 6.0
    footprint_weight = 1.5
    slewtime_weight = 3.0
    stayfilter_weight = 3.0
    repeat_weight = -20
    # Add the same basis functions, but M5 and footprint
    # basis functions need to be added twice, with half the weight.
    rf1 = example.simple_rewards(
        footprints=footprints,
        filtername=filtername,
        nside=nside,
        m5_weight=m5_weight / 2.0,
        footprint_weight=footprint_weight / 2.0,
        slewtime_weight=slewtime_weight,
        stayfilter_weight=stayfilter_weight,
        repeat_weight=repeat_weight,
    )
    rf2 = example.simple_rewards(
        footprints=footprints,
        filtername=filtername2,
        nside=nside,
        m5_weight=m5_weight / 2.0,
        footprint_weight=footprint_weight / 2.0,
        slewtime_weight=0,
        stayfilter_weight=0,
        repeat_weight=0,
    )
    # Now clean up and combine these - and remove the separate
    # BasisFunction for FilterLoadedBasisFunction.
    reward_functions = [(i[0], i[1]) for i in rf1 if i[1] > 0] + [
        (i[0], i[1]) for i in rf2 if i[1] > 0
    ]
    # Remove the M5Diff basis functions as unusable at present
    reward_functions = [
        (bf, weight)
        for (bf, weight) in reward_functions
        if not isinstance(bf, basis_functions.M5DiffBasisFunction)
    ]

    # unpack the basis functions and weights
    reward_basis_functions_weights = [val[1] for val in reward_functions]
    reward_basis_functions = [val[0] for val in reward_functions]

    # Set up blob surveys.
    pair_time = 20
    if filtername2 is None:
        survey_name = "simple pair %i, %s" % (pair_time, filtername)
    else:
        survey_name = "simple pair %i, %s%s" % (pair_time, filtername, filtername2)

    # Set up detailers for each requested observation.
    detailer_list = []
    # Avoid camera rotator limits.
    detailer_list.append(
        detailers.CameraRotDetailer(
            min_rot=np.min(camera_rot_limits), max_rot=np.max(camera_rot_limits)
        )
    )
    # Reorder visits in a blob so that closest to current altitude is first.
    detailer_list.append(detailers.CloseAltDetailer())
    # Add a detailer to label visits as either first or second of the pair.
    if filtername2 is not None:
        detailer_list.append(detailers.TakeAsPairsDetailer(filtername=filtername2))

    # Set up the survey.
    ignore_obs = ["DD"]

    BlobSurvey_params = {
        "slew_approx": 7.5,
        "filter_change_approx": 140.0,
        "read_approx": 2.4,
        "flush_time": pair_time * 3,
        "smoothing_kernel": None,
        "nside": nside,
        "seed": 42,
        "dither": True,
        "twilight_scale": False,
    }

    pair_survey = BlobSurvey(
        reward_basis_functions + mask_basis_functions,
        reward_basis_functions_weights + mask_basis_functions_weights,
        filtername1=filtername,
        filtername2=filtername2,
        exptime=150,
        ideal_pair_time=pair_time,
        survey_name=survey_name,
        ignore_obs=ignore_obs,
        nexp=1,
        detailers=detailer_list,
        science_program=science_program,
        **BlobSurvey_params,
    )

    # Tucking this here so we can look at how many observations
    # recorded for this survey and what was the last one.
    pair_survey.extra_features["ObsRecorded"] = features.NObsCount()
    pair_survey.extra_features["LastObs"] = features.LastObservation()

    scheduler = CoreScheduler([pair_survey], nside=nside)
    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

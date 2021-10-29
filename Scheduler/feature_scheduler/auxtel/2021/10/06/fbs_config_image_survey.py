import os

import numpy as np

import astropy.units as u

from pathlib import Path

from astropy.coordinates import Angle
from astropy.io import ascii as astropy_ascii

from rubin_sim.scheduler import basis_functions

from rubin_sim.scheduler.utils import empty_observation
from rubin_sim.scheduler.schedulers import Core_scheduler
from rubin_sim.scheduler.surveys import Greedy_survey, FieldSurvey


def get_basis_functions_image_survey(ra, nside, note, ha_limits):
    sun_alt_limit = -18.0
    time_needed = 62.0

    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Time_to_twilight_basis_function(time_needed=time_needed),
        basis_functions.Hour_Angle_limit_basis_function(RA=ra, ha_limits=ha_limits),
        basis_functions.M5_diff_basis_function(nside=nside),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="g"),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.0, nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=1440.0),
    ]


def get_basis_functions_cwfs_survey(nside, note, time_gap_min):
    sun_alt_limit = -12.0
    weights = [1.0, 1000.0, 1.0, 1.0, 1]
    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="g"),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.0, nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=time_gap_min),
    ], weights


if __name__ == "config":

    nside = 32

    path = Path(__file__).parent
    tiles = astropy_ascii.read(path / "latiss_tiles_goods.txt")

    reward_value = 10
    nexp = 1
    ha_limit = [[24.0 - 2.5, 24.0], [0.0, 2.5]]

    target_list = [
        (tile["Name"], tile["RA"], tile["Dec"], ha_limit, reward_value)
        for tile in tiles
    ]

    surveys = [[], []]

    bfs, weights = get_basis_functions_cwfs_survey(
        nside=nside, note="cwfs", time_gap_min=120.0
    )

    surveys[0].append(
        Greedy_survey(
            bfs, weights, nside=nside, survey_name="cwfs", nexp=4, filtername="g"
        )
    )

    for name, ra_str, dec_str, ha_limits, reward in target_list:

        ra = Angle(ra_str, unit=u.hourangle).to(u.deg).value
        dec = Angle(dec_str, unit=u.deg).to(u.deg).value

        bfs = get_basis_functions_image_survey(
            ra=ra, nside=nside, note=name, ha_limits=ha_limits
        )

        observation = empty_observation()
        observation["RA"] = np.radians(ra)
        observation["dec"] = np.radians(dec)
        observation["filter"] = "g"
        observation["exptime"] = 30.0
        observation["nexp"] = 2
        observation["note"] = f"{name}"
        sequence = [observation]

        surveys[1].append(
            FieldSurvey(
                bfs,
                np.array(
                    [
                        ra,
                    ]
                ),
                np.array(
                    [
                        dec,
                    ]
                ),
                sequence=sequence,
                survey_name=name,
                reward_value=reward,
                nside=nside,
                nexp=nexp,
                detailers=[],
            )
        )

    scheduler = Core_scheduler(surveys, nside=nside)

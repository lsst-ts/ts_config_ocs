import os

import numpy as np

import astropy.units as u

from pathlib import Path

from astropy.coordinates import Angle

from rubin_sim.scheduler import basis_functions

from rubin_sim.scheduler.utils import empty_observation
from rubin_sim.scheduler.schedulers import Core_scheduler
from rubin_sim.scheduler.surveys import Greedy_survey, FieldSurvey


def get_basis_functions_cwfs_survey(
    nside,
    note,
    time_gap_min,
    wind_speed_maximum,
):
    """Get the basis functions for the CWFS survey.

    This is a background survey that will activate at specific points in time
    to make sure the telescope optics is aligned.

    Parameters
    ----------
    nside : `int`
        The nside value for the healpix grid.
    note : `str`
        A identifier string to be attached to the survey observations.
    time_gap_min : `float`
        The gap between observations of this survey, in minutes.
    wind_speed_maximu : `float`
        Maximum wind speed tolerated for the observations of the survey,
        in m/s.

    Returns
    -------
    `list` of `basis_functions.Base_basis_function`
    """
    sun_alt_limit = -12.0
    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="g"),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="r"),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="i"),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.0, nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=time_gap_min),
    ]


def get_basis_functions_sp_survey(
    ra,
    nside,
    note,
    ha_limits,
    wind_speed_maximum,
    gap_min,
):
    # This will fallback to using the night boundaries specified on the
    # driver.
    sun_alt_limit = -12.0

    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Hour_Angle_limit_basis_function(RA=ra, ha_limits=ha_limits),
        basis_functions.M5_diff_basis_function(nside=nside),
        basis_functions.Slewtime_basis_function(nside=nside),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.0, nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=gap_min),
        basis_functions.AvoidDirectWind(
            wind_speed_maximum=wind_speed_maximum, nside=nside
        ),
    ]


def get_scheduler():
    nside = 32

    reward_value = 10
    nexp = 2

    spec_ha_limit = [
        [18.0, 24.0],
        [0.0, 6.0],
    ]
    spec_ha_limit_pole = [
        [0.0, 24.0],
    ]

    wind_speed_maximum = 8.0  # maximum direct wind in m/s

    spec_target_list = [
        (
            "HD185975",
            "20:28:18",
            "-87:28:19.9",
            spec_ha_limit_pole,
            reward_value * 2.0,
            60.0,
        ),
        (
            "HD160617",
            "17:42:49",
            "-40:19:15.5",
            spec_ha_limit,
            reward_value,
            0.0,
        ),
    ]

    surveys = [
        [],
    ]

    # CWFS survey
    bfs = get_basis_functions_cwfs_survey(
        nside=nside,
        note="cwfs",
        time_gap_min=120.0,
        wind_speed_maximum=wind_speed_maximum,
    )

    surveys[0].append(
        Greedy_survey(
            bfs,
            np.ones_like(bfs) * 10000.0,
            nside=nside,
            survey_name="cwfs",
            nexp=4,
        )
    )

    # Spectroscopic survey
    for name, ra_str, dec_str, ha_limits, reward, gap_min in spec_target_list:
        ra = Angle(ra_str, unit=u.hourangle).to(u.deg).value
        dec = Angle(dec_str, unit=u.deg).to(u.deg).value

        bfs = get_basis_functions_sp_survey(
            ra=ra,
            nside=nside,
            note=name,
            ha_limits=ha_limits,
            wind_speed_maximum=wind_speed_maximum,
            gap_min=gap_min,
        )

        observation = empty_observation()
        observation["RA"] = np.radians(ra)
        observation["dec"] = np.radians(dec)
        observation["filter"] = "r"
        observation["exptime"] = 360.0
        observation["nexp"] = 1.0
        observation["note"] = f"spec:{name}"
        sequence = [observation]

        surveys.append(
            [
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
                ),
            ]
        )

    scheduler = Core_scheduler(surveys, nside=nside)

    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

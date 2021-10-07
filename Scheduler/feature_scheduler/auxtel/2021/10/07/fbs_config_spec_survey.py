import os

import numpy as np

import astropy.units as u

import matplotlib.pyplot as plt

from astropy.coordinates import Angle

from rubin_sim.scheduler import basis_functions

from rubin_sim.scheduler.utils import empty_observation
from rubin_sim.scheduler.schedulers import Core_scheduler
from rubin_sim.scheduler.surveys import Greedy_survey, FieldSurvey


def get_basis_functions_sp_survey(ra, nside, note, ha_limits, frac_total):
    sun_alt_limit = -18.0
    time_needed = 62.0

    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Time_to_twilight_basis_function(time_needed=time_needed),
        basis_functions.Hour_Angle_limit_basis_function(RA=ra, ha_limits=ha_limits),
        basis_functions.M5_diff_basis_function(nside=nside),
        basis_functions.Slewtime_basis_function(nside=nside),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85., nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=30.0),
    ]


def get_basis_functions_cwfs_survey(nside, note, time_gap_min):
    sun_alt_limit = -12.0
    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Slewtime_basis_function(nside=nside),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85., nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=time_gap_min),
    ]


if __name__ == "config":

    nside = 32

    reward_value = 10
    nexp = 1
    ha_limit = [[18.0, 24.0], [0.0, 6.0]]

    target_list = [
        ("HD2811", "00:31:18", "-43:36:23.0", ha_limit, reward_value),
        ("HD009051", "01:28:46", "-24:20:25.4", ha_limit, reward_value),
        ("HD14943", "02:22:54", "-51:05:31.7", ha_limit, reward_value),
        ("HD031128", "04:52:09", "-27:03:50.9", ha_limit, reward_value),
        ("LAMLEP", "05:19:34", "-13:10:36.4", ha_limit, reward_value),
        ("HD37962", "05:40:51", "-31:21:04.0", ha_limit, reward_value),
        ("MUCOL", "05:46:00", "-32:18:23.2", ha_limit, reward_value),
        ("HD38949", "05:48:20", "-24:27:49.9", ha_limit, reward_value),
        ("ETA1DOR", "06:06:09", "-66:02:23", ha_limit, reward_value),
        ("HD185975", "20:28:18", "-87:28:19.9", [[0.0, 24.0]], reward_value * 2.0),
        ("HD200654", "21:06:34", "-49:57:50.3", ha_limit, reward_value),
        ("HD205905", "21:39:10", "-27:18:23.7", ha_limit, reward_value),
    ]

    surveys = [[], []]

    bfs = get_basis_functions_cwfs_survey(nside=32, note="cwfs", time_gap_min=120.0)

    surveys[0].append(
        Greedy_survey(
            bfs, np.ones_like(bfs) * 10000.0, nside=32, survey_name="cwfs", nexp=4
        )
    )

    for name, ra_str, dec_str, ha_limits, reward in target_list:
        ra = Angle(ra_str, unit=u.hourangle).to(u.deg).value
        dec = Angle(dec_str, unit=u.deg).to(u.deg).value

        bfs = get_basis_functions_sp_survey(
            ra=ra, nside=32, note=name, ha_limits=ha_limits, frac_total=0.2
        )

        observation = empty_observation()
        observation["RA"] = np.radians(ra)
        observation["dec"] = np.radians(dec)
        observation["filter"] = "r"
        observation["exptime"] = 360.0
        observation["nexp"] = 1.0
        observation["note"] = f"spec:{name}"
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

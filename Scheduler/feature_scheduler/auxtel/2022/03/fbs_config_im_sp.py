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


def get_basis_functions_image_survey(
    ra,
    nside,
    note,
    ha_limits,
    wind_speed_maximum,
    nobs_reference,
    note_interest,
):
    """Get the basis functions for the image survey.

    Parameters
    ----------
    ra : `float`
        Right Ascention for the observavtions, in hours.
    nside : `int`
        The nside value for the healpix grid.
    note : `str`
        A identifier string to be attached to the survey observations.
    ha_limits : 'list` of `float`
        A two-element list with the hour angle limits, in hours.
    wind_speed_maximu : `float`
        Maximum wind speed tolerated for the observations of the survey,
        in m/s.
    nobs_reference : `int`
        Reference number of observations.
    note_interest : `str`
        A substring that maps to surveys to be accounted for agains the
        reference number of observations.

    Returns
    -------
    `list` of `basis_functions.Base_basis_function`
    """

    sun_alt_limit = -12.0
    time_needed = 62.0

    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Hour_Angle_limit_basis_function(RA=ra, ha_limits=ha_limits),
        # basis_functions.M5_diff_basis_function(nside=nside),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="g"),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="r"),
        basis_functions.Slewtime_basis_function(nside=nside, filtername="i"),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=20.0, max_alt=85.0, nside=nside
        ),
        basis_functions.VisitGap(note=note, gap_min=1440.0),
        basis_functions.AvoidDirectWind(
            wind_speed_maximum=wind_speed_maximum, nside=nside
        ),
        basis_functions.BalanceVisits(
            nobs_reference=nobs_reference, note_survey=note, note_interest=note_interest
        ),
    ]


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


def generate_image_survey(
    nside,
    reward,
    ra_str,
    dec_str,
    name,
    name_survey,
    nexp,
    ha_limits,
    wind_speed_maximum,
    filters,
    nfields,
    survey_detailers,
):

    ra = Angle(ra_str, unit=u.hourangle).to(u.deg).value
    dec = Angle(dec_str, unit=u.deg).to(u.deg).value

    bfs = get_basis_functions_image_survey(
        ra=ra,
        nside=nside,
        note=name,
        note_interest=name_survey,
        ha_limits=ha_limits,
        wind_speed_maximum=wind_speed_maximum,
        nobs_reference=nfields,
    )

    sequence = [empty_observation() for i in range(len(filters))]

    for filter_obs, observation in zip(filters, sequence):

        observation["RA"] = np.radians(ra)
        observation["dec"] = np.radians(dec)
        observation["filter"] = filter_obs
        observation["exptime"] = 60.0
        observation["nexp"] = 2
        observation["note"] = f"{name}"

    return FieldSurvey(
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
        detailers=survey_detailers,
    )


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
    nside = 128

    reward_value = 10
    nexp = 2

    spec_ha_limit = [
        [18.0, 24.0],
        [0.0, 6.0],
    ]
    image_ha_limit = [
        [24.0 - 4.5, 24.0],
        [0.0, 4.5],
    ]
    image_ha_limit_pole = [
        [0.0, 24.0],
    ]

    wind_speed_maximum = 8.0  # maximum direct wind in m/s

    spec_target_list = [
        ("ETA1DOR", "06:06:09", "-66:02:23", spec_ha_limit, reward_value, 1.0),
        ("HD111980", "12:53:15.05", "-18:31:20.0", spec_ha_limit, reward_value, 1.0),
    ]

    path = Path(__file__).parent.parent.parent
    tiles_file = path / "latiss_tiles.txt"

    tiles = astropy_ascii.read(str(tiles_file))

    image_target_list_pole = [
        (
            tile["Name"],
            "_POLE_",
            tile["RA"],
            tile["Dec"],
            image_ha_limit_pole,
            reward_value - 5.0,
            "gri",
        )
        for tile in tiles
        if "_POLE_" in tile["Name"]
    ]

    image_target_list_md02 = [
        (
            tile["Name"],
            "_MD02_",
            tile["RA"],
            tile["Dec"],
            image_ha_limit,
            reward_value,
            "gr",
        )
        for tile in tiles
        if "_MD02_" in tile["Name"]
    ]

    image_target_list_e6a = [
        (
            tile["Name"],
            "_E6A_",
            tile["RA"],
            tile["Dec"],
            image_ha_limit,
            reward_value,
            "gri",
        )
        for tile in tiles
        if "_E6A_" in tile["Name"]
    ]

    surveys = [
        [],
        [],
        [],
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

    # Image surveys
    for image_target_list in [
        image_target_list_md02,
        image_target_list_e6a,
        # image_target_list_pole,
    ]:
        survey_detailers = []
        for (
            name,
            name_survey,
            ra_str,
            dec_str,
            ha_limits,
            reward,
            filters,
        ) in image_target_list:

            surveys[1].append(
                generate_image_survey(
                    nside=nside,
                    reward=reward,
                    ra_str=ra_str,
                    dec_str=dec_str,
                    name=name,
                    name_survey=name_survey,
                    nexp=nexp,
                    ha_limits=ha_limits,
                    wind_speed_maximum=wind_speed_maximum,
                    filters=filters,
                    nfields=len(image_target_list),
                    survey_detailers=survey_detailers,
                )
            )

    # Image surveys
    for image_target_list in [
        image_target_list_pole,
    ]:
        survey_detailers = []

        for (
            name,
            name_survey,
            ra_str,
            dec_str,
            ha_limits,
            reward,
            filters,
        ) in image_target_list:

            surveys[2].append(
                generate_image_survey(
                    nside=nside,
                    reward=reward,
                    ra_str=ra_str,
                    dec_str=dec_str,
                    name=name,
                    name_survey=name_survey,
                    nexp=nexp,
                    ha_limits=ha_limits,
                    wind_speed_maximum=wind_speed_maximum,
                    filters=filters,
                    nfields=len(image_target_list),
                    survey_detailers=survey_detailers,
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

        surveys[3].append(
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

    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

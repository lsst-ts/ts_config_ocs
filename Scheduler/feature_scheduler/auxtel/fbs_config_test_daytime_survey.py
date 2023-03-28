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

from lsst.ts.fbs.utils import Tiles

from lsst.ts.fbs.utils.auxtel.make_scheduler import MakeScheduler, SurveyType


def get_scheduler():
    """Construct feature based scheduler.

    The Feature Based Scheduler configuration constructed here is intended for
    testing purposes only. If does not contain any constraint on skybrightness
    or night boundaries, so it will produce targets any anytime.

    Returns
    -------
    nside : int
        Healpix map resolution.
    scheduler : Core_scheduler
        Feature based scheduler.
    """
    nside = 64
    reward_values = dict(
        default=10.0,
        image_pole=1.0,
        image_survey=2.0,
        spec_pole=20.0,
    )

    image_nexp = 2  # number of exposures
    image_exptime = 60.0  # total exposure time in seconds
    image_visit_gap = 1440.0
    wind_speed_maximum = 13.0  # maximum direct wind in m/s

    image_ha_limit = [
        (24.0 - 3.5, 24.0),
        (0.0, 3.5),
    ]
    image_ha_limit_pole = [
        (0.0, 24.0),
    ]

    image_tiles = [
        Tiles(
            survey_name="LATISS_POLE",
            hour_angle_limit=image_ha_limit_pole,
            reward_value=reward_values["image_pole"],
            filters=["r"],
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
        ),
        Tiles(
            survey_name="AUXTEL_DRP_IMAGING",
            hour_angle_limit=image_ha_limit,
            reward_value=reward_values["image_survey"],
            filters=["r"],
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
        ),
    ]

    spec_detailers = []
    image_detailers = []

    make_scheduler = MakeScheduler()

    nside, scheduler = make_scheduler.get_scheduler(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        survey_type=SurveyType.Image,
        spec_targets=[],
        image_tiles=image_tiles,
        spec_detailers=spec_detailers,
        image_detailers=image_detailers,
    )

    # Remove the Not_twilight_basis_function
    scheduler.survey_lists[0][0].basis_functions.pop(0)

    for survey in scheduler.survey_lists[1]:
        # Remove the Not_twilight_basis_function
        survey.basis_functions.pop(0)

        # Increase weight on slewtime basis functions.
        for i, basis_func in enumerate(survey.basis_functions):
            if "Slewtime" in str(basis_func):
                survey.basis_weights[i] *= 10.0

    # Add "_sim" to all survey names
    for survey_list in scheduler.survey_lists:
        for survey in survey_list:
            survey.survey_name += "_sim"
            if hasattr(survey, "observations"):
                note = str(survey.observations[0]["note"])
                survey_name, target_name = note.split(":", maxsplit=1)
                survey.observations[0]["note"] = f"{survey_name}_sim:{target_name}"

    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

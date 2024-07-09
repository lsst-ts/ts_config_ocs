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

from astropy import units
from astropy.coordinates import Angle
from lsst.ts.fbs.utils import Target, Tiles
from lsst.ts.fbs.utils.auxtel.make_scheduler import MakeScheduler, SurveyType
from rubin_scheduler.scheduler.detailers import DitherDetailer


def get_scheduler():
    """Construct feature based scheduler.

    Returns
    -------
    nside : int
        Healpix map resolution.
    scheduler : Core_scheduler
        Feature based scheduler.
    """
    nside = 64
    reward_values = dict(
        default=5.0,
        image_pole=1.0,
        image_survey=2.0,
        spec_backup=1.0,
        spec_pole=30.0,
        spec_boost=20.0,
    )

    image_nexp = 1  # number of exposures
    image_exptime = 120.0  # total exposure time in seconds
    image_visit_gap = 12 * 60.0
    wind_speed_maximum = 13.0  # maximum direct wind in m/s

    spec_ha_limit = [
        (18.0, 24.0),
        (0.0, 6.0),
    ]
    spec_ha_limit_pole = [
        (0.0, 24.0),
    ]
    image_ha_limit = [
        (23.5, 24.0),
        (0.0, 1.5),
    ]

    spec_target_list = [
        Target(
            target_name="HD185975",
            survey_name="spec",
            ra=Angle("20:28:18", unit=units.hourangle),
            dec=Angle("-87:28:19.9", unit=units.deg),
            hour_angle_limit=spec_ha_limit_pole,
            reward_value=reward_values["spec_pole"],
            filters=["r"],
            visit_gap=105.0,
            exptime=360.0,
            nexp=1,
        ),
        Target(
            target_name="HD2811",
            survey_name="spec",
            ra=Angle("00:31:18", unit=units.hourangle),
            dec=Angle("-43:36:23.0", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["spec_boost"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
        ),
        Target(
            target_name="HD38666",
            survey_name="spec_bright",
            ra=Angle("05:46:00", unit=units.hourangle),
            dec=Angle("-32:18:23.2", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["spec_boost"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
            moon_distance=20.0,
        ),
        Target(
            target_name="HD73495",
            survey_name="spec_bright",
            ra=Angle("08:37:52", unit=units.hourangle),
            dec=Angle("-26:15:18.0", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["default"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
        ),
        Target(
            target_name="HD111980",
            survey_name="spec",
            ra=Angle("12:53:15", unit=units.hourangle),
            dec=Angle("-18:31:20.0", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["spec_boost"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
        ),
        Target(
            target_name="HD146233",
            survey_name="spec_bright",
            ra=Angle("16:15:37", unit=units.hourangle),
            dec=Angle("-08:22:10.0", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["default"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
            moon_distance=20.0,
        ),
        Target(
            target_name="HD177517",
            survey_name="spec_bright",
            ra=Angle("19:05:41.18", unit=units.hourangle),
            dec=Angle("-15:39:37.51", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["spec_boost"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
            moon_distance=20.0,
        ),
        Target(
            target_name="HD202025",
            survey_name="spec",
            ra=Angle("21:14:01.78", unit=units.hourangle),
            dec=Angle("-22:12:43.64", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["default"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
        ),
        Target(
            target_name="HD205905",
            survey_name="spec_bright",
            ra=Angle("21:39:10", unit=units.hourangle),
            dec=Angle("-27:18:23.7", unit=units.deg),
            hour_angle_limit=spec_ha_limit,
            reward_value=reward_values["spec_boost"],
            filters=["r"],
            visit_gap=10.0,
            exptime=420.0,
            nexp=1,
            moon_distance=20.0,
        ),
    ]

    image_tiles = [
        Tiles(
            survey_name="AUXTEL_PHOTO_IMAGING",
            hour_angle_limit=image_ha_limit,
            reward_value=reward_values["default"],
            filters=["g"],
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
        ),
    ]

    spec_detailers = []
    image_detailers = [
        DitherDetailer(max_dither=(25.0 / (60.0 * 60.0)), per_night=True)
    ]

    make_scheduler = MakeScheduler()

    return make_scheduler.get_scheduler(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        survey_type=SurveyType.ImageSpec,
        spec_targets=spec_target_list,
        image_tiles=image_tiles,
        spec_detailers=spec_detailers,
        image_detailers=image_detailers,
    )


if __name__ == "config":
    nside, scheduler = get_scheduler()

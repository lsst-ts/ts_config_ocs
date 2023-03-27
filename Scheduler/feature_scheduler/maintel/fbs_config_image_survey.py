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

from lsst.ts.fbs.utils.maintel.make_scheduler import MakeScheduler


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
        default=10.0,
        image_pole=5.0,
    )

    image_nexp = 3  # number of exposures
    image_exptime = 18.0  # total exposure time in seconds
    image_visit_gap = 60.0
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
            survey_name="STAR_TRACKER_POLE",
            hour_angle_limit=image_ha_limit_pole,
            reward_value=reward_values["image_pole"],
            filters=["g"],
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
        ),
        Tiles(
            survey_name="STAR_TRACKER",
            hour_angle_limit=image_ha_limit,
            reward_value=reward_values["default"],
            filters=["g"],
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
        ),
    ]

    make_scheduler = MakeScheduler()

    return make_scheduler.get_scheduler(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        image_tiles=image_tiles,
    )


if __name__ == "config":
    nside, scheduler = get_scheduler()

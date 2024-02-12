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

from lsst.ts.fbs.utils.maintel.make_scheduler import MakeScheduler, SurveyType


def get_scheduler():
    """Construct feature based scheduler.

    Returns
    -------
    nside : int
        Healpix map resolution.
    scheduler : Core_scheduler
        Feature based scheduler.
    """
    nside = 32

    wind_speed_maximum = 13.0  # maximum direct wind in m/s

    make_scheduler = MakeScheduler()

    nside, scheduler = make_scheduler.get_scheduler(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        survey_type=SurveyType.SIT,
        survey_name="BLOCK-224",
        image_tiles=[],
    )

    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

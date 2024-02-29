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
from rubin_scheduler.scheduler import basis_functions, surveys
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.utils import standard_goals


def get_scheduler():
    """Construct feature based scheduler.

    The Feature Based Scheduler configuration constructed here is intended for
    testing purposes only. If does not contain any constraint on sky
    brightness or night boundaries, so it will produce targets any anytime.

    Returns
    -------
    nside : int
        Healpix map resolution.
    scheduler : Core_scheduler
        Feature based scheduler.
    """
    target_map = standard_goals()["r"]
    nside = 32

    bfs = []
    bfs.append(
        basis_functions.HaMaskBasisFunction(
            ha_min=-1.5,
            ha_max=1.5,
            nside=nside,
        )
    )
    bfs.append(
        basis_functions.ZenithShadowMaskBasisFunction(
            min_alt=40.0,
            max_alt=82.0,
            nside=nside,
        )
    )
    bfs.append(basis_functions.SlewtimeBasisFunction(filtername="r", nside=nside))
    bfs.append(basis_functions.TargetMapBasisFunction(target_map=target_map))

    weights = np.ones(len(bfs))
    survey = surveys.GreedySurvey(
        basis_functions=bfs,
        basis_weights=weights,
        filtername="r",
        nside=nside,
        survey_name="TEST_ANYTIME_SURVEY",
    )
    scheduler = CoreScheduler([survey])

    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

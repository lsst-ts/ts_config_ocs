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
from rubin_scheduler.scheduler import example
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.utils import CurrentAreaMap


def get_scheduler():
    nside = 32

    masks = example.standard_masks(
        nside=nside,
        # Let's avoid the moon by this many degrees
        moon_distance=30.0,
        # Erik says to make wind speed minor so set limit high
        wind_speed_maximum=50.0,
        # I think these are the values appropriate for alt limits now?
        min_alt=30,
        max_alt=80,
        min_az=0,
        max_az=360,
        # Avoid going into avoidance regions 30 minutes into the future
        shadow_minutes=30,
    )

    map_band_to_filtername = {
        "u": "u_02",
        "g": "g_01",
        "r": "r_03",
        "i": "i_06",
        "z": "z_03",
        "y": "y_04",
    }

    filter_one = map_band_to_filtername["r"]
    filter_two = map_band_to_filtername["g"]

    # need to remap this to filtername not band
    footprint = CurrentAreaMap(nside=nside)
    footprint_hp, labels = footprint.return_maps()
    new_dtype = np.dtype([(map_band_to_filtername[f], "<f8") for f in "ugrizy"])
    footprint_hp_filter = footprint_hp.astype(new_dtype)

    pair_survey = example.simple_pairs_survey(
        nside=nside,
        filtername=filter_one,
        filtername2=filter_two,
        mask_basis_functions=masks,
        # Use the default reward basis functions
        reward_basis_functions=None,
        reward_basis_functions_weights=None,
        # Let's just set survey_start to be close to now
        survey_start=60653.5,
        footprints_hp=footprint_hp_filter,
        camera_rot_limits=[-80, 80],
        pair_time=30,
        exptime=150,
        nexp=1,
        science_program="BLOCK-T345",
    )

    scheduler = CoreScheduler([pair_survey], nside=nside)
    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

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

from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
)
from rubin_scheduler.scheduler import basis_functions, detailers


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

    # Mapping from band to filter from
    # obs_lsst/python/lsst/obs/lsst/filters.py
    band_to_filter = {
        "u": "u_24",
        "g": "g_6",
        "r": "r_57",
        "i": "i_39",
        "z": "z_20",
        "y": "y_10",
    }

    nvisits = {"u": 0, "g": 0, "r": 1, "i": 0, "z_03": 0, "y": 0}
    sequence = ["r"]

    # exposure time in seconds
    exptimes = {"u": 38, "g": 30, "r": 15, "i": 30, "z": 30, "y": 30}
    # 1 --> single 30 second exposuree
    nexps = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}

    min_alt = 40.0

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    config_basis_functions = [
        basis_functions.AltAzShadowMaskBasisFunction(
            nside=nside,
            min_alt=min_alt,
            max_alt=83.0,
            shadow_minutes=2.0,
        ),
        basis_functions.SlewtimeBasisFunction(bandname=None, nside=nside),
        basis_functions.MoonAvoidanceBasisFunction(nside=nside),
    ]

    config_detailers = [
        detailers.AltAz2RaDecDetailer(),
        detailers.CameraRotDetailer(
            max_rot=70,
            min_rot=-70,
            dither="all",
        ),
    ]

    observation_reason = "ptg_model"
    science_program = "BLOCK-387"  # json BLOCK to be used
    survey_name = science_program  # match nextVisit metadata

    tier = 0

    make_scheduler = MakeFieldSurveyScheduler(
        targets=dict(),
        nside=nside,
        ntiers=1,
        band_to_filter=band_to_filter,
    )
    make_scheduler.add_field_altaz_surveys(
        tier,
        observation_reason,
        science_program,
        survey_name=survey_name,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

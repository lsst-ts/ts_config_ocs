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

    make_scheduler = MakeFieldSurveyScheduler(nside=nside, ntiers=1)

    nvisits = {"u_02": 0, "g_01": 0, "r_03": 1, "i_06": 0, "z_03": 0, "y": 0}
    sequence = ["r_03"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 15, "i_06": 30, "z_03": 30, "y": 30}
    # 1 --> single 30 second exposuree
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y": 1}

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
    ]

    config_detailers = [detailers.AltAz2RaDecDetailer()]

    observation_reason = "ptg_model"
    science_program = "BLOCK-324"  # json BLOCK to be used
    survey_name = science_program  # match nextVisit metadata

    tier = 0

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

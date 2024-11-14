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

from lsst.ts.fbs.utils.maintel.basis_functions import get_basis_functions_field_survey
from lsst.ts.fbs.utils.maintel.detailers import get_detailers_field_survey
from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
    get_comcam_sv_targets,
)


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

    nvisits = {"u_02": 20, "g_01": 20, "r_03": 20, "i_06": 20, "z_03": 20, "y": 20}
    sequence = ["u_02", "g_01", "r_03", "i_06", "z_03", "y"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 30, "i_06": 30, "z_03": 30, "y": 30}
    # 1 --> single 30 second exposuree
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y": 1}

    wind_speed_maximum = 20.0  # maximum direct wind in m/s
    min_alt = 40.0

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    basis_functions = get_basis_functions_field_survey(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        min_alt=min_alt,
    )

    detailers = get_detailers_field_survey()

    observation_reason = "science"
    science_program = "BLOCK-320"  # json BLOCK to be used
    survey_name = science_program  # match nextVisit metadata

    tier = 0
    target_names = get_comcam_sv_targets().keys()
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        survey_name=survey_name,
        basis_functions=basis_functions,
        detailers=detailers,
        **field_survey_kwargs,
    )

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

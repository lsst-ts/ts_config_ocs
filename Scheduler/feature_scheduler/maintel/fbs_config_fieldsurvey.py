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

from lsst.ts.fbs.utils.data.field_survey_centers import get_sv_fields
from lsst.ts.fbs.utils.maintel.basis_functions import get_basis_functions_field_survey
from lsst.ts.fbs.utils.maintel.detailers import get_detailers_field_survey
from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
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

    nvisits = {"u": 20, "g": 20, "r": 20, "i": 20, "z": 20, "y": 20}
    sequence = "ugrizy"
    # exposure time in seconds
    exptimes = {"u": 38, "g": 30, "r": 30, "i": 30, "z": 30, "y": 30}
    # 1 --> single 30 second exposure
    nexps = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}

    wind_speed_maximum = 13.0  # maximum direct wind in m/s

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    # This might move to be part of a separate function
    basis_functions = get_basis_functions_field_survey(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
    )

    detailers = get_detailers_field_survey()

    # Specify the json BLOCK to be used
    program = "MAINTEL_COMCAM_IMAGING"

    tier = 0
    field_names = get_sv_fields().keys()
    make_scheduler.add_field_surveys(
        tier,
        program,
        field_names,
        basis_functions=basis_functions,
        detailers=detailers,
        **field_survey_kwargs,
    )

    """
    tier = 0
    # program must be the name of program in json BLOCK to be used
    field_names = [
        "EDFS_A",
        "EDFS_B",
    ]
    make_scheduler.add_field_surveys(
        tier,
        program,
        field_names,
        basis_functions=basis_functions,
        detailers=detailers,
        **field_survey_kwargs,
    )

    tier = 1
    # program must be the name of program in json BLOCK to be used
    field_names = [
        "DEEP_A0",
        "DEEP_B0",
    ]
    make_scheduler.add_field_surveys(
        tier,
        program,
        field_names,
        basis_functions=basis_functions,
        detailers=detailers,
        **field_survey_kwargs,
    )
    """
    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

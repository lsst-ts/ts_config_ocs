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
from rubin_scheduler.scheduler.utils import ObservationArray
from rubin_scheduler.scheduler.detailers import StartFieldSequenceDetailer

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

    # Scheduler will be the field survey scheduler
    make_scheduler = MakeFieldSurveyScheduler(nside=nside, ntiers=1)

    target_info = get_comcam_sv_targets()
    # Edit HERE to reduce the number of fields included each night
    target_names = target_info.keys()

    # Main survey metadata
    observation_reason = "science"
    science_program = "BLOCK-320"  # json BLOCK to be used

    # And AOS visits will be configured and run as a detailer on top of
    # each field survey.
    aos_scheduler_note = "Close Loop sequences"
    aos_science_program = "BLOCK-330"
    # For each AOS detailer (which must be separately defined)
    # we will add an ObservationArray specifically for that target.
    aos_obs_lists = {}
    for target in target_names:
        obslist = ObservationArray()
        obslist["exptime"] = 90
        obslist["RA"] = np.radians(target_info[target]["ra"])
        obslist["dec"] = np.radians(target_info[target]["dec"])
        obslist["rotTelPos"] = np.radians(0)
        obslist["filter"] = "r"
        obslist["science_program"] = aos_science_program
        obslist["scheduler_note"] = aos_scheduler_note
        obslist["target_name"] = target
        aos_obs_lists[target] = [obslist]

    # Define the standard sequence for all field surveys.
    nvisits = {"u_02": 20, "g_01": 20, "r_03": 20, "i_06": 20, "z_03": 20, "y": 20}
    sequence = ["u_02", "g_01", "r_03", "i_06", "z_03", "y"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 30, "i_06": 30, "z_03": 30, "y": 30}
    # 1 --> single 30 second exposure
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y": 1}

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    # Define basis functions to choose between field surveys
    wind_speed_maximum = 20.0  # maximum direct wind in m/s
    min_alt = 40.0

    basis_functions = get_basis_functions_field_survey(
        nside=nside,
        wind_speed_maximum=wind_speed_maximum,
        min_alt=min_alt,
    )

    # Generic detailers
    detailers = get_detailers_field_survey()

    tier = 0
    for target in target_names:
        aos_detailer = StartFieldSequenceDetailer(
            sequence_obs_list=aos_obs_lists[target],
            ang_distance_match=3.5,
            time_match_hours=2,
            ra=target_info[target]["ra"],
            dec=target_info[target]["dec"],
            scheduler_note=aos_scheduler_note,
            science_program=aos_science_program,
        )
        make_scheduler.add_field_surveys(
            tier,
            observation_reason,
            science_program,
            [target],
            survey_name=target,
            basis_functions=basis_functions,
            detailers=[aos_detailer] + detailers,
            **field_survey_kwargs,
        )

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

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
from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
    get_comcam_sv_targets,
)
from rubin_scheduler.scheduler import basis_functions, detailers
from rubin_scheduler.scheduler.utils import ObservationArray


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

    # Main science program setup
    observation_reason = "science"
    science_program = "BLOCK-320"  # json BLOCK to be used

    # AOS visits will be configured and run as a detailer on top of
    # each field survey.
    aos_scheduler_note = "Close Loop sequences"
    aos_science_program = "BLOCK-330"
    # For each AOS detailer (which must be separately defined)
    # we will add an ObservationArray specifically for that target.
    # (it has to know about the RA/Dec of the target field).
    target_info = get_comcam_sv_targets()
    aos_obs_lists = {}
    for target in target_info:
        obslist = ObservationArray()
        obslist["exptime"] = 90
        obslist["RA"] = np.radians(target_info[target]["ra"])
        obslist["dec"] = np.radians(target_info[target]["dec"])
        obslist["rotTelPos"] = np.radians(0)
        obslist["science_program"] = aos_science_program
        obslist["scheduler_note"] = aos_scheduler_note
        obslist["target_name"] = target
        obslist["filter"] = "r_03"
        # I'm assuming that most of the aos_obs request will be overridden by
        # the json block, but the scheduler_note should be maintained
        # and the result of this observation should be fed back to the FBS
        # (like any other requested observation).
        aos_obs_lists[target] = [obslist]

    # Now configure main science surveys
    # All surveys have the same basis functions
    config_basis_functions = [
        basis_functions.NotTwilightBasisFunction(sun_alt_limit=-12.0),
        basis_functions.AltAzShadowMaskBasisFunction(
            nside=nside,
            min_alt=40.0,
            max_alt=83.0,
            shadow_minutes=2.0,
        ),
        basis_functions.SlewtimeBasisFunction(filtername="u_02", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="g_01", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="r_03", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="i_06", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="z_03", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="y_04", nside=nside),
    ]

    # Configure ecliptic target survey
    ecliptic_targets = ["Rubin_SV_38_7"]

    nvisits = {"u_02": 8, "g_01": 16, "r_03": 8, "i_06": 8, "z_03": 8, "y_04": 8}
    sequence = ["r_03", "i_06"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 30, "i_06": 30, "z_03": 30, "y_04": 30}
    # 1 --> single 30 second exposure
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y_04": 1}
    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    # Detailers for all ecliptic surveys
    config_detailers = [detailers.ComCamGridDitherDetailer()]

    tier = 0
    for target in ecliptic_targets:
        aos_detailer = detailers.StartFieldSequenceDetailer(
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
            basis_functions=config_basis_functions,
            detailers=[aos_detailer] + config_detailers,
            **field_survey_kwargs,
        )

    # And now configure standard survey fields
    # ComCam Deep Drilling Fields

    nvisits = {"u_02": 5, "g_01": 10, "r_03": 5, "i_06": 5, "z_03": 5, "y_04": 5}
    sequence = ["r_03", "i_06"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 30, "i_06": 30, "z_03": 30, "y_04": 30}
    # 1 --> single 30 second exposure
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y_04": 1}

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    config_detailers = [
        detailers.DitherDetailer(max_dither=0.2, per_night=False),
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=40.0, min_rot=-40.0, telescope="comcam"
        ),
    ]

    tier = 0
    target_names = get_comcam_sv_targets(
        exclude=ecliptic_targets,
    ).keys()
    for target in target_names:
        aos_detailer = detailers.StartFieldSequenceDetailer(
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
            basis_functions=config_basis_functions,
            detailers=[aos_detailer] + config_detailers,
            **field_survey_kwargs,
        )

    # Ecliptic Field

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

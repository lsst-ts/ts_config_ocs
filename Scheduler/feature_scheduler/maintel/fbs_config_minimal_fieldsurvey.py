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
    get_comcam_sv_targets,
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

    ecliptic_targets = ["Rubin_SV_38_7"]

    # ComCam Deep Drilling Fields

    nvisits = {"u_02": 5, "g_01": 5, "r_03": 5, "i_06": 5, "z_03": 5, "y_04": 5}
    sequence = ["u_02", "g_01", "r_03"]
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
        basis_functions.FilterLoadedBasisFunction(filternames=sequence),
    ]

    config_detailers = [
        detailers.DitherDetailer(max_dither=0.2, per_night=False),
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=40.0, min_rot=-40.0, telescope="comcam"
        ),
    ]

    observation_reason = "science"
    science_program = "BLOCK-320"  # json BLOCK to be used

    tier = 0
    target_names = get_comcam_sv_targets(
        exclude=ecliptic_targets,
    ).keys()
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # Ecliptic Field

    nvisits = {"u_02": 8, "g_01": 12, "r_03": 8, "i_06": 8, "z_03": 8, "y_04": 8}
    sequence = ["g_01", "r_03", "i_06"]
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

    config_detailers = [detailers.ComCamGridDitherDetailer()]
    config_detailers[0].survey_features = {}

    tier = 0
    target_names = ecliptic_targets
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

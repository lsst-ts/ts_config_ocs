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

from pathlib import Path

from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
    get_sv_targets,
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

    # Get target coordinates - edit YAML file for updates
    # YAML file should be in the same directory as this .py config
    # ts_config_ocs/Scheduler/feature_scheduler/maintel/
    # fieldsurvey_centers.yaml
    target_dir = Path(__file__).parent
    target_file = Path.joinpath(target_dir, "fieldsurvey_centers.yaml")
    if not Path.exists(target_file):
        raise ValueError(f"Expected target yaml file does not exist at {target_file}")
    targets = get_sv_targets(target_file)

    make_scheduler = MakeFieldSurveyScheduler(
        targets=targets, nside=nside, ntiers=1, band_to_filter=band_to_filter
    )

    nvisits = {"u": 5, "g": 5, "r": 5, "i": 5, "z": 5, "y": 5}
    sequence = ["g", "r", "i"]
    # exposure time in seconds
    exptimes = {"u": 38, "g": 30, "r": 30, "i": 30, "z": 30, "y": 30}
    # 1 --> single 30 second exposure
    nexps = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}

    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    config_basis_functions = [
        # TODO: return NotTwilightBasisFunction when rotator test is completed.
        # basis_functions.NotTwilightBasisFunction(sun_alt_limit=-12.0),
        basis_functions.AltAzShadowMaskBasisFunction(
            nside=nside,
            min_alt=30.0,
            max_alt=83.0,
            shadow_minutes=10.0,
        ),
        basis_functions.SlewtimeBasisFunction(bandname=None, nside=nside),
        # TODO: add basis function to mask out azimuth range at end of night
        # once SP-2080 functionality is available at summit.
    ]

    config_detailers = [
        detailers.DitherDetailer(max_dither=0.7, per_night=False),
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=45.0,
            min_rot=-45.0,
            per_visit_rot=1.0,
        ),
    ]

    observation_reason = "Full System ENGTEST"
    science_program = "BLOCK-T447"  # json BLOCK to be used

    tier = 0
    target_names = []
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

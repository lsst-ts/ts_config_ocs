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

import numpy as np
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

    # Defaults

    config_basis_functions = [
        basis_functions.NotTwilightBasisFunction(sun_alt_limit=-12.0),
        basis_functions.AltAzShadowMaskBasisFunction(
            nside=nside,
            min_alt=30.0,
            max_alt=83.0,
            shadow_minutes=10.0,
        ),
        basis_functions.AltAzShadowTimeLimitedBasisFunction(
            nside=nside,
            min_alt=30.0,
            max_alt=83.0,
            min_az=180.0,
            max_az=270.0,
            shadow_minutes=10.0,
            time_to_sun=3.0,
            sun_keys=["sunrise"],
        ),
        basis_functions.SlewtimeBasisFunction(bandname=None, nside=nside),
    ]

    observation_reason = "small field science"
    science_program = "BLOCK-365"  # json BLOCK to be used

    nvisits = {"u": 30, "g": 30, "r": 30, "i": 30, "z": 30, "y": 30}
    sequence = ["i"]
    # exposure time in seconds
    exptimes = {"u": 38.0, "g": 30.0, "r": 30.0, "i": 30.0, "z": 30.0, "y": 30.0}
    # 1 --> single 30 second exposure
    nexps = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}
    field_survey_kwargs = {
        "nvisits": nvisits,
        "sequence": sequence,
        "exptimes": exptimes,
        "nexps": nexps,
    }

    # LARGE FILL FACTOR TARGETS

    field_survey_kwargs["sequence"] = ["i"]

    # Carina
    # Custom landscape dither
    radius = np.sqrt(1.8)
    orientation = np.radians(-10.0)
    delta_ra = [-1.0 * radius * np.cos(orientation), radius * np.cos(orientation)]
    delta_dec = [-1.0 * radius * np.sin(orientation), radius * np.sin(orientation)]
    config_detailers = [
        detailers.DitherDetailer(max_dither=0.7, per_night=False),
        detailers.DeltaCoordDitherDetailer(delta_ra=delta_ra, delta_dec=delta_dec),
        # Note: 2 centers * 2 deg per visit * 30 visits = 120 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=60.0,
            min_rot=-60.0,
            per_visit_rot=2.0,
        ),
    ]
    tier = 0
    target_names = ["Carina"]
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # Trifid-Lagoon
    # Custom landscape dither
    radius = np.sqrt(1.8)
    orientation = np.radians(-10.0)
    delta_ra = [-1.0 * radius * np.cos(orientation), radius * np.cos(orientation)]
    delta_dec = [-1.0 * radius * np.sin(orientation), radius * np.sin(orientation)]
    config_detailers = [
        detailers.DitherDetailer(max_dither=0.7, per_night=False),
        detailers.DeltaCoordDitherDetailer(delta_ra=delta_ra, delta_dec=delta_dec),
        # Note: 2 centers * 2 deg per visit * 30 visits = 120 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=60.0,
            min_rot=-60.0,
            per_visit_rot=2.0,
        ),
    ]
    tier = 0
    target_names = ["Trifid-Lagoon"]
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # Prawn
    # Custom landscape dither
    radius = np.sqrt(1.8)
    orientation = np.radians(10.0)
    delta_ra = [-1.0 * radius * np.cos(orientation), radius * np.cos(orientation)]
    delta_dec = [-1.0 * radius * np.sin(orientation), radius * np.sin(orientation)]
    config_detailers = [
        detailers.DitherDetailer(max_dither=0.7, per_night=False),
        detailers.DeltaCoordDitherDetailer(delta_ra=delta_ra, delta_dec=delta_dec),
        # Note: 2 centers * 2 deg per visit * 30 visits = 120 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=60.0,
            min_rot=-60.0,
            per_visit_rot=2.0,
        ),
    ]
    tier = 0
    target_names = ["Prawn"]
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # LOW ECLIPTIC LATITUDE TARGETS

    field_survey_kwargs["sequence"] = ["i"]

    # Low ecliptic latitude, near opposition April / May
    # Detector scale dithers
    config_detailers = [
        detailers.DitherDetailer(max_dither=0.2, per_night=False),
        # Note: 1 center * 3 deg per visit * 30 visits = 90 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=45.0,
            min_rot=-45.0,
            per_visit_rot=3.0,
        ),
    ]
    tier = 0
    target_names = [
        "Rubin_SV_216_-17",
        "Rubin_SV_225_-19",
    ]
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # LSST DEEP DRILLING FIELDS

    field_survey_kwargs["sequence"] = ["i"]

    # LSST DDFs
    # Detector scale dithers
    config_detailers = [
        detailers.DitherDetailer(max_dither=0.2, per_night=False),
        # Note: 1 center * 3 deg per visit * 30 visits = 90 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=45.0,
            min_rot=-45.0,
            per_visit_rot=3.0,
        ),
    ]
    tier = 0
    target_names = [
        "COSMOS",
        "ELAIS_S1",
        "XMM_LSS",
        "ECDFS",
    ]
    make_scheduler.add_field_surveys(
        tier,
        observation_reason,
        science_program,
        target_names,
        basis_functions=config_basis_functions,
        detailers=config_detailers,
        **field_survey_kwargs,
    )

    # DENSELY DITHERED STAR FIELDS

    field_survey_kwargs["sequence"] = ["i"]

    # Densely dithered star fields
    # Spectrophotometric calibrators
    # Default for other fields
    # 2x raft scale dithers
    config_detailers = [
        detailers.DitherDetailer(max_dither=1.4, per_night=False),
        # Note: 1 center * 3 deg per visit * 30 visits = 90 deg
        detailers.CameraSmallRotPerObservationListDetailer(
            max_rot=45.0,
            min_rot=-45.0,
            per_visit_rot=3.0,
        ),
    ]
    tier = 0
    exclude = [
        "Carina",
        "Trifid-Lagoon",
        "Prawn",
        "Rubin_SV_216_-17",
        "Rubin_SV_225_-19",
        "COSMOS",
        "ELAIS_S1",
        "XMM_LSS",
        "ECDFS",
    ]
    target_names = get_sv_targets(target_file, exclude=exclude)

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

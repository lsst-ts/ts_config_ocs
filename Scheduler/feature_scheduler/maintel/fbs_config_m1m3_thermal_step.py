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

from rubin_scheduler.scheduler.basis_functions import (
    AltAzShadowMaskBasisFunction,
    AvoidDirectWind,
    VisitGap,
)
from rubin_scheduler.scheduler.detailers import AltAz2RaDecDetailer, ZeroRotDetailer
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import FieldAltAzSurvey


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

    survey_name = "BLOCK-T609"
    wind_speed_maximum = 20.0

    # FYI: There is a bug in the calculation of
    # the sky angle for the FieldAltAzSurvey which
    # which forced me to hard code the sky angle in
    # the observation block. If you change the az
    # you will have to update the sky angle in the
    # BLOCK-T609 block.
    regular_images_survey_alt = 60
    regular_images_survey_az = 179

    regular_images_survey_basis_functions = [
        AltAzShadowMaskBasisFunction(min_alt=26.0, max_alt=85.0, nside=nside),
        AvoidDirectWind(wind_speed_maximum=wind_speed_maximum, nside=nside),
    ]
    regular_images_survey_sequence = ["r"]
    regular_images_survey_nvisits = dict(r=1)
    regular_images_survey_exptimes = dict(r=30.0)
    regular_images_survey_nexps = dict(r=1)
    regular_images_survey_target_name = (
        f"Field{regular_images_survey_az}_{regular_images_survey_alt}"
    )
    regular_images_survey_science_program = "BLOCK-T609"
    regular_images_survey_detailers = [
        AltAz2RaDecDetailer(),
        ZeroRotDetailer(),
    ]

    additional_images_survey_target_name = (
        f"AdditionalField{regular_images_survey_az}_{regular_images_survey_alt}"
    )
    additional_images_survey_basis_functions = [
        VisitGap(
            note=additional_images_survey_target_name, gap_min=30.0, band_names=["r"]
        ),
        AltAzShadowMaskBasisFunction(min_alt=26.0, max_alt=85.0, nside=nside),
        AvoidDirectWind(wind_speed_maximum=wind_speed_maximum, nside=nside),
    ]
    additional_images_survey_science_program = "BLOCK-T609_1"
    additional_images_survey_detailers = [
        AltAz2RaDecDetailer(),
        ZeroRotDetailer(),
    ]

    regular_images_survey = FieldAltAzSurvey(
        basis_functions=regular_images_survey_basis_functions,
        alt=regular_images_survey_alt,
        az=regular_images_survey_az,
        sequence=regular_images_survey_sequence,
        nvisits=regular_images_survey_nvisits,
        exptimes=regular_images_survey_exptimes,
        nexps=regular_images_survey_nexps,
        ignore_obs=None,
        survey_name=survey_name,
        target_name=regular_images_survey_target_name,
        science_program=regular_images_survey_science_program,
        observation_reason="M1M3ThermalOnSkyTest",
        scheduler_note=regular_images_survey_target_name,
        nside=nside,
        flush_pad=30.0,
        detailers=regular_images_survey_detailers,
    )

    additional_images_survey = FieldAltAzSurvey(
        basis_functions=additional_images_survey_basis_functions,
        alt=regular_images_survey_alt,
        az=regular_images_survey_az,
        sequence=regular_images_survey_sequence,
        nvisits=regular_images_survey_nvisits,
        exptimes=regular_images_survey_exptimes,
        nexps=regular_images_survey_nexps,
        ignore_obs=None,
        survey_name=survey_name,
        target_name=additional_images_survey_target_name,
        science_program=additional_images_survey_science_program,
        observation_reason="M1M3ThermalOnSkyTest",
        scheduler_note=additional_images_survey_target_name,
        nside=nside,
        flush_pad=30.0,
        detailers=additional_images_survey_detailers,
    )

    survey_lists = [
        [additional_images_survey],
        [regular_images_survey],
    ]

    return nside, CoreScheduler(
        survey_lists,
        nside=nside,
        band_to_filter=band_to_filter,
    )


if __name__ == "config":
    nside, scheduler = get_scheduler()

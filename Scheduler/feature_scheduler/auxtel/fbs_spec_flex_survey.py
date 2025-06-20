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

from astropy import units
from astropy.coordinates import Angle
from lsst.ts.fbs.utils import Target
from lsst.ts.fbs.utils.auxtel.surveys import (
    generate_cwfs_survey,
    generate_image_survey_from_target,
    generate_spectroscopic_survey,
    get_auxtel_targets,
)
from rubin_scheduler.scheduler.detailers import DitherDetailer, FixedSkyAngleDetailer
from rubin_scheduler.scheduler.schedulers import CoreScheduler


def get_scheduler():
    """Construct feature based scheduler.

    Returns
    -------
    nside : int
        Healpix map resolution.
    scheduler : Core_scheduler
        Feature based scheduler.
    """
    # Information for all surveys
    nside = 32
    avoid_wind = False
    if avoid_wind:
        wind_speed_maximum = 13.0  # maximum direct wind in m/s
    else:
        wind_speed_maximum = 30

    # Detailers - for now, just simple image or spectroscopy detailers.
    image_detailers = [
        # Dither up to half the FOV, per exposure.
        DitherDetailer(max_dither=(7 / 2 / 60), per_night=False)
    ]
    spec_detailers_zero = [FixedSkyAngleDetailer(sky_angle=0)]
    spec_detailers_flip = [FixedSkyAngleDetailer(sky_angle=180)]
    # HA used in rubin-scheduler runs 0-24
    # The limits here are the *allowed* values
    spec_default_ha_limits = None
    flip_default = True

    # Get target information - edit YAML file for updates
    # YAML file should be in the same directory as this .py config
    # ts_config_ocs/Scheduler/feature_scheduler/auxtel/auxtel_targets.yaml
    target_dir = Path(__file__).parent
    target_file = Path.joinpath(target_dir, "auxtel_targets.yaml")
    if not Path.exists(target_file):
        raise ValueError(f"Expected target yaml file does not exist at {target_file}")
    target_pointings = get_auxtel_targets(target_file)

    # The targets below must be in the target_pointings
    # But can be specified to be all or just a subset

    # Imaging priority - high priority imaging, tier 1
    imaging_priority_targets = ["Photo08000-1"]
    # Imaging backup - low priority, tier -1
    # These are added because spectroscopy targets unavailable near transit
    # So if there are few spectroscopy targets, a backup imaging is good.
    imaging_backup_targets = ["Photo08000-1"]

    # Spectroscopy priority - high priority spectroscopy - tier 1
    spectroscopy_priority_targets = ["HD146233", "HD205905"]
    # Standard spectroscopy - tier 2
    spectroscopy_standard_targets = ["HD185975"]

    # Backup spectroscopy - tier 3
    spectroscopy_backup_targets = [
        "HD185975",
        "HD111980",
        "HD167060",
    ]

    # CWFS - tier 0
    cwfs_time_gap = 720.0  # Gap between cwfs images, in minutes
    cwfs_block = "BLOCK-305"

    cwfs_survey = generate_cwfs_survey(
        nside=nside,
        time_gap_min=cwfs_time_gap,
        wind_speed_maximum=wind_speed_maximum,
        cwfs_block_name=cwfs_block,
    )

    # Go through imaging targets ('auxtel_imaging_targets' category)
    imaging_priority = []
    imaging_backup = []
    for target_name in target_pointings["auxtel_imaging_targets"]:
        tt = target_pointings["auxtel_imaging_targets"][target_name]
        cat = "IMG"
        target = Target(
            target_name=target_name,
            survey_name=f"{cat}:{target_name}",
            science_program=tt["block"],
            ra=Angle(tt["ra"], unit=units.hourangle),
            dec=Angle(tt["dec"], unit=units.deg),
            hour_angle_limit=None,
            filters=["r"],
            visit_gap=tt.get("visit_gap", 0),
            exptime=tt.get("exptime", 30),
            nexp=tt.get("nexp", 8),
            reward_value=tt.get("priority", 1),
        )
        if target_name in imaging_priority_targets:
            imaging_priority.append(
                generate_image_survey_from_target(
                    nside=nside,
                    target=target,
                    wind_speed_maximum=wind_speed_maximum,
                    survey_detailers=image_detailers,
                    include_slew=False,
                )
            )
        if target_name in imaging_backup_targets:
            target = Target(
                target_name=target_name,
                survey_name=f"{cat}:{target_name} backup",
                science_program=tt["block"],
                ra=Angle(tt["ra"], unit=units.hourangle),
                dec=Angle(tt["dec"], unit=units.deg),
                hour_angle_limit=None,
                filters=["r"],
                visit_gap=0,
                exptime=tt.get("exptime", 30),
                nexp=1,
                reward_value=tt.get("priority", 1),
            )
            imaging_backup.append(
                generate_image_survey_from_target(
                    nside=nside,
                    target=target,
                    wind_speed_maximum=wind_speed_maximum,
                    survey_detailers=image_detailers,
                    include_slew=True,
                )
            )

    # Go through spectroscopy targets
    spectroscopy_categories = [
        "auxtel_candidate_catalog_targets",
        "auxtel_standard_catalog_targets",
    ]
    spectroscopy_priority = []
    spectroscopy_standard = []
    spectroscopy_backup = []
    for category in spectroscopy_categories:
        cat = category.split("_")[1].upper()
        for target_name in target_pointings[category]:
            tt = target_pointings[category][target_name]
            flip = tt.get("flip", flip_default)
            if flip:
                spec_detailers = spec_detailers_flip
            else:
                spec_detailers = spec_detailers_zero
            target = Target(
                target_name=target_name,
                survey_name=f"{cat}:{target_name}",
                science_program=tt["block"],
                ra=Angle(tt["ra"], unit=units.hourangle),
                dec=Angle(tt["dec"], unit=units.deg),
                hour_angle_limit=tt.get("ha_limits", spec_default_ha_limits),
                filters=["r"],
                visit_gap=tt.get("visit_gap", 0),
                exptime=tt.get("exptime", 300),
                nexp=tt.get("nexp", 1),
                reward_value=tt.get("priority", 1),
            )
            if target_name in spectroscopy_priority_targets:
                spectroscopy_priority.append(
                    generate_spectroscopic_survey(
                        nside=nside,
                        target=target,
                        wind_speed_maximum=wind_speed_maximum,
                        survey_detailers=spec_detailers,
                        include_slew=False,
                        nfields=0,
                        avoid_wind=avoid_wind,
                    )
                )
            if target_name in spectroscopy_standard_targets:
                spectroscopy_standard.append(
                    generate_spectroscopic_survey(
                        nside=nside,
                        target=target,
                        wind_speed_maximum=wind_speed_maximum,
                        survey_detailers=spec_detailers,
                        include_slew=False,
                        nfields=0,
                        avoid_wind=avoid_wind,
                    )
                )
            if target_name in spectroscopy_backup_targets:
                target = Target(
                    target_name=target_name,
                    survey_name=f"{cat}:{target_name} backup",
                    science_program=tt["block"],
                    ra=Angle(tt["ra"], unit=units.hourangle),
                    dec=Angle(tt["dec"], unit=units.deg),
                    hour_angle_limit=tt.get("ha_limits", spec_default_ha_limits),
                    filters=["r"],
                    visit_gap=0,
                    exptime=tt.get("exptime", 400),
                    nexp=1,
                    reward_value=tt.get("priority", 1),
                )
                spectroscopy_backup.append(
                    generate_spectroscopic_survey(
                        nside=nside,
                        target=target,
                        wind_speed_maximum=wind_speed_maximum,
                        survey_detailers=spec_detailers,
                        include_slew=False,
                        nfields=0,
                        avoid_wind=avoid_wind,
                    )
                )

    # assemble surveys into list of lists
    surveys = [
        [cwfs_survey],
        spectroscopy_priority,
        spectroscopy_standard,
        spectroscopy_backup,
        imaging_backup,
    ]

    scheduler = CoreScheduler(
        surveys=surveys,
        nside=nside,
        telescope="rubin",
    )
    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

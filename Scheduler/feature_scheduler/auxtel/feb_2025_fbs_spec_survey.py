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

from astropy import units
from astropy.coordinates import Angle
from lsst.ts.fbs.utils import Target
from lsst.ts.fbs.utils.auxtel.surveys import (
    generate_cwfs_survey,
    generate_image_survey_from_target,
    generate_spectroscopic_survey,
    get_auxtel_targets,
)
from rubin_scheduler.scheduler.detailers import DitherDetailer
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
    nside = 64
    avoid_wind = False
    if avoid_wind:
        wind_speed_maximum = 13.0  # maximum direct wind in m/s
    else:
        wind_speed_maximum = 0

    # Get target information - edit YAML file for updates
    target_pointings = get_auxtel_targets("auxtel_targets.yaml")
    # It would be possible to drop targets here too, but easier in yaml.

    # CWFS - tier 0
    cwfs_time_gap = 120.0  # Gap between cwfs images, in minutes
    cwfs_block = "BLOCK-305"

    cwfs_survey = generate_cwfs_survey(
        nside=nside,
        time_gap_min=cwfs_time_gap,
        wind_speed_maximum=wind_speed_maximum,
        cwfs_block_name=cwfs_block,
    )

    # Tier 1 will be primary surveys
    # This includes imaging survey and spectroscopic surveys

    # IMAGING
    image_nexp = 8  # number of imaging exposures in sequence (per filter)
    image_filters = ["r"]
    image_exptime = 35.0  # total exposure time in seconds
    image_visit_gap = 10 * 60  # gap between return visits, in minutes
    image_detailers = [
        # Dither up to half the FOV, per exposure.
        DitherDetailer(max_dither=(7 / 2 / 60), per_night=False)
    ]
    # Note we will put imaging program in backup tier as well

    imaging_priority = []
    imaging_backup = []
    for target_name in target_pointings["auxtel_imaging_targets"]:
        tt = target_pointings["auxtel_imaging_targets"][target_name]
        cat = "IMG"
        target = Target(
            target_name=target_name,
            survey_name=f"{cat}:{target_name}",
            scheduler_note=f"{target_name}",
            science_program=tt["block"],
            ra=Angle(tt["ra"], unit=units.hourangle),
            dec=Angle(tt["dec"], unit=units.deg),
            hour_angle_limit=[],
            filters=image_filters,
            visit_gap=image_visit_gap,
            exptime=image_exptime,
            nexp=image_nexp,
            reward_value=tt.get("priority", 1),
        )
        imaging_priority.append(
            generate_image_survey_from_target(
                nside=nside,
                target=target,
                wind_speed_maximum=wind_speed_maximum,
                survey_detailers=image_detailers,
                include_slew=False,
            )
        )
        # Add to backup tier with similar setup, but no visit_gap
        target.visit_gap = 0
        imaging_backup.append(
            generate_image_survey_from_target(
                nside=nside,
                target=target,
                wind_speed_maximum=wind_speed_maximum,
                survey_detailers=image_detailers,
                include_slew=True,
            )
        )

    # SPECTROSCOPY
    # The Spectroscopy targets are handled with more complicated
    # JSON BLOCKS. The exptime is pulled from the yaml, because
    # it can vary widely (needs improvement). The nexp is always 1,
    # and filters don't matter (as long as only one listed).
    spec_detailers = []
    spectroscopy_categories = ["auxtel_wd_targets", "auxtel_calspec_targets"]
    spectroscopy_priority = []
    for category in spectroscopy_categories:
        cat = category.split("_")[1].upper()
        for target_name in target_pointings[category]:
            tt = target_pointings[category][target_name]
            target = Target(
                target_name=target_name,
                survey_name=f"{cat}:{target_name}",
                science_program=tt["block"],
                ra=Angle(tt["ra"], unit=units.hourangle),
                dec=Angle(tt["dec"], unit=units.deg),
                hour_angle_limit=[],
                filters=["r"],
                visit_gap=tt.get("visit_gap", 5),
                exptime=tt.get("exptime", 300),
                nexp=1,
                reward_value=tt.get("priority", 1),
            )
            spectroscopy_priority.append(
                generate_spectroscopic_survey(
                    nside=nside,
                    target=target,
                    wind_speed_maximum=wind_speed_maximum,
                    survey_detailers=spec_detailers,
                    include_slew=False,
                )
            )

    # assemble surveys into list of lists
    surveys = [
        [cwfs_survey],
        [imaging_priority + spectroscopy_priority],
        [imaging_backup],
    ]

    scheduler = CoreScheduler(
        surveys=surveys,
        nside=nside,
        telescope="auxtel",
    )
    return nside, scheduler


if __name__ == "config":
    nside, scheduler = get_scheduler()

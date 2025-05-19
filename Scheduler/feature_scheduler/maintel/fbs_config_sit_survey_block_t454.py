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
)
from rubin_scheduler.scheduler import detailers, surveys


def get_scheduler():
    """Construct feature based scheduler

    Returns
    -------
    nside : int
        Healpix map resolution
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

    nvisits = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}
    sequence = ["u", "g", "r", "i", "z", "y"]

    # exposure time in seconds
    exptimes = {"u": 38, "g": 30, "r": 15, "i": 30, "z": 30, "y": 30}
    # 1 --> single 30 second exposuree
    nexps = {"u": 1, "g": 1, "r": 1, "i": 1, "z": 1, "y": 1}

    target_name = "SimTarget"
    observation_reason = "All day CCD clearing"
    science_program = "BLOCK-T454"  # json BLOCK to be used
    survey_name = science_program  # match nextVisit metadata

    config_detailers = [
        detailers.AltAz2RaDecDetailer(),
        detailers.TrackingInfoDetailer(
            science_program=survey_name,
            target_name=target_name,
        ),
    ]

    config_basis_functions = []

    make_scheduler = MakeFieldSurveyScheduler(
        targets=dict(),
        nside=nside,
        ntiers=1,
        band_to_filter=band_to_filter,
    )
    make_scheduler.surveys[0].append(
        surveys.FieldAltAzSurvey(
            basis_functions=config_basis_functions,
            alt=45,
            az=0,
            sequence=sequence,
            nvisits=nvisits,
            exptimes=exptimes,
            nexps=nexps,
            ignore_obs=None,
            survey_name=survey_name,
            target_name=target_name,
            science_program=science_program,
            observation_reason=observation_reason,
            scheduler_note=target_name,
            nside=nside,
            flush_pad=30.0,
            detailers=config_detailers,
        )
    )

    return make_scheduler.get_scheduler()


if __name__ == "config":
    nside, scheduler = get_scheduler()

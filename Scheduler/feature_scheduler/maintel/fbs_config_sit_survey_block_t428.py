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
import rubin_scheduler.scheduler.basis_functions as bf
import rubin_scheduler.scheduler.detailers as detailers
from rubin_scheduler.scheduler.model_observatory import ModelObservatory
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import GreedySurvey
from rubin_scheduler.scheduler.utils import Footprint, SkyAreaGenerator
from rubin_scheduler.utils import SURVEY_START_MJD as MJD_START


def gen_greedy_surveys(
    nside=32,
    nexp=1,
    exptime=30.0,
    filters=["g", "r", "z"],
    camera_rot_limits=[-80.0, 80.0],
    shadow_minutes=60.0,
    max_alt=76.0,
    moon_distance=30.0,
    ignore_obs="DD",
    footprint_weight=0.3,
    slewtime_weight=3.0,
    stayfilter_weight=3.0,
    footprints=None,
    seed=42,
):
    """Generate a feature scheduler survey configuration that does not employ
    any daylight constraints. Useful for unit testing.

    This is a convenience function to generate a list of survey objects that
    can be used with lsst.sims.featureScheduler.schedulers.CoreScheduler.
    To ensure we are robust against changes in the sims_featureScheduler
    codebase, all kwargs are explicitly set.

    Parameters
    ----------
    nside : int (32)
        The HEALpix nside to use.
    nexp : int (1)
        The number of exposures to use in a visit.
    exptime : float (30.)
        The exposure time to use per visit (seconds).
    filters : list of str (['r', 'i', 'z', 'y'])
        Which filters to generate surveys for.
    camera_rot_limits : list of float ([-80., 80.])
        The limits to impose when rotationally dithering the camera (degrees).
    shadow_minutes : float (60.)
        Used to mask regions around zenith (minutes).
    max_alt : float (76.)
        The maximium altitude to use when masking zenith (degrees).
    moon_distance : float (30.)
        The mask radius to apply around the moon (degrees).
    ignore_obs : str or list of str ('DD')
        Ignore observations by surveys that include the given substring(s).
    footprint_weight : float (0.3)
        The weight on the survey footprint basis function.
    slewtime_weight : float (3.)
        The weight on the slewtime basis function.
    stayfilter_weight : float (3.)
        The weight on basis function that tries to stay avoid filter changes.
    seed : int (42)
        The random generator seed.
    """
    # Define the extra parameters that are used in the greedy survey. I
    # think these are fairly set, so no need to promote to utility func kwargs
    greed_survey_params = {
        "block_size": 1,
        "smoothing_kernel": None,
        "seed": seed,
        "camera": "LSST",
        "dither": True,
        "survey_name": "BLOCK-T428",
    }

    surveys = []
    survey_detailers = [
        detailers.TrackingInfoDetailer(
            science_program=greed_survey_params["survey_name"], target_name="SimTarget"
        ),
        detailers.CameraRotDetailer(
            min_rot=np.min(camera_rot_limits), max_rot=np.max(camera_rot_limits)
        ),
    ]

    for filtername in filters:
        bfs = [
            (
                bf.FootprintBasisFunction(
                    filtername=filtername,
                    footprint=footprints,
                    out_of_bounds_val=np.nan,
                    nside=nside,
                ),
                footprint_weight,
            ),
            (
                bf.SlewtimeBasisFunction(filtername=filtername, nside=nside),
                slewtime_weight,
            ),
            (
                bf.AltAzShadowMaskBasisFunction(
                    nside=nside,
                    shadow_minutes=shadow_minutes,
                    max_alt=max_alt,
                    min_alt=30.0,
                ),
                0,
            ),
            (bf.AvoidFastRevisitsBasisFunction(bandname=filtername, gap_min=60.0), 0),
        ]

        weights = [val[1] for val in bfs]
        basis_functions = [val[0] for val in bfs]
        surveys.append(
            GreedySurvey(
                basis_functions,
                weights,
                exptime=exptime,
                filtername=filtername,
                nside=nside,
                ignore_obs=ignore_obs,
                nexp=nexp,
                detailers=survey_detailers,
                **greed_survey_params,
            )
        )

    return surveys


if __name__ == "config":
    nside = 32
    per_night = True  # Dither DDF per night
    seed = 42

    camera_ddf_rot_limit = 75.0

    observatory = ModelObservatory(nside=nside, mjd_start=MJD_START)
    observatory.sky_model.load_length = 3
    conditions = observatory.return_conditions()

    sky = SkyAreaGenerator(nside=nside)
    footprints_hp, footprints_labels = sky.return_maps()

    footprints = Footprint(MJD_START, sun_ra_start=conditions.sun_ra, nside=nside)
    for i, key in enumerate(footprints_hp.dtype.names):
        footprints.footprints[i, :] = footprints_hp[key]

    greedy = gen_greedy_surveys(
        nside, nexp=1, footprints=footprints, seed=seed, filters=["r"]
    )
    surveys = [greedy]
    scheduler = CoreScheduler(surveys, nside=nside)

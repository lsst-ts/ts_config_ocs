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
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import FieldSurvey


def gen_field_survey(
    name,
    ra=0.0,
    dec=-70.0,
    sequence=["r_03"],
    visits=1,
    nexp=1,
    exptime=30.0,
    nside=32,
    camera_rot_limits=[-80.0, 80.0],
    shadow_minutes=60.0,
    max_alt=86.0,
    ignore_obs="DD",
    slewtime_weight=3.0,
    stayfilter_weight=3.0,
):
    """A survey class for running field surveys.

    Parameters
    ----------
    name : `str`  name of survey
    RA : `float`
        The RA of the field (degrees)
    dec : `float`
        The dec of the field to observe (degrees)
    sequence : `list` [`str`]
        The sequence of observations to take. (specify which filters to use).
    nvisits : `dict` {`str`: `int`}
        Dictionary of the number of visits in each filter.
        Default of None will use a backup sequence of 20 visits per filter.
        Must contain all filters in sequence.
    exptimes : `dict` {`str`: `float`}
        Dictionary of the exposure time for visits in each filter.
        Default of None will use a backup sequence of 38s in u, and
        29.2s in all other bands. Must contain all filters in sequence.
    nexps : dict` {`str`: `int`}
        Dictionary of the number of exposures per visit in each filter.
        Default of None will use a backup sequence of 1 exposure per visit
        in u band, 2 in all other bands. Must contain all filters in sequence.
    ignore_obs : `list` [`str`] or None
        Ignore observations with this string in the `scheduler_note`.
        Will ignore observations which match subsets of the string, as well as
        the entire string. Ignoring 'mysurvey23' will also ignore 'mysurvey2'.
    survey_name : `str` or None.
        The name to give this survey, for debugging and visualization purposes.
        Also propagated to the 'target_name' in the observation.
        The default None will construct a name based on the
        RA/Dec of the field.
    nside : `float` or None
        Nside for computing survey basis functions and maps.
        The default of None will use rubin_scheduler.utils.set_default_nside().
    camera_rot_limits : list of float ([-80., 80.])
        The limits to impose when rotationally dithering the camera (degrees).
    shadow_minutes : float (60.)
        Used to mask regions around zenith (minutes).
    max_alt : float (76.)
        The maximium altitude to use when masking zenith (degrees).
    ignore_obs : str or list of str ('DD')
        Ignore observations by surveys that include the given substring(s).
    slewtime_weight : float (3.)
        The weight on the slewtime basis function.
    stayfilter_weight : float (3.)
        The weight on basis function that tries to stay avoid filter changes.
    """
    # Define the extra parameters that are used in the greedy survey. I
    # think these are fairly set, so no need to promote to utility func kwargs

    survey_detailers = [
        detailers.TrackingInfoDetailer(science_program=name),
        detailers.CameraRotDetailer(
            min_rot=np.min(camera_rot_limits), max_rot=np.max(camera_rot_limits)
        ),
    ]

    for filtername in sequence:
        bfs = [
            (bf.StrictFilterBasisFunction(filtername=filtername), stayfilter_weight),
            (bf.FilterLoadedBasisFunction(filternames=filtername), 0),
            (bf.VisitGap(name, gap_min=720.0), 0),
        ]

        exptimes = {filter: exptime for filter in sequence}
        nexps = {filter: nexp for filter in sequence}
        nvisits = {filter: visits for filter in sequence}
        basis_functions = [val[0] for val in bfs]
        survey = FieldSurvey(
            basis_functions,
            ra,
            dec,
            sequence=sequence,
            exptimes=exptimes,
            nexps=nexps,
            nvisits=nvisits,
            nside=nside,
            ignore_obs=ignore_obs,
            detailers=survey_detailers,
            survey_name=name,
            science_program=name,
        )

    return survey


if __name__ == "config":
    nside = 32

    filters_list = ["r_03"]

    surveys = []
    for i in range(0, 30):
        surveys.append(gen_field_survey(f"BLOCK-T248_{i}", sequence=filters_list))
    scheduler = CoreScheduler(surveys, nside=nside)

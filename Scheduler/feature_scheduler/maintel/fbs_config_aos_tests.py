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


import datetime

import healpy as hp
import numpy as np
import rubin_scheduler.scheduler.basis_functions as bf
from astropy.coordinates import get_sun
from astropy.time import Time
from rubin_scheduler.scheduler import detailers
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import BlobSurvey
from rubin_scheduler.scheduler.utils import Footprint
from rubin_scheduler.utils import DEFAULT_NSIDE, hpid2_ra_dec


def standard_bf(
    nside,
    bandname="g",
    bandname2="i",
    m5_weight=6.0,
    footprint_weight=1.5,
    slewtime_weight=3.0,
    stayband_weight=3.0,
    footprints=None,
    season=365.25,
    season_start_hour=-4.0,
    season_end_hour=2.0,
    moon_distance=30.0,
    strict=True,
    wind_speed_maximum=20.0,
):
    """Generate the standard basis functions that are shared by blob surveys

    Parameters
    ----------
    nside : `int`
        The HEALpix nside to use. Defaults to DEFAULT_NSIDE
    bandname : `str`
        The band name for the first observation. Default "g".
    bandname2 : `str`
        The band name for the second in the pair (None if unpaired).
        Default "i".
    season : `float`
        The length of season (i.e., how long before templates expire) (days).
        Default 365.25.
    season_start_hour : `float`
        Hour angle limits to use when gathering templates.
        Default -4 (hours)
    sesason_end_hour : `float`
       Hour angle limits to use when gathering templates.
       Default +2 (hours)
    moon_distance : `float`
        The mask radius to apply around the moon (degrees).
        Default 30.
    m5_weight : `float`
        The weight for the 5-sigma depth difference basis function.
        Default 6.0 (unitless)
    footprint_weight : `float`
        The weight on the survey footprint basis function.
        Default 0.3 (unitless)
    slewtime_weight : `float`
        The weight on the slewtime basis function. Default 3 (unitless).
    stayband_weight : `float`
        The weight on basis function that tries to stay avoid band changes.
        Default 3 (unitless).

    Returns
    -------
    basis_functions_weights : `list`
        list of tuple pairs (basis function, weight) that is
        (rubin_scheduler.scheduler.BasisFunction object, float)

    """

    bfs = []

    if bandname2 is not None:
        bfs.append(
            (
                bf.M5DiffBasisFunction(bandname=bandname, nside=nside),
                m5_weight / 2.0,
            )
        )
        bfs.append(
            (
                bf.M5DiffBasisFunction(bandname=bandname2, nside=nside),
                m5_weight / 2.0,
            )
        )

    else:
        bfs.append((bf.M5DiffBasisFunction(bandname=bandname, nside=nside), m5_weight))

    if bandname2 is not None:
        bfs.append(
            (
                bf.FootprintBasisFunction(
                    bandname=bandname,
                    footprint=footprints,
                    out_of_bounds_val=np.nan,
                    nside=nside,
                ),
                footprint_weight / 2.0,
            )
        )
        bfs.append(
            (
                bf.FootprintBasisFunction(
                    bandname=bandname2,
                    footprint=footprints,
                    out_of_bounds_val=np.nan,
                    nside=nside,
                ),
                footprint_weight / 2.0,
            )
        )
    else:
        bfs.append(
            (
                bf.FootprintBasisFunction(
                    bandname=bandname,
                    footprint=footprints,
                    out_of_bounds_val=np.nan,
                    nside=nside,
                ),
                footprint_weight,
            )
        )

    bfs.append(
        (
            bf.SlewtimeBasisFunction(bandname=bandname, nside=nside),
            slewtime_weight,
        )
    )
    if strict:
        bfs.append((bf.StrictBandBasisFunction(bandname=bandname), stayband_weight))
    else:
        bfs.append((bf.BandChangeBasisFunction(bandname=bandname), stayband_weight))

    # The shared masks
    bfs.append(
        (
            bf.MoonAvoidanceBasisFunction(nside=nside, moon_distance=moon_distance),
            0.0,
        )
    )
    bfs.append(
        (bf.AvoidDirectWind(nside=nside, wind_speed_maximum=wind_speed_maximum), 0)
    )
    bandnames = [fn for fn in [bandname, bandname2] if fn is not None]
    bfs.append((bf.BandLoadedBasisFunction(bandnames=bandnames), 0))
    bfs.append((bf.PlanetMaskBasisFunction(nside=nside), 0.0))

    return bfs


def generate_blobs(
    nside,
    nexp=2,
    exptime=30,
    band1s=["u", "u", "g", "r", "i", "z", "y"],
    band2s=["g", "r", "r", "i", "z", "y", "y"],
    pair_time=33.0,
    camera_rot_limits=[-80.0, 80.0],
    season=365.25,
    season_start_hour=-4.0,
    season_end_hour=2.0,
    shadow_minutes=60.0,
    max_alt=76.0,
    moon_distance=30.0,
    ignore_obs=["DD", "twilight_near_sun"],
    m5_weight=6.0,
    footprint_weight=1.5,
    slewtime_weight=3.0,
    stayband_weight=3.0,
    footprints=None,
    u_nexp1=True,
    scheduled_respect=0.0,
    mjd_start=1,
    repeat_weight=-20,
    u_exptime=38.0,
    target_name=None,
    science_program=None,
    observation_reason=None,
):
    """
    Generate surveys that take observations in blobs.

    Parameters
    ----------
    nside : `int`
        The HEALpix nside to use
    nexp : int
        The number of exposures to use in a visit.
        Default 1.
    exptime : `float`
        The exposure time to use per visit (seconds).
        Default 30
    band1s : `list` [`str`]
        The bandnames for the first set.
        Default ["u", "u", "g", "r", "i", "z", "y"]
    band2s : `list` of `str`
        The band names for the second in the pair (None if unpaired)
        Default ["g", "r", "r", "i", "z", "y", "y"].
    pair_time : `float`
        The ideal time between pairs (minutes).
        Default 33.
    camera_rot_limits : `list` of `float`
        The limits to impose when rotationally dithering the camera (degrees).
        Default [-80., 80.].
    n_obs_template : `dict`
        The number of observations to take every season in each band.
        If None, sets to 3 each.
    season : `float`
        The length of season (i.e., how long before templates expire) (days).
        Default 365.25.
    season_start_hour : `float`
        Hour angle limits to use when gathering templates.
        Default -4 (hours)
    sesason_end_hour : `float`
       Hour angle limits to use when gathering templates.
       Default +2 (hours)
    shadow_minutes : `float`
        Used to mask regions around zenith (minutes).
        Default 60.
    max_alt : `float`
        The maximium altitude to use when masking zenith (degrees).
        Default 76.
    moon_distance : `float`
        The mask radius to apply around the moon (degrees).
        Default 30.
    ignore_obs : `str` or `list` of `str`
        Ignore observations by surveys that include the given substring(s).
        Default ["DD", "twilight_near_sun"].
    m5_weight : `float`
        The weight for the 5-sigma depth difference basis function.
        Default 3 (unitless).
    footprint_weight : `float`
        The weight on the survey footprint basis function.
        Default 0.3 (uniteless).
    slewtime_weight : `float`
        The weight on the slewtime basis function.
        Default 3.0 (uniteless).
    stayband_weight : `float`
        The weight on basis function that tries to stay avoid band changes.
        Default 3.0 (uniteless).
    u_nexp1 : `bool`
        Add a detailer to make sure the number of expossures in a visit
        is always 1 for u observations. Default True.
    scheduled_respect : `float`
        How much time to require there be before a pre-scheduled
        observation (minutes). Default 45.
    """

    BlobSurvey_params = {
        "slew_approx": 7.5,
        "band_change_approx": 140.0,
        "read_approx": 2.0,
        "flush_time": 30.0,
        "smoothing_kernel": None,
        "nside": nside,
        "seed": 42,
        "dither": "night",
        "twilight_scale": False,
    }

    surveys = []

    for bandname, bandname2 in zip(band1s, band2s):
        detailer_list = []
        detailer_list.append(
            detailers.CameraRotDetailer(
                min_rot=np.min(camera_rot_limits), max_rot=np.max(camera_rot_limits)
            )
        )
        detailer_list.append(detailers.CloseAltDetailer())
        detailer_list.append(detailers.FlushForSchedDetailer())
        detailer_list.append(
            detailers.TrackingInfoDetailer(
                target_name=target_name,
                science_program=science_program,
                observation_reason=observation_reason,
            )
        )
        # List to hold tuples of (basis_function_object, weight)
        bfs = []
        bfs.extend(
            standard_bf(
                nside,
                bandname=bandname,
                bandname2=bandname2,
                m5_weight=m5_weight,
                footprint_weight=footprint_weight,
                slewtime_weight=slewtime_weight,
                stayband_weight=stayband_weight,
                footprints=footprints,
                season=season,
                season_start_hour=season_start_hour,
                season_end_hour=season_end_hour,
            )
        )

        bfs.append(
            (
                bf.VisitRepeatBasisFunction(
                    gap_min=0, gap_max=3 * 60.0, bandname=None, nside=nside, npairs=20
                ),
                repeat_weight,
            )
        )

        # Make sure we respect scheduled observations
        bfs.append((bf.TimeToScheduledBasisFunction(time_needed=scheduled_respect), 0))
        # Masks, give these 0 weight
        bfs.append(
            (
                bf.AltAzShadowMaskBasisFunction(
                    nside=nside, shadow_minutes=shadow_minutes, max_alt=max_alt, pad=3.0
                ),
                0.0,
            )
        )

        # unpack the basis functions and weights
        weights = [val[1] for val in bfs]
        basis_functions = [val[0] for val in bfs]
        if bandname2 is None:
            survey_name = "pair_%i, %s" % (pair_time, bandname)
        else:
            survey_name = "pair_%i, %s%s" % (pair_time, bandname, bandname2)
        if bandname2 is not None:
            detailer_list.append(detailers.TakeAsPairsDetailer(bandname=bandname2))

        if u_nexp1:
            detailer_list.append(
                detailers.BandNexp(bandname="u", nexp=1, exptime=u_exptime)
            )
        surveys.append(
            BlobSurvey(
                basis_functions,
                weights,
                bandname1=bandname,
                bandname2=bandname2,
                exptime=exptime,
                ideal_pair_time=pair_time,
                survey_name=survey_name,
                ignore_obs=ignore_obs,
                nexp=nexp,
                detailers=detailer_list,
                **BlobSurvey_params,
            )
        )

    return surveys


if __name__ == "config":

    nside = DEFAULT_NSIDE
    nexp = 1  # number of snaps per visit

    band_to_filter = {
        "u": "u_24",
        "g": "g_6",
        "r": "r_57",
        "i": "i_39",
        "z": "z_20",
        "y": "y_10",
    }

    # set the start to 2 days ago
    start_from_now = -2
    t_now = Time(datetime.datetime.now(datetime.UTC), scale="utc")
    mjd_start = t_now.mjd + start_from_now
    sun_loc = get_sun(Time(mjd_start, format="mjd"))

    # Set footprint as constant up to dec +33
    ra, dec = hpid2_ra_dec(nside, np.arange(hp.nside2npix(nside)))
    footprint = np.zeros(ra.size)
    footprint[np.where(dec < 33)] = 1

    fp = Footprint(mjd_start, sun_loc.ra.rad)
    for bandname in "ugrizy":
        fp.set_footprint(bandname, footprint)

    blobs = generate_blobs(
        nside,
        nexp=nexp,
        footprints=fp,
        mjd_start=mjd_start,
        band1s=["u", "u", "g", "r", "i", "z", "y"],
        band2s=["g", "r", "r", "i", "z", "y", "y"],
        camera_rot_limits=[-60.0, 60.0],
        target_name="all_sky_aos_test",
        science_program="BLOCK-365",
        observation_reason="BLOCK-T548",
    )

    surveys = blobs

    scheduler = CoreScheduler(surveys, nside=nside, band_to_filter=band_to_filter)

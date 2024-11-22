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
from lsst.ts.fbs.utils.maintel.make_fieldsurvey_scheduler import (
    MakeFieldSurveyScheduler,
    get_comcam_sv_targets,
)
from rubin_scheduler.scheduler import basis_functions, detailers
from rubin_scheduler.scheduler.detailers import BaseDetailer
from rubin_scheduler.scheduler.utils import wrap_ra_dec
from rubin_scheduler.utils import (
    _approx_ra_dec2_alt_az,
    gnomonic_project_tosky,
    rotation_converter,
)


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

    nvisits = {"u_02": 24, "g_01": 24, "r_03": 24, "i_06": 24, "z_03": 24, "y": 24}
    sequence = ["r_03", "i_06", "z_03"]
    # exposure time in seconds
    exptimes = {"u_02": 38, "g_01": 30, "r_03": 30, "i_06": 30, "z_03": 30, "y": 30}
    # 1 --> single 30 second exposure
    nexps = {"u_02": 1, "g_01": 1, "r_03": 1, "i_06": 1, "z_03": 1, "y": 1}

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
            min_alt=20.0,
            max_alt=83.0,
            shadow_minutes=2.0,
        ),
        basis_functions.SlewtimeBasisFunction(filtername="u_02", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="g_01", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="r_03", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="i_06", nside=nside),
        basis_functions.SlewtimeBasisFunction(filtername="z_03", nside=nside),
        basis_functions.FilterLoadedBasisFunction(filternames=sequence),
    ]

    config_detailers = [
        # detailers.DitherDetailer(max_dither=0.2, per_night=False),
        # detailers.CameraRotDetailer(max_rot=10.0, min_rot=-10.0),
        detailers.ComCamGridDitherDetailer(),
    ]

    observation_reason = "science"
    science_program = "BLOCK-320"  # json BLOCK to be used

    tier = 0
    target_names = get_comcam_sv_targets().keys()
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


class ComCamGridDitherDetailer(BaseDetailer):
    """
    Generate an offset pattern to synthesize a 2x2 grid of ComCam pointings.

    Parameters
    ----------
    rotSkyPos : `float`, (0.)
        The rotation angle of the camera relative to the sky E of N. (degrees)
    scale : `float` (0.355)
        Half of the offset between grid pointing centers. (degrees)
    dither : `float` (0.05)
        Dither offsets within grid to fill chip gaps. (degrees)
    telescope : `str`, optional
        Telescope name. Options of "rubin" or "auxtel". Default "rubin".
        This is used to determine conversions between rotSkyPos and rotTelPos.
    """

    def __init__(
        self, rotTelPos_desired=0.0, scale=0.355, dither=0.05, telescope="comcam"
    ):
        self.rotTelPos_desired = np.radians(rotTelPos_desired)
        self.scale = np.radians(scale)
        self.dither = np.radians(dither)
        self.rc = rotation_converter(telescope=telescope)

    def _rotate(self, x, y, angle):
        x_rot = x * np.cos(angle) - y * np.sin(angle)
        y_rot = x * np.sin(angle) + y * np.cos(angle)
        return x_rot, y_rot

    def _generate_offsets(self, n_offsets, filter_list, rotSkyPos):
        # 2 x 2 pointing grid
        x_grid = np.array(
            [-1.0 * self.scale, -1.0 * self.scale, self.scale, self.scale]
        )
        y_grid = np.array(
            [-1.0 * self.scale, self.scale, self.scale, -1.0 * self.scale]
        )
        x_grid_rot, y_grid_rot = self._rotate(x_grid, y_grid, -1.0 * rotSkyPos)
        offsets_grid_rot = np.array([x_grid_rot, y_grid_rot]).T

        # Dither pattern within grid to fill chip gaps
        # Psuedo-random offsets
        x_dither = np.array(
            [
                0.0,
                -0.5 * self.dither,
                -1.25 * self.dither,
                1.5 * self.dither,
                0.75 * self.dither,
            ]
        )
        y_dither = np.array(
            [
                0.0,
                -0.75 * self.dither,
                1.5 * self.dither,
                1.25 * self.dither,
                -0.5 * self.dither,
            ]
        )
        x_dither_rot, y_dither_rot = self._rotate(x_dither, y_dither, -1.0 * rotSkyPos)
        offsets_dither_rot = np.array([x_dither_rot, y_dither_rot]).T

        # Find the indices of the filter changes
        filter_changes = np.where(
            np.array(filter_list[:-1]) != np.array(filter_list[1:])
        )[0]
        filter_changes = np.concatenate([np.array([-1]), filter_changes])
        filter_changes += 1

        offsets = []
        index_filter = 0
        for ii in range(0, n_offsets):
            if ii in filter_changes:
                # Reset the count after each filter change
                index_filter = 0

            index_grid = index_filter % 4
            index_dither = np.floor(index_filter / 4).astype(int) % 5
            offsets.append(
                offsets_grid_rot[index_grid] + offsets_dither_rot[index_dither]
            )
            index_filter += 1

        return np.vstack(offsets)

    def __call__(self, observation_list, conditions):
        if len(observation_list) == 0:
            return observation_list

        filter_list = [np.asarray(obs["filter"]).item() for obs in observation_list]

        # Initial estimate of rotSkyPos corresponding to desired rotTelPos
        alt, az, pa = _approx_ra_dec2_alt_az(
            observation_list[0]["RA"],
            observation_list[0]["dec"],
            conditions.site.latitude_rad,
            conditions.site.longitude_rad,
            conditions.mjd,
            return_pa=True,
        )
        rotSkyPos = self.rc._rottelpos2rotskypos(self.rotTelPos_desired, pa)

        # Generate offsets in RA and Dec
        offsets = self._generate_offsets(len(observation_list), filter_list, rotSkyPos)

        # Project offsets onto sky
        obs_array = np.concatenate(observation_list)
        new_ra, new_dec = gnomonic_project_tosky(
            offsets[:, 0], offsets[:, 1], obs_array["RA"], obs_array["dec"]
        )
        new_ra, new_dec = wrap_ra_dec(new_ra, new_dec)

        # Update observations
        for ii in range(0, len(observation_list)):
            observation_list[ii]["RA"] = new_ra[ii]
            observation_list[ii]["dec"] = new_dec[ii]

            alt, az, pa = _approx_ra_dec2_alt_az(
                new_ra[ii],
                new_dec[ii],
                conditions.site.latitude_rad,
                conditions.site.longitude_rad,
                conditions.mjd,
                return_pa=True,
            )
            observation_list[ii]["rotSkyPos"] = rotSkyPos
            observation_list[ii]["rotTelPos"] = self.rc._rotskypos2rottelpos(
                rotSkyPos, pa
            )

        return observation_list


if __name__ == "config":
    nside, scheduler = get_scheduler()

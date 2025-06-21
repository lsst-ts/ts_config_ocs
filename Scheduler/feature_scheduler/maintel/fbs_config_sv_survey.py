from pathlib import Path

import lsst.ts.fbs.utils.maintel.sv_config as svc
import lsst.ts.fbs.utils.maintel.sv_surveys as svs
import rubin_scheduler.scheduler.detailers as detailers
from astropy.time import Time
from rubin_scheduler.scheduler.schedulers import CoreScheduler
from rubin_scheduler.scheduler.surveys import LongGapSurvey

__all__ = ("get_scheduler",)


def get_scheduler() -> tuple[int, CoreScheduler]:
    """Construct the SV survey scheduler.

    Returns
    -------
    nside : `int`
        Healpix map resolution.
    scheduler : `rubin_scheduler.scheduler.scheduler.CoreScheduler`
        Feature based scheduler.
    """

    nside = 32
    science_program = "BLOCK-365"
    band_to_filter = {
        "u": "u_24",
        "g": "g_6",
        "r": "r_57",
        "i": "i_39",
        "z": "z_20",
        "y": "y_10",
    }
    exptime = 30
    nexp = 1
    u_exptime = 38
    u_nexp = 1

    # survey_start is used to "start the clock" for several basis functions
    survey_start_mjd = Time("2025-06-20T12:00:00", format="isot", scale="utc").mjd
    # survey_length controls distribution of DDF sequences
    survey_length = 100  # days

    camera_rot_limits = (-80.0, 80.0)
    pair_time = 33.0
    # Adjust these as the expected timing vary.
    # They set the expected time and number of pointings in a 'blob'.
    blob_survey_params = {
        "slew_approx": 11,
        "band_change_approx": 140.0,
        "read_approx": 2.4,
        "flush_time": 30.0,
        "smoothing_kernel": None,
        "nside": nside,
        "seed": 42,
        "dither": "night",
        "twilight_scale": True,
    }

    # DDF dither dithers
    camera_ddf_rot_limit = -75  # Rotator limit for DDF (degrees)
    max_dither = 0.2  # Max radial dither for DDF (degrees)
    per_night = True  # Dither DDF per night
    # Get path for ddf sequence configuration file
    config_dir = Path(__file__).parent
    ddf_config_file = Path.joinpath(config_dir, "ddf_sv.dat")
    if not Path.exists(ddf_config_file):
        raise ValueError(
            f"Expected target yaml file does not exist at {ddf_config_file}"
        )

    # Template acquisition parameters
    template_ha_range = 2.5
    template_area = 50.0
    template_time = 33.0

    # Long gaps frequency
    nights_off = 3  # For long gaps
    gaps_night_pattern = [True] + [False] * nights_off

    # Survey footprints
    survey_info = svc.survey_footprint(survey_start_mjd=survey_start_mjd, nside=nside)
    # footprints for primary Surveys
    footprints = survey_info["Footprints"]

    long_gaps = svs.gen_long_gaps_survey(
        nside=nside,
        footprints=footprints,
        pair_time=pair_time,
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        u_exptime=u_exptime,
        u_nexp=u_nexp,
        night_pattern=gaps_night_pattern,
        blob_survey_params=blob_survey_params,
    )

    # Set up the DDF surveys to dither
    single_ddf_dither = detailers.DitherDetailer(
        per_night=per_night, max_dither=max_dither
    )
    dither_detailer = detailers.SplitDetailer(
        single_ddf_dither, detailers.EuclidDitherDetailer()
    )
    detailer_list = [
        detailers.CameraRotDetailer(
            min_rot=-camera_ddf_rot_limit, max_rot=camera_ddf_rot_limit
        ),
        dither_detailer,
        detailers.BandSortDetailer(),
    ]

    ddfs = svs.gen_ddf_surveys(
        detailer_list=detailer_list,
        nside=nside,
        expt={
            "u": u_exptime,
            "g": exptime,
            "r": exptime,
            "i": exptime,
            "z": exptime,
            "y": exptime,
        },
        nexp={"u": u_nexp, "g": nexp, "r": nexp, "i": nexp, "z": nexp, "y": nexp},
        survey_start=survey_start_mjd,
        survey_length=survey_length / 365.25,
        ddf_config_file=ddf_config_file,
    )

    greedy = svs.gen_greedy_surveys(
        nside=nside,
        footprints=footprints,
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        u_exptime=u_exptime,
        u_nexp=u_nexp,
    )

    blobs = svs.generate_blobs(
        nside=nside,
        footprints=footprints,
        pair_time=pair_time,
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        u_exptime=u_exptime,
        u_nexp=u_nexp,
        survey_start=survey_start_mjd,
        blob_survey_params=blob_survey_params,
    )

    twi_blobs = svs.generate_twi_blobs(
        nside=nside,
        footprints=footprints,
        pair_time=15.0,
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        night_pattern=[True, True],
        blob_survey_params=blob_survey_params,
    )

    templ_surveys = svs.gen_template_surveys(
        nside=nside,
        footprints=footprints,
        pair_time=template_time,
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        u_exptime=u_exptime,
        u_nexp=u_nexp,
        area_required=template_area,
        HA_min=template_ha_range,
        HA_max=24 - template_ha_range,
        science_program=science_program,
        blob_survey_params=blob_survey_params,
    )

    lvk_templates = svs.gen_lvk_templates(
        nside=nside,
        bands=("g", "i"),
        survey_start=survey_start_mjd,
        footprints_hp=survey_info["extra_templates_array"],
        camera_rot_limits=camera_rot_limits,
        exptime=exptime,
        nexp=nexp,
        science_program=science_program,
    )

    # No near-sun twilight survey yet
    # No Roman survey yet
    surveys = [ddfs, long_gaps, templ_surveys, blobs, twi_blobs, greedy, lvk_templates]

    # Label regions for all surveys
    for tier in surveys:
        for survey in tier:
            if isinstance(survey, LongGapSurvey):
                survey.blob_survey.detailers.append(detailers.LabelRegionsAndDDFs())
                survey.scripted_survey.detailers.append(detailers.LabelRegionsAndDDFs())
            else:
                survey.detailers.append(detailers.LabelRegionsAndDDFs())

    scheduler = CoreScheduler(surveys, nside=nside, band_to_filter=band_to_filter)

    return (nside, scheduler)


if __name__ == "config":
    (nside, scheduler) = get_scheduler()

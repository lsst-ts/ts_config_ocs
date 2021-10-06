import os

import numpy as np

import astropy.units as u

import matplotlib.pyplot as plt

from astropy.coordinates import Angle

from rubin_sim.scheduler import basis_functions
from rubin_sim.scheduler import features
from rubin_sim.scheduler import sim_runner

from rubin_sim.scheduler.utils import empty_observation
from rubin_sim.utils import _raDec2Hpid
from rubin_sim.scheduler.schedulers import Core_scheduler, simple_filter_sched
from rubin_sim.scheduler.surveys import Greedy_survey, Deep_drilling_survey
from rubin_sim.scheduler.modelObservatory import Model_observatory


class NoteLastObserved(features.BaseSurveyFeature):
    """Track when the last observation that matches a certain condition
    was made.
    """

    def __init__(self, note):
        self.note = note
        self.feature = None

    def add_observation(self, observation, indx=None):
        if self.note in observation["note"]:
            self.feature = observation["mjd"]


class VisitGap(basis_functions.Base_basis_function):
    def __init__(self, note, gap_min=25.0, penalty_val=np.nan):
        super().__init__()
        self.penalty_val = penalty_val

        self.gap = gap_min / 60.0 / 24.0
        self.survey_features = dict()
        self.survey_features["NoteLastObserved"] = NoteLastObserved(note=note)

    def _check_feasibility(self, conditions):
        if self.survey_features["NoteLastObserved"].feature is None:
            return True

        diff = conditions.mjd - self.survey_features["NoteLastObserved"].feature

        if diff <= self.gap:
            return False
        else:
            return True

    def check_feasibility(self, conditions):
        return self._check_feasibility(conditions)

    def _calc_value(self, conditions, indx=None):
        return 1.0 if self._check_feasibility(conditions) else self.penalty_val


class FieldSurvey(Deep_drilling_survey):
    def __init__(
        self,
        basis_functions,
        RA,
        dec,
        sequence="rgizy",
        nvis=[20, 10, 20, 26, 20],
        exptime=30.0,
        u_exptime=30.0,
        nexp=2,
        ignore_obs=None,
        survey_name="DD",
        reward_value=None,
        readtime=2.0,
        filter_change_time=120.0,
        nside=None,
        flush_pad=30.0,
        seed=42,
        detailers=None,
    ):
        super().__init__(
            basis_functions=basis_functions,
            RA=RA,
            dec=dec,
            sequence=sequence,
            nvis=nvis,
            exptime=exptime,
            u_exptime=u_exptime,
            nexp=nexp,
            ignore_obs=ignore_obs,
            survey_name=survey_name,
            reward_value=reward_value,
            readtime=readtime,
            filter_change_time=filter_change_time,
            nside=nside,
            flush_pad=flush_pad,
            seed=seed,
            detailers=detailers,
        )
        self.basis_weights = np.ones(len(basis_functions)) / len(basis_functions)

    def calc_reward_function(self, conditions):
        self.reward_checked = True
        indx = _raDec2Hpid(self.nside, self.ra, self.dec)
        if self._check_feasibility(conditions):
            self.reward = 0
            indx = _raDec2Hpid(self.nside, self.ra, self.dec)
            for bf, weight in zip(self.basis_functions, self.basis_weights):
                basis_value = bf(conditions, indx=indx)
                self.reward += basis_value * weight

            self.reward = np.sum(self.reward[indx])

            if np.any(np.isinf(self.reward)):
                self.reward = np.inf
        else:
            # If not feasable, negative infinity reward
            self.reward = -np.inf
            return self.reward

        return self.reward


def get_basis_functions_sp_survey(ra, nside, note, ha_limits, frac_total):
    sun_alt_limit = -18.0
    time_needed = 62.0

    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Time_to_twilight_basis_function(time_needed=time_needed),
        basis_functions.Hour_Angle_limit_basis_function(RA=ra, ha_limits=ha_limits),
        basis_functions.M5_diff_basis_function(nside=nside),
        basis_functions.Slewtime_basis_function(nside=nside),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.5, nside=nside
        ),
        VisitGap(note=note, gap_min=15.0),
    ]


def get_basis_functions_cwfs_survey(nside, note, time_gap_min):
    sun_alt_limit = -12.0
    return [
        basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit),
        basis_functions.Slewtime_basis_function(nside=nside),
        basis_functions.Moon_avoidance_basis_function(nside=nside),
        basis_functions.Zenith_shadow_mask_basis_function(
            min_alt=28.0, max_alt=85.5, nside=nside
        ),
        VisitGap(note=note, gap_min=time_gap_min),
    ]


if __name__ == "config":

    nside = 32

    reward_value = 10
    nexp = 1
    ha_limit = [[18.0, 24.0], [0.0, 6.0]]

    target_list = [
        ("HD2811", "00:31:18", "-43:36:23.0", ha_limit, reward_value),
        ("HD009051", "01:28:46", "-24:20:25.4", ha_limit, reward_value),
        ("HD14943", "02:22:54", "-51:05:31.7", ha_limit, reward_value),
        ("HD031128", "04:52:09", "-27:03:50.9", ha_limit, reward_value),
        ("LAMLEP", "05:19:34", "-13:10:36.4", ha_limit, reward_value),
        ("HD37962", "05:40:51", "-31:21:04.0", ha_limit, reward_value),
        ("MUCOL", "05:46:00", "-32:18:23.2", ha_limit, reward_value),
        ("HD38949", "05:48:20", "-24:27:49.9", ha_limit, reward_value),
        ("ETA1DOR", "06:06:09", "-66:02:23", ha_limit, reward_value),
        ("HD185975", "20:28:18", "-87:28:19.9", [[0.0, 24.0]], reward_value * 2.0),
        ("HD200654", "21:06:34", "-49:57:50.3", ha_limit, reward_value),
        ("HD205905", "21:39:10", "-27:18:23.7", ha_limit, reward_value),
    ]

    surveys = [[], []]

    bfs = get_basis_functions_cwfs_survey(nside=32, note="cwfs", time_gap_min=120.0)

    surveys[0].append(
        Greedy_survey(
            bfs, np.ones_like(bfs) * 10.0, nside=32, survey_name="cwfs", nexp=4
        )
    )

    for name, ra_str, dec_str, ha_limits, reward in target_list:
        ra = Angle(ra_str, unit=u.hourangle).to(u.deg).value
        dec = Angle(dec_str, unit=u.deg).to(u.deg).value

        bfs = get_basis_functions_sp_survey(
            ra=ra, nside=32, note=name, ha_limits=ha_limits, frac_total=0.2
        )

        observation = empty_observation()
        observation["RA"] = np.radians(ra)
        observation["dec"] = np.radians(dec)
        observation["filter"] = "g"
        observation["exptime"] = 130.0
        observation["nexp"] = 1.0
        observation["note"] = f"spec:{name}"
        sequence = [observation]

        surveys[1].append(
            FieldSurvey(
                bfs,
                np.array(
                    [
                        ra,
                    ]
                ),
                np.array(
                    [
                        dec,
                    ]
                ),
                sequence=sequence,
                survey_name=name,
                reward_value=reward,
                nside=nside,
                nexp=nexp,
                detailers=[],
            )
        )

    scheduler = Core_scheduler(surveys, nside=nside)

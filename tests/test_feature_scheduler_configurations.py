# This file is part of ts_config_ocs.
#
# Developed for Vera C. Rubin Observatory Telescope and Site Systems.
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

import importlib
import pathlib

import pytest

if importlib.util.find_spec("rubin_scheduler") is None:
    pytest.skip(allow_module_level=True)


@pytest.mark.parametrize(
    "fbs_config",
    [
        fbs_config
        for fbs_config in pathlib.PosixPath("Scheduler/feature_scheduler/").glob(
            "**/*.py"
        )
    ],
)
def test_feature_scheduler_configurations(fbs_config: list[str]) -> None:
    """Test that all fbs configurations can be loaded and that
    they define a scheduler and nside.

    Parameters
    ----------
    fbs_config : `list`[`pathlib.PosixPath`]
        List of feature based scheduler configurations.
    """
    assert pathlib.Path(fbs_config).exists()

    spec = importlib.util.spec_from_file_location("config", fbs_config)
    conf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conf)

    assert hasattr(conf, "scheduler")

    assert hasattr(conf, "nside")


def test_all_fbs_configurations_in_use() -> None:
    """Test that all fbs configrations are in use."""

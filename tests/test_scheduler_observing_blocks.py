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

import pathlib
import subprocess
from string import Template

import pytest
import yaml
try:
    from lsst.ts import externalscripts, observing, standardscripts
except ImportError:
    pytest.skip(allow_module_level=True)
from lsst.ts.salobj import DefaultingValidator

scheduler_config_path = pathlib.Path(__file__).parents[1] / "Scheduler"


def get_scripts_schema(
    scripts: set[tuple[str, bool]]
) -> dict[tuple[str, bool], DefaultingValidator | None]:
    standardscripts_scripts_dir = standardscripts.utils.get_scripts_dir()
    externalscripts_scripts_dir = externalscripts.utils.get_scripts_dir()

    scripts_validators = dict()

    for script_name, standard in scripts:
        script_path = (
            standardscripts_scripts_dir if standard else externalscripts_scripts_dir
        ) / script_name

        process = subprocess.run([script_path, "0", "--schema"], capture_output=True)
        if process.returncode != 0:
            raise RuntimeError(
                f"Failed to get script {script_name} schema.\n"
                f"{process.stdout.decode()}\n"
                f"{process.stderr.decode()}"
            )
        script_schema_str = process.stdout.decode()

        scripts_validators[(script_name, standard)] = (
            DefaultingValidator(schema=yaml.safe_load(script_schema_str))
            if script_schema_str
            else None
        )

    return scripts_validators


@pytest.mark.parametrize("instance", ["auxtel", "maintel", "ocs"])
def test_blocks_valid_json(instance: list[str]) -> None:
    blocks_dir = scheduler_config_path / f"observing_blocks_{instance}"

    programs = list()
    observing_blocks = list()
    scripts = set()

    for block in blocks_dir.glob("**/*.json"):
        observing_block = observing.ObservingBlock.parse_file(block)
        observing_blocks.append(observing_block)
        programs.append(observing_block.program)
        for script in observing_block.scripts:
            scripts.add((script.name, script.standard))

    scripts_schema = get_scripts_schema(scripts)

    assert len(programs) == len(set(programs))

    for block in observing_blocks:
        for script in block.scripts:
            script_config_validator = scripts_schema[(script.name, script.standard)]
            if script_config_validator is None:
                continue
            script_configuration = Template(
                script.get_script_configuration()
            ).substitute(**get_driver_overrides())
            script.parameters = yaml.safe_load(script_configuration)
            try:
                script_config_validator.validate(script.parameters)
            except Exception as e:
                raise AssertionError(f"Failed to validate {script.name}. {e}") from e


def get_driver_overrides() -> dict:
    """Returns a dictionary with the parameters to be used for the
    observing scripts.

    Returns
    -------
    script_config : `dict`
        Script configuration.
    """
    return {
        "targetid": 123,
        "band_filter": "r",
        "name": "Target",
        "ra": "abc",
        "dec": "abc",
        "rot_sky": 0.0,
        "alt": 0.0,
        "az": 0.0,
        "rot": 0.0,
        "obs_time": 0.0,
        "num_exp": 1,
        "exp_times": [
            30.0,
        ],
        "estimated_slew_time": 0.0,
        "program": "PROGRAM",
    }

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
import unittest

from lsst.ts import salobj
from lsst.ts.salobj.configurable_csc import ConfigurableCsc
from lsst.ts.salobj.validator import StandardValidator

try:
    from lsst.ts import watcher
except ImportError:
    raise unittest.SkipTest("Cannot import Watcher module.")


class ConfigTestCase(salobj.BaseConfigTestCase, unittest.TestCase):
    def test_Watcher_rule_config(self):
        """Validate the Watcher rule configuration.

        The Watcher CSC itself only defines the general configuration schema.
        That schema indicates that there is more than one CSC instance and
        that each instance can define one or more DataClients. The
        configuration of each rule is defined in rule-specific schemas inside
        the rule classes.

        A separate test is required because the generic configuration file
        tests in test_config_files.py only validate the CSC schema and not any
        sub-schemas if they exist.
        """
        config_package_root = pathlib.Path(__file__).parents[1]
        sal_name = "Watcher"

        # Validate that there is only one config file.
        config_dir_name = self.get_config_dir(
            config_package_root=config_package_root,
            sal_name=sal_name,
            schema=watcher.CONFIG_SCHEMA,
        )
        self.config_dir = pathlib.Path(config_dir_name)

        # Validate that the expected config file exists.
        config_file = self.config_dir / "_init.yaml"
        assert config_file.exists(), "Didn't find Watcher config file _init.yaml."

        # Get a list of all site config files, for which the name starts with
        # an "_" and doesn't equal "_init.yaml" to avoid validating
        # ["_init.yaml", "_init.yaml"].
        site_config_files = [
            f for f in list(self.config_dir.glob("_*.yaml")) if f.name != "_init.yaml"
        ]

        # Validate "_init.yaml".
        self.validate_config_file_list([])

        # Load and validate the site config files.
        for site_config_file in site_config_files:
            self.validate_config_file_list([site_config_file])

        # Also get a list of user config files, for which the name does not
        # start with an "_".
        user_config_files = [
            f for f in list(self.config_dir.glob("*.yaml")) if f.name[0] != "_"
        ]

        # Now test all combinations of the user and site config files.
        for user_config_file in user_config_files:
            for site_config_file in site_config_files:
                self.validate_config_file_list([site_config_file, user_config_file])

    def validate_config_file_list(self, config_file_list: list[pathlib.Path]) -> None:
        files_to_read = ["_init.yaml"] + [n.name for n in config_file_list]
        print(f"Validating {files_to_read}.")
        config = ConfigurableCsc.read_config_files(
            config_validator=StandardValidator(watcher.CONFIG_SCHEMA),
            config_dir=self.config_dir,
            files_to_read=files_to_read,
        )

        # Loop over the CSC instances and validate the config for all the
        # rules.
        for rule in config.rules:
            classname = rule["classname"]
            client_class = watcher.get_rule_class(classname)
            config_schema = client_class.get_schema()
            if config_schema is not None:
                validator = salobj.DefaultingValidator(config_schema)
                for rule_config in rule["configs"]:
                    validator.validate(rule_config)

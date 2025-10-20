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
import unittest

from lsst.ts import salobj
from lsst.ts.salobj.configurable_csc import ConfigurableCsc
from lsst.ts.salobj.validator import StandardValidator

try:
    from lsst.ts import eas
except ImportError:
    raise unittest.SkipTest("Cannot import EAS module.")


class ConfigTestCase(salobj.BaseConfigTestCase, unittest.TestCase):
    def test_EAS_model_config(self):
        """Validate the EAS individual model configuration.

        The EAS CSC itself only defines the general configuration schema.
        Within the CSC are sub-modules that are configured independently,
        similar to, e.g., DREAM or ESS.

        A separate test is required because the generic configuration file
        tests in test_config_files.py only validate the CSC schema and not any
        sub-schemas if they exist.
        """
        print("test start")
        config_package_root = pathlib.Path(__file__).parents[1]
        sal_name = "EAS"

        # Validate that there is only one config file.
        config_dir_name = self.get_config_dir(
            config_package_root=config_package_root,
            sal_name=sal_name,
            schema=eas.CONFIG_SCHEMA,
        )
        self.config_dir = pathlib.Path(config_dir_name)

        # Validate that the expected config file exists.
        config_file = self.config_dir / "_init.yaml"
        assert config_file.exists(), "Didn't find EAS config file _init.yaml."

        # Get a list of all site config files, for which the name starts with
        # an "_" and doesn't equal "_init.yaml" to avoid validating
        # ["_init.yaml", "_init.yaml"].
        site_config_files = [f for f in list(self.config_dir.glob("_*.yaml")) if f.name != "_init.yaml"]

        # Validate "_init.yaml".
        self.validate_config_file_list([])

        # Load and validate the site config files.
        for site_config_file in site_config_files:
            self.validate_config_file_list([site_config_file])

        # Also get a list of user config files, for which the name does not
        # start with an "_".
        user_config_files = [f for f in list(self.config_dir.glob("*.yaml")) if f.name[0] != "_"]

        # Now test all combinations of the user and site config files.
        for user_config_file in user_config_files:
            for site_config_file in site_config_files:
                self.validate_config_file_list([site_config_file, user_config_file])

    def validate_config_file_list(self, config_file_list: list[pathlib.Path]) -> None:
        files_to_read = ["_init.yaml"] + [n.name for n in config_file_list]
        print(f"Validating {files_to_read}.")

        validators: dict[str, salobj.DefaultingValidator] = dict()

        config = ConfigurableCsc.read_config_files(
            config_validator=StandardValidator(eas.CONFIG_SCHEMA),
            config_dir=self.config_dir,
            files_to_read=files_to_read,
        )

        # Loop over the configuration and find all configuration sub-modules.
        for model_name, model_config in vars(config).items():
            if not isinstance(model_config, dict):
                continue

            # Dynamically import the schema based on the key name
            module_name = f"lsst.ts.eas.{model_name}_model"
            class_name = f"{model_name.capitalize()}Model"

            if model_name in validators:
                validator = validators[model_name]
            else:
                try:
                    mod = importlib.import_module(module_name)
                    cls = getattr(mod, class_name)
                    schema = cls.get_config_schema()
                except (ImportError, AttributeError) as e:
                    raise RuntimeError(f"Could not load schema for {model_name}") from e

                validator = salobj.DefaultingValidator(schema)
                validators[model_name] = validator

            # Validate the sub-configuration against the schema.
            validator.validate(model_config)

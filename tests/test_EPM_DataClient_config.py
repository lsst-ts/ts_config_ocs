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
    from lsst.ts import epm
    from lsst.ts.ess import common
except ImportError:
    raise unittest.SkipTest("Cannot import EPM modules.")


class ConfigTestCase(salobj.BaseConfigTestCase, unittest.TestCase):
    def setUp(self):
        self.config_package_root = pathlib.Path(__file__).parents[1]

    def test_EPM_DataClient_config(self):
        """Validate the EPM DataClient configuration.

        The EPM CSC itself only defines the general configuration schema. That
        schema indicates that there is more than one CSC instance and that each
        instance can define one or more DataClients. The configuration of each
        DataClient is defined in DataClient-specific schemas inside the
        DataClient classes.

        A separate test is required because the generic configuration file
        tests in test_config_files.py only validate the CSC schema and not any
        sub-schemas if they exist.
        """
        config_package_root = self.config_package_root
        sal_name = "EPM"

        # Validate that there is only one config file.
        config_dir_name = self.get_config_dir(
            config_package_root=config_package_root,
            sal_name=sal_name,
            schema=epm.CONFIG_SCHEMA,
        )
        config_dir = pathlib.Path(config_dir_name)
        config_files = list(config_dir.glob("*.yaml"))
        assert len(config_files) == 1, "Expected only one EPM configuration file."

        # Validate that the expected config file exists.
        config_file = config_dir / "_init.yaml"
        assert config_file.exists(), "Didn't find EPM config file _init.yaml."

        # Load the config.
        config = ConfigurableCsc.read_config_files(
            config_validator=StandardValidator(epm.CONFIG_SCHEMA),
            config_dir=config_dir,
            files_to_read=["_init.yaml"],
        )

        # Loop over the CSC instances and validate the config for all the
        # DataClients of each instance.
        for instance in config.instances:
            for client_data in instance["data_clients"]:
                client_class = common.data_client.get_data_client_class(
                    client_data["client_class"]
                )
                config_schema = client_class.get_config_schema()
                validator = salobj.DefaultingValidator(config_schema)
                client_config_dict = client_data["config"]
                validator.validate(client_config_dict)

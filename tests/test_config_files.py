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


class ConfigTestCase(salobj.BaseConfigTestCase, unittest.TestCase):
    def setUp(self):
        self.config_package_root = pathlib.Path(__file__).parents[1]

    def test_DIMM(self):
        self.check_standard_config_files(
            sal_name="DIMM",
            module_name="lsst.ts.dimm",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_EAS(self):
        self.check_standard_config_files(
            sal_name="EAS",
            module_name="lsst.ts.eas",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_Electrometer(self):
        self.check_standard_config_files(
            sal_name="Electrometer",
            module_name="lsst.ts.electrometer",
            config_package_root=self.config_package_root,
        )

    def test_EPM(self):
        self.check_standard_config_files(
            sal_name="EPM",
            module_name="lsst.ts.epm",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_ESS(self):
        self.check_standard_config_files(
            sal_name="ESS",
            module_name="lsst.ts.ess.csc",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_FiberSpectrograph(self):
        self.check_standard_config_files(
            sal_name="FiberSpectrograph",
            module_name="lsst.ts.fiberspectrograph",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_GenericCamera(self):
        self.check_standard_config_files(
            sal_name="GenericCamera",
            module_name="lsst.ts.genericcamera",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_GIS(self):
        self.check_standard_config_files(
            sal_name="GIS",
            module_name="lsst.ts.gis",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_MTEEC(self):
        self.check_standard_config_files(
            sal_name="MTEEC",
            module_name="lsst.ts.mteec",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_PMD(self):
        self.check_standard_config_files(
            sal_name="PMD",
            module_name="lsst.ts.pmd",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_Scheduler(self):
        self.check_standard_config_files(
            sal_name="Scheduler",
            module_name="lsst.ts.scheduler",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_all_fbs_configurations_in_use(self) -> None:
        """Test that all fbs configrations are in use."""
        module_name = "lsst.ts.scheduler"
        schema_name = "CONFIG_SCHEMA"
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise unittest.SkipTest(f"Cannot import {module_name}")
        schema = getattr(module, schema_name)
        scheduler_config_dir = self.get_config_dir(
            config_package_root=self.config_package_root,
            sal_name="Scheduler",
            schema=schema,
        )
        scheduler_config_files_path = scheduler_config_dir.glob("**/*.yaml")
        scheduler_config_all = [
            open(config_file, "r").read() for config_file in scheduler_config_files_path
        ]
        fbs_config_files = set(
            [
                str(fbs_config)
                for fbs_config in pathlib.PosixPath(
                    "Scheduler/feature_scheduler/"
                ).glob("**/*.py")
            ]
        )
        fbs_config_file_in_scheduler_config = set()
        for fbs_config_file in fbs_config_files:
            for scheduler_config in scheduler_config_all:
                if fbs_config_file in scheduler_config:
                    fbs_config_file_in_scheduler_config.add(fbs_config_file)
                    break
        assert fbs_config_file_in_scheduler_config == fbs_config_files

    def test_Test(self):
        self.check_standard_config_files(
            sal_name="Test",
            module_name="lsst.ts.salobj",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

    def test_Watcher(self):
        self.check_standard_config_files(
            sal_name="Watcher",
            module_name="lsst.ts.watcher",
            schema_name="CONFIG_SCHEMA",
            config_package_root=self.config_package_root,
        )

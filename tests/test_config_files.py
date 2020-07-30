# This file is part of ts_config_ocs.
#
# Developed for the LSST Telescope and Site Systems.
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


class ConfigTestCase(salobj.BaseConfigTestCase, unittest.TestCase):
    def setUp(self):
        self.config_package_root = pathlib.Path(__file__).parents[1]

    def test_DIMM(self):
        self.check_standard_config_files(sal_name="DIMM",
                                         module_name="lsst.ts.dimm",
                                         config_package_root=self.config_package_root)

    def test_Electrometer(self):
        self.check_standard_config_files(sal_name="Electrometer",
                                         module_name="lsst.ts.electrometer",
                                         config_package_root=self.config_package_root)

    def test_Environment(self):
        self.check_standard_config_files(sal_name="Environment",
                                         module_name="lsst.ts.environment",
                                         config_package_root=self.config_package_root)

    def test_FiberSpectrograph(self):
        self.check_standard_config_files(sal_name="FiberSpectrograph",
                                         module_name="lsst.ts.FiberSpectrograph",
                                         config_package_root=self.config_package_root)

    def test_GenericCamera(self):
        # Use env var TS_GENERICCAMERA_DIR because importing the module
        # requires a package that is not in the standard Docker image.
        self.check_standard_config_files(sal_name="GenericCamera",
                                         package_name="ts_GenericCamera",
                                         config_package_root=self.config_package_root)

    def test_Hexapod(self):
        self.check_standard_config_files(sal_name="Hexapod",
                                         module_name="lsst.ts.hexapod",
                                         config_package_root=self.config_package_root)

    def test_Rotator(self):
        self.check_standard_config_files(sal_name="Rotator",
                                         module_name="lsst.ts.rotator",
                                         config_package_root=self.config_package_root)

    def test_Test(self):
        self.check_standard_config_files(sal_name="Test",
                                         module_name="lsst.ts.salobj",
                                         config_package_root=self.config_package_root)

    def test_Watcher(self):
        self.check_standard_config_files(sal_name="Watcher",
                                         module_name="lsst.ts.watcher",
                                         config_package_root=self.config_package_root)

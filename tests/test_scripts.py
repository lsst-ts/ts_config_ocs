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
import unittest


class ScriptsTestCase(unittest.TestCase):
    def setUp(self):
        self.scripts_dir = pathlib.Path(__file__).parents[1] / "scripts"
        self.data_dir = pathlib.Path(__file__).parents[0] / "data"

    def test_compute_ess_labjack_accelerometer_config(self):
        args = [
            self.scripts_dir / "compute_ess_labjack_accelerometer_config",
            self.data_dir / "ess_labjack_accelerometer_data.yaml",
        ]
        proc = subprocess.run(args=args, capture_output=True)
        assert (
            proc.stdout.decode()
            == """          accelerometers:
            - sensor_name: "name of accelerometer 1234"
              location: "location for 1234"
              analog_inputs: [5, 6, 7]
              # serial number: 1234
              # published offsets: [2111.11, -2222.22, 2333.33]
              # published scales:  [987.65, 876.54, -765.43]
              # desired scale (m/s2)/V = 1000 mv/V * 9.8 (m/s2)/g / published scale mV/g
              offsets: [2.1111, -2.2222, 2.3333]
              scales: [9.9225, 11.1803, -12.8033]
            - sensor_name: "name of accelerometer #523"
              location: "location of accelerometer #523"
              analog_inputs: [8, 9, 10]
              # serial number: #523
              # published offsets: [2498.74, 2495.95, 2414.23]
              # published scales:  [997.40, 1001.42, 995.95]
              # desired scale (m/s2)/V = 1000 mv/V * 9.8 (m/s2)/g / published scale mV/g
              offsets: [2.4987, 2.4959, 2.4142]
              scales: [9.8255, 9.7861, 9.8399]
"""
        )

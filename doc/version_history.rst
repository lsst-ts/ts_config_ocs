.. _Version_History:

===============
Version History
===============

.. towncrier release notes start

v0.30.3 (2026-11-11)
====================

Other Changes and Additions
---------------------------

- Added M1M3 flow meters. (`SSW-3141 <https://rubinobs.atlassian.net//browse/SSW-3141>`_)
- Added ESS 132 (M1M3 Thermal Gradients). (`SSW-3141 <https://rubinobs.atlassian.net//browse/SSW-3141>`_)


v0.30.2 (2026-11-11)
====================

Other Changes and Additions
---------------------------

- Updated EAS v9 configuration: reduced the TMA convergence timeout from 3600 s to 60 s. (`SVAB-28 <https://rubinobs.atlassian.net//browse/SVAB-28>`_)
- Updated EAS v9 configuration: changed the maximum fan glycol heater offset from -1.6 to -2.0. (`SVAB-28 <https://rubinobs.atlassian.net//browse/SVAB-28>`_)
- Updated EAS v9 configuration: disabled the glycol dew point constraint. (`SVAB-28 <https://rubinobs.atlassian.net//browse/SVAB-28>`_)
- Updated EAS v9 configuration: reduced maximum TMA fan speed from 1700 to 1500. (`SVAB-28 <https://rubinobs.atlassian.net//browse/SVAB-28>`_)


v0.30.1 (2026-11-05)
====================

Other Changes and Additions
---------------------------

- Changed VEC-04 fan windspeed threshold from 10 m/s to 30 m/s. (`SCC-32 <https://rubinobs.atlassian.net//browse/SCC-32>`_)


v0.30.0 (2026-10-16)
====================

New Features
------------

- Updated EAS configuration to schema v10, adding the louver section for nighttime louver control and the in-dome anemometer ESS indices. The v9 configuration is kept for EAS versions from before OSW-1891. (`OSW-2426 <https://rubinobs.atlassian.net//browse/OSW-2426>`_)


v0.29.0 (2026-09-30)
====================

New Features
------------

- Updated Watcher configuration to add ClosedLoopDisabled alarm for Summit and BTS. (`OSW-2923 <https://rubinobs.atlassian.net//browse/OSW-2923>`_)
- Updated Watcher configuration to add MTImageIngestionLag alarm for Summit and BTS. (`SSW-2997 <https://rubinobs.atlassian.net//browse/SSW-2997>`_)
- Updated Watcher configuration to add Telemetry alarm for missing DIMM:1 telemetry for Summit and BTS. (`SSW-2997 <https://rubinobs.atlassian.net//browse/SSW-2997>`_)
- Updated Watcher configuration to add MTAOSLag alarm for Summit and BTS. (`SSW-2997 <https://rubinobs.atlassian.net//browse/SSW-2997>`_)


Documentation
-------------

- Add support for towncrier. (`OSW-2923 <https://rubinobs.atlassian.net//browse/OSW-2923>`_)


Other Changes and Additions
---------------------------

- Update license headers. (`OSW-2923 <https://rubinobs.atlassian.net//browse/OSW-2923>`_)

.. _Version_History:

===============
Version History
===============

.. towncrier release notes start

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

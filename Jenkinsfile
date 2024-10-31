@Library('JenkinsShared')_
DevelopPipeline(
    name: "ts_config_ocs",
    idl_names: [], 
    module_name: "",
    has_doc_site: false,
    extra_packages: [
        // Dependencies
        "lsst-ts/ts_ess_common",
        "lsst-ts/ts_ess_labjack",
        "lsst-ts/ts_simactuators",
        "lsst-ts/ts_tcpip",
        // Package tested by this package
        "lsst-ts/ts_dimm",
        "lsst-ts/ts_eas",
        "lsst-ts/ts_electrometer",
        "lsst-ts/ts_epm",
        "lsst-ts/ts_ess_csc",
        "lsst-ts/ts_fiberspectrograph",
        "lsst-ts/ts_genericcamera",
        "lsst-ts/ts_gis",
        "lsst-ts/ts_mteec",
        "lsst-ts/ts_pmd",
        "lsst-ts/ts_salobj",  // For the Test component.
        "lsst-ts/ts_observing",  // For the scheduler observing blocks test.
        // ts_scheduler has too many dependencies
        "lsst-ts/ts_watcher",
        "lsst-ts/ts_fbs_utils"
    ]
)


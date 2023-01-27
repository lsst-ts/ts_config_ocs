properties([
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '',
            daysToKeepStr: '14',
            numToKeepStr: '10',
        )
    ),
    // Make new builds terminate existing builds
    disableConcurrentBuilds(
        abortPrevious: true,
    )
])
pipeline {
    agent {
        // Run as root to avoid permission issues when creating files.
        // To run on a specific node, e.g. for a specific architecture, add `label '...'`.
        docker {
            alwaysPull true
            image 'lsstts/develop-env:develop'
            args "--entrypoint=''"
        }
    }
    environment {
        // Python module name.
        MODULE_NAME = 'lsst.ts.config.ocs'

        WORK_BRANCHES = "${GIT_BRANCH} ${CHANGE_BRANCH} develop"
        LSST_IO_CREDS = credentials('lsst-io')
        XML_REPORT_PATH = 'jenkinsReport/report.xml'
    }
    stages {
        stage ('Update branches of required packages') {
            steps {
                // When using the docker container, we need to change the WHOME path
                // to WORKSPACE to have the authority to install the packages.
                withEnv(["WHOME=${env.WORKSPACE}"]) {
                    sh """
                        source /home/saluser/.setup_dev.sh || echo "Loading env failed; continuing..."

                        function update_package {
                            # Update the specified T&S package
                            cd /home/saluser/repos/\${1}
                            /home/saluser/.checkout_repo.sh ${WORK_BRANCHES}
                            git pull
                        }

                        function update_or_clone_package {
                            # Update the specified T&S package if it exists,
                            # else git clone it from https://github.com/lsst-ts/\${1}.git
                            if [ -d "/home/saluser/repos/\${1}" ]; then
                                update_package "\${1}"
                            else
                                # Package does not exist; clone it
                                cd /home/saluser/repos
                                git clone https://github.com/lsst-ts/\${1}.git
                                cd /home/saluser/repos/\${1}
                                /home/saluser/.checkout_repo.sh ${WORK_BRANCHES}
                                pip install --ignore-installed -e .
                                eups declare -r . -t current
                            fi
                        }

                        # Update base required packages
                        update_package ts_idl
                        update_package ts_sal
                        update_package ts_salobj
                        update_package ts_utils
                        update_package ts_xml

                        # Update dependencies for the CSC packages
                        update_package ts_simactuators
                        update_package ts_tcpip

                        # Update CSC packages
                        update_or_clone_package ts_authorize
                        update_or_clone_package ts_dimm
                        update_or_clone_package ts_eas
                        update_or_clone_package ts_electrometer
                        update_or_clone_package ts_ess
                        update_or_clone_package ts_FiberSpectrograph
                        update_or_clone_package ts_genericcamera
                        update_or_clone_package ts_gis
                        update_or_clone_package ts_mteec
                        update_or_clone_package ts_pmd
                        update_or_clone_package ts_salobj  # for Test
                        update_or_clone_package ts_watcher
                        update_or_clone_package ts_weatherstation
                     """
                }
            }
        }
        stage('Run unit tests') {
            steps {
                withEnv(["WHOME=${env.WORKSPACE}"]) {
                    sh """
                        source /home/saluser/.setup_dev.sh || echo "Loading env failed; continuing..."
                        setup -r .
                        pytest --cov-report html --cov=${env.MODULE_NAME} --junitxml=${env.XML_REPORT_PATH}
                    """
                }
            }
        }
    }
    post {
        always {
            // The path of xml needed by JUnit is relative to the workspace.
            junit 'jenkinsReport/*.xml'

            // Publish the HTML report.
            publishHTML (
                target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: false,
                    keepAll: true,
                    reportDir: 'jenkinsReport',
                    reportFiles: 'index.html',
                    reportName: "Coverage Report"
                ]
            )
        }
        cleanup {
            // Clean up the workspace.
            deleteDir()
        }
    }
}

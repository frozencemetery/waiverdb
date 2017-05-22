/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

node('fedora') {
    try {
        checkout scm
        sh 'sudo dnf -y builddep waiverdb.spec'
        sh 'sudo dnf -y install python2-flake8 pylint python2-sphinx python-sphinxcontrib-httpdomain'
        stage('Invoke Flake8') {
            sh 'flake8'
        }
        stage('Invoke Pylint') {
            sh 'pylint --reports=n waiverdb'
        }
        stage('Build Docs') {
            sh 'make -C docs html'
            archiveArtifacts artifacts: 'docs/_build/html/**'
        }
        stage('Build SRPM') {
            sh './rpmbuild.sh -bs'
            archiveArtifacts artifacts: 'rpmbuild-output/**'
        }
        /* We take a flock on the mock configs, to avoid multiple unrelated jobs on 
         * the same Jenkins slave trying to use the same mock root at the same 
         * time, which will error out. */
        stage('Build RPM') {
            parallel (
                'EPEL7': {
                    sh """
                    mkdir -p mock-result/el7
                    flock /etc/mock/epel-7-x86_64.cfg \
                    /usr/bin/mock --resultdir=mock-result/el7 -r epel-7-x86_64 --clean --rebuild rpmbuild-output/*.src.rpm
                    """
                    archiveArtifacts artifacts: 'mock-result/el7/**'
                },
                'F25': {
                    sh """
                    mkdir -p mock-result/f25
                    flock /etc/mock/fedora-25-x86_64.cfg \
                    /usr/bin/mock --resultdir=mock-result/f25 -r fedora-25-x86_64 --clean --rebuild rpmbuild-output/*.src.rpm
                    """
                    archiveArtifacts artifacts: 'mock-result/f25/**'
                },
            )
        }
        stage('Invoke Rpmlint') {
            parallel (
                'EPEL7': {
                    sh 'rpmlint -f rpmlint-config.py mock-result/el7/*.rpm'
                },
                'F25': {
                    sh 'rpmlint -f rpmlint-config.py mock-result/f25/*.rpm'
                },
            )
        }
        stage('Invoke Rpmdeplint') {
            parallel (
                'EPEL7': {
                    sh """
                    rpmdeplint check \
                        --repo rhel7,http://pulp.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7Server/x86_64/os/ \
                        --repo rhel7-optional,http://pulp.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7Server/x86_64/optional/os/ \
                        --repo rhel7-extras,http://pulp.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7Server/x86_64/extras/os/ \
                        --repo epel7,http://dl.fedoraproject.org/pub/epel/7/x86_64/ \
                        --arch x86_64 \
                        mock-result/el7/*.noarch.rpm
                    """
                },
                'F25': {
                    sh """
                    rpmdeplint check \
                        --repo fedora,http://dl.fedoraproject.org/pub/fedora/linux/releases/25/Everything/x86_64/os/ \
                        --repo updates,http://dl.fedoraproject.org/pub/fedora/linux/updates/25/x86_64/ \
                        --arch x86_64 \
                        mock-result/f25/*.noarch.rpm
                    """
                },
            )
        }
    } catch (e) {
        currentBuild.result = "FAILED"
        /* Can't use GIT_BRANCH because of this issue https://issues.jenkins-ci.org/browse/JENKINS-35230 */
        def git_branch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
        if (git_branch == 'master') {
            step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'pnt-factory2-devel@redhat.com'])
        }
        throw e
    }
}
node('rcm-tools-jslave-rhel-7-docker') {
    try {
        checkout scm
        stage('Build Docker container') {
            unarchive mapping: ['mock-result/el7/': '.']
            def el7_rpm = findFiles(glob: 'mock-result/el7/**/*.noarch.rpm')[0]
            def appversion = sh(returnStdout: true, script: """
                rpm2cpio ${el7_rpm} | \
                cpio --quiet --extract --to-stdout ./usr/lib/python2.7/site-packages/waiverdb\\*.egg-info/PKG-INFO | \
                awk '/^Version: / {print \$2}'
            """).trim()
            docker.withRegistry(
                    'https://docker-registry.engineering.redhat.com/',
                    'docker-registry-factory2-builder-sa-credentials') {
                /* Note that the docker.build step has some magic to guess the
                 * Dockerfile used, which will break if the build directory (here ".")
                 * is not the final argument in the string. */
                def image = docker.build "factory2/waiverdb:${appversion}", "--build-arg waiverdb_rpm=$el7_rpm ."
                image.push()
            }
            /* Save container version for later steps (this is ugly but I can't find anything better...) */
            writeFile file: 'appversion', text: appversion
            archiveArtifacts artifacts: 'appversion'
        }
    } catch (e) {
        currentBuild.result = "FAILED"
        def git_branch = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
        if (git_branch == 'master') {
            step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'pnt-factory2-devel@redhat.com'])
        }
        throw e
    }
}
node('fedora') {
    sh 'sudo dnf -y install /usr/bin/py.test'
    checkout scm
    stage('Perform functional tests') {
        unarchive mapping: ['appversion': 'appversion']
        def appversion = readFile('appversion').trim()
        openshift.withCluster('open.paas.redhat.com') {
            openshift.doAs('openpaas-waiverdb-test-jenkins-credentials') {
                openshift.withProject('waiverdb-test') {
                    def template = readYaml file: 'openshift/waiverdb-test-template.yaml'
                    def models = openshift.process(template,
                            '-p', "TEST_ID=${env.BUILD_TAG}",
                            '-p', "WAIVERDB_APP_VERSION=${appversion}")
                    def environment_label = "test-${env.BUILD_TAG}"
                    try {
                        def objects = openshift.create(models)
                        echo "Waiting for pods with label environment=${environment_label} to become Ready"
                        def pods = openshift.selector('pods', ['environment': environment_label])
                        timeout(15) {
                            pods.untilEach(3) {
                                def conds = it.object().status.conditions
                                for (int i = 0; i < conds.size(); i++) {
                                    if (conds[i].type == 'Ready' && conds[i].status == 'True') {
                                        return true
                                    }
                                }
                                return false
                            }
                        }
                        def route_hostname = objects.narrow('route').object().spec.host
                        echo "Running tests against https://${route_hostname}/"
                        withEnv(["WAIVERDB_TEST_URL=https://${route_hostname}/"]) {
                            sh 'py.test functional-tests/'
                        }
                    } finally {
                        /* Tear down everything we just created */
                        openshift.selector('dc,deploy,pod,configmap,secret,svc,route',
                                ['environment': environment_label]).delete()
                    }
                }
            }
        }
    }
}

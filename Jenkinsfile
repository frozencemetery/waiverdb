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
node('docker') {
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

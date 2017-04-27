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

node('rcm-tools-jslave-rhel-7') {
    checkout scm
    stage('Invoke Flake8') {
        sh 'flake8'
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
}
node('rcm-tools-jslave-rhel-7-docker') {
    checkout scm
    stage('Build Docker container') {
        unarchive mapping: ['mock-result/el7/': '.']
        def el7_rpm = findFiles(glob: 'mock-result/el7/**/*.noarch.rpm')[0]
        /* Note that the docker.build step has some magic to guess the
         * Dockerfile used, which will break if the build directory (here ".")
         * is not the final argument in the string. */
        def image = docker.build 'waiverdb', "--build-arg waiverdb_rpm=$el7_rpm ."
    }
}

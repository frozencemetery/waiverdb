FROM centos:7
RUN yum -y install epel-release && yum -y clean all
# The caller should build a waiverdb RPM package using ./rpmbuild.sh and then pass it in this arg.
ARG waiverdb_rpm
COPY $waiverdb_rpm /tmp
# XXX take out epel-testing eventually
RUN yum -y install --setopt=tsflags=nodocs --enablerepo=epel-testing python-gunicorn /tmp/$(basename $waiverdb_rpm) && yum -y clean all
USER 1001
EXPOSE 8080
ENTRYPOINT gunicorn --bind 0.0.0.0:8080 --access-logfile=- waiverdb.wsgi:app

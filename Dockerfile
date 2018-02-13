FROM fedora:26
LABEL \
    name="WaiverDB application" \
    vendor="WaiverDB developers" \
    license="GPLv2+" \
    build-date=""
# The caller should build a waiverdb RPM package using ./rpmbuild.sh and then pass it in this arg.
ARG waiverdb_rpm
ARG waiverdb_common_rpm
COPY $waiverdb_rpm /tmp
COPY $waiverdb_common_rpm /tmp
RUN dnf -y install \
    python-gunicorn \
    python-psycopg2 \
    /tmp/$(basename $waiverdb_rpm) \
    /tmp/$(basename $waiverdb_common_rpm) \
    && dnf -y clean all
USER 1001
EXPOSE 8080
ENTRYPOINT gunicorn --bind 0.0.0.0:8080 --access-logfile=- waiverdb.wsgi:app 2>&1

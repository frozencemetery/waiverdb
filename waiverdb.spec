
%global upstream_version --help

Name:           waiverdb
Version:        --help
Release:        1%{?dist}
Summary:        Service for waiving results in ResultsDB
License:        GPLv2+
URL:            https://pagure.io/waiverdb
Source0:        https://files.pythonhosted.org/packages/source/w/%{name}/%{name}-%{upstream_version}.tar.gz

BuildRequires:  python2-devel
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires:  python2-setuptools
BuildRequires:  python2-sphinx
BuildRequires:  python-sphinxcontrib-httpdomain
BuildRequires:  python-sphinxcontrib-issuetracker
BuildRequires:  python2-flask
%if 0%{?fedora} > 25
BuildRequires:  python2-sqlalchemy
%else
BuildRequires:  python-sqlalchemy
%endif
BuildRequires:  python2-flask-restful
BuildRequires:  python2-flask-sqlalchemy
%if 0%{?fedora} > 27
BuildRequires:  python2-sqlalchemy-utils
%else
BuildRequires:  python-sqlalchemy-utils
%endif
BuildRequires:  python2-kerberos
BuildRequires:  python2-systemd
BuildRequires:  python2-pytest
BuildRequires:  python2-mock
BuildRequires:  python2-flask-oidc
BuildRequires:  python2-configparser
BuildRequires:  python2-click
BuildRequires:  python2-flask-migrate
BuildRequires:  stomppy
%else # EPEL7 uses python- naming
BuildRequires:  python-setuptools
BuildRequires:  python-flask
BuildRequires:  python-sqlalchemy
BuildRequires:  python-flask-restful
BuildRequires:  python-flask-sqlalchemy
BuildRequires:  python-sqlalchemy-utils
BuildRequires:  python-kerberos
BuildRequires:  systemd-python
BuildRequires:  pytest
BuildRequires:  python-mock
BuildRequires:  python-flask-oidc
BuildRequires:  python-click
BuildRequires:  python-configparser
BuildRequires:  python-flask-migrate
BuildRequires:  stomppy
%endif
BuildRequires:  fedmsg
%{?systemd_requires}
BuildRequires:  systemd
BuildArch:      noarch
%if 0%{?fedora} || 0%{?rhel} > 7
Requires:       python2-flask
%if 0%{?fedora} > 25
Requires:       python2-sqlalchemy
%else
Requires:       python-sqlalchemy
%endif
Requires:       python2-flask-restful
Requires:       python2-flask-sqlalchemy
%if 0%{?fedora} > 27
Requires:       python2-sqlalchemy-utils
%else
Requires:       python-sqlalchemy-utils
%endif
Requires:       python2-kerberos
Requires:       python2-systemd
Requires:       python2-mock
Requires:       python2-flask-oidc
Requires:       python2-click
Requires:       python2-configparser
Requires:       python2-flask-migrate
Requires:       stomppy
%else
Requires:       python-flask
Requires:       python-sqlalchemy
Requires:       python-flask-restful
Requires:       python-flask-sqlalchemy
Requires:       python-kerberos
Requires:       systemd-python
Requires:       python-mock
Requires:       python-flask-oidc
Requires:       python-click
Requires:       python-configparser
Requires:       python-flask-migrate
Requires:       stomppy
%endif
Requires:       fedmsg

Requires:       waiverdb-common = %{version}-%{release}

%description
WaiverDB is a companion service to ResultsDB, for recording waivers
against test results.

%package common
Summary: Common resources for WaiverDB subpackages.

%description common
This package is not useful on its own.  It contains common filesystem resources
for other WaiverDB subpackages.

%package cli
Summary: A CLI tool for interacting with waiverdb
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires:  python2-click
Requires:       python2-click
Requires:       python2-configparser
%else
BuildRequires:  python-click
Requires:       python-click
Requires:       python-configparser
%endif

Requires:       waiverdb-common = %{version}-%{release}

%description cli
This package contains a CLI tool for interacting with waiverdb.

Primarily, submitting new waiverdbs.

%prep
%setup -q -n %{name}-%{upstream_version}

# Replace any staging urls with prod ones
sed -i 's/\.stg\.fedoraproject\.org/.fedoraproject.org/g' conf/client.conf.example

%build
%py2_build
%if 0%{?fedora}
make -C docs SPHINXOPTS= html text
%endif

%install
%py2_install
install -d %{buildroot}%{_unitdir}
install -m0644 \
    systemd/%{name}.service \
    systemd/%{name}.socket \
    %{buildroot}%{_unitdir}

install -d %{buildroot}%{_sysconfdir}/waiverdb/
install -m0644 \
    conf/client.conf.example \
    %{buildroot}%{_sysconfdir}/waiverdb/client.conf

%check
export PYTHONPATH=%{buildroot}/%{python2_sitelib}
py.test tests/

%files
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}*.egg-info
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%attr(755,root,root) %{_bindir}/waiverdb

%files common
%license COPYING
%doc README.md conf
%if 0%{?fedora}
%doc docs/_build/html docs/_build/text
%endif
%{python2_sitelib}/%{name}/__init__.py*
%{python2_sitelib}/%{name}*.egg-info

%files cli
%license COPYING
%{python2_sitelib}/%{name}/cli.py*
%attr(755,root,root) %{_bindir}/waiverdb-cli
%config(noreplace) %{_sysconfdir}/waiverdb/client.conf

%post
%systemd_post %{name}.service
%systemd_post %{name}.socket

%preun
%systemd_preun %{name}.service
%systemd_preun %{name}.socket

%postun
%systemd_postun_with_restart %{name}.service

%changelog

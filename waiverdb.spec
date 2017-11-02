
%global upstream_version 0.3.1

Name:           waiverdb
Version:        0.3.1
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
BuildRequires:  python2-kerberos
BuildRequires:  python2-systemd
BuildRequires:  python2-pytest
BuildRequires:  python2-mock
BuildRequires:  python2-flask-oidc
BuildRequires:  python2-configparser
BuildRequires:  python2-click
BuildRequires:  stomppy
%else # EPEL7 uses python- naming
BuildRequires:  python-setuptools
BuildRequires:  python-flask
BuildRequires:  python-sqlalchemy
BuildRequires:  python-flask-restful
BuildRequires:  python-flask-sqlalchemy
BuildRequires:  python-kerberos
BuildRequires:  systemd-python
BuildRequires:  pytest
BuildRequires:  python-mock
BuildRequires:  python-flask-oidc
BuildRequires:  python-click
BuildRequires:  python-configparser
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
Requires:       python2-kerberos
Requires:       python2-systemd
Requires:       python2-mock
Requires:       python2-flask-oidc
Requires:       python2-click
Requires:       python2-configparser
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
Requires:       stomppy
%endif
Requires:       fedmsg

%description
WaiverDB is a companion service to ResultsDB, for recording waivers
against test results.

%prep
%setup -q -n %{name}-%{upstream_version}

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

%check
export PYTHONPATH=%{buildroot}/%{python2_sitelib}
py.test tests/

%files
%license COPYING
%doc README.md conf
%if 0%{?fedora}
%doc docs/_build/html docs/_build/text
%endif
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}*.egg-info
%attr(755,root,root) %{_bindir}/waiverdb-cli
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket

%post
%systemd_post %{name}.service
%systemd_post %{name}.socket

%preun
%systemd_preun %{name}.service
%systemd_preun %{name}.socket

%postun
%systemd_postun_with_restart %{name}.service

%changelog

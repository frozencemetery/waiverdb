
%global upstream_version 0.1.1

Name:           waiverdb
Version:        0.1.1
Release:        1%{?dist}
Summary:        Service for waiving results in ResultsDB
License:        GPLv2+
URL:            https://pagure.io/waiverdb
Source0:        https://files.pythonhosted.org/packages/source/w/%{name}/%{name}-%{upstream_version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-flask
BuildRequires:  python-sqlalchemy
BuildRequires:  python-flask-restful
BuildRequires:  python-flask-sqlalchemy
BuildRequires:  python-kerberos
BuildRequires:  pytest
BuildRequires:  python-mock
BuildRequires:  pytest
BuildRequires:  fedmsg
BuildRequires:  python-flask-oidc
%{?systemd_requires}
BuildRequires:  systemd
BuildArch:      noarch
Requires:       python-flask
Requires:       python-sqlalchemy
Requires:       python-flask-restful
Requires:       python-flask-sqlalchemy
Requires:       python-kerberos
Requires:       python-mock
Requires:       fedmsg
Requires:       python-flask-oidc

%description
WaiverDB is a companion service to ResultsDB, for recording waivers against test results.

%prep
%setup -q -n %{name}-%{upstream_version}

%build
%py2_build

%install
%py2_install
install -d %{buildroot}%{_sysconfdir}/waiverdb
install -p -m 0644 conf/settings.py.example %{buildroot}%{_sysconfdir}/waiverdb/settings.py
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
%doc README.md conf docs
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}*.egg-info
%{_sysconfdir}/waiverdb
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

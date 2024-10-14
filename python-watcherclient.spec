%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0xf8675126e2411e7748dd46662fc2093e4682645f
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order tempest
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global sname watcherclient
%global with_doc 1

%global common_desc \
This is a client for the OpenStack Watcher API. There's a osc plugin (the \
and a command-line script (watcher).

Name:             python-watcherclient
Version:          XXX
Release:          XXX
Summary:          Python API and CLI for OpenStack Watcher

License:          Apache-2.0
URL:              https://launchpad.net/python-watcherclient
Source0:          https://tarballs.openstack.org/%{name}/%{name}-%{version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{name}/%{name}-%{version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:        noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:    git-core
BuildRequires:    openstack-macros

%description
%{common_desc}

%package -n python3-%{sname}
Summary:          Python API and CLI for OpenStack Watcher

BuildRequires:    python3-devel
BuildRequires:    pyproject-rpm-macros

%description -n python3-%{sname}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Watcher API Client

%description      doc
%{common_desc}

This package contains auto-generated documentation.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{name}-%{upstream_version} -S git

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i '/sphinx-build/ s/-W//' tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%install
%pyproject_install

mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
install -pm 644 tools/watcher.bash_completion \
    %{buildroot}%{_sysconfdir}/bash_completion.d/watcher

# Delete tests
rm -fr %{buildroot}%{python3_sitelib}/watcherclient/tests

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%check
# CentOS CI environment is setting "http://cache.rdu2.centos.org:8080" which breaks the unit tests.
unset http_proxy
unset https_proxy
%tox -e %{default_toxenv}

%files -n python3-%{sname}
%doc README.rst
%license LICENSE
%{python3_sitelib}/watcherclient
%{python3_sitelib}/*.dist-info
%{_sysconfdir}/bash_completion.d
%{_bindir}/watcher

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%license LICENSE
%endif

%changelog

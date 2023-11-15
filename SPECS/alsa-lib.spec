#define  prever     rc3
#define  prever_dot .rc3
#define  postver    a

%define version_alsa_lib  1.2.9
%define version_alsa_ucm  1.2.9
%define version_alsa_tplg 1.2.5

%if 0%{?rhel}
%global _without_topology 1
%endif

Summary:  The Advanced Linux Sound Architecture (ALSA) library
Name:     alsa-lib
Version:  %{version_alsa_lib}
Release:  1%{?prever_dot}%{?dist}
License:  LGPLv2+
Group:    System Environment/Libraries
URL:      http://www.alsa-project.org/

Source:   ftp://ftp.alsa-project.org/pub/lib/%{name}-%{version}%{?prever}%{?postver}.tar.bz2
Source1:  ftp://ftp.alsa-project.org/pub/lib/alsa-ucm-conf-%{version_alsa_ucm}.tar.bz2
%if 0%{!?_without_topology:1}
Source2:  ftp://ftp.alsa-project.org/pub/lib/alsa-topology-conf-%{version_alsa_tplg}.tar.bz2
%endif
Source10: asound.conf
Source11: modprobe-dist-alsa.conf
Source12: modprobe-dist-oss.conf
Source20: alsa-ucm-git.patch
Patch0:   alsa-git.patch
Patch1:   alsa-lib-1.2.3-config.patch
Patch2:   alsa-lib-1.0.14-glibc-open.patch

BuildRequires:  doxygen
BuildRequires:  autoconf automake libtool
Requires(post): /sbin/ldconfig, coreutils

%description
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.

This package includes the ALSA runtime libraries to simplify application
programming and provide higher level functionality as well as support for
the older OSS API, providing binary compatibility for most OSS programs.

%package  devel
Summary:  Development files from the ALSA library
Group:    Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description devel
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.

This package includes the ALSA development libraries for developing
against the ALSA libraries and interfaces.

%package  -n alsa-ucm
Summary:   ALSA Use Case Manager configuration
Group:     System Environment/Libraries
BuildArch: noarch
License:   BSD
Requires:  %{name} >= %{version_alsa_lib}

%description -n alsa-ucm
The Advanced Linux Sound Architecture (ALSA) Universal Configuration 
Manager allows configuration of Audio input/output names and routing

%if 0%{!?_without_topology:1}
%package  -n alsa-topology
Summary:   ALSA Topology configuration
Group:     System Environment/Libraries
BuildArch: noarch
License:   BSD
Requires:  %{name} >= %{version_alsa_lib}
%endif

%if 0%{!?_without_topology:1}
%description -n alsa-topology
The Advanced Linux Sound Architecture (ALSA) topology configuration
contains alsa-lib configuration of SoC topology
%endif

%prep
%setup -q -n %{name}-%{version}%{?prever}%{?postver}
%patch0 -p1 -b .alsa-git
%patch1 -p1 -b .config
%patch2 -p1 -b .glibc-open

%build
autoreconf -vif
%configure --disable-aload --with-plugindir=%{_libdir}/alsa-lib --disable-alisp

# Remove useless /usr/lib64 rpath on 64bit archs
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags} V=1
make doc

%install
%global sysmodprobedir %{_prefix}/lib/modprobe.d

make DESTDIR=%{buildroot} install

# Install global configuration files
mkdir -p -m 755 %{buildroot}/etc
install -p -m 644 %{SOURCE10} %{buildroot}/etc

# Install the modprobe files for ALSA
mkdir -p -m 755 %{buildroot}%{sysmodprobedir}
install -p -m 644 %{SOURCE11} %{buildroot}%{sysmodprobedir}/dist-alsa.conf
# bug#926973, place this file to the doc directory
install -p -m 644 %{SOURCE12} .

# Create UCM directories
mkdir -p %{buildroot}/%{_datadir}/alsa/ucm
mkdir -p %{buildroot}/%{_datadir}/alsa/ucm2

# Unpack UCMs
tar xvjf %{SOURCE1} -C %{buildroot}/%{_datadir}/alsa --strip-components=1 "*/ucm" "*/ucm2"
patch -d %{buildroot}/%{_datadir}/alsa -p1 < %{SOURCE20}

# Create topology directory
mkdir -p %{buildroot}/%{_datadir}/alsa/topology

# Unpack topologies
%if 0%{!?_without_topology:1}
tar xvjf %{SOURCE2} -C %{buildroot}/%{_datadir}/alsa --strip-components=1 "*/topology"
%endif

# Remove libtool archives.
find %{buildroot} -name '*.la' -delete

# Remove /usr/include/asoundlib.h
rm %{buildroot}/%{_includedir}/asoundlib.h

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc doc/asoundrc.txt modprobe-dist-oss.conf
%config %{_sysconfdir}/asound.conf
/%{_libdir}/libasound.so.*
/%{_libdir}/libatopology.so.*
%{_bindir}/aserver
#{_libdir}/alsa-lib/
%{_datadir}/alsa/
%exclude %{_datadir}/alsa/ucm
%exclude %{_datadir}/alsa/ucm2
%exclude %{_datadir}/alsa/topology
%{sysmodprobedir}/dist-*

%files devel
%doc TODO doc/doxygen/
%{_includedir}/alsa/
%{_includedir}/sys/asoundlib.h
%{_libdir}/libasound.so
%{_libdir}/libatopology.so
%{_libdir}/pkgconfig/alsa.pc
%{_libdir}/pkgconfig/alsa-topology.pc
%{_datadir}/aclocal/alsa.m4

%files -n alsa-ucm
# BSD
%{_datadir}/alsa/ucm
%{_datadir}/alsa/ucm2

%if 0%{!?_without_topology:1}
%files -n alsa-topology
# BSD
%{_datadir}/alsa/topology
%endif

%changelog
* Mon May 15 2023 Jaroslav Kysela <perex@perex.cz> - 1.2.9-1
- update to alsa-lib 1.2.9 and alsa-ucm-conf 1.2.9

* Thu Jan  5 2023 Jaroslav Kysela <perex@perex.cz> - 1.2.8-2
- update to alsa-lib 1.2.8 and alsa-ucm-conf 1.2.8
- remove alsa-topology package for rhel

* Fri Jul  8 2022 Jaroslav Kysela <perex@perex.cz> - 1.2.7.2-1
- Updated to 1.2.7.2

* Fri Feb 11 2022 Jaroslav Kysela <perex@perex.cz> - 1.2.6.1-3
- import fixes from upstream (UCM: AMD ACP6x, HDA, sof-hda-dsp)

* Mon Dec 20 2021 Jaroslav Kysela <perex@perex.cz> - 1.2.6.1-1
- Updated to alsa-lib 1.2.6.1 and alsa-ucm-conf 1.2.6.3

* Mon Jun 14 2021 Jaroslav Kysela <perex@perex.cz> - 1.2.5-4
- Updated to 1.2.5

* Mon Feb  1 2021 Jaroslav Kysela <perex@perex.cz> - 1.2.4-5
- Apply fixes from upstream (alsa-lib, alsa-ucm-conf)

* Mon Oct 19 2020 Jaroslav Kysela <perex@perex.cz> - 1.2.4-3
- Updated to 1.2.4

* Mon Jun 29 2020 Jaroslav Kysela <perex@perex.cz> - 1.2.3.2-1
- update to 1.2.3.2

* Tue Mar 17 2020 Jaroslav Kysela <perex@perex.cz> - 1.2.1.2-3
- Fix for HDA Intel dual codecs

* Tue Dec 10 2019 Jaroslav Kysela <perex@perex.cz> - 1.2.1.2-2
- Updated to 1.2.1.2
- UCM fixes

* Fri Nov 15 2019 Jaroslav Kysela <perex@perex.cz> - 1.2.1-2
- Updated to 1.2.1

* Mon May 27 2019 Jaroslav Kysela <perex@perex.cz> - 1.1.9-4
- Moved topology files to alsa-topology
- Updated to 1.1.9

* Fri Jan 25 2019 Jaroslav Kysela <jkysela@redhat.com> - 1.1.6-3
- Sync with the RHEL 7
- Add Dell WD15/WD19 Dock to USB-Audio.conf and create UCM configs
- Resolves: rhbz#1664247

* Wed Apr 04 2018 Jaroslav Kysela <perex@perex.cz> - 1.1.6-2
- Changed add-on directory to /etc/alsa/conf.d

* Tue Apr 03 2018 Jaroslav Kysela <perex@perex.cz> - 1.1.6-1
- Updated to 1.1.6

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Nov 14 2017 Jaroslav Kysela <perex@perex.cz> - 1.1.5-1
- Updated to 1.1.5

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 13 2017 Jaroslav Kysela <perex@perex.cz> - 1.1.4.1-1
- Updated to 1.1.4.1

* Fri May 12 2017 Jaroslav Kysela <perex@perex.cz> - 1.1.4-1
- Updated to 1.1.4

* Mon Mar 20 2017 Peter Robinson <pbrobinson@fedoraproject.org> 1.1.3-3
- Add upstream patch for Raspberry Pi HDMI audio

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 20 2016 Jaroslav Kysela <perex@perex.cz> - 1.1.3-1
- Updated to 1.1.3

* Tue Aug  2 2016 Jaroslav Kysela <perex@perex.cz> - 1.1.2-1
- Updated to 1.1.2

* Tue Jul 19 2016 Bastien Nocera <bnocera@redhat.com> - 1.1.1-2
- Add Surface 3 configuration file

* Thu Mar 31 2016 Jaroslav Kysela <perex@perex.cz> - 1.1.1-1
- Updated to 1.1.1

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Nov  9 2015 Jaroslav Kysela <perex@perex.cz> - 1.1.0-3
- Replaced source files with the alsa-lib v1.1.0 final

* Thu Nov  5 2015 Jaroslav Kysela <perex@perex.cz> - 1.1.0-2
- Replaced source files with the alsa-lib v1.1.0 test2

* Tue Oct 27 2015 Jaroslav Kysela <perex@perex.cz> - 1.1.0-1
- Updated to 1.1.0 test1

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.29-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Feb 26 2015 Jaroslav Kysela <perex@perex.cz> - 1.0.29-1
- Updated to 1.0.29

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 1.0.28-4
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Tue Feb  3 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.28-3
- Add UCM sub package
- Use %%license

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.28-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.28-1
- Update to 1.0.28

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.27.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Aug  1 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.0.27.2-2
- Fix build with unversioned %%{_docdir_fmt}.

* Mon Jul 08 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.2-1
- Updated to 1.0.27.2

* Thu May 30 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.1-2
- Fixed bug#953352

* Tue May 21 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27.1-1
- Updated to 1.0.27.1

* Tue May 07 2013 Rex Dieter <rdieter@fedoraproject.org> 1.0.27-3
- pull in upstream fix for building in C90 mode

* Thu Apr 11 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27-2
- move dist-oss.conf to doc as modprobe-dist-oss.conf

* Thu Apr 11 2013 Jaroslav Kysela <perex@perex.cz> - 1.0.27-1
- Updated to 1.0.27

* Wed Apr 03 2013 Stephen Gallagher <sgallagh@redhat.com> - 1.0.26-4
- Add upstream patch to explicitly include sys/types.h

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.26-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec  3 2012 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.26-2
- Create and own ucm directory so alsaucm doesn't crash.
- Cleanup and modernise spec

* Thu Sep  6 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.26-1
- Updated to 1.0.26

* Thu Jul 26 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 1.0.25-6
- Don't package ancient ChangeLog that ends at alsa-lib 0.2.0 (#510212).

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  2 2012 Josh Boyer <jwboyer@redhat.com> - 1.0.25-4
- Install ALSA related module conf files

* Wed Feb  1 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.25-3
- Remove the pulse audio configuration from /etc/asound.conf

* Sat Jan 28 2012 Jaroslav Kysela <jkysela@redhat.com> - 1.0.25-1
- Updated to 1.0.25 final

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.24-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 28 2011 Jaroslav Kysela <jkysela@redhat.com> - 1.0.24-1
- Updated to 1.0.24 final

* Tue Nov  9 2010 Jochen Schmitt <Jochen herr-schmitt de> 1.0.23-2
- Set plugindir to %%{_libdir}/alsa-lib (bz#651507)

* Fri Apr 16 2010 Jaroslav Kysela <jkysela@redhat.com> - 1.0.23-1
- Updated to 1.0.23 final

* Mon Dec 28 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.22-1
- Updated to 1.0.22 final
- Fix file descriptor leak in pcm_hw plugin
- Fix sound distortions for S24_LE - softvol plugin

* Wed Sep  9 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.21-3
- Add Speaker and Beep control names to mixer weight list
- Fix redhat bug #521988

* Wed Sep  2 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.21-1
- Updated to 1.0.21 final

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed May  6 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.20-1
- Updated to 1.0.20 final

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.19-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb  4 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.19-2
- Make doxygen documentation same for all architectures (bz#465205)

* Tue Jan 20 2009 Jaroslav Kysela <jkysela@redhat.com> - 1.0.19-1
- Updated to 1.0.19 final

#needsrootforbuild
%global debug_package %{nil}

%define VERSION 2.1.0
%define RELEASE 3

Name:           kata-containers
Version:        %{VERSION}
Release:        %{RELEASE}
Summary:        Kata Container, the speed of containers, the security of VMs
License:        Apache 2.0
URL:            https://github.com/kata-containers
Source0:        kata_integration-v1.0.0.tar.gz
Source1:        kata-containers-%{version}.tar.gz
Source2:        kernel.tar.gz

BuildRoot:      %_topdir/BUILDROOT
BuildRequires:  automake golang gcc bc glibc-devel glibc-static busybox glib2-devel glib2 ipvsadm conntrack-tools nfs-utils
BuildRequires:  patch elfutils-libelf-devel openssl-devel bison flex rust cargo rust-packaging libgcc dtc-devel

%description
This is core component of Kata Container, to make it work, you need a isulad/docker engine.

%prep
%setup -T -c -a 0 -n kata_integration
%setup -T -c -a 1 -n kata-containers-%{version}
%setup -T -c -a 2 -n kernel

# extract the kata_integration.tar.gz file
cd %{_builddir}/kata_integration
# apply kata_integration patches
sh apply-patches

# build kernel
cd %{_builddir}/kernel
mv kernel linux
cd %{_builddir}/kernel/linux/
%ifarch %{ix86} x86_64
cp %{_builddir}/kata_integration/hack/config-kata-x86_64 ./.config
%else
cp %{_builddir}/kata_integration/hack/config-kata-arm64 ./.config
%endif

%build
cd %{_builddir}/kernel/linux/
make %{?_smp_mflags}

mv %{_builddir}/kata-containers-%{version} %{_builddir}/kata-containers
cd %{_builddir}/kata-containers/
sh -x apply-patches
cd %{_builddir}/kata-containers/src/runtime
make clean
make

cd %{_builddir}/kata-containers/src/agent
mkdir vendor && tar -xzf %{_builddir}/kata-containers/vendor.tar.gz -C vendor/
cp -f ./vendor/version.rs ./src/
cat > .cargo/config << EOF
[build]
rustflags = ["-Clink-arg=-s","-Clink-arg=-lgcc","-Clink-arg=-lfdt"]

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF
/usr/bin/env CARGO_HOME=.cargo RUSTC_BOOTSTRAP=1 cargo build
cd %{_builddir}/kata_integration
mkdir -p -m 750 build
cp %{_builddir}/kata-containers/src/agent/target/debug/kata-agent ./build/
strip ./build/kata-agent
make initrd

%install
mkdir -p -m 755  %{buildroot}/var/lib/kata
%ifarch %{ix86} x86_64
install -p -m 755 -D %{_builddir}/kernel/linux/arch/x86_64/boot/bzImage %{buildroot}/var/lib/kata/kernel
%else
install -p -m 755 -D %{_builddir}/kernel/linux/arch/arm64/boot/Image %{buildroot}/var/lib/kata/kernel
%endif

cd %{_builddir}/kata_integration
mkdir -p -m 750  %{buildroot}/usr/bin
install -p -m 750 %{_builddir}/kata-containers/src/runtime/kata-runtime %{buildroot}/usr/bin/
install -p -m 750 %{_builddir}/kata-containers/src/runtime/kata-netmon %{buildroot}/usr/bin/
install -p -m 750 %{_builddir}/kata-containers/src/runtime/kata-monitor %{buildroot}/usr/bin/
install -p -m 750 %{_builddir}/kata-containers/src/runtime/containerd-shim-kata-v2 %{buildroot}/usr/bin/
install -p -m 640 -D %{_builddir}/kata-containers/src/runtime/cli/config/configuration-qemu.toml %{buildroot}/usr/share/defaults/kata-containers/configuration.toml
install -p -m 640 -D %{_builddir}/kata-containers/src/runtime/cli/config/configuration-stratovirt.toml %{buildroot}/usr/share/defaults/kata-containers/configuration-stratovirt.toml
install -p -m 640 ./build/kata-containers-initrd.img %{buildroot}/var/lib/kata/
mkdir -p -m 750 %{buildroot}/usr/share/defaults/kata-containers/
strip %{buildroot}/usr/bin/kata*
strip %{buildroot}/usr/bin/containerd-shim-kata-v2

%clean

%files
/usr/bin/kata-runtime
/usr/bin/kata-netmon
/usr/bin/kata-monitor
/usr/bin/containerd-shim-kata-v2
/var/lib/kata/kernel
/var/lib/kata/kata-containers-initrd.img
%config(noreplace) /usr/share/defaults/kata-containers/configuration.toml
%config(noreplace) /usr/share/defaults/kata-containers/configuration-stratovirt.toml

%doc

%changelog
* Tue Aug 24 2021 yangfeiyu <yangfeiyu2@huawei.com> - 2.1.0-3
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:add configuration-stratovirt.toml

* Fri Aug 20 2021 yangfeiyu <yangfeiyu2@huawei.com> - 2.1.0-2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:support with stratovirt and isulad

* Wed Aug 18 2021 yangfeiyu <yangfeiyu2@huawei.com> - 2.1.0-1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:upgrade kata-containers

* Fri Feb 19 2021 xinghe <xinghe1@huawei.com> - 1.11.1-10
- Type:CVE
- ID:NA
- SUG:NA
- DESC:fix CVE-2020-28914

* Fri Jan 8 2021 LiangZhang<zhangliang5@huawei.com> - 1.11.1-9
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fixup that the getPids functions returns pid

* Thu Jan 7 2021 LiangZhang<zhangliang5@huawei.com> - 1.11.1-8
- Type:feature
- ID:NA
- SUG:NA
- DESC:add suport for stratovirt of kata-check cli

* Tue Dec 22 2020 jiangpengfei<jiangpengfei9@huawei.com> - 1.11.1-7
- Type:enhancement
- ID:NA
- SUG:update
- DESC:update kata-containers source forms of organization to move all kata-containers related source repo into one repo kata-containers

* Fri Nov 6 2020 yangfeiyu<yangfeiyu2@huawei.com> - 1.11.1-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:revert the kata-containers.spec to still build kata-containers components into one package

* Fri Oct 9 2020 yangfeiyu<yangfeiyu2@huawei.com> - 1.11.1-5
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:directly copy kata binary files instead of building them

* Wed Sep 30 2020 yangfeiyu<yangfeiyu2@huawei.com> - 1.11.1-4
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:kata-runtime retry inserting of CNI interface

* Sun Sep 27 2020 LiangZhang<zhangliang5@Huawei.com> - 1.11.1-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix cmd params of direct use stratovirt binary

* Sun Sep 20 2020 jiangpengf<jiangpengfei9@huawei.com> - 1.11.1-2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix del-iface doesn't delete the tap interface in the host problem

* Thu Aug 27 2020 jiangpengf<jiangpengfei9@huawei.com> - 1.11.1-1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:update kata-containers version to v1.11.1-1

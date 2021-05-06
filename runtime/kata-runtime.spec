%define debug_package %{nil}

%define VERSION 1.11.1
%define RELEASE 12

Name:           kata-runtime
Version:        %{VERSION}
Release:        %{RELEASE}
Summary:        Kata Runtime
License:        Apache 2.0
URL:            https://github.com/kata-containers/runtime
Source0:        https://github.com/kata-containers/runtime/archive/%{version}.tar.gz#/%{name}-v%{version}.tar.gz

BuildRoot:      %_topdir/BUILDROOT
BuildRequires:  automake golang gcc

%description
Kata-runtime is core component of Kata Container.

%prep
%setup -q -c -a 0 -n %{name}-%{version}

%build
cd %{_builddir}/%{name}-%{version}

set -e
# apply patches read from series.conf
sh apply-patches

# create tmp GOPATH dir to build kata-runtime
rm -rf /tmp/kata-build/
mkdir -p /tmp/kata-build/
GOPATH=/tmp/kata-build/
kata_base=$GOPATH/src/github.com/kata-containers
mkdir -p $kata_base

# get current kata-runtime absolute path
kata_runtime_path=$(readlink -f .)
ln -s $kata_runtime_path $kata_base/runtime

# export GOPATH env
export GOPATH=$(readlink -f $GOPATH)
cd ${kata_base}/runtime && make clean && make
rm -rf $GOPATH

# make kata-runtime default configuration
kata_config_path=$kata_runtime_path/cli/config/configuration-qemu.toml
ARCH=`arch`

# arch related config options
if [ "$ARCH" == "aarch64" ];then
    sed -i 's/^machine_type.*$/machine_type = \"virt\"/' $kata_config_path
    sed -i 's/^block_device_driver.*$/block_device_driver = \"virtio-scsi\"/' $kata_config_path
    sed -i 's/^kernel_params.*$/kernel_params = \"pcie_ports=native pci=pcie_bus_perf agent.netlink_recv_buf_size=2MB\"/' $kata_config_path
    sed -i 's/^hypervisor_params.*$/hypervisor_params = \"kvm-pit.lost_tick_policy=discard pcie-root-port.fast-plug=1 pcie-root-port.x-speed=16 pcie-root-port.x-width=32 pcie-root-port.fast-unplug=1\"/' $kata_config_path
    sed -i 's/^#pcie_root_port.*$/pcie_root_port = 25/' $kata_config_path
else
    sed -i 's#block_device_driver = \"virtio-scsi\"#block_device_driver = \"virtio-blk\"#' $kata_config_path
    sed -i 's/^#hotplug_vfio_on_root_bus/hotplug_vfio_on_root_bus/' $kata_config_path
fi

# debug config
sed -i 's/^#enable_debug.*$/enable_debug = true/' $kata_config_path

# other config
sed -i 's#"/usr/bin/qemu.*"$#"/usr/bin/qemu-kvm"#' $kata_config_path
sed -i 's#/usr/share/kata-containers/vmlinuz\.container#/var/lib/kata/kernel#' $kata_config_path
sed -i 's#/usr/share/kata-containers/kata-containers-initrd\.img#/var/lib/kata/kata-containers-initrd\.img#' $kata_config_path
sed -i 's/^image/#image/' $kata_config_path
sed -i 's/^default_memory.*$/default_memory = 1024/' $kata_config_path
sed -i 's/^#enable_blk_mount/enable_blk_mount/' $kata_config_path
sed -i 's/^#block_device_cache_direct.*$/block_device_cache_direct = true/' $kata_config_path
sed -i 's/^#block_device_cache_set.*$/block_device_cache_set = true/' $kata_config_path
sed -i 's#/usr/libexec/kata-containers/kata-proxy#/usr/bin/kata-proxy#' $kata_config_path
sed -i 's#/usr/libexec/kata-containers/kata-shim#/usr/bin/kata-shim#' $kata_config_path
sed -i 's#/usr/libexec/kata-containers/kata-netmon#/usr/bin/kata-netmon#' $kata_config_path
sed -i 's/^#disable_new_netns.*$/disable_new_netns = true/' $kata_config_path
sed -i 's/^#disable_vhost_net.*$/disable_vhost_net = true/' $kata_config_path
sed -i 's/^internetworking_model.*$/internetworking_model=\"none\"/' $kata_config_path
sed -i 's/^enable_compat_old_cni.*$/#enable_compat_old_cni = true/' $kata_config_path
sed -i 's/^sandbox_cgroup_only.*$/sandbox_cgroup_only = true/' $kata_config_path

set +e

%install
cd %{_builddir}/%{name}-%{version}
mkdir -p -m 750  %{buildroot}/usr/bin
install -p -m 750 ./kata-runtime %{buildroot}/usr/bin
install -p -m 750 ./kata-netmon %{buildroot}/usr/bin
install -p -m 750 ./containerd-shim-kata-v2 %{buildroot}/usr/bin
mkdir -p -m 750 %{buildroot}/usr/share/defaults/kata-containers
install -p -m 640 ./cli/config/configuration-qemu.toml %{buildroot}/usr/share/defaults/kata-containers/configuration.toml

%clean

%files
/usr/bin/kata-runtime
/usr/bin/kata-netmon
/usr/bin/containerd-shim-kata-v2
/usr/share/defaults/kata-containers/configuration.toml

%changelog
* Wed Apr 28 2021 gaohuatao<gaohuatao@huawei.com> - 1.11.1-12
- Type:feature
- ID:NA
- SUG:NA
- DESC:support kata shimv2 used by iSulad and containerd

* Tue Nov 17 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-11
- Type:bugfix
- ID:NA
- SUG:upgrade
- DESC:fix cpu resource limited problem when sandox_cgroup_with_emulator config is enabled

* Fri Oct 9 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-10
- Type:feature
- ID:NA
- SUG:restart
- DESC:support using CNI plugin to insert mutiple network interfaces at the same time

* Mon Sep 28 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-9
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:retry inserting of CNI interface when netmon is enable

* Sun Sep 27 2020 LiangZhang<zhangliang5@Huawei.com> - 1.11.1-8
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix cmd params of direct use stratovirt binary

* Thu Sep 24 2020 LiangZhang<zhangliang5@Huawei.com> - 1.11.1-7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix invalid cmdline when start sandbox stratovirt

* Mon Sep 21 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix sandboxRuntimeRootPath left problem

* Mon Sep 21 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-5
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:add support for host cgroups with emulator

* Mon Sep 21 2020 LiangZhang<zhangliang5@Huawei.com> - 1.11.1-4
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:add support of new sandbox StratoVirt

* Sat Sep 19 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-3
- Type:bugfix
- ID:NA 
- SUG:NA
- DESC:fix del-iface doesn't delete the tap interface in the host problem

* Sat Sep 5 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-2
- Type:enhancement
- ID:NA 
- SUG:NA
- DESC:use URL format for Source0

* Wed Aug 26 2020 yangfeiyu<yangfeiyu20102011@163.com> - 1.11.1-1
- Type:enhancement
- ID:NA 
- SUG:NA
- DESC:modify kata-runtime spec file to build seperately

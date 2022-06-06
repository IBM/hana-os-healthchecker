
Main logic besides this tool:
- Keep it easy to update as all input of data is via JSON files.
- Not checking stuff that is already checked elsewhere (hwcct, saptune , ...).
- Currently checks: OS, NTP, sysctl, packages, IBM productivity tools.
- Open to check other things.

To use the tool, download it directly or via git with:

```
git clone https://github.com/IBM/hana-os-healthchecker
```

If you want to update to latest version via git:

```
cd hana-os-healthchecker

git pull
```

Enter the directory and run the tool with one parameter (XFS/ESS/NFS):

```
cd hana-os-healthchecker

./hoh.py XFS
```

At this point the tool starts

```
Welcome to HANA OS Healthchecker (HOH) version 1.14

Please use https://github.com/IBM/hana-os-healthchecker to get latest versions and report issues about HOH.

The purpose of HOH is to supplement the official tools like HWCCT not to substitute them, always refer to official documentation from IBM, SuSE/RedHat, and SAP

You should always check your system with latest version of HWCCT as explained on SAP note:1943937 - Hardware Configuration Check Tool - Central Note

JSON files versions:
        Supported OS:                           0.6
        sysctl:                                 1.3
        Packages:                               0.2
        IBM Power packages:                     0.4
        IBM Spectrum Virtualize multipath:      1.0

This software comes with absolutely no warranty of any kind. Use it at your own risk

Do you want to continue? (y/n):
 ```

You can the agree or disagree to run HOH

As example output of a SuSE system:

```
Checking OS version

OK:  SUSE Linux Enterprise Server 12 SP3 is a supported OS for this tool

Checking NTP status

OK: NTP is configured in this system
OK: Network time sync is activated in this system

Checking if saptune solution is set to HANA

The system fully conforms to the tuning guidelines of the specified SAP solution.
OK: saptune is using the solution HANA

The following individual SAP notes recommendations are available via sapnote
Consider enabling ALL of them, including 2161991 as only sets NOOP as I/O scheduler

All notes (+ denotes manually enabled notes, * denotes notes enabled by solutions):
*	1275776	Linux: Preparing SLES for SAP environments
*	1557506	Linux paging improvements
*	1984787	SUSE LINUX Enterprise Server 12: Installation notes
+	2161991	VMware vSphere (guest) configuration guidelines
*	2205917	SAP HANA DB: Recommended OS settings for SLES 12 / SLES for SAP Applications 12
	SAP_ASE	SAP_Adaptive_Server_Enterprise
	SAP_BOBJ	SAP_Business_OBJects
+	SUSE-GUIDE-01	SLES 12 OS Tuning & Optimization Guide – Part 1
+	SUSE-GUIDE-02	SLES 12: Network, CPU Tuning and Optimization – Part 2

Remember: if you wish to automatically activate the solution's tuning options after a reboot,you must instruct saptune to configure "tuned" daemon by running:
    saptune daemon start

Checking sysctl settings:

OK: net.core.rmem_max it is set to the recommended value of 56623104
OK: net.core.somaxconn it is set to the recommended value of 4096
OK: net.ipv4.tcp_mem it is set to the recommended value of 56623104 56623104 56623104
OK: net.ipv4.tcp_tw_reuse it is set to the recommended value of 1
OK: net.ipv4.tcp_timestamps it is set to the recommended value of 1
OK: net.ipv4.tcp_max_syn_backlog it is set to the recommended value of 8192
OK: net.ipv4.tcp_slow_start_after_idle it is set to the recommended value of 0
OK: net.ipv4.tcp_rmem it is set to the recommended value of 65536 262088 56623104
OK: net.ipv4.tcp_wmem it is set to the recommended value of 65536 262088 56623104
OK: net.core.wmem_max it is set to the recommended value of 56623104
OK: net.ipv4.tcp_syn_retries it is set to the recommended value of 8
OK: kernel.numa_balancing it is set to the recommended value of 0
OK: net.ipv4.tcp_tw_recycle it is set to the recommended value of 1

Checking packages install status:

OK: ipmitool installation status is as expected
OK: powerpc-utils installation status is as expected
OK: pseries-energy installation status is as expected
OK: ibmPMLinux installation status is as expected
OK: ppc64-diag installation status is as expected

Checking IBM service and productivity tools packages install status:

WARNING: ibm-power-baremetal-sles12 installation status is *NOT* as expected. Check that at least one package is installed
OK: ibm-power-managed-sles12 installation status is installed
WARNING: ibm-power-nonmanaged-sles12 installation status is *NOT* as expected. Check that at least one package is installed
OK: ibm-power-kvmguest-sles12 installation status is not installed


The summary of this run:

  SELinux reported no deviations
  time configurations reported no deviations
  saptune reported no deviations
  sysctl reported no deviations
  packages reported no deviations
  IBM service and productivity tools packages reported no deviations
```

As example output of a RedHat system:

```
OK:  Red Hat Enterprise Linux Server 7.4 is a supported OS for this tool

Checking SELinux status with sestatus

OK: SELinux is disabled in this system

Checking NTP status with timedatectl

OK: NTP is configured in this system
OK: NTP sync is activated in this system

Checking if tune-adm profile is set to sap-hana

OK: current active profile is sap-hana
OK: tuned is matching the active profile

Checking sysctl settings:

OK: net.core.rmem_max it is set to the recommended value of 56623104
OK: net.core.somaxconn it is set to the recommended value of 4096
OK: net.ipv4.tcp_mem it is set to the recommended value of 56623104 56623104 56623104
OK: net.ipv4.tcp_tw_reuse it is set to the recommended value of 1
OK: net.ipv4.tcp_timestamps it is set to the recommended value of 1
OK: net.ipv4.tcp_max_syn_backlog it is set to the recommended value of 8192
OK: net.ipv4.tcp_slow_start_after_idle it is set to the recommended value of 0
OK: net.ipv4.tcp_rmem it is set to the recommended value of 65536 262088 56623104
OK: net.ipv4.tcp_wmem it is set to the recommended value of 65536 262088 56623104
OK: net.core.wmem_max it is set to the recommended value of 56623104
OK: net.ipv4.tcp_syn_retries it is set to the recommended value of 8
OK: kernel.numa_balancing it is set to the recommended value of 0
OK: net.ipv4.tcp_tw_recycle it is set to the recommended value of 1

Checking packages install status:

OK: ipmitool installation status is as expected
OK: powerpc-utils installation status is as expected
OK: pseries-energy installation status is as expected
OK: ibmPMLinux installation status is as expected
OK: ppc64-diag installation status is as expected

Checking IBM service and productivity tools packages install status:

WARNING: ibm-power-nonmanaged-rhel7 installation status is *NOT* as expected. Check that at least one package is installed
WARNING: ibm-power-nonmanaged-sles12 installation status is *NOT* as expected. Check that at least one package is installed
OK: ibm-power-kvmguest-sles12 installation status is not installed
OK: ibm-power-managed-rhel7 installation status is installed
OK: ibm-power-kvmguest-rhel7 installation status is not installed
WARNING: ibm-power-baremetal-rhel7 installation status is *NOT* as expected. Check that at least one package is installed
WARNING: ibm-power-managed-sles12 installation status is *NOT* as expected. Check that at least one package is installed
WARNING: ibm-power-baremetal-sles12 installation status is *NOT* as expected. Check that at least one package is installed


The summary of this run:

	SELinux reported no deviations
	time configurations reported no deviations
	saptune/tuned reported no deviations
	sysctl reported no deviations
	packages reported no deviations
	IBM service and productivity tools packages reported no deviations
```

#!/usr/bin/python
from __future__ import print_function
import json
import os
import sys
import subprocess
import platform

try:
    raw_input      # Python 2
except NameError:  # Python 3
    raw_input = input

#Colorful constants
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
NOCOLOR = '\033[0m'

#GITHUB URL
GITHUB_URL = "https://github.com/IBM/hana-os-healthchecker"

#IBM_STORAGE_SIZING_GUIDELINE
IBM_STORAGE_SIZING_GUIDELINE="https://www-01.ibm.com/support/docview.wss?uid=tss1flash10859&aid=1"

#REDBOOK URL
REDBOOK_URL = "http://www.redbooks.ibm.com/abstracts/sg248432.html?Open"

#devnull redirect destination
DEVNULL = open(os.devnull, 'w')

#This script version, independent from the JSON versions
HOH_VERSION = "1.23"

def load_json(json_file_str):
    #Loads  JSON into a dictionary or quits the program if it cannot. Future might add a try to donwload the JSON if not available before quitting
    try:
        with open(json_file_str, "r") as json_file:
            json_variable = json.load(json_file)
            return json_variable
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot open JSON file: " + json_file_str)

def check_parameters():
    main_script=sys.argv[0]
    error_message = RED + "QUIT: " + NOCOLOR + "To run hoh, you need to pass the argument of type of storage (XFS/NFS/ESS). In example: ./hoh.py XFS\n"
    try: #in case no argument is passed
        argument1=sys.argv[1]
    except:
        print("")
        sys.exit(error_message)

    #Optional --with-multipath argument
    try: #in case no argument is passed
        argument2=sys.argv[2]
        if argument2 == '--with-multipath':
            with_multipath = 1
        else:
            with_multipath = 0
    except:
        with_multipath = 0

    if argument1.upper() in ('XFS', 'NFS', 'ESS'): #To check is a wanted argument
        return argument1.upper(),with_multipath
    else:
        print("")
        sys.exit(error_message)

def show_header(hoh_version,json_version):
    #Say hello and give chance to disagree to the no warranty of any kind
    while True:
        print("")
        print(GREEN + "Welcome to HANA OS Healthchecker (HOH) version " + hoh_version + NOCOLOR)
        print("")
        print("Please use " + GITHUB_URL + " to get latest versions and report issues about HOH.")
        print("")
        print("The purpose of HOH is to supplement the official tools like HWCCT not to substitute them, always refer to official documentation from IBM, SuSE/RedHat, and SAP")
        print("")
        print("You should always check your system with latest version of HWCCT as explained on SAP note:1943937 - Hardware Configuration Check Tool - Central Note")
        print("")
        print("JSON files versions:")
        print("\tSupported OS:\t\t\t\t" + json_version['supported_OS'])
        print("\tsysctl: \t\t\t\t" + json_version['sysctl'])
        print("\tPackages: \t\t\t\t" + json_version['packages'])
        print("\tIBM Power packages:\t\t\t" + json_version['ibm_power_packages'])
        print(("\tIBM Spectrum Virtualize multipath:\t") + json_version['svc_multipath'])
        print("")
        print(RED + "This software comes with absolutely no warranty of any kind. Use it at your own risk" + NOCOLOR)
        print("")
        run_this = raw_input("Do you want to continue? (y/n): ")
        if run_this.lower() == 'y':
            print("")
            break
        if run_this.lower() == 'n':
            print("")
            sys.exit("Have a nice day! Bye.\n")

def check_processor():
    expected_processor = 'ppc64le' #Not supporting other than ppc64le as now. Hardcoding here ppc64le
    error_message = RED + "QUIT: " + NOCOLOR + "Only " + expected_processor + " processor is supported.\n"
    current_processor = platform.processor()
    #print(current_processor)
    if current_processor != expected_processor:
        print("")
        sys.exit(error_message)

def check_os_suse(os_dictionary):
    #Checks the OS string vs the JSON file. If supported goes, if explecitely not supported quits. If no match also quits
    print("")
    print("Checking OS version")
    print("")

    with open("/etc/os-release") as os_release_file:
        os_release = {}
        for line in os_release_file:
            if line == "\n": #Protect against empty line
                continue
            key,value = line.rstrip().split("=")
            os_release[key] = value.strip('"')

    error_message = RED + "QUIT: " + NOCOLOR + " " + os_release['PRETTY_NAME'] + " is not a supported OS for this tool\n"

    try:
        if os_dictionary[os_release['PRETTY_NAME']] == 'OK':
            print(GREEN + "OK: "+ NOCOLOR + " " + os_release['PRETTY_NAME'] + " is a supported OS for this tool")
        else:
            print("")
            sys.exit(error_message)
    except:
        print("")
        sys.exit(error_message)

def check_os_redhat(os_dictionary):
    #Check redhat-release vs dictionary list
    redhat_distribution = platform.linux_distribution()
    redhat_distribution_str = redhat_distribution[0] + " " + redhat_distribution[1]

    error_message = RED + "QUIT: " + NOCOLOR + " " + redhat_distribution_str + " is not a supported OS for this tool\n"
    try:
        if os_dictionary[redhat_distribution_str] == 'OK':
            print(GREEN + "OK: "+ NOCOLOR + " " + redhat_distribution_str + " is a supported OS for this tool")
        else:
            print("")
            sys.exit(error_message)
    except:
        print("")
        sys.exit(error_message)

def check_distribution():
    #Decide if this is a redhat or a suse
    what_dist = platform.dist()[0]
    if what_dist == "redhat":
        return what_dist
    else:#everything esle we say is suse. It gets caught later if not. Suse does not return any string for dist
        what_dist = "suse"
        return what_dist

def check_selinux():
    #Check sestatus is disabled
    errors = 0
    print("")
    print("Checking SELinux status with sestatus")
    print("")
    try:
        return_code = subprocess.call(['sestatus'],stdout=DEVNULL, stderr=DEVNULL)
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot run sestatus. It is a needed package for this tool\n") # Not installed or else.

    sestatus = subprocess.Popen(['sestatus'], stdout=subprocess.PIPE)
    grep_rc_selinux = subprocess.call(['grep', 'disabled'], stdin=sestatus.stdout, stdout=DEVNULL, stderr=DEVNULL)
    sestatus.wait()

    if grep_rc_selinux == 0: #Is disabled
        print(GREEN + "OK: " + NOCOLOR + "SELinux is disabled in this system")
    else: #None found
        print(RED + "ERROR: " + NOCOLOR + "SELinux is not disabled in this system")
        errors = errors + 1

    return errors

def get_json_versions(os_dictionary,sysctl_dictionary,packages_dictionary,ibm_power_packages_dictionary,svc_multipath_dictionary):
    #Gets the versions of the json files into a dictionary
    json_version = {}

    #Lets see if we can load version, if not quit
    try:
        json_version['supported_OS'] = os_dictionary['json_version']
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot load version from supported OS JSON")

    try:
        json_version['sysctl'] = sysctl_dictionary['json_version']
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot load version from sysctl JSON")

    try:
        json_version['packages'] = packages_dictionary['json_version']
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot load version from packages JSON")

    try:
        json_version['ibm_power_packages'] = ibm_power_packages_dictionary['json_version']
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot load version from IBM Power packages JSON")

    try:
        json_version['svc_multipath'] = svc_multipath_dictionary['json_version']
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "Cannot load version from IBM 2145 mulitpath JSON")


    #If we made it this far lets return the dictionary. This was being stored in its own file before
    return json_version

def check_time():
    #Leverages timedatectl from systemd to check if NTP is configured and if is is actively syncing. Raises error count if some of those are not happening.
    errors = 0
    print("")
    print("Checking NTP status with timedatectl")
    print("")
    #Lets check if the tool is even there
    try:
        return_code = subprocess.call(['timedatectl','status'],stdout=DEVNULL, stderr=DEVNULL)
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot run timedatectl. It is a needed package for this tool\n") # Not installed or else.

    #First we see if NTP is configured. Agnostic of ntpd or chronyd. SuSE and RedHat have different outputs!
    timedatectl = subprocess.Popen(['timedatectl', 'status'], stdout=subprocess.PIPE)
    grep_rc_ntp = subprocess.call(['grep', 'NTP synchronized: yes'], stdin=timedatectl.stdout, stdout=DEVNULL, stderr=DEVNULL)
    timedatectl.wait()

    if grep_rc_ntp == 0: #Is configured
        print(GREEN + "OK: " + NOCOLOR + "NTP is configured in this system")

    else: #Lets try for RedHat
        timedatectl = subprocess.Popen(['timedatectl', 'status'], stdout=subprocess.PIPE)
        grep_rc_ntp = subprocess.call(['grep', 'NTP enabled: yes'], stdin=timedatectl.stdout, stdout=DEVNULL, stderr=DEVNULL)
        timedatectl.wait()

        if grep_rc_ntp == 0: #RedHat and is on
            print(GREEN + "OK: " + NOCOLOR + "NTP is configured in this system")
        else: #None found
            print(RED + "ERROR: " + NOCOLOR + "NTP is not configured in this system. Please check timedatectl command")
            errors = errors + 1

    #Lets check if sync is actually working
    timedatectl = subprocess.Popen(['timedatectl', 'status'], stdout=subprocess.PIPE)
    grep_rc_sync = subprocess.call(['grep', 'Network time on: yes'], stdin=timedatectl.stdout, stdout=DEVNULL, stderr=DEVNULL)
    if grep_rc_sync == 0:
        print(GREEN + "OK: " + NOCOLOR + "NTP sync is activated in this system")
    else: #Lets see if is on in RedHat
        timedatectl = subprocess.Popen(['timedatectl', 'status'], stdout=subprocess.PIPE)
        grep_rc_ntp = subprocess.call(['grep', 'NTP enabled: yes'], stdin=timedatectl.stdout, stdout=DEVNULL, stderr=DEVNULL)
        timedatectl.wait()
        if grep_rc_ntp == 0: #RedHat and is on
            print(GREEN + "OK: " + NOCOLOR + "NTP sync is activated in this system")
            print("")
        else: #None found
            print(RED + "ERROR: " + NOCOLOR + "NTP sync is not activated in this system. Please check timedatectl command")
            print("")
            errors = errors + 1
    return errors

def tuned_adm_check():
    errors = 0
    tuned_profiles_package = "tuned-profiles-sap-hana"
    print("Checking if tune-adm profile is set to sap-hana")
    print("")
    profile_package_installed_rc = rpm_is_installed(tuned_profiles_package)
    if profile_package_installed_rc == 1:
        print (RED + "ERROR: " + NOCOLOR + tuned_profiles_package + " is not installed. ")
        errors = errors + 1

    if profile_package_installed_rc == 0: #RPM is installed lets check the if applied

        try: #Can we run tune-adm?
            return_code = subprocess.call(['tuned-adm','active'],stdout=DEVNULL, stderr=DEVNULL)
        except:
            sys.exit(RED + "QUIT: " + NOCOLOR + "cannot run tuned-adm. It is a needed package for this tool\n") # Not installed or else.

        tuned_adm = subprocess.Popen(['tuned-adm', 'active'], stdout=subprocess.PIPE)
        vmware_grep = subprocess.Popen(['grep', '-v', 'vmware'], stdin=tuned_adm.stdout, stdout=subprocess.PIPE) #There is a sap-hana-vmware profile
        tuned_adm.wait()
        grep_rc_tuned = subprocess.call(['grep', 'Current active profile: sap-hana'], stdin=vmware_grep.stdout, stdout=DEVNULL, stderr=DEVNULL)
        vmware_grep.wait()

        if grep_rc_tuned == 0: #sap-hana profile is active
            print(GREEN + "OK: " + NOCOLOR + "current active profile is sap-hana")
        else: #Some error
            print(RED + "ERROR: " + NOCOLOR + "current active profile is not sap-hana")
            errors = errors + 1

        #try: #Is it fully matching?
        return_code = subprocess.call(['tuned-adm','verify'],stdout=DEVNULL, stderr=DEVNULL)
        #except:
        if return_code == 1:
            print(RED + "ERROR: " + NOCOLOR + "tuned profile is *NOT* fully matching the active profile")
            print("")
            errors = errors + 1

        if return_code == 0:
            print(GREEN + "OK: " + NOCOLOR + "tuned is matching the active profile")
            print("")

    return errors

def saptune_check():
    #It uses saptune command to check the solution and show the avaialble notes. Changes version to version of saptune, we are just calling saptune
    errors = 0
    print("")
    print("Checking if saptune solution is set to HANA")
    print("")
    try:
        return_code = subprocess.call(['saptune','solution','verify','HANA'])
        if return_code == 0:
            print(GREEN + "OK: " + NOCOLOR + "saptune is using the solution HANA")
            print("")
        else:
            print(RED + "ERROR: " + NOCOLOR + "saptune is *NOT* fully using the solution HANA")
            print("")
            errors = errors + 1
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot run saptune. It is a needed package for this tool\n") # Not installed or else. On SuSE for SAP it is installed by default

    print("The following individual SAP notes recommendations are available via sapnote")
    print("Consider enabling ALL of them, including 2161991 as only sets NOOP as I/O scheduler")
    print("")
    #subprocess.check_output(['saptune','note','list'])
    os.system("saptune note list")
    print("")
    return errors

def sysctl_check(sysctl_dictionary):
    #Runs checks versus values on sysctl on JSON file
    errors = 0
    warnings = 0
    print("Checking sysctl settings:")
    print("")
    for sysctl in sysctl_dictionary.keys():
        if sysctl != "json_version":
            recommended_value_str = str(sysctl_dictionary[sysctl])
            recommended_value = int(recommended_value_str.replace(" ", "")) #Need to clean the entries that have spaces or tabs for integer comparision
            try:
                current_value_str = subprocess.check_output(['sysctl','-n',sysctl], stderr=subprocess.STDOUT)
                current_value_str = current_value_str.replace("\t", " ").replace("\n", "")
                current_value = int(current_value_str.replace(" ", "")) #Need to clean the entries that have spaces for integer comparision
                #This creates an possible colision issue, might fix this in the future

                if recommended_value != current_value:
                    print (RED + "ERROR: " + NOCOLOR + sysctl + " is " + current_value_str + " and should be " + recommended_value_str)
                    errors = errors + 1
                else:
                    print(GREEN + "OK: " + NOCOLOR + sysctl + " it is set to the recommended value of " + recommended_value_str)
            except:
                    print(YELLOW + "WARNING: " + NOCOLOR + sysctl + " does not apply to this OS")
                    warnings = warnings + 1
    print("")
    return warnings,errors

def rpm_is_installed(rpm_package):
    #returns the RC of rpm -q rpm_package or quits if it cannot run rpm
    errors = 0
    try:
        return_code = subprocess.call(['rpm','-q',rpm_package],stdout=DEVNULL, stderr=DEVNULL)
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot run rpm. It is a needed package for this tool\n")
    return return_code

def packages_check(packages_dictionary):
    #Checks if packages from JSON are installed or not based on the input data ont eh JSON
    errors = 0
    print("Checking packages install status:")
    print("")
    for package in packages_dictionary.keys():
        if package != "json_version":
            current_package_rc = rpm_is_installed(package)
            expected_package_rc = packages_dictionary[package]
            if current_package_rc == expected_package_rc:
                print(GREEN + "OK: " + NOCOLOR + package + " installation status is as expected")
            else:
                print(RED + "ERROR: " + NOCOLOR + package + " installation status is *NOT* as expected")
                errors = errors + 1
    print("")
    return(errors)

def ibm_power_package_check(ibm_power_packages_dictionary):
    errors = 1
    print("Checking IBM service and productivity tools packages install status:")
    print("")
    for package in ibm_power_packages_dictionary.keys():
        if package != "json_version":
            current_package_rc = rpm_is_installed(package)
            expected_package_rc = ibm_power_packages_dictionary[package]
            if current_package_rc == expected_package_rc == 0:
                print(GREEN + "OK: " + NOCOLOR + package + " installation status is installed")
                errors = 0
            elif current_package_rc == expected_package_rc == 1:
                print(GREEN + "OK: " + NOCOLOR + package + " installation status is not installed")
            else:
                print(YELLOW + "WARNING: " + NOCOLOR + package + " installation status is *NOT* as expected. This is not a problem by itself. Check the summary at the end of the run")
    print("")
    if errors == 0:
        print(GREEN + "OK: " + NOCOLOR + " IBM service and productivity tools packages install status is as expected")
    else:
        print(RED + "ERROR: " + NOCOLOR + " IBM service and productivity tools packages install status is *NOT* as expected")
    print("")
    return(errors)

def multipath_checker(svc_multipath_dictionary,mp_conf_dictionary):
    #Missing warnings and header
    mp_errors = 0
    for mp_attr in svc_multipath_dictionary.keys():
        mp_value = svc_multipath_dictionary[mp_attr]
        #We go to check each entry on the JSON to both defaults and devices
        #We assume only defaults or devices contains the configuration for multipath
        #Lets look at defaults first if what we look is not there or worng value mark errors
        #If does not exist we move to look into devices 2145
        if mp_attr == 'json_version': #Ignore JSON version
            continue


        for item in mp_conf_dictionary:
            is_found = 0
            if 'defaults' in item:
                for default in item['defaults']:
                    if mp_attr in default:
                        is_found = 1
                        current_value = default[mp_attr]
                        if current_value == mp_value:
                            print(GREEN + "OK: " + NOCOLOR + mp_attr + " has the recommended value of " + str(mp_value))
                        else:
                            print (RED + "ERROR: " + NOCOLOR + mp_attr + " is " + str(current_value) + " and should be " + str(mp_value))
                            mp_errors = mp_errors + 1
            #if 'devices' in item:
            #    for devices in item['devices']:
            #        if 'device' in devices:
            #            for device in devices:
            #                if device['vendor'] != "IBM" or device['product'] != "2145":
            ##                    no_ibm_storage = 1
    return mp_errors


def load_multipath(multipath_file):
    #Load multipath file
    print("Loading multipath file")
    try:
        with open(multipath_file, 'r') as mp_file:
            mp_dictionary = config_parser(mp_file)
            return mp_dictionary
    except:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot read multipath file "+ multipath_file +" \n")

def config_parser(conf_lines):
    config = []

    # iterate on config lines
    for line in conf_lines:
        #Get rid of inline comments
        line = line.split('#')[0]
        # remove left and right spaces
        line = line.strip()
        line = line.translate(None, '"')

        if line.startswith('#'):
            # skip comment lines
            continue
        elif line.endswith('{'):
            # new dict (notice the recursion here)
            config.append({line.split()[0]: config_parser(conf_lines)})
        else:
            # inside a dict
            if line.endswith('}'):
                # end of current dict
                break
            else:
                # parameter line
                line = line.split()
                if len(line) > 1:
                    config.append({line[0]: " ".join(line[1:])})
    return config

def print_important_multipath_values(svc_multipath_dictionary):
    #We show the JSON values that have to be in the configuration
    print("")
    print (YELLOW + "Be sure to check that your current multipath.conf has the following attributtes set:" + NOCOLOR)
    print("")
    for mp_attr in svc_multipath_dictionary.keys():
        if mp_attr != "json_version":
            mp_value = str(svc_multipath_dictionary[mp_attr])
            print("\t" + mp_attr + "\t  --->\t" + mp_value)
    print("")
    print ("For a multipath.conf example for IBM Spectrum Virtualize storage (2145) with HANA please check Appendix B of " + REDBOOK_URL)
    print("")


def detect_disk_type(disk_type):
    #Will do a simple check on /proc/scsi/sg/device_strs for disk_type > 0
    try:
        cat_scsi_sg = subprocess.Popen(['cat', '/proc/scsi/sg/device_strs'], stdout=subprocess.PIPE, stderr=DEVNULL)
        grep_disk_type = subprocess.Popen(['grep', disk_type], stdin=cat_scsi_sg.stdout, stdout=subprocess.PIPE, stderr=DEVNULL)
        cat_scsi_sg.wait()
        wc_proc = subprocess.Popen(['wc', '-l'], stdin=grep_disk_type.stdout, stdout=subprocess.PIPE, stderr=DEVNULL)
        grep_disk_type.wait()

        number_of_disk_type = wc_proc.stdout.read()
        wc_proc.wait()

        if int(number_of_disk_type) > 0:
            return 1
        else:
            return 0
    except:
            sys.exit(RED + "QUIT: " + NOCOLOR + "cannot read proc/scsi/sg/device_strs\n")

def simple_multipath_check(multipath_dictionary, ibm_storage):
    error = 0
    print ("Checking simple multipath.conf test")
    print("")
    #mp_conf_dictionary = load_multipath("/etc/multipath.conf")
    #multipath_errors = multipath_checker(svc_multipath_dictionary,mp_conf_dictionary)
    #is_2145 = detect_disk_type("2145")
    if ibm_storage: #If this is 2145 lets check if there is a multipath.cpnf file
        print(GREEN + "OK: " + NOCOLOR +  "2145 disk type detected")
        mp_exists = os.path.isfile('/etc/multipath.conf')
        if mp_exists:
            print(GREEN + "OK: " + NOCOLOR +  "multipath.conf exists")
        else:
            print(RED + "ERROR: " + NOCOLOR + "multipath.conf does not exists")
            error = error + 1
        if os.path.isfile('/etc/udev/rules.d/99-ibm-2145.rules') == True:
            print(GREEN + "OK: " + NOCOLOR +  "99-ibm-2145.rules exists")
        else:
            print(RED + "ERROR: " + NOCOLOR + "99-ibm-2145.rules does not exists")
            error = error + 1
        if mp_exists:
            print_important_multipath_values(multipath_dictionary)
    else: #This is NOT 2145 so lets just throw a warning to go check vendor for recommended values
        print(YELLOW + "WARNING: " + NOCOLOR + " this is not IBM Spectrum Virtualize storage, please refer to storage vendor documentation for recommended settings")
    return error

def print_errors(linux_distribution,selinux_errors,timedatectl_errors,saptune_errors,sysctl_warnings,sysctl_errors,packages_errors,ibm_power_packages_errors,multipath_errors,with_multipath,ibm_storage):
    #End summary and say goodbye
    print("")
    print("The summary of this run:")
    print("")

    if linux_distribution == "redhat":
        if selinux_errors > 0:
            print(RED + "\tSELinux reported deviations" + NOCOLOR)
        else:
            print(GREEN + "\tSELinux reported no deviations" + NOCOLOR)

    if linux_distribution == "suse":
        print(GREEN + "\tSELinux not tested" + NOCOLOR)

    if timedatectl_errors > 0:
        print(RED + "\ttime configuration reported " + str(timedatectl_errors) + " deviation[s]" + NOCOLOR)
    else:
        print(GREEN + "\ttime configurations reported no deviations" + NOCOLOR)

    if saptune_errors > 0:
        print(RED + "\tsaptune/tuned reported deviations" + NOCOLOR)
    else:
        print(GREEN + "\tsaptune/tuned reported no deviations" + NOCOLOR)

    if sysctl_errors > 0:
        print(RED + "\tsysctl reported " + str(sysctl_errors) + " deviation[s] and " + str(sysctl_warnings) + " warning[s]" + NOCOLOR)
    elif sysctl_warnings > 0:
        print (YELLOW + "\tsysctl reported " + str(sysctl_warnings) + " warning[s]" + NOCOLOR)
    else:
        print(GREEN + "\tsysctl reported no deviations" + NOCOLOR)

    if packages_errors > 0:
        print(RED + "\tpackages reported " + str(packages_errors) + " deviation[s]" + NOCOLOR)
    else:
        print(GREEN + "\tpackages reported no deviations" + NOCOLOR)

    if ibm_power_packages_errors > 0:
        print(RED + "\tIBM service and productivity tools packages reported deviations" + NOCOLOR)
    else:
        print(GREEN + "\tIBM service and productivity tools packages reported no deviations" + NOCOLOR)

    if multipath_errors > 0:
        print(RED + "\tXFS with IBM Spectrum Virtualize in use and not all configuration files detected" + NOCOLOR)

    if with_multipath == 1:
        print(YELLOW + "\tmultipath option was called. Please refer to storage vendor documentation for recommended settings" + NOCOLOR)

    if ibm_storage == 1:
        print(YELLOW + "\t2145 disk detected. Be sure to follow IBM Storage sizing guidelines: " + IBM_STORAGE_SIZING_GUIDELINE + NOCOLOR)

def main():
    #Check parameters are passed
    storage,with_multipath = check_parameters()

    #JSON loads
    os_dictionary = load_json("supported_OS.json")
    sysctl_dictionary = load_json(storage + "_sysctl.json")
    packages_dictionary = load_json("packages.json")
    ibm_power_packages_dictionary = load_json("ibm_power_packages.json")
    svc_multipath_dictionary = load_json("2145_multipath.json")

    #Initial header and checks
    json_version = get_json_versions(os_dictionary,sysctl_dictionary,packages_dictionary,ibm_power_packages_dictionary,svc_multipath_dictionary)
    show_header(HOH_VERSION,json_version)
    check_processor()

    #Check linux_distribution
    linux_distribution = check_distribution()

    if linux_distribution == "suse":
        check_os_suse(os_dictionary)
    elif linux_distribution == "redhat":
        check_os_redhat(os_dictionary)
    else:
        sys.exit(RED + "QUIT: " + NOCOLOR + "cannot determine Linux distribution\n")

    #Run
    if linux_distribution == "redhat": #This has being checked already so it is a "good" variable
        selinux_errors = check_selinux()
    else:
        selinux_errors = 0

    timedatectl_errors = check_time()

    if linux_distribution == "suse":
        saptune_errors = saptune_check()
    if linux_distribution == "redhat":
        saptune_errors = tuned_adm_check()

    sysctl_warnings,sysctl_errors = sysctl_check(sysctl_dictionary)

    packages_errors = packages_check(packages_dictionary)

    ibm_power_packages_errors = ibm_power_package_check(ibm_power_packages_dictionary)

    #Check multipath
    multipath_errors = 0
    if storage == 'XFS':
        ibm_storage = detect_disk_type("2145")
        multipath_errors = simple_multipath_check(svc_multipath_dictionary, ibm_storage)


    #Exit protocol
    DEVNULL.close()
    print_errors(linux_distribution,selinux_errors,timedatectl_errors,saptune_errors,sysctl_warnings,sysctl_errors,packages_errors,ibm_power_packages_errors,multipath_errors,with_multipath,ibm_storage)
    print("")
    print("")

if __name__ == '__main__':
    main()

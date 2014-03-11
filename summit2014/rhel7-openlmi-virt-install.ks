#version=RHEL7
# System authorization information
auth --enableshadow --passalgo=sha512

# Use network installation
#url --url="http://qafiler.bos.redhat.com/redhat/nightly/latest-RHEL-7/compose/Server/x86_64/os/"
# Run the Setup Agent on first boot
firstboot --enable
ignoredisk --only-use=vda
# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8

# Network information
network  --bootproto=dhcp --device=eth0 --noipv6 --activate
network  --hostname=openlmi.demo.redhat.com

# Root password: "redhat"
rootpw --iscrypted $6$jJ9T6NrbdFdg8XUd$OxxiYdlzlqdEg7vkNxkiT2D.yqWBRMo/7jmV.CYj3i78U9W.JPpTJ5gF6W1lfAXA.I0NVsNR4UkkhvRXCziNC1

# System timezone
timezone America/New_York --isUtc

# System bootloader configuration
bootloader --location=mbr --boot-drive=vda
autopart --type=lvm

# Partition clearing information
clearpart --none --initlabel 


# === OpenLMI-specific enhancements ===
services --enabled=tog-pegasus,slpd,http
selinux --permissive

# Open CIMOM and SLP ports
firewall --service=wbem-https,http --port=427:tcp,427:udp

# Reboot automatically when install completes
reboot

%packages
@core
openlmi
openslp-server
%end

%post

# Assign a password to the pegsus user
echo "redhat"|passwd --stdin pegasus

# Work around a bug in the software provider
# by adding the hostname to the /etc/hosts file
/usr/bin/sed -ie "s/localhost /openlmi.demo.redhat.com localhost /" /etc/hosts

#Create repo pointing to the nightlies

cat << EOF > /etc/yum.repos.d/nightlies.repo
[Server]
name=Server
baseurl=http://download.englab.brq.redhat.com/pub/rhel/rel-eng/latest-RHEL-7/compose/Server/x86_64/os
enabled=1
gpgcheck=0
skip_if_unavailable=1

[Server-optional]
name=Server-optional
baseurl=http://download.englab.brq.redhat.com/pub/rhel/rel-eng/latest-RHEL-7/compose/Server-optional/x86_64/os
enabled=1
gpgcheck=0
skip_if_unavailable=1

[Server-debuginfo]
name=Server-debuginfo
baseurl=http://download.englab.brq.redhat.com/pub/rhel/rel-eng/latest-RHEL-7/compose/Server/x86_64/debug/tree
enabled=1
gpgcheck=0
skip_if_unavailable=1

[Server-optional-debuginfo]
name=Server-optional-debuginfo
baseurl=http://download.englab.brq.redhat.com/pub/rhel/rel-eng/latest-RHEL-7/compose/Server-optional/x86_64/debug/tree
enabled=1
gpgcheck=0
skip_if_unavailable=1
EOF

cat >  /etc/systemd/system/tog-pegasus.service << EOF
[Unit]
Description=OpenPegasus CIM Server
After=syslog.target slpd.service

[Service]
Type=forking
ExecStart=/usr/sbin/cimserver
PIDFile=/var/run/tog-pegasus/cimserver.pid

[Install]
WantedBy=multi-user.target
EOF

# Configure pegasus to use openslp
/usr/sbin/cimconfig -s slp=True -p

%end


#!/bin/bash

# specify a path to some rhel7 bootable image
LOCATION==${LOCATION:-/mnt/globalsync/rhel/nightly/latest-RHEL-7/compose/Server/x86_64/os/}
QEMU="${QEMU:-qemu:///system}"
SYSTEMDISK=${SYSTEMDISK:-/var/tmp/openlmi-demo-system.img,size=5}
TESTDISKS=${TESTDISKS:-/var/tmp/openlmi-demo-test%d.img,size=1}
MAINNETWORK=${MAINNETWORK:-virbr0}
TESTNETWORK=${TESTNETWORK:-test}
TESTNETWORKIP=${TESTNETWORKIP:-192.168.122.1}
GUESTNAME=${GUESTNAME:-openlmi-stgnet-demo}
KICKSTART=${KICKSTART:-stgnet.ks}

VIRSHCMD="virsh -c ${QEMU}"

function install_test_network() {
    if $VIRSHCMD net-list --all | grep -q "^\s*${TESTNETWORK}\>"; then
        return 0
    fi

    echo "Configuring network"
    testnetcfg=`mktemp`
    if ! [[ ${TESTNETWORKIP} =~ ^(([[:digit:]]+\.){3})([[:digit:]]+)$ ]]; then
        echo "Failed to parse network ip address \"$TESTNETWORKIP\"!" >&2
        exit 1
    fi
    range_start="${BASH_REMATCH[1]}128"
    range_end="${BASH_REMATCH[1]}254"
    cat >$testnetcfg <<-EOF
	<network>
	  <name>$TESTNETWORK</name>
	  <bridge name='virbr1' stp='on' delay='0' />
	  <mac address='52:54:00:BF:CC:48'/>
	  <ip address='${TESTNETWORKIP}' netmask='255.255.255.0'>
	    <dhcp>
	      <range start='$range_start' end='$range_end' />
	    </dhcp>
	  </ip>
	</network>
	EOF
    $VIRSHCMD net-create $testnetcfg || exit 1
    if $VIRSHCMD net-info "${TESTNETWORK}" | grep -qi 'active\s*:\s*no'; then
        $VIRSHCMD net-start "${TESTNETWORK}" || exit 1
    fi
    rm $testnetcfg
}

[ -e local.cfg ] && . local.cfg

if ! [[ -e "${LOCATION}" ]]; then
    echo "Location '$LOCATION' does not exist!" >&2
    exit 1
elif [[ -f "${LOCATION}" ]]; then
    isodir=`mktemp -d`
    echo "Mounting iso $isodir"
    mount -o loop "${LOCATION}" $isodir || exit 1
    LOCATION=$isodir
fi

test_disk_opts=''
for i in `seq 4`; do
    test_disk_opts+=" --disk=$(printf ${TESTDISKS} $i)"
done

echo "Checking network settings."
install_test_network || exit 1


if $VIRSHCMD list --all | grep -q "\<$GUESTNAME\>"; then
    read -p "Seems like domain ${GUESTNAME} already exists, do you want to delete it? [y/n]" \
        answer
    case $answer in
        y*)
            if $VIRSHCMD list --all | grep -q "${GUESTNAME}.*running"; then
                echo "Shutting down \"${GUESTNAME}\" forcefully."
                $VIRSHCMD destroy "${GUESTNAME}" || exit 1
                sleep 2
            fi
            echo "Removing \"${GUESTNAME}\"."
            $VIRSHCMD undefine "${GUESTNAME}" || exit 1
            ;;
        n*)
            echo "Nothing to do."
            exit 0
            ;;
        *)
            echo "Expected 'y' or 'n'!" >&2
            exit 1
            ;;
    esac
fi

initrd_arg=''
if ! [[ "$KICKSTART" =~ ^(http|https|ftp):// ]]; then
    if [[ "$KICKSTART" =~ ^(file://)?(.*) ]]; then
        file_path="${BASH_REMATCH[2]}"
        if [[ "${file_path:0:1}" != / ]]; then
            file_path=`pwd`/$file_path
        fi
        initrd_arg="--initrd-inject=$file_path"
        KICKSTART="file:/$(basename $file_path)"
    fi
fi

echo "Running virt-install"
set -x
virt-install --connect "$QEMU" \
    --virt-type=kvm \
    --hvm \
    --name="$GUESTNAME" \
    --ram=1024 \
    --disk=${SYSTEMDISK} $test_disk_opts \
    --vcpus=2 \
    --network=network:${MAINNETWORK} \
    --network=network:${TESTNETWORK} \
    --network=network:${TESTNETWORK} \
    --location=${LOCATION} \
    --os-type=linux \
    --os-variant=rhel7 \
    ${initrd_arg} \
    --extra-args="ks=${KICKSTART} console=ttyS0,115200 serial text" \
    --console=pty \
    --graphics=none

if [ -d "$isodir" ]; then
    umount $isodir
    rmdir $isodir
fi

#!/bin/bash
# Clean up after storage-demo.sh.

. base.sh

# Do not exit upon first error.
set +e

title +x "Cleaning up after storage demo"

lmi -h $URI <<-EOF
	storage mount delete /mnt/lmivol
	file deletedir /mnt/lmivol
	:cd storage
	lv delete lmivol
	vg delete lmivg
	raid delete microraid
	EOF

# Above could fail if we clean up results of demo run on previous
# installation of guest.
for raid in `lmi -N -h $URI storage raid list | cut -f 1 -d \ `; do
    lmi -h $URI storage raid delete "$raid" || exit 1
done

echo "Cleanup successful."

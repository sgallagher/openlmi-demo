basearch        := x86_64
COMPOSEURL      ?= http://download.eng.brq.redhat.com/pub/rhel/nightly/latest-RHEL-7/compose/Server/$(basearch)/os/
KICKSTART       ?= stgnet.ks
LOCATION        ?= /mnt/globalsync/rhel/nightly/latest-RHEL-7/compose/Server/x86_64/os/
TESTHOSTNAME    ?= openlmi-stgnet-demo.example.com
GUESTNAME       := $(shell echo $(TESTHOSTNAME) | sed 's/\([^.]\+\).*/\1/')

provision: $(KICKSTART)
	KICKSTART=$(KICKSTART) LOCATION=$(LOCATION) GUESTNAME=$(GUESTNAME) \
		  bash provision.sh

%.ks: %.ks.skel
	sed \
	    -e 's,@@COMPOSEURL@@,$(COMPOSEURL),g' \
	    -e 's,@@TESTHOSTNAME@@,$(TESTHOSTNAME),g' <$? >$@

dist: $(KICKSTART)
	scp $^ 'miminar@fedorapeople.org:~/public_html/openlmi-demo'

clean:
	-rm $(KICKSTART)

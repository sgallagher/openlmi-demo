basearch        := x86_64
COMPOSEURL      ?= http://download.lab.bos.redhat.com/nightly/latest-RHEL-7/compose/Server/$(basearch)/os/
KICKSTART       ?= stgnet.ks
LOCATION        ?= ${COMPOSEURL}
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

PKG_DIR = $(NCS_DIR)/packages/auth/cisco-nso-saml2-auth

.PHONY: all packages/cisco-nso-saml2-auth
all: pyvenv packages/cisco-nso-saml2-auth flask-saml2 load start-idp

load:
	ncs-setup --dest .
	cp ncs.conf.example ncs.conf
	(. pyvenv/bin/activate ; make start )


packages/cisco-nso-saml2-auth:
	cp -a $(PKG_DIR) $@
	$(MAKE) clean all -C $@/src

pyvenv:
	virtualenv $@
	pyvenv/bin/pip $(PIP_OPTS) install pip --upgrade

flask-saml2: pyvenv
	git clone https://github.com/mx-moth/flask-saml2.git
	# Patch flask-saml2 to use SHA-256 by default instead of SHA-1
	(cd flask-saml2/flask_saml2; sed -i'' -e 's/Sha1/Sha256/g' idp/idp.py sp/sp.py )
	pyvenv/bin/pip $(PIP_OPTS) install -e flask-saml2 
	pyvenv/bin/pip $(PIP_OPTS) install -r flask-saml2/tests/requirements.txt
	# pyOpenSSL 22.0.0 is needed on platforms with OpenSSL 3.0.
	# Note that flask-saml2 requires pyOpenSSL < 18, but works with newer.
	pyvenv/bin/pip $(PIP_OPTS) install pyopenssl --upgrade
	pyvenv/bin/pip $(PIP_OPTS) install requests 

cisco-nso-saml2-auth-deps: pyvenv
	pyvenv/bin/pip $(PIP_OPTS) install -r \
		$(PACKAGE_DIR)/cisco-nso-saml2-auth/requirements.txt
	touch $@

.PHONY: start-idp
start-idp: flask-saml2
	(. pyvenv/bin/activate ; nohup ./idp.py &)

.PHONY: clean
clean: stop
	$(MAKE) -C packages/cisco-nso-saml2-auth/src clean || true
	rm -rf ./netsim running.DB logs/* state/* ncs-cdb/*
	rm -rf pyvenv flask-saml2 __pycache__
	rm -f README.n* cisco-nso-saml2-auth-deps ncs.conf

.PHONY: clean
clean-logs:
	rm -f logs/*

.PHONY: start
start:
	ncs --with-package-reload-force
	ncs_load -l -m cisco-nso-saml2-auth.xml

.PHONY: stop
stop:
	-ncs --stop
	-pkill -f idp.py

.PHONY: cli-c
cli-c:
	ncs_cli -C -uadmin

.PHONY: cli-j
cli-j:
	ncs_cli -J -uadmin

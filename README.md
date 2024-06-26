# NSO Example - Single Sign-On with Yubikey OTP
The Single Sign-On functionality enables users to login via HTTP based northbound APIs with a single sign-on authentication scheme, such as SAMLv2. This example is the modified example from "misc/single-sign-on" that use Yubikey to authenticate the user "admin". The goal of this example is to show how to modify the original example in "misc/single-sign-on" and create your own SSO service.  To use thie example, one must have the Yubikey hardware. 


## Prequisition
virtualenv
nohup
NSO 6.3       
Yubikey hardware

## Running the Example
Based on the original makefile and steps in the README, this example automate and simplified few steps. If one would like to know in detail how SSO is configured, please refer back to the "misc/single-sign-on"

1. Copy or softlink the "cisco-nso-saml2-auth" packages into the packages folder
2. Setup Enviorment (idp is running in the background now)- make clean all
3. Access WEBUI One - http://localhost:8080/
4. Click on "cisco-nso-saml2-auth" button on the right buttom of the screen
5. Choose user "admin"
6. Register the Yubikey first
7. Log in with Yubikey
8. Confirm the login and redirect back to the WebUI One 


## References
Assertions and Protocols for the OASIS Security Assertion Markup Language
(SAML) V2.0

    https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf


flask-saml2

    https://github.com/mx-moth/flask-saml2


## License
The idp.py file is based on example/idp.py from flask-saml2.

See LICENSE and flask-saml2/LICENSE for further details.

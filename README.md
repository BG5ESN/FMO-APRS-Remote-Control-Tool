# FMO-APRS-Remote-Control-Tool
This tool uses APRS-IS as a network relay to control FMO. There is no command encryption; only the method of signing with hmac(secret, context) is used to ensure the reliability and validity of commands. This open-source library will fully disclose the encryption method to facilitate quick remote control of FMOs via APRS.

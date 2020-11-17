This automates deployment of ssl certificates (e.g. from letsencrypt) to epson printers.

Confirmed working printer models:
  - Epson WF-3720

Usage:

```
usage: epson-certificate-deploy.py [-h] [--headless] [--insecure]
                                   [--no-screenshots] [--debug]
                                   host password certfile keyfile

positional arguments:
  host              printer hostname
  password          printer admin password
  certfile          file which contains the certificate
  keyfile           file which contains the private key

optional arguments:
  -h, --help        show this help message and exit
  --headless        run headless
  --insecure        ignore invalid ssl cert on phone (useful for first setup)
  --no-screenshots  disable saving screenshots for each step
  --debug           debug output
```

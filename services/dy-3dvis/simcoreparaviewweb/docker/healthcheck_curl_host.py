""" Healthcheck script to run inside docker

Example of usage in a Dockerfile
```
    COPY --chown=scu:scu scripts/docker/healthcheck_curl_host.py /healthcheck/healthcheck_curl_host.py
    HEALTHCHECK --interval=30s \
                --timeout=30s \
                --start-period=1s \
                --retries=3 \
                CMD [ "python", "/healthcheck/healthcheck_curl_host.py", "http://localhost:8080/v0/" ]
    ...
```


Q&A:
    1. why not to use curl instead of a python script?
        - SEE https://blog.sixeyed.com/docker-healthchecks-why-not-to-use-curl-or-iwr/

"""


import os
import sys

from urllib.request import urlopen

BOOTS_WITH_DEBUGGER = "2"
if os.environ.get("DEBUG") == BOOTS_WITH_DEBUGGER:
    # Healthcheck disabled with service is boot with a debugger
    print(0)
else:
    print(0 if urlopen("{host}{port}{baseurl}{path}".format(
        host=sys.argv[1],
        port=os.environ.get("SERVER_PORT", 8777),
        baseurl=os.environ.get("SIMCORE_NODE_BASEPATH", ""),
        path=sys.argv[2] if len(sys.argv)>2 else "")
        ).getcode() == 200
        else 1)

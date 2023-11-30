import subprocess
import sys
import os
import shutil
import ctypes
from urllib import request, error
import re
import json
import tarfile
import tempfile
from pathlib import Path
import encodings.idna


CLONE_NEWPID = 0x20000000
REGISTRY_URL = "https://registry.hub.docker.com/v2"
AUTH_URL = "https://auth.docker.io/token"
TMP_DIR_NAME = "/tmp"


def switch_namespace(temp_path):
    # switch PID namespace
    os.chroot(temp_path)
    libc = ctypes.CDLL(None)
    libc.unshare(CLONE_NEWPID)


def download_layers(image, manifest, token, destination_dir):
    manifest_version = manifest["schemaVersion"]

    digests = []
    if manifest_version == 1:
        for layer in manifest["manifests"]:
            digests.append(layer["digest"])
    elif manifest_version == 2:
        for layer in manifest["layers"]:
            digests.append(layer["digest"])

    else:
        raise NotImplementedError("unsupported manifest version")

    with open("response.tgz", "wb") as f:
        for digest in digests:
            req = request.Request(
                f"https://registry.hub.docker.com/v2/library/{image}/blobs/{digest}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.docker.distribution.manifest.v2+json",
                },
            )
            res = request.urlopen(req)
            f.write(res.read())

    tarfile.open("response.tgz").extractall(destination_dir)


def get_manifest(image, tag, token):
    manifest_url = f"{REGISTRY_URL}/library/{image}/manifests/{tag}"

    req = request.Request(
        manifest_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        },
    )

    res = request.urlopen(req)
    res_json = json.loads(res.read().decode("utf-8"))
    return res_json


def download_image(destination_dir, image, tag):
    manifest_url = f"{REGISTRY_URL}/library/{image}/manifests/{tag}"

    try:
        res = request.urlopen(manifest_url)
    except error.HTTPError as e:
        auth = e.headers["www-authenticate"]
        realm = re.search(r'realm="(.+?)"', auth).group(1)
        service = re.search(r'service="(.+?)"', auth).group(1)
        scope = re.search(r'scope="(.+?)"', auth).group(1)

    auth_url = f"{realm}?service={service}&scope={scope}"
    req = request.Request(auth_url)
    res = request.urlopen(req)

    auth_token = json.loads(res.read().decode("utf-8"))["token"]

    manifest = get_manifest(image, tag, auth_token)

    download_layers(image, manifest, auth_token, destination_dir)


def main():
    img = sys.argv[2]
    directory = sys.argv[3]
    args = sys.argv[4:]

    tmp_dir_path = tempfile.TemporaryDirectory()

    image, tag = img.split(":")
    download_image(tmp_dir_path.name, image, tag)

    switch_namespace(tmp_dir_path.name)

    completed_process = subprocess.run([directory, *args], capture_output=True)
    if completed_process.stdout:
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end="")
    else:
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end="")

    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()

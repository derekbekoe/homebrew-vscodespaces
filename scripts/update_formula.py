# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import sys
import logging
import subprocess
import json
import re
import urllib.request
import hashlib
import fileinput

RUBY_FILE_EXTENSION = ".rb"

AGENT_VERSION_ENDPOINTS = [
    "https://online.visualstudio.com/api/v1/Agents/vsoagentosx",
    "https://westeurope.online.visualstudio.com/api/v1/Agents/vsoagentosx",
    "https://westus2.online.visualstudio.com/api/v1/Agents/vsoagentosx",
    "https://eastus.online.visualstudio.com/api/v1/Agents/vsoagentosx",
    "https://southeastasia.online.visualstudio.com/api/v1/Agents/vsoagentosx"
]

AGENT_DOWNLOAD_URL = "https://vsoagentdownloads.blob.core.windows.net/vsoagent/VSOAgent_osx_{}.zip"

class ScriptException(Exception):
    pass

def remote_file_sha256(url):
    logging.debug(f"Calculating sha256 for {url}")
    try:
        response = urllib.request.urlopen(url)
        h = hashlib.sha256()
        for chunk in iter(lambda: response.read(4096), b""):
            h.update(chunk)
        h_digest = h.hexdigest()
        logging.debug(f"SHA256: {h_digest}")
        return h_digest
    except urllib.error.HTTPError as e:
        logging.exception(e)
        raise ScriptException("Unable to get sha256 for the new agent file.")

def ensure_valid_formula_file(formula_filepath):
    if not os.path.isfile(formula_filepath):
        raise ScriptException(f"Formula file '{formula_filepath}' not found.")
    if not formula_filepath.endswith(RUBY_FILE_EXTENSION):
        raise ScriptException(f"A valid formula file should end with {RUBY_FILE_EXTENSION}.")

def get_formula_info(formula_filepath):
    cmd = ['brew', 'info', '--json', formula_filepath]
    logging.debug(f"Running command: {cmd}")
    brew_output_raw = subprocess.check_output(cmd)
    logging.debug(f"Command output: {brew_output_raw}")
    info = json.loads(brew_output_raw)
    if len(info) != 1:
        raise ScriptException(f"Expected information for one formula but got {len(info)}.")
    return info[0]

def get_current_agent_version():
    versions = []
    for endpoint in AGENT_VERSION_ENDPOINTS:
        logging.debug(f"Making GET request to {endpoint}")
        try:
            contents = urllib.request.urlopen(endpoint).read()
            agent_name = json.loads(contents)['name']
            logging.debug(f"Response: name={agent_name}")
            v = re.findall(r'\d+', agent_name)
            if len(v) != 1:
                logging.error(f"Found more than one possible candidate for version number in {agent_name}")
                raise ScriptException("Unable to get agent version from name.")
            versions.append(v[0])
        except urllib.error.HTTPError as e:
            logging.exception(e)
            raise ScriptException("Unable to get the current agent version.")
    return min(versions)

def updated_version_available(formula_info):
    logging.debug(f"Determining if the formula should be updated.")
    current_formula_version = formula_info['versions']['stable']
    current_agent_version = get_current_agent_version()
    logging.debug(f"Current formula version: {current_formula_version}")
    logging.debug(f"Current deployed agent version: {current_agent_version}")
    try:
        if int(current_agent_version) > int(current_formula_version):
            return current_agent_version
    except ValueError as e:
        logging.exception(e)
        raise ScriptException("Unable to determine if an updated version is available.")
    return None

def update_formula(formula_filepath):
    ensure_valid_formula_file(formula_filepath)
    formula_info = get_formula_info(formula_filepath)
    new_version = updated_version_available(formula_info)
    if new_version is None:
        logging.info("No newer version available to update formula to.")
        return None
    else:
        logging.info("Preparing to update the formula file...")
        new_download_url = AGENT_DOWNLOAD_URL.format(new_version)
        new_sha256 = remote_file_sha256(new_download_url)
        logging.info(f"New formula url will be: {new_download_url}")
        logging.info(f"New formula sha256 will be: {new_sha256}")
        replaced_url = False
        replaced_sha = False
        with fileinput.input(formula_filepath, inplace=True) as f:
            for line in f:
                if not replaced_url:
                    line, replaced_url = re.subn(r'url "https://(.+)"', f'url "{new_download_url}"', line, count=1)
                if not replaced_sha:
                    line, replaced_sha = re.subn(r'sha256 "[A-Fa-f0-9]{64}"', f'sha256 "{new_sha256}"', line, count=1)
                print(line, end='')
        logging.info("Completed updates to formula file.")
        return new_version

def main():
    """Main Method

    The only output to stdout should be the new formula version if there is one.
    All other output should use logging which outputs to stderr.
    """
    if len(sys.argv) != 2:
        raise ScriptException(f"Usage: python3 {sys.argv[0]} FORMULA_FILEPATH")
    formula_filepath = sys.argv[1]
    logging.debug(f"Using file {formula_filepath}")
    new_formula_version = update_formula(formula_filepath)
    if new_formula_version is None:
        pass
    else:
        logging.info(f"The new version is {new_formula_version}")
        print(new_formula_version)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG)
    try:
        main()
    except ScriptException as e:
        logging.error(e)
        sys.exit(1)

#!/usr/bin/env bash
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ../..
python3.6 ./infra/run/app_client.py "$@"
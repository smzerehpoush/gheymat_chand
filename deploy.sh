#!/bin/bash
set -e

cd /root/projects/personal/gheymat_chand
docker compose down
docker compose up --build -d

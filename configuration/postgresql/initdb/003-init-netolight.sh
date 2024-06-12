#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    create role netolight with login password 'netolight';
    create database nl with owner netolight;
    create database nls with owner netolight;
EOSQL

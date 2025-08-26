#!/bin/bash
gunicorn investmentdb.wsgi:application

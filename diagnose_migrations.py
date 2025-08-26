import os, sys, django, traceback, sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
log_path = BASE_DIR / 'migration_log.txt'

def writeln(msg: str):
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Reset log
if log_path.exists():
    log_path.unlink()

writeln(f"=== Migration Diagnose Run {datetime.utcnow().isoformat()}Z ===")
try:
    import django
    writeln(f"Django version: {django.get_version()}")
    django.setup()
    writeln("Django setup OK")
except Exception as e:
    writeln("Django setup FAILED: " + repr(e))
    writeln(traceback.format_exc())
    sys.exit(1)

from django.apps import apps
from django.db import connection
from django.core.management import call_command
from django.db.migrations.recorder import MigrationRecorder

writeln("Installed apps:")
for app_config in apps.get_app_configs():
    writeln(f" - {app_config.label} ({app_config.name})")

# List current tables
try:
    with connection.cursor() as c:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in c.fetchall()]
    writeln(f"Existing tables BEFORE migrate ({len(tables)}): {tables}")
except Exception as e:
    writeln("Error listing tables before migrate: " + repr(e))

# List applied migrations before
try:
    recorder = MigrationRecorder(connection)
    applied = recorder.migration_qs.values_list('app', 'name')
    applied_list = list(applied)
    writeln(f"Applied migrations BEFORE migrate ({len(applied_list)}): {applied_list}")
except Exception as e:
    writeln("MigrationRecorder error BEFORE: " + repr(e))

# Run migrate
writeln("Running call_command('migrate', verbosity=2)...")
try:
    call_command('migrate', verbosity=2, interactive=False)
    writeln("call_command migrate finished OK")
except Exception as e:
    writeln("call_command migrate FAILED: " + repr(e))
    writeln(traceback.format_exc())

# After migrate
try:
    with connection.cursor() as c:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables_after = [r[0] for r in c.fetchall()]
    writeln(f"Existing tables AFTER migrate ({len(tables_after)}): {tables_after}")
except Exception as e:
    writeln("Error listing tables after migrate: " + repr(e))

try:
    recorder = MigrationRecorder(connection)
    applied = recorder.migration_qs.values_list('app', 'name')
    applied_list_after = list(applied)
    writeln(f"Applied migrations AFTER migrate ({len(applied_list_after)}): {applied_list_after}")
except Exception as e:
    writeln("MigrationRecorder error AFTER: " + repr(e))

writeln("=== END ===")

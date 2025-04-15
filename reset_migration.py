# reset_migration.py
import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

apps = ["bookings.0001_initial", "bookings.0002_alter_booking_services"]
for app in apps:
    cursor.execute("DELETE FROM django_migrations WHERE app = ? AND name = ?", tuple(app.split('.')))
    print(f"✅ Migrationseintrag für '{app}' erfolgreich entfernt.")

conn.commit()
conn.close()

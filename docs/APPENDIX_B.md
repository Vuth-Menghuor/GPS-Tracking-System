# Appendix B — GPS Tracking System Project

## B.1 Frontend Application UI

What to attach:

- Screenshots of the running app (home page, device table, actions). Run the Nuxt dev server and capture: `http://localhost:3000/`.
- Short description of each screenshot (route, purpose).

Key files (copy/paste short snippets):

- `frontend/nuxt-app/pages/index.vue` (main dashboard)

Representative excerpt from `frontend/nuxt-app/pages/index.vue`:

```vue
<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold flex items-center">
          <Icon name="mdi:map-marker-radius" class="mr-3 text-4xl" />
          GPS Tracking System Dashboard
        </h1>
        <p class="text-blue-200 mt-2">
          Manage and monitor your GPS tracking devices
        </p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
              <Icon name="mdi:devices" class="text-2xl" />
            </div>
            <div>
              <p class="text-sm text-gray-600">Total Devices</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.total_devices }}
              </p>
            </div>
          </div>
        </div>

        <!-- more cards... -->
      </div>

      <!-- Action Buttons -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <Icon name="mdi:cog" class="mr-2" />
          Actions
        </h2>

        <div class="flex flex-wrap gap-4">
          <button
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg flex items-center font-semibold transition duration-200"
            :disabled="loading.fetch"
            @click="fetchTrackingData"
          >
            <Icon name="mdi:download" class="mr-2" />
            {{ loading.fetch ? "Fetching..." : "Fetch GPS Data" }}
          </button>

          <!-- other action buttons -->
        </div>
      </div>

      <!-- Device Data Table -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900 flex items-center">
            <Icon name="mdi:table" class="mr-2" />
            Device Records
          </h2>
        </div>

        <!-- Table ... -->
      </div>
    </main>
  </div>
</template>
```

Notes: include 2–4 screenshots (home, a record detail or map view if available) with captions and the route. Mention tech stack: Nuxt 3, Vue 3, Tailwind CSS.

---

## B.2 API Request and Response Data

What to attach:

- Endpoint list (see `backend/api/urls.py` and `backend/protrack/urls.py`).
- Example request/response pairs and the full example response logs.
- The repository contains recorded response logs under `backend/response_logs/`.

Representative sample from `backend/response_logs/tracking_run_2025-10-04_07-39-49/all_records.json` (trimmed):

```json
[
  {
    "imei": "355139085087770",
    "latitude": 10.620982,
    "longitude": 103.537527,
    "coordinates": "10.620982,103.537527",
    "datastatus": 4,
    "datastatus_description": "Offline",
    "hearttime_date": "2025-05-03",
    "hearttime_time": "15:12:30",
    "hearttime_unix": 1746259950,
    "status": "success"
  },
  {
    "imei": "355139085087861",
    "latitude": 10.629293,
    "longitude": 103.520264,
    "coordinates": "10.629293,103.520264",
    "datastatus": 4,
    "datastatus_description": "Offline",
    "hearttime_date": "2025-02-08",
    "hearttime_time": "17:28:15",
    "hearttime_unix": 1739010495,
    "status": "success"
  }
  /* trimmed for brevity */
]
```

Example curl request to list devices (replace path with actual API route):

```bash
curl -s http://127.0.0.1:8000/api/devicedata/ | jq .
```

Location of full logs:

- `backend/response_logs/tracking_run_2025-10-04_07-39-49/all_records.json`

Include in appendix: for each major endpoint, add a 1–2 line description, a sample request, and a trimmed JSON response (1–3 objects).

---

## B.3 Database Schema

Source of truth: Django models in `backend/api/models.py` and the migrations in `backend/api/migrations/`.

Key model (excerpt from `backend/api/models.py`):

```python
from django.db import models
from django.utils import timezone

class DeviceData(models.Model):
    ranking_id = models.AutoField(primary_key=True)
    imei = models.CharField(max_length=20, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    coordinates = models.CharField(max_length=50)
    datastatus = models.IntegerField()
    datastatus_description = models.CharField(max_length=50)
    hearttime_date = models.DateField(null=True, blank=True)
    hearttime_time = models.TimeField(null=True, blank=True)
    hearttime_unix = models.BigIntegerField()
    status = models.CharField(max_length=20)
    last_update_detailed_db = models.DateTimeField(default=timezone.now)
    last_update_relative_db = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ranking_id']

    def __str__(self):
        return f"IMEI: {self.imei} - {self.status}"
```

Generated SQL for migration `0002` (trimmed):

```sql
BEGIN;
--
-- Create model DeviceData
--
CREATE TABLE "api_devicedata" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "imei" varchar(20) NOT NULL UNIQUE,
  "latitude" decimal NOT NULL,
  "longitude" decimal NOT NULL,
  "coordinates" varchar(50) NOT NULL,
  "datastatus" integer NOT NULL,
  "datastatus_description" varchar(50) NOT NULL,
  "hearttime_date" date NOT NULL,
  "hearttime_time" time NOT NULL,
  "hearttime_unix" bigint NOT NULL,
  "status" varchar(20) NOT NULL,
  "created_at" datetime NOT NULL,
  "updated_at" datetime NOT NULL
);
COMMIT;
```

Notes:

- Migrations are stored in `backend/api/migrations/` (0001..0009). Use `manage.py sqlmigrate api <migration>` to recreate SQL statements for each migration.
- If you need a Postgres schema dump, run `docker exec -i gps-postgres pg_dump -U postgres -s postgres > schema_postgres.sql`.

---

## Files referenced (for instructor review)

- Frontend: `frontend/nuxt-app/pages/index.vue`, `frontend/nuxt-app/nuxt.config.ts`, `frontend/nuxt-app/package.json`
- Backend API: `backend/api/views.py`, `backend/api/urls.py`, `backend/protrack/urls.py`
- Logged API responses: `backend/response_logs/*/all_records.json`
- Models & migrations: `backend/api/models.py`, `backend/api/migrations/`

---

## How I extracted these artifacts (quick commands)

- Frontend page snippet:
  sed -n '1,240p' frontend/nuxt-app/pages/index.vue

- Sample response log (trimmed):
  sed -n '1,200p' backend/response_logs/tracking_run_2025-10-04_07-39-49/all_records.json

- Models:
  sed -n '1,240p' backend/api/models.py

- SQL for migration 0002:
  .venv/bin/python backend/manage.py sqlmigrate api 0002

---

(End of Appendix B)

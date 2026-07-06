# IT Inventory Management Web App Implementation Plan

## 1. Project Overview

Build a Dockerized IT inventory management web app for an IT assistant/team to manage laptops and IT devices.

The app will:

- Maintain a master inventory of all known devices.
- Track what devices are physically in the IT office.
- Track check-in, check-out, storage, repair, missing, retired, and disposed states.
- Import ServiceNow CSV reports from scheduled emails.
- Sync Intune device data using a pasted bearer token.
- Detect and identify devices using webcam OCR and later YOLO-assisted scanning.
- Show conflicts between ServiceNow, Intune, local inventory, and OCR results.
- Provide dashboards, reports, and device history.

---

## 2. Final Technology Stack

```text
Frontend:
Next.js + TypeScript + Tailwind CSS + shadcn/ui

Backend:
FastAPI + Python

Database:
PostgreSQL

ORM and migrations:
SQLAlchemy 2 + Alembic

Background jobs:
Redis + RQ

Email import:
Microsoft Graph mail API if available, otherwise IMAP

AI scanning:
OpenCV + PaddleOCR first
Ultralytics YOLO11n or YOLOv8n second

Deployment:
Docker Compose on Windows using Docker Desktop + WSL 2
```

### Why this stack?

- **Next.js** is strong for dashboards, routing, forms, tables, and modern React apps.
- **FastAPI** is ideal because the backend needs Python for OCR, YOLO, OpenCV, CSV imports, and API integrations.
- **PostgreSQL** is the best database because the data is relational and needs reliable history, reporting, and search.
- **Redis + RQ** is useful because email imports, CSV processing, Intune sync, and heavy OCR tasks should run in the background.
- **Docker Compose** makes the app easier to run on Windows without installing many dependencies directly.

---

## 3. Final Architecture

```text
Windows 11 Machine
  |
  |-- Docker Desktop + WSL 2
        |
        |-- frontend container
        |     Next.js web app
        |
        |-- backend container
        |     FastAPI REST API
        |
        |-- worker container
        |     RQ worker for background jobs
        |
        |-- scheduler container
        |     scheduled email CSV import jobs
        |
        |-- postgres container
        |     main database
        |
        |-- redis container
              background job queue
```

The frontend should only communicate with the FastAPI backend.

```text
Next.js frontend
  -> FastAPI backend
      -> PostgreSQL
      -> Redis queue
      -> Email inbox
      -> Microsoft Graph Intune endpoint
      -> OCR / YOLO scanner
```

---

## 4. Why Redis Is Included

Redis is not used to store inventory data. PostgreSQL stores the real data.

Redis is used for background jobs such as:

```text
Check email inbox
Find latest ServiceNow CSV
Download attachment
Import CSV
Match devices
Detect conflicts
Sync Intune
Generate reports
Process heavy OCR images
```

Correct background flow:

```text
Scheduler triggers job
  -> Redis stores job
  -> Worker processes job
  -> PostgreSQL stores result
  -> Frontend shows status
```

---

## 5. Main App Modules

```text
1. Authentication and users
2. Dashboard
3. Device master inventory
4. ServiceNow email CSV import
5. Intune sync
6. Device matching engine
7. Office inventory
8. Check-in / check-out workflow
9. Webcam OCR/YOLO scanner
10. Conflict review
11. Device history timeline
12. Reports
13. Settings
14. Audit logs
```

---

## 6. Source-of-Truth Rules

The app should treat each data source differently.

```text
Local app:
Truth for physical office inventory.

ServiceNow:
Truth for official asset ownership and administrative data.

Intune:
Truth for live device management state.

OCR/YOLO:
Suggested truth only. User must confirm before updating records.
```

Example conflict:

```text
ServiceNow says assigned_to = John
Intune says userPrincipalName = Sarah
Local app says status = IN_OFFICE
OCR reads asset_tag = CON4136579
```

The app should show this as a conflict, not silently overwrite everything.

---

## 7. Inventory Concepts

### 7.1 Master Device Inventory

This is every device the team owns or knows about.

Examples:

```text
Laptops
Desktops
Monitors
Printers
Routers
Docks
Chargers
Accessories
Loaners
Retired devices
Disposed devices
```

### 7.2 Office Physical Inventory

This is what is physically in the IT office right now.

Statuses:

```text
IN_OFFICE
CHECKED_OUT
STORED
UNDER_REPAIR
READY_FOR_PICKUP
LOANER
RETURNED
MISSING
RETIRED
DISPOSED
```

A device can exist in the master inventory but not be in the office.

Example:

```text
Device: CON4136579
Master inventory: owned by department
ServiceNow status: installed
Intune status: compliant
Office status: checked out
Checked out to: rrwesten@asurite.asu.edu
```

---

# 8. Database Design

Use PostgreSQL from the beginning.

---

## 8.1 users

```sql
users
- id UUID primary key
- email unique
- full_name
- role
- password_hash
- is_active
- created_at
- updated_at
```

Roles:

```text
ADMIN
IT_ASSISTANT
VIEWER
```

Permissions:

```text
ADMIN:
imports, syncs, settings, all edits

IT_ASSISTANT:
scan, check-in, check-out, update inventory

VIEWER:
read-only dashboard and reports
```

---

## 8.2 devices

Main master device table.

```sql
devices
- id UUID primary key
- asset_tag
- serial_number
- device_name
- display_name
- manufacturer
- model
- model_category
- device_type
- mac_address
- department
- cost_center
- lifecycle_status
- source_confidence
- notes
- created_at
- updated_at
```

Lifecycle statuses:

```text
ACTIVE
INACTIVE
RETIRED
DISPOSED
LOST
UNKNOWN
PENDING_REVIEW
```

Important indexes:

```sql
index on asset_tag
index on serial_number
index on device_name
index on mac_address
index on department
```

Do not hard-delete devices. Mark them retired, disposed, inactive, or lost.

---

## 8.3 service_now_assets

Stores latest ServiceNow values.

```sql
service_now_assets
- id UUID primary key
- device_id foreign key
- asset_tag
- model_category
- display_name
- u_assigned_to
- assigned_to
- u_cost_center
- install_status
- serial_number
- u_mac_address
- ci
- comments
- department
- imported_at
- import_run_id
- raw_json JSONB
```

Required ServiceNow CSV fields:

```text
asset_tag
model_category
display_name
u_assigned_to
assigned_to
u_cost_center
install_status
serial_number
u_mac_address
ci
comments
department
```

---

## 8.4 intune_devices

Stores latest Intune data.

```sql
intune_devices
- id UUID primary key
- device_id foreign key
- intune_id
- device_name
- management_agent
- owner_type
- compliance_state
- device_type
- os_version
- user_principal_name
- last_sync_datetime
- device_registration_state
- management_state
- exchange_access_state
- exchange_access_state_reason
- jail_broken
- enrolled_datetime
- device_enrollment_type
- synced_at
- sync_run_id
- raw_json JSONB
```

Your current Graph endpoint uses `/beta`. The backend should keep the Graph URL configurable so it can be changed later without rewriting the sync logic.

---

## 8.5 office_inventory

Stores the current physical office status.

```sql
office_inventory
- id UUID primary key
- device_id unique foreign key
- current_status
- current_location
- assigned_user_name
- assigned_user_email
- checked_out_to
- checked_out_by
- checked_out_at
- expected_return_at
- checked_in_by
- checked_in_at
- condition
- notes
- updated_at
```

Conditions:

```text
GOOD
MINOR_DAMAGE
MAJOR_DAMAGE
MISSING_CHARGER
NEEDS_REIMAGE
NEEDS_REPAIR
UNKNOWN
```

---

## 8.6 inventory_events

Every inventory movement creates an event.

```sql
inventory_events
- id UUID primary key
- device_id foreign key
- event_type
- from_status
- to_status
- performed_by
- assigned_to_name
- assigned_to_email
- location
- condition
- notes
- created_at
```

Event types:

```text
IMPORTED_FROM_SERVICENOW
SYNCED_FROM_INTUNE
SCANNED_BY_WEBCAM
ADDED_TO_OFFICE
CHECKED_OUT
CHECKED_IN
MOVED_TO_STORAGE
MARKED_UNDER_REPAIR
MARKED_READY_FOR_PICKUP
MARKED_MISSING
MARKED_RETIRED
MARKED_DISPOSED
UPDATED_MANUALLY
CONFLICT_DETECTED
CONFLICT_RESOLVED
DEVICE_MERGED
```

This lets the team answer:

```text
Who touched this device?
When was it checked out?
When was it returned?
Was it ever marked missing?
Who scanned it?
What changed?
```

---

## 8.7 scan_results

Stores webcam scan results.

```sql
scan_results
- id UUID primary key
- device_id nullable foreign key
- detected_asset_tag
- detected_serial_number
- detected_model
- detected_device_name
- detected_text
- confidence_score
- image_path
- scan_status
- confirmed_by
- confirmed_at
- created_at
```

Scan statuses:

```text
PENDING_CONFIRMATION
MATCHED
NO_MATCH
LOW_CONFIDENCE
CONFIRMED
REJECTED
```

---

## 8.8 data_conflicts

Tracks mismatches.

```sql
data_conflicts
- id UUID primary key
- device_id foreign key
- field_name
- service_now_value
- intune_value
- local_value
- ocr_value
- conflict_type
- severity
- status
- resolved_value
- resolved_by
- resolved_at
- created_at
```

Conflict statuses:

```text
OPEN
RESOLVED
IGNORED
NEEDS_REVIEW
```

Examples:

```text
ServiceNow assigned_to != Intune userPrincipalName
ServiceNow serial_number missing but OCR found one
Intune device exists but not in ServiceNow
ServiceNow device exists but not in Intune
Local status says IN_OFFICE but Intune shows active user
```

---

## 8.9 import_runs

Tracks each ServiceNow import.

```sql
import_runs
- id UUID primary key
- source
- started_at
- finished_at
- status
- file_name
- email_subject
- email_received_at
- total_rows
- created_devices
- updated_devices
- matched_devices
- conflicts_created
- errors_count
- error_log JSONB
```

Source values:

```text
EMAIL
MANUAL_UPLOAD
```

---

## 8.10 sync_runs

Tracks Intune syncs.

```sql
sync_runs
- id UUID primary key
- source
- started_at
- finished_at
- status
- total_records
- matched_devices
- created_devices
- conflicts_created
- errors_count
- error_log JSONB
```

---

## 8.11 email_import_state

Prevents duplicate imports.

```sql
email_import_state
- id UUID primary key
- provider
- mailbox
- last_processed_message_id
- last_processed_received_at
- last_successful_import_at
- updated_at
```

---

## 8.12 audit_logs

Tracks important system actions.

```sql
audit_logs
- id UUID primary key
- user_id
- action
- entity_type
- entity_id
- old_value JSONB
- new_value JSONB
- ip_address
- created_at
```

---

# 9. Device Matching Engine

Create this service:

```text
backend/app/services/device_matching_service.py
```

Matching priority:

```text
1. serial_number exact match
2. asset_tag exact match
3. device_name exact match
4. mac_address exact match
5. ServiceNow CI match
6. Intune id match
7. fuzzy display_name match
8. assigned user + model similarity
```

Confidence scoring:

```text
100 = serial_number exact match
98  = Intune id exact match
95  = asset_tag exact match
92  = ServiceNow CI exact match
90  = device_name exact match
85  = MAC address exact match
75  = display_name fuzzy match
60  = model + assigned user match
50  = weak possible match
```

Rules:

```text
confidence >= 90:
safe auto-match

confidence 75-89:
show suggested match, require confirmation

confidence < 75:
do not match automatically
```

Never auto-merge low-confidence devices.

---

# 10. ServiceNow Email CSV Import Workflow

Recommended flow:

```text
1. ServiceNow sends scheduled CSV report to mailbox.
2. Scheduler container runs at configured time.
3. Scheduler enqueues email import job in Redis.
4. Worker picks up job.
5. Worker reads mailbox.
6. Worker finds latest ServiceNow email.
7. Worker downloads CSV attachment.
8. Worker validates required columns.
9. Worker creates import_run.
10. Worker parses CSV.
11. Worker matches rows to devices.
12. Worker updates service_now_assets.
13. Worker updates missing master device fields carefully.
14. Worker creates conflicts.
15. Worker stores import summary.
16. Dashboard shows latest import result.
```

Required CSV validation:

```text
asset_tag
model_category
display_name
u_assigned_to
assigned_to
u_cost_center
install_status
serial_number
u_mac_address
ci
comments
department
```

Important import rule:

ServiceNow can update:

```text
asset_tag
model_category
display_name
assigned_to
cost_center
install_status
serial_number
mac_address
ci
department
comments
```

ServiceNow should not overwrite:

```text
current office status
checked out state
local inventory event history
local notes
scan history
```

---

# 11. Email Integration Options

## Best option if allowed

Use Microsoft Graph mail API with proper app registration.

Benefits:

```text
More secure
Modern authentication
No password storage
Works well with Microsoft 365
```

## Practical option if Graph mail access is not available

Use IMAP with an app password or service account, only if the organization allows it.

Email settings should be stored in environment variables:

```env
EMAIL_PROVIDER=imap
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
EMAIL_USERNAME=your-service-mailbox
EMAIL_PASSWORD=secret
SERVICENOW_EMAIL_FROM=servicenow@example.edu
SERVICENOW_EMAIL_SUBJECT_CONTAINS=Asset Report
```

Do not store email passwords in code.

---

# 12. Intune Sync Workflow

The current process requires pasting a bearer token from the browser. This is acceptable for an internal tool if handled carefully.

Flow:

```text
1. Admin opens /sync/intune.
2. Admin pastes bearer token.
3. Frontend sends token to backend over HTTPS/local network.
4. Backend calls Microsoft Graph Intune endpoint.
5. Backend follows pagination until all records are fetched.
6. Backend stores latest Intune records.
7. Backend matches Intune records to devices.
8. Backend creates conflicts.
9. Backend stores sync summary.
10. Backend discards token immediately.
```

Security rules:

```text
Never store the bearer token.
Never log the bearer token.
Never show token in error messages.
Never save token in browser localStorage.
Use memory state only in frontend.
Use HTTPS if hosted for the team.
Restrict access to ADMIN role.
```

Pagination rule:

The backend must support pagination until no more records remain.

Also store full raw Intune JSON in `raw_json` for debugging.

---

# 13. Webcam Scanner Implementation

Build this in two phases.

---

## 13.1 Phase A: OCR-only scanner

Start with OCR only.

```text
Browser webcam
  -> capture image
  -> send image to FastAPI
  -> OpenCV preprocessing
  -> PaddleOCR
  -> regex extraction
  -> search device database
  -> return possible matches
  -> user confirms match
```

This is faster to build and may already solve much of the use case.

---

## 13.2 Phase B: YOLO + OCR scanner

Then add YOLO.

```text
Browser webcam
  -> capture image
  -> FastAPI
  -> YOLO detects device / label area
  -> crop label region
  -> OpenCV preprocessing
  -> PaddleOCR reads text
  -> regex extracts asset tag/model/serial
  -> matching engine finds possible devices
  -> user confirms action
```

YOLO detects where the label/device is.

OCR reads what text is on it.

---

# 14. OCR Extraction Rules

Create:

```text
backend/app/utils/regex_extractors.py
```

Patterns:

```python
ASSET_TAG_PATTERNS = [
    r"\bCON\d+\b",
    r"\bIT[- ]?\d{4,}\b",
    r"\bASSET[- #:]*[A-Z0-9-]+\b",
    r"\bINV[- ]?\d{4,}\b"
]

SERIAL_PATTERNS = [
    r"\bS\/N[: ]*[A-Z0-9-]+\b",
    r"\bSN[: ]*[A-Z0-9-]+\b",
    r"\bSERIAL[: ]*[A-Z0-9-]+\b",
    r"\bSERVICE TAG[: ]*[A-Z0-9-]+\b"
]

MODEL_PATTERNS = [
    r"\bLATITUDE\s+\d{4}\b",
    r"\bELITEBOOK\s+\d{3,4}\b",
    r"\bTHINKPAD\s+[A-Z0-9-]+\b",
    r"\bOPTIPLEX\s+\d{4}\b",
    r"\bPRECISION\s+\d{4}\b",
    r"\bSURFACE\s+[A-Z0-9 ]+\b"
]
```

Since an example device is:

```text
CON4136579
```

`CON\d+` should be a primary asset/device-name pattern.

---

# 15. Scanner Page Behavior

Frontend page:

```text
/scan
```

UI:

```text
Live webcam preview

Buttons:
- Capture
- Scan continuously
- Stop scanning

Detected:
- Raw text
- Asset tag
- Serial number
- Model
- Confidence

Possible matches:
- Device card
- Confidence score
- Reason for match

Actions:
- Confirm Match
- Add to Office
- Check Out
- Check In
- Mark Under Repair
- Update Device Info
- Create New Device
```

Do not send every video frame.

Send one frame every 700-1000 ms during continuous scanning.

---

# 16. Office Inventory Workflows

## 16.1 Add to office

```text
Scan/search device
Select location
Select condition
Add notes
Save
```

Database actions:

```text
office_inventory.current_status = IN_OFFICE
create inventory_event: ADDED_TO_OFFICE
```

---

## 16.2 Check out to user

```text
Scan/search device
Enter user name/email
Select reason
Set expected return date
Add notes
Save
```

Database actions:

```text
office_inventory.current_status = CHECKED_OUT
office_inventory.checked_out_to = user
create inventory_event: CHECKED_OUT
```

---

## 16.3 Check in from user

```text
Scan/search device
Confirm returned item
Select condition
Mark missing accessories if needed
Add notes
Save
```

Database actions:

```text
office_inventory.current_status = IN_OFFICE or UNDER_REPAIR
create inventory_event: CHECKED_IN
```

---

## 16.4 Mark under repair

```text
Select device
Set condition
Add repair notes
Save
```

Database actions:

```text
office_inventory.current_status = UNDER_REPAIR
create inventory_event: MARKED_UNDER_REPAIR
```

---

## 16.5 Move to storage

```text
Select device
Choose storage location
Save
```

Database actions:

```text
office_inventory.current_status = STORED
create inventory_event: MOVED_TO_STORAGE
```

---

# 17. Backend API Plan

## 17.1 Auth

```http
POST /auth/login
POST /auth/logout
GET  /auth/me
POST /auth/change-password
```

## 17.2 Devices

```http
GET    /devices
GET    /devices/{device_id}
POST   /devices
PATCH  /devices/{device_id}
GET    /devices/{device_id}/history
GET    /devices/{device_id}/conflicts
POST   /devices/{device_id}/merge
```

## 17.3 ServiceNow imports

```http
POST /imports/servicenow/manual-upload
POST /imports/servicenow/from-email
GET  /imports/servicenow/history
GET  /imports/servicenow/{import_run_id}
```

## 17.4 Intune sync

```http
POST /sync/intune
GET  /sync/intune/history
GET  /sync/intune/{sync_run_id}
```

Request:

```json
{
  "bearer_token": "eyJ...",
  "graph_url": "optional override"
}
```

## 17.5 Inventory actions

```http
GET  /inventory/office
GET  /inventory/checked-out
POST /inventory/add-to-office
POST /inventory/check-out
POST /inventory/check-in
POST /inventory/mark-under-repair
POST /inventory/move-to-storage
POST /inventory/mark-missing
POST /inventory/mark-retired
POST /inventory/mark-disposed
```

## 17.6 Scanning

```http
POST /scan/image
POST /scan/confirm
GET  /scan/history
GET  /scan/{scan_id}
```

## 17.7 Conflicts

```http
GET  /conflicts
GET  /conflicts/{conflict_id}
POST /conflicts/{conflict_id}/resolve
POST /conflicts/{conflict_id}/ignore
```

## 17.8 Jobs

```http
GET  /jobs/{job_id}
GET  /jobs
```

## 17.9 Reports

```http
GET /reports/dashboard-summary
GET /reports/office-inventory
GET /reports/checked-out
GET /reports/overdue
GET /reports/missing
GET /reports/servicenow-not-intune
GET /reports/intune-not-servicenow
GET /reports/conflicts
GET /reports/export/csv
```

## 17.10 Settings

```http
GET   /settings
PATCH /settings
```

---

# 18. Frontend Pages

Use Next.js App Router.

```text
/app
  /login
  /dashboard
  /devices
  /devices/[id]
  /inventory/office
  /inventory/checked-out
  /imports/servicenow
  /sync/intune
  /scan
  /conflicts
  /reports
  /settings
```

Dashboard cards:

```text
Total devices
In office
Checked out
Under repair
Missing
Overdue loaners
Open conflicts
Last ServiceNow import
Last Intune sync
```

Device detail page should show:

```text
Main identity
Office status
ServiceNow data
Intune data
Scan history
Inventory event timeline
Conflict list
Notes
Action buttons
```

Device list filters:

```text
Asset tag
Serial number
Device name
Assigned user
Department
Model
Device type
Office status
Compliance state
Lifecycle status
Conflict status
```

Use TanStack Table for sorting, filtering, pagination, and column visibility.

---

# 19. Project Folder Structure

```text
it-inventory-app/
  docker-compose.yml
  .env.example
  README.md

  backend/
    Dockerfile
    requirements.txt
    alembic.ini

    app/
      main.py
      config.py
      database.py
      security.py
      dependencies.py

      models/
        user.py
        device.py
        service_now_asset.py
        intune_device.py
        office_inventory.py
        inventory_event.py
        scan_result.py
        data_conflict.py
        import_run.py
        sync_run.py
        audit_log.py
        email_import_state.py

      schemas/
        auth.py
        device.py
        inventory.py
        imports.py
        intune.py
        scan.py
        conflict.py
        reports.py

      routers/
        auth.py
        devices.py
        inventory.py
        imports.py
        intune.py
        scan.py
        conflicts.py
        reports.py
        jobs.py
        settings.py

      services/
        auth_service.py
        device_service.py
        inventory_service.py
        servicenow_import_service.py
        email_service.py
        intune_sync_service.py
        device_matching_service.py
        conflict_service.py
        ocr_service.py
        yolo_service.py
        report_service.py
        audit_service.py

      workers/
        rq_worker.py
        jobs.py
        scheduler.py

      utils/
        regex_extractors.py
        csv_validation.py
        image_preprocessing.py
        pagination.py
        logging.py

      migrations/
        versions/

      tests/
        test_device_matching.py
        test_servicenow_import.py
        test_inventory_actions.py
        test_regex_extractors.py

  frontend/
    Dockerfile
    package.json
    next.config.ts
    tailwind.config.ts

    src/
      app/
        login/
        dashboard/
        devices/
        inventory/
        imports/
        sync/
        scan/
        conflicts/
        reports/
        settings/

      components/
        layout/
        tables/
        forms/
        device/
        inventory/
        scan/
        dashboard/

      lib/
        api-client.ts
        auth.ts
        utils.ts

      types/
        device.ts
        inventory.ts
        scan.ts
```

---

# 20. Docker Compose Plan

Final services:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
      - redis

  worker:
    build: ./backend
    command: rq worker default
    env_file:
      - .env
    depends_on:
      - postgres
      - redis

  scheduler:
    build: ./backend
    command: python -m app.workers.scheduler
    env_file:
      - .env
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: it_inventory
      POSTGRES_USER: inventory_user
      POSTGRES_PASSWORD: inventory_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

For production/team use, remove public database and Redis ports unless needed:

```text
Remove:
5432:5432
6379:6379
```

Only frontend and backend should be exposed.

---

# 21. Environment Variables

Create `.env.example`:

```env
APP_ENV=development
APP_SECRET_KEY=change_me
ACCESS_TOKEN_EXPIRE_MINUTES=720

DATABASE_URL=postgresql+psycopg://inventory_user:inventory_password@postgres:5432/it_inventory
REDIS_URL=redis://redis:6379/0

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

SERVICENOW_REQUIRED_COLUMNS=asset_tag,model_category,display_name,u_assigned_to,assigned_to,u_cost_center,install_status,serial_number,u_mac_address,ci,comments,department

EMAIL_IMPORT_ENABLED=true
EMAIL_PROVIDER=imap
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
EMAIL_USERNAME=
EMAIL_PASSWORD=
SERVICENOW_EMAIL_FROM=
SERVICENOW_EMAIL_SUBJECT_CONTAINS=

INTUNE_GRAPH_URL=https://graph.microsoft.com/beta/deviceManagement/managedDevices
INTUNE_PAGE_SIZE=50

SCAN_IMAGE_STORAGE_PATH=/app/storage/scans
OCR_ENGINE=paddleocr
YOLO_ENABLED=false
YOLO_MODEL_PATH=/app/models/yolo11n.pt
```

---

# 22. Build Order

## Phase 0: Setup

Build:

```text
Git repository
Docker Compose
FastAPI skeleton
Next.js skeleton
PostgreSQL connection
Alembic migrations
Basic README
```

Success condition:

```text
docker compose up --build
Frontend opens at localhost:3000
Backend docs open at localhost:8000/docs
Database connects
```

---

## Phase 1: Auth and users

Build:

```text
Login page
JWT authentication
User roles
Protected frontend routes
Backend auth dependencies
```

Success condition:

```text
Admin can log in
Unauthenticated users cannot access app
Roles are available in backend
```

---

## Phase 2: Database models and migrations

Build all core tables:

```text
users
devices
service_now_assets
intune_devices
office_inventory
inventory_events
scan_results
data_conflicts
import_runs
sync_runs
audit_logs
email_import_state
```

Success condition:

```text
Alembic can create full schema
Database has indexes and foreign keys
```

---

## Phase 3: Manual device inventory

Build:

```text
Device list
Device detail
Create device
Edit device
Search/filter
Basic dashboard
```

Success condition:

```text
You can use the app manually even before imports exist
```

---

## Phase 4: Office inventory actions

Build:

```text
Add to office
Check out
Check in
Move to storage
Mark under repair
Mark missing
Mark retired
Event timeline
```

Success condition:

```text
Every movement updates office_inventory
Every movement creates inventory_events row
Device detail shows full timeline
```

---

## Phase 5: ServiceNow manual CSV import

Build manual CSV upload before email automation.

```text
Upload CSV
Validate columns
Preview data
Import rows
Match devices
Create/update service_now_assets
Create conflicts
Show import summary
```

Success condition:

```text
A ServiceNow CSV can populate your database
Import summary is stored
Conflicts are visible
```

---

## Phase 6: ServiceNow email CSV import

Build:

```text
Email connection
Find latest ServiceNow report email
Download CSV attachment
Prevent duplicate imports
Run import as RQ background job
Show job status
Show import result
```

Success condition:

```text
Scheduled email report can be imported without manual upload
Dashboard shows latest import
```

---

## Phase 7: Intune sync

Build:

```text
Paste bearer token page
Graph API call
Pagination support
Store intune_devices
Device matching
Conflict detection
Sync summary
```

Success condition:

```text
You can paste token, sync Intune, and match records to existing devices
```

---

## Phase 8: Conflict review

Build:

```text
Conflict list
Conflict detail
Resolve conflict
Ignore conflict
Accept ServiceNow value
Accept Intune value
Keep local value
Manual merge
```

Success condition:

```text
Mismatches are not hidden
You can clean data safely
```

---

## Phase 9: OCR scanner

Build:

```text
Webcam page
Capture image
Send to backend
OpenCV preprocessing
PaddleOCR text extraction
Regex field extraction
Database match suggestions
Confirm match
Perform inventory action from scan result
```

Success condition:

```text
Show device label to webcam
App detects asset tag like CON4136579
App shows possible matching device
User confirms and updates inventory
```

---

## Phase 10: YOLO scanner upgrade

Build:

```text
YOLO model loading
Detect device/label region
Crop image
Run OCR on crop
Improve scan confidence
```

Success condition:

```text
OCR becomes more accurate because background text is ignored
```

---

## Phase 11: Reports

Build:

```text
Office inventory report
Checked-out devices
Overdue loaners
Under repair devices
Missing devices
ServiceNow but not Intune
Intune but not ServiceNow
Devices not synced recently
Devices missing serial number
Devices missing asset tag
Open conflicts
CSV export
```

Success condition:

```text
The team can use reports for daily work
```

---

## Phase 12: Hardening and deployment

Build:

```text
Backups
Logging
Error handling
HTTPS or internal network protection
Role permissions
Docker production compose
Database restore test
```

Success condition:

```text
App is safe enough for team use
Data is backed up
Failures are visible
```

---

# 23. Backup Plan

Backups are required from the beginning.

Add a backup script:

```text
backup_postgres.sh
```

Backup frequency:

```text
Daily database backup
Keep last 14 or 30 backups
Manual backup before big imports
```

Store backups outside the container volume.

Example backup destination on Windows:

```text
C:\ITInventoryBackups
```

Example backup destination inside WSL:

```text
~/backups/it-inventory
```

Also back up uploaded scan images if they are stored.

---

# 24. Logging Plan

Log these:

```text
User login
CSV import started/finished/failed
Email import started/finished/failed
Intune sync started/finished/failed
Inventory check-in/check-out
Conflict created/resolved
OCR scan result
Device merge
Permission failures
```

Never log:

```text
Bearer tokens
Passwords
Email passwords
Full authorization headers
Sensitive session tokens
```

---

# 25. Security Plan

Minimum security:

```text
Login required
Role-based access
JWT tokens
Password hashing
Do not store Intune bearer token
Do not log secrets
Environment variables for secrets
HTTPS if accessed by other team members
Database not exposed publicly
Redis not exposed publicly
```

Later improvement:

```text
Microsoft Entra ID login
Audit export
Device-level permissions
HTTPS reverse proxy
```

---

# 26. Testing Plan

## 26.1 Must-have backend tests

```text
Device matching
ServiceNow CSV validation
ServiceNow CSV import
Duplicate device handling
Inventory check-out/check-in
Conflict detection
Regex extraction
Intune pagination handling
Email duplicate prevention
```

## 26.2 Must-have manual tests

```text
Upload valid CSV
Upload invalid CSV
Import same CSV twice
Sync Intune with expired token
Sync Intune with valid token
Scan blurry asset tag
Scan clear asset tag
Check out device
Check in device
Resolve conflict
Export report
```

---

# 27. Data Quality Rules

## 27.1 Do not overwrite local status

ServiceNow and Intune should not overwrite:

```text
office_inventory.current_status
checked_out_to
checked_out_at
local condition
inventory event history
```

## 27.2 Do not auto-update from OCR

OCR should suggest:

```text
detected_asset_tag
detected_serial_number
detected_model
```

User confirms before database update.

## 27.3 Do not auto-merge weak matches

Only auto-match when confidence is high.

---

# 28. Scanner Accuracy Improvement Plan

Start simple:

```text
Good lighting
Device close to webcam
Manual capture button
OCR-only
```

Then improve:

```text
Crop center area
Grayscale
Sharpen
Increase contrast
Deskew image
Run OCR
```

Then add YOLO:

```text
Detect label area
Crop label
Run OCR on crop
```

Then train custom YOLO if needed:

```text
asset_label
serial_label
barcode_label
laptop
monitor
printer
router
dock
charger
```

---

# 29. Future Features Worth Designing For

The database design supports these later features:

```text
Barcode / QR scanning
Accessory tracking
Loaner agreements
Device photos
Damage photos
Expected return reminders
Email notification for overdue devices
Microsoft Entra login
ServiceNow API integration if approved later
Automatic Intune sync using app registration if approved later
Mobile-friendly scanning page
```

---

# 30. What Not To Do

Avoid these design mistakes:

```text
Do not use SQLite for the final app.
Do not store only the latest status without event history.
Do not let OCR overwrite records automatically.
Do not treat ServiceNow and Intune as always correct.
Do not store bearer tokens.
Do not run email import inside page load.
Do not expose PostgreSQL/Redis to the network.
Do not start with YOLO before OCR works.
Do not build without conflict tracking.
Do not hard-delete device records.
```

---

# 31. Final Recommended Implementation Order

Build exactly in this order:

```text
1. Docker + project setup
2. FastAPI + PostgreSQL + Alembic
3. Next.js frontend shell
4. Auth and roles
5. Device master inventory
6. Office inventory actions
7. Inventory event timeline
8. ServiceNow manual CSV import
9. ServiceNow email CSV import using Redis/RQ
10. Intune bearer-token sync
11. Matching engine
12. Conflict review
13. OCR webcam scanner
14. YOLO scanner upgrade
15. Reports and exports
16. Backup, logging, and hardening
```

---

# 32. Final System Summary

The final app should use:

```text
Next.js + TypeScript frontend
FastAPI backend
PostgreSQL database
Redis + RQ background jobs
Docker Compose on Windows with WSL 2
ServiceNow CSV email importer
Intune sync using pasted bearer token
OCR-first webcam scanner
YOLO-assisted scanner later
Full inventory event history
Conflict review system
Reports and CSV exports
```

The stable design separates:

```text
Master device identity
ServiceNow source data
Intune source data
Local office inventory state
Event history
OCR scan suggestions
Conflicts
Reports
```

This separation prevents future redesign and keeps the implementation maintainable.

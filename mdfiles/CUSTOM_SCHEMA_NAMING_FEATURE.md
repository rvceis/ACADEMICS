# Custom Schema Naming Feature - Implementation Complete ✅

## Overview
Users can now provide optional custom schema names when uploading files. This feature allows for better organization and labeling of schemas with user-defined names instead of relying solely on auto-generated names.

## What Changed

### Backend Changes (`flask_backend/app/routes/uploads.py`)

#### 1. **Custom Name Extraction** (Line ~925)
```python
schema_name = data.get('schema_name')  # Optional custom schema name from user
```
The backend now extracts the optional `schema_name` parameter from the import request.

#### 2. **Auto-detection with Custom Naming** (Lines ~940-956)
When a schema is auto-detected (exact field match), if a custom name is provided:
- The existing schema's name is updated to the custom name
- This allows users to rename existing schemas during import
```python
if schema_name and schema_name.strip():
    old_name = schema.name
    schema.name = schema_name.strip()
    db.session.commit()
    print(f"✓ AUTO-REUSED EXISTING SCHEMA (EXACT MATCH): {old_name} → {schema.name}")
```

#### 3. **Schema Reuse with Custom Naming** (Lines ~962-975)
When reusing an existing schema with the 'reuse' action:
- If a custom name is provided, the schema name is updated
- Changes are committed to the database
```python
if schema_name and schema_name.strip():
    old_name = schema.name
    schema.name = schema_name.strip()
    print(f"✓ REUSING EXISTING SCHEMA: {old_name} → {schema.name}")
    db.session.commit()
```

#### 4. **New Schema Creation with Custom Naming** (Lines ~1135-1165)
When creating a new schema:
- Custom name takes priority (if provided)
- Falls back to record name or auto-generated name
- Prevents overwriting the custom name variable
```python
if schema_name and schema_name.strip():
    # Custom name provided by user
    auto_generated_name = schema_name.strip()
    print(f"✓ Using custom schema name: {auto_generated_name}")
elif record_name and record_name.strip():
    # Use record name as base
    ...
else:
    # Auto-generate from data
    ...

schema = SchemaModel(
    name=auto_generated_name,  # Now includes custom name if provided
    ...
)
```

### Frontend Changes (`Frontend/src/components/FileImportDialog.tsx`)

#### 1. **Schema Name State Management**
Added state variable for tracking user input:
```typescript
const [schemaName, setSchemaName] = useState('');
```

#### 2. **Input Field**
Added optional text field in the import dialog:
```typescript
<TextField
    size="small"
    label="Schema Name (optional)"
    value={schemaName}
    onChange={(e) => setSchemaName(e.target.value)}
    fullWidth
    helperText="Custom name for the schema (if creating new)"
/>
```

#### 3. **Import Payload**
Updated the payload sent to backend:
```typescript
const importPayload = {
    // ... other fields ...
    schema_name: schemaName || undefined  // Only included if user provided
}
```

## Usage Flow

### Step-by-step User Workflow

1. **Upload File**
   - User selects a file (CSV, JSON, or any format)
   - File is uploaded via `/uploads/import-file`

2. **Schema Preview**
   - Backend analyzes file and returns field suggestions
   - Frontend displays possible schema matches
   - User optionally enters custom schema name
   - User selects action: "Create New", "Reuse", "Add Fields", etc.

3. **Confirm Import with Custom Name**
   - User clicks "Confirm Import"
   - Frontend sends `schema_name` in request body
   - Backend receives custom name parameter

4. **Backend Processing**
   ```
   If auto-detected exact match:
     → Update schema name to custom name
   
   Else if action is 'reuse':
     → Update existing schema name to custom name
   
   Else if action is 'create_new' or fallback:
     → Use custom name for new schema
   
   Else (no custom name):
     → Use auto-generated or record name
   ```

5. **Result**
   - Schema is created/updated with custom name
   - Frontend receives updated schema info
   - Analytics view shows the custom schema name

## Examples

### Example 1: Create New Schema with Custom Name
```
File: employees.csv (contains: id, name, department, salary)

User Flow:
1. Upload employees.csv
2. Suggested action: "Create New Schema"
3. User enters "Employee Records" as schema name
4. Confirm import
5. Result: Schema created with name "Employee Records"
```

### Example 2: Reuse Existing Schema with Name Update
```
File: more_employees.csv (same fields as existing schema)

User Flow:
1. Upload more_employees.csv
2. Suggested action: "Reuse Existing Schema"
3. User optionally enters "Updated Employee Records" as schema name
4. Confirm import
5. Result: Existing schema renamed to "Updated Employee Records"
```

### Example 3: Auto-detected with Custom Name
```
File: customers.csv (exact fields match existing schema)

User Flow:
1. Upload customers.csv
2. Backend auto-detects exact match
3. User can optionally enter custom name "Customer Profiles"
4. Confirm import
5. Result: Existing schema renamed to "Customer Profiles"
```

## Technical Details

### Schema Name Priority Order
1. **Custom name provided by user** (highest priority)
   - Must be non-empty and non-whitespace
   - Is trimmed of leading/trailing whitespace

2. **Record name** (if no custom name)
   - From `record_name` parameter
   - Used as base for generated schema name

3. **First record field value** (if no custom name)
   - Looks for 'name', 'title', or 'product_name' field
   - Uses first 30 characters, cleaned of special chars

4. **Timestamp-based auto-generated** (fallback)
   - Format: `Dataset_YYYYMMDD_HHMMSS`

### Database Changes
- No schema table changes required
- Uses existing `SchemaModel.name` field
- Existing schema versioning still works
- Change tracking via `ChangeLog` table (if enabled)

### API Changes

**POST `/uploads/import-file-confirm`**
- New optional parameter: `schema_name`
- Type: `string`
- Example payload:
```json
{
  "records_data": [...],
  "suggested_fields": [...],
  "record_name": "My Data",
  "tag": "production",
  "schema_choice": {
    "action": "create_new"
  },
  "schema_name": "Custom Schema Name"
}
```

## Validation & Error Handling

### Input Validation
- `schema_name` parameter is optional
- If provided, must be a string
- Empty or whitespace-only names are ignored
- Names are trimmed of leading/trailing whitespace

### Error Cases
- Invalid JSON in request: Returns 400 error
- Schema not found: Returns 404 error
- Database commit failure: Returns 500 error with message

### Logging
Backend prints debug information:
```
✓ Using custom schema name: My Schema Name
✓ AUTO-REUSED EXISTING SCHEMA (EXACT MATCH): Old Name → New Name
✓ REUSING EXISTING SCHEMA: Old Name → New Name
```

## Testing

### Unit Tests Included
1. **test_naming_logic.py** - Tests naming priority logic
   - Custom name overrides auto-generated ✅
   - Empty names fall back to auto-generated ✅
   - Whitespace-only names fall back ✅
   - Names are properly trimmed ✅
   - None values handled correctly ✅

### Manual Testing
1. Upload CSV with custom schema name → Schema created with custom name
2. Upload file matching existing schema with custom name → Schema renamed
3. Upload file without custom name → Schema uses auto-generated name
4. Verify in Analytics view that custom names persist

## Backward Compatibility

✅ **Fully backward compatible**
- `schema_name` parameter is optional
- If not provided, behavior is identical to before
- Existing code paths unchanged
- No breaking changes to API

## Future Enhancements

Possible improvements:
1. Schema name validation (length limits, forbidden chars)
2. Unique name enforcement (prevent duplicate schema names)
3. Schema name templates/patterns
4. Bulk rename operations
5. Schema name history/audit trail

## Summary

✅ **Feature Complete**
- Backend: Custom schema naming implemented
- Frontend: Input field added for user input
- API: Supports optional schema_name parameter
- Logic: Priority order properly enforced
- Testing: Logic tests passing
- Documentation: Complete

**Status**: Ready for integration testing and user acceptance testing.

# Custom Schema Naming - Quick Reference Guide

## For Developers

### Adding to Your Project

**No additional dependencies required.** Uses existing Flask, SQLAlchemy, and React.

### Code Locations

#### Backend Integration
- **File**: `flask_backend/app/routes/uploads.py`
- **Parameter Extraction**: Line 925
- **Auto-detect Logic**: Lines 947-959
- **Reuse Logic**: Lines 970-985
- **New Schema Logic**: Lines 1138-1165

#### Frontend Integration
- **File**: `Frontend/src/components/FileImportDialog.tsx`
- **State**: Line 46
- **Input Field**: Lines 310-317
- **API Call**: Line 169
- **Cleanup**: Line 228

### Key Code Snippets

#### Extract Parameter (Backend)
```python
schema_name = data.get('schema_name')  # From request body
```

#### Apply to New Schema
```python
if schema_name and schema_name.strip():
    auto_generated_name = schema_name.strip()
else:
    auto_generated_name = "Auto Generated Name"

schema = SchemaModel(name=auto_generated_name, ...)
```

#### Apply to Existing Schema
```python
if schema_name and schema_name.strip():
    schema.name = schema_name.strip()
    db.session.commit()
```

#### Send from Frontend
```typescript
const importPayload = {
    records_data,
    schema_name: schemaName || undefined,  // Only if provided
    // ... other fields
}
```

### Testing Locally

#### Logic Tests
```bash
python3 test_naming_logic.py
```

#### Integration Tests (requires running server)
```bash
# Terminal 1: Start Flask
python3 flask_backend/app.py

# Terminal 2: Run tests
python3 test_schema_naming.py
```

### Debugging

#### Enable Debug Logging
Backend prints custom naming operations:
```
✓ Using custom schema name: My Schema
✓ AUTO-REUSED EXISTING SCHEMA: Old Name → New Name (ID: 42)
✓ REUSING EXISTING SCHEMA: Old Name → New Name (ID: 42)
```

Check Flask logs:
```bash
# If running in terminal
tail -f /tmp/flask.log

# If running in background
ps aux | grep flask_backend
kill <PID>  # to stop
```

### API Contract

**Parameter**: `schema_name`
- Type: `string` or `null`
- Optional: Yes
- Max Length: No limit (but recommend < 255 chars)
- Pattern: Any UTF-8 string (no validation)
- Trimmed: Yes (leading/trailing whitespace removed)

**Behavior**:
- If provided and non-empty: Use as schema name
- If empty or whitespace: Fall back to auto-generated
- If null/undefined: Fall back to auto-generated

### Database Considerations

- **No Migration Needed**: Uses existing `SchemaModel.name` field
- **No Index Changes**: Existing indexes still valid
- **Backward Compatible**: Old schemas keep their names
- **Soft Deletes**: Still work correctly
- **Change Log**: Optional, not triggered by this feature

### Performance Impact

- **Minimal**: Single name assignment per import
- **No Additional Queries**: Uses existing schema query
- **One Extra Commit**: When updating existing schema name
- **I/O**: Negligible

### Known Limitations

1. **No Uniqueness Constraint**: Multiple schemas can have same name
2. **No Name Validation**: Special characters allowed
3. **No Length Limit**: Should validate in UI
4. **Silent Truncation**: If name too long, may be truncated by DB

### Future Enhancements

Could add:
```python
# Schema name uniqueness
if SchemaModel.query.filter_by(name=schema_name).first():
    return jsonify({'error': 'Schema name already exists'}), 409

# Length validation
if len(schema_name) > 255:
    return jsonify({'error': 'Schema name too long'}), 400

# Reserved names
RESERVED_NAMES = {'System', 'Temp', 'Archive'}
if schema_name in RESERVED_NAMES:
    return jsonify({'error': 'Reserved schema name'}), 400

# Special character validation
if not re.match(r'^[a-zA-Z0-9_\-\s]+$', schema_name):
    return jsonify({'error': 'Invalid characters in name'}), 400
```

### Troubleshooting

#### Issue: Custom name not being applied
**Solution**: Check that `schema_name` is included in request body
```javascript
console.log('Import payload:', importPayload);
```

#### Issue: 500 error on import
**Solution**: Check Flask logs for stack trace
```
Look for: 
- Database commit failure
- Invalid schema ID
- NULL constraint violation
```

#### Issue: Name not persisting
**Solution**: Ensure `db.session.commit()` is called
```python
schema.name = new_name
db.session.commit()  # MUST be called!
```

#### Issue: Frontend input not sending
**Solution**: Check state is being updated
```typescript
console.log('schemaName state:', schemaName);
```

### Best Practices

1. **Always trim input**: `value.strip()`
2. **Check for empty**: `if schema_name and schema_name.strip():`
3. **Commit after update**: `db.session.commit()`
4. **Log important actions**: `print(f"✓ Updated schema: {schema.name}")`
5. **Handle None gracefully**: Use `value or fallback`

### Version Compatibility

- **Python**: 3.6+ (uses f-strings)
- **Flask**: 1.0+
- **SQLAlchemy**: 1.3+
- **React**: 16.8+ (uses hooks)
- **TypeScript**: 3.5+

### Related Features

- **Schema Versioning**: Works with existing versioning
- **Change Log**: Automatic logging available
- **Bulk Operations**: Can be added later
- **Search/Filter**: Can search schemas by name
- **Export/Import**: Schema names included in exports

### Security Considerations

✅ **SQL Injection**: Protected by SQLAlchemy ORM
✅ **XSS**: Input stored as data, not rendered as HTML
✅ **Authorization**: Uses existing JWT auth
⚠️ **No name validation**: Could add validation if needed

---

**Last Updated**: February 2024
**Stability**: Production Ready

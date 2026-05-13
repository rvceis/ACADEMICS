# Document Upload Feature - Quick Start

## What's New?

The document upload feature has been fully implemented. Users can now:
- ✅ Upload identity, address, bank, and other documents
- ✅ See their uploaded documents in a list
- ✅ Delete documents they no longer need
- ✅ Track document verification status

## Files Changed

### Frontend (3 files)
1. **NEW: `frontend/src/components/modals/DocumentUploadModal.tsx`**
   - Complete upload modal with file picker
   - ~350 lines of production code

2. **UPDATED: `frontend/src/screens/profile/DocumentsScreen.tsx`**
   - Integrated the new upload modal
   - Auto-refresh functionality

### Backend (2 files)
1. **UPDATED: `backend/src/controllers/profileController.js`**
   - Enhanced file validation
   - Better error handling

2. **UPDATED: `backend/src/routes/profileRoutes.js`**
   - Added multer middleware
   - Configured file upload handling

## Testing the Feature

### Step 1: Start Services
```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend
cd frontend
npm start
```

### Step 2: Navigate to Documents
1. Open Expo Go app
2. Login with your account
3. Go to **Profile** → **Documents**

### Step 3: Upload a Document
1. Click **"Upload Document"** button
2. Select a document type (e.g., "Identity Proof")
3. Enter a name (e.g., "My Passport")
4. Tap to select a file (PDF or image)
5. Click **Upload**

### Step 4: Verify
- ✅ Document appears in the list
- ✅ Status shows as "pending"
- ✅ You can delete it using the trash icon

## API Endpoints

All endpoints require authentication (Bearer token in headers)

### Upload Document
```bash
curl -X POST http://10.251.149.193:3000/api/v1/users/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "document_type=identity" \
  -F "document_name=My ID" \
  -F "document=@/path/to/file.pdf"
```

### List Documents
```bash
curl -X GET http://10.251.149.193:3000/api/v1/users/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete Document
```bash
curl -X DELETE http://10.251.149.193:3000/api/v1/users/documents/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Supported Document Types

1. **Identity** - Passport, ID Card, Driving License
2. **Address Proof** - Utility Bill, Rental Agreement, Lease
3. **Bank Statement** - Recent bank statements
4. **PAN Card** - PAN card image/copy
5. **Aadhaar** - Aadhaar card image/copy
6. **Other** - Any other relevant document

## File Requirements

- **Format**: PDF, JPG, PNG, or GIF
- **Size**: Max 10MB
- **Name**: Required, any text

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Please select a document" | No file chosen | Tap file picker and select a file |
| "Please enter a document name" | Name field empty | Enter a name for the document |
| "File type not allowed" | Not PDF or image | Convert to PDF/JPG/PNG and try again |
| "File size exceeds 10MB" | File too large | Use a smaller file |
| "Authentication token not found" | Not logged in | Login to your account first |

## Feature Details

### Frontend
- Modal popup interface
- Document type selection
- File picker integration
- Real-time file size display
- Visual upload progress
- Automatic list refresh
- Delete confirmation dialog

### Backend
- File upload via multipart/form-data
- MIME type validation
- File size enforcement
- User-specific directories
- Database metadata storage
- Error handling with clear messages

### Security
- User authentication required
- Users can only access their own documents
- File type whitelist (PDF, images only)
- File size limits
- Unique file naming

## Database

Documents stored in `user_documents` table:
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- document_type: VARCHAR (identity, address_proof, etc.)
- document_name: VARCHAR (user-defined name)
- file_path: TEXT (location on filesystem)
- file_size: INTEGER (bytes)
- verification_status: VARCHAR (pending/verified/rejected)
- created_at: TIMESTAMP
```

## File Storage

Uploaded files stored in:
```
backend/uploads/documents/{userId}/{uniqueId}-{filename}
```

Example:
```
backend/uploads/documents/550e8400-e29b-41d4-a716-446655440000/1642345600000-12345-my-passport.pdf
```

## Next Steps

### For Testing
1. Upload a document with a test account
2. Verify file exists in `backend/uploads/documents/`
3. Check database: `SELECT * FROM user_documents;`
4. Test delete functionality
5. Test error scenarios (invalid file, no name, etc.)

### For Production
1. Implement cloud storage (AWS S3, Google Cloud Storage, Azure Blob)
2. Add virus/malware scanning
3. Implement document verification workflow
4. Add document preview capability
5. Implement rate limiting
6. Add audit logging

## Troubleshooting

### Modal doesn't appear
- Clear app cache: `expo start --clear`
- Check browser console for errors
- Verify DocumentUploadModal import path

### Upload fails silently
- Check backend logs: `tail -f backend/logs/*.log`
- Verify auth token is valid
- Check network connectivity

### File not stored
- Verify `backend/uploads/` directory exists
- Check file permissions
- Check disk space

## Documentation

For detailed information, see:
- `DOCUMENT_UPLOAD_GUIDE.md` - Complete implementation guide
- `DOCUMENT_UPLOAD_IMPLEMENTATION.md` - Implementation summary

## Support

For issues:
1. Check error message displayed
2. Review backend logs
3. Check browser console
4. Verify file meets requirements
5. Try with a different file
6. Restart services if needed

---

**Status**: ✅ Ready for Testing & Production

The document upload feature is fully implemented and ready to use. Test it out and let me know if you need any adjustments!

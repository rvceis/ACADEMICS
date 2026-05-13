# Document Upload Feature - Implementation Guide

## Overview
The document upload feature has been fully implemented for both frontend and backend, allowing users to upload KYC documents securely.

## Components Implemented

### Frontend

#### 1. **DocumentUploadModal** (`frontend/src/components/modals/DocumentUploadModal.tsx`)
A comprehensive modal component for uploading documents with the following features:
- **Document Type Selection**: Choose from Identity, Address Proof, Bank Statement, PAN Card, Aadhaar, or Other
- **Document Name Input**: Custom naming for uploaded documents
- **File Picker Integration**: Uses Expo Document Picker to browse and select files
- **File Validation**: 
  - Supports PDF, JPG, PNG, and GIF formats
  - Maximum file size: 10MB
  - Displays file size in human-readable format
- **Upload Progress**: Shows loading indicator during upload
- **Error Handling**: Comprehensive error messages for validation failures

#### 2. **DocumentsScreen** (`frontend/src/screens/profile/DocumentsScreen.tsx`)
Updated to include:
- **Modal Integration**: Opens DocumentUploadModal on "Upload Document" button press
- **Document List Display**: Shows all uploaded documents with status badges
- **Auto-refresh**: Uses `useFocusEffect` to reload documents when returning to the screen
- **Delete Functionality**: Allows users to delete previously uploaded documents
- **Status Indicators**: Color-coded status (Verified, Pending, Rejected)

### Backend

#### 1. **ProfileController** (`backend/src/controllers/profileController.js`)
Enhanced `uploadDocument` method with:
- **File Validation**: 
  - Checks for file presence
  - Validates document type against allowed types
  - Validates file size (max 10MB)
  - Validates MIME types (PDF, JPEG, PNG, GIF)
- **Error Handling**: Comprehensive error messages for each validation failure
- **File Storage**: Handles file storage via multer middleware

#### 2. **Profile Routes** (`backend/src/routes/profileRoutes.js`)
Added multer middleware configuration:
- **Upload Directory**: `uploads/documents/{userId}/{randomId}-filename`
- **File Size Limit**: 10MB maximum
- **MIME Type Filtering**: Only allows PDF and image files
- **Dynamic Directory Creation**: Automatically creates user-specific upload directories
- **Route**: `POST /users/documents` - Requires authentication and file upload

#### 3. **ProfileService** (`backend/src/services/ProfileService.js`)
Already implemented with three key methods:
- `getUserDocuments(userId)`: Retrieves all documents for a user
- `addUserDocument(userId, documentData)`: Stores document metadata in database
- `deleteUserDocument(userId, documentId)`: Deletes a document record

## Database Schema

### user_documents Table
```sql
CREATE TABLE user_documents (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  document_type VARCHAR(50) -- 'identity', 'address_proof', 'bank_statement', 'pan_card', 'aadhaar', 'other'
  document_name VARCHAR(255),
  file_path TEXT,
  file_size INTEGER,
  mime_type VARCHAR(100),
  verification_status VARCHAR(20) DEFAULT 'pending',
  rejection_reason TEXT,
  verified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
)
```

## API Endpoints

### Get User Documents
**GET** `/api/v1/users/documents`
- **Authentication**: Required (Bearer token)
- **Response**: Array of document objects

### Upload Document
**POST** `/api/v1/users/documents`
- **Authentication**: Required (Bearer token)
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `document_type` (string, required): Type of document
  - `document_name` (string, required): Name for the document
  - `document` (file, required): The actual file to upload
- **Validation**:
  - File size max: 10MB
  - Accepted formats: PDF, JPG, PNG, GIF
  - document_name must not be empty
  - document_type must be valid

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "id": "uuid",
    "document_type": "identity",
    "document_name": "My ID Card",
    "file_size": 1024,
    "verification_status": "pending",
    "created_at": "2026-01-16T06:00:00Z"
  }
}
```

### Delete Document
**DELETE** `/api/v1/users/documents/{id}`
- **Authentication**: Required (Bearer token)
- **Parameters**: Document ID in URL path
- **Response**: Success message

## File Structure

```
Solar_Sharing/
├── frontend/
│   └── src/
│       ├── api/
│       │   ├── config.ts (API configuration)
│       │   ├── client.ts (Axios client with auth)
│       │   └── profileService.ts (API calls)
│       ├── components/
│       │   └── modals/
│       │       └── DocumentUploadModal.tsx (NEW)
│       └── screens/
│           └── profile/
│               └── DocumentsScreen.tsx (UPDATED)
└── backend/
    ├── src/
    │   ├── controllers/
    │   │   └── profileController.js (UPDATED)
    │   ├── routes/
    │   │   └── profileRoutes.js (UPDATED)
    │   ├── services/
    │   │   └── ProfileService.js (EXISTING)
    │   └── database/
    │       └── schema.js (user_documents table)
    └── uploads/
        └── documents/ (File storage location)
```

## Testing the Feature

### 1. Frontend Testing
```bash
# Make sure the frontend is running
cd frontend
npm start

# In Expo Go app, navigate to:
# Profile → Documents → Upload Document
```

### 2. Test Scenarios

#### Scenario 1: Successful Upload
1. Click "Upload Document" button
2. Select "Identity Proof" document type
3. Enter document name: "My Passport"
4. Tap file picker and select a PDF or image
5. Click "Upload"
6. Document should appear in the list with "pending" status

#### Scenario 2: Validation Error - No File
1. Click "Upload Document"
2. Enter document name only
3. Try to click "Upload" (should be disabled)

#### Scenario 3: Validation Error - Invalid File
1. Click "Upload Document"
2. Select a document type
3. Enter document name
4. Try to select a Word document or other non-image file
5. Should see error: "File type not allowed"

#### Scenario 4: Delete Document
1. Go to Documents screen
2. Find an uploaded document
3. Click trash icon
4. Confirm deletion
5. Document should be removed from list

### 3. Backend Testing with cURL

```bash
# Upload a document (multipart/form-data)
curl -X POST http://localhost:3000/api/v1/users/documents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "document_type=identity" \
  -F "document_name=My ID" \
  -F "document=@/path/to/file.pdf"

# Get all documents
curl -X GET http://localhost:3000/api/v1/users/documents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Delete a document
curl -X DELETE http://localhost:3000/api/v1/users/documents/{document_id} \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Handling

### Frontend Error Messages
- "Please select a document" - No file selected
- "Please enter a document name" - Document name is empty
- "Authentication token not found" - User not logged in
- "File type not allowed" - Invalid file format
- "File size exceeds 10MB limit" - File is too large

### Backend Error Responses

```json
{
  "success": false,
  "error": "document_type is required"
}
```

**Common Error Codes:**
- 400: Bad Request (validation error)
- 401: Unauthorized (missing auth token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (document not found)
- 413: Payload Too Large (file exceeds limit)
- 500: Internal Server Error

## Features

✅ **File Upload**
- Multiple document types supported
- File format validation (PDF, JPG, PNG, GIF)
- File size validation (max 10MB)
- Progress indication during upload

✅ **Document Management**
- List all uploaded documents
- View document status (pending/verified/rejected)
- Delete documents
- Auto-refresh on screen focus

✅ **Security**
- Authentication required for all endpoints
- User can only access their own documents
- File stored in user-specific directories
- MIME type validation on backend

✅ **User Experience**
- Intuitive modal interface
- Clear error messages
- Visual feedback during upload
- Auto-filled document names
- Color-coded status indicators

## Future Enhancements

1. **Document Verification** - Integrate AI/ML for document verification
2. **Image Cropping** - Allow users to crop/adjust images before upload
3. **Retry Logic** - Automatic retry on upload failures
4. **Progress Tracking** - Show upload progress percentage
5. **Document Preview** - View uploaded documents
6. **Document Templates** - Guided upload with document-specific instructions
7. **Bulk Upload** - Upload multiple documents at once
8. **Expiry Management** - Track document expiry dates

## Configuration

### Environment Variables

**Backend (.env)**
```
# File Upload Settings (already configured)
NODE_ENV=development
PORT=3000

# Database (already configured)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=solar_platform
```

**Frontend (api/config.ts)**
```typescript
const LOCAL_IP = '10.251.149.193'; // Update with your machine IP
const API_BASE_URL = `http://${LOCAL_IP}:3000/api/v1`;
```

## Performance Considerations

- **File Size Limit**: 10MB (configurable in multer)
- **Upload Timeout**: 30 seconds (configurable in apiClient)
- **Storage Location**: Local filesystem under `uploads/documents/{userId}/`
- **Database Queries**: Indexed on user_id and document_type for fast retrieval

## Security Considerations

✅ **Implemented**:
- User authentication required
- File type validation (MIME type check)
- File size limits
- User isolation (users can only access their own documents)
- Unique file naming with timestamps

🔄 **Recommended for Production**:
- Use cloud storage (S3, GCS, Azure Blob)
- Implement virus scanning on uploaded files
- Add rate limiting to prevent abuse
- Encrypt files at rest
- Implement document retention policies
- Add audit logging for document access

## Troubleshooting

### Upload Fails with "Authentication token not found"
- Ensure user is logged in
- Check that AsyncStorage has the access token
- Verify token hasn't expired

### File Not Uploaded Despite Success Message
- Check `uploads/documents/` folder exists
- Verify permissions on uploads directory
- Check disk space availability

### "File type not allowed" Error
- Ensure file is PDF or image (JPG, PNG, GIF)
- Check file extension matches MIME type
- Retry with a different file

### Modal Doesn't Close After Upload
- Check for JavaScript console errors
- Verify network response is valid JSON
- Check backend logs for upload errors

## Dependencies

**Frontend**
- `expo-document-picker`: File selection
- `expo-file-system`: File system access
- `@react-native-async-storage/async-storage`: Token storage
- `react-native`: Core framework

**Backend**
- `multer`: File upload middleware
- `express`: Web framework
- `pg`: PostgreSQL database
- `pino`: Logging

## Support & Debugging

### Enable Debug Logging
```typescript
// In DocumentUploadModal.tsx
console.log('Upload response:', responseData);
console.log('File selected:', selectedFile);
```

### Check Backend Logs
```bash
# Watch backend logs
tail -f backend/logs/*.log

# Check upload directory
ls -lah backend/uploads/documents/
```

### Database Query for Documents
```sql
SELECT * FROM user_documents WHERE user_id = 'YOUR_USER_ID';
```

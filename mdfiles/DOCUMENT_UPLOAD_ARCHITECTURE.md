# Document Upload Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React Native)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  DocumentsScreen.tsx                                                 │
│  ├─ State: documents[], uploadModalVisible                          │
│  ├─ useEffect: loadDocuments()                                      │
│  ├─ useFocusEffect: reload on focus                                 │
│  ├─ Displays: Document list                                         │
│  └─ Actions: Upload, Delete                                         │
│       │                                                              │
│       ↓                                                              │
│  DocumentUploadModal.tsx (NEW)                                       │
│  ├─ State: selectedType, documentName, selectedFile, loading       │
│  ├─ Features:                                                        │
│  │  ├─ Document type picker (6 types)                              │
│  │  ├─ File picker (Expo DocumentPicker)                           │
│  │  ├─ File validation (format, size)                              │
│  │  ├─ FormData upload                                             │
│  │  └─ Error handling                                               │
│  └─ Upload: fetch() with Bearer token                              │
│       │                                                              │
│       ├─ AsyncStorage.getItem(ACCESS_TOKEN)                        │
│       └─ FormData: document_type, document_name, document file    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
              │                                    │
              │ HTTP Request                       │ HTTP Response
              ↓                                    ↑
┌─────────────────────────────────────────────────────────────────────┐
│                    NETWORK & API CLIENT                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  profileApi.ts                                                       │
│  ├─ getDocuments()     → GET /users/documents                       │
│  ├─ uploadDocument()   → POST /users/documents (metadata only)     │
│  └─ deleteDocument()   → DELETE /users/documents/{id}              │
│                                                                       │
│  apiClient.ts (Axios)                                               │
│  ├─ Interceptors: Add Bearer token                                  │
│  ├─ Base URL: http://10.251.149.193:3000/api/v1                    │
│  └─ Timeout: 30 seconds                                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
              │                                    │
              │ multipart/form-data               │ JSON response
              ↓                                    ↑
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Express.js)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  profileRoutes.js (UPDATED)                                         │
│  ├─ GET  /users/documents          ← authenticate middleware       │
│  ├─ POST /users/documents          ← authenticate + upload.single()│
│  └─ DELETE /users/documents/:id    ← authenticate middleware       │
│       │                                                              │
│       ├─ Multer Configuration:                                      │
│       │  ├─ Storage: disk storage in uploads/documents/{userId}/   │
│       │  ├─ File size: max 10MB                                    │
│       │  ├─ MIME types: PDF, JPEG, PNG, GIF only                  │
│       │  └─ Filename: {timestamp}-{randomId}-{original}           │
│       │                                                              │
│       ↓                                                              │
│  profileController.js (UPDATED)                                     │
│  ├─ getDocuments(req, res)                                         │
│  │  └─ Calls: ProfileService.getUserDocuments(userId)             │
│  │                                                                   │
│  ├─ uploadDocument(req, res) [ENHANCED]                            │
│  │  ├─ Validate: document_type, document_name, file              │
│  │  ├─ Check: File size, MIME type                                │
│  │  ├─ Error: Return 400 if invalid                               │
│  │  └─ Success: Call ProfileService.addUserDocument()            │
│  │                                                                   │
│  └─ deleteDocument(req, res)                                       │
│     └─ Calls: ProfileService.deleteUserDocument(userId, docId)    │
│       │                                                              │
│       ↓                                                              │
│  ProfileService.js (EXISTING)                                       │
│  ├─ getUserDocuments(userId)                                       │
│  │  └─ Query: SELECT * FROM user_documents WHERE user_id = $1     │
│  │                                                                   │
│  ├─ addUserDocument(userId, documentData)                          │
│  │  └─ Query: INSERT INTO user_documents (...)                    │
│  │                                                                   │
│  └─ deleteUserDocument(userId, documentId)                         │
│     └─ Query: DELETE FROM user_documents WHERE ...                │
│       │                                                              │
│       ↓                                                              │
│  PostgreSQL Database                                                │
│  └─ user_documents table                                            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
              │                                    │
              │ File storage                       │ Metadata storage
              ↓                                    ↑
┌─────────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  File System                          Database                       │
│  ├─ Directory:                        ├─ user_documents table:      │
│  │  backend/uploads/documents/        │  ├─ id (UUID)             │
│  │  ├─ {userId}/                      │  ├─ user_id (FK)          │
│  │  │  ├─ 1642345600000-12345-        │  ├─ document_type         │
│  │  │  │  my-passport.pdf             │  ├─ document_name         │
│  │  │  ├─ 1642345700000-67890-        │  ├─ file_path             │
│  │  │  │  my-address.jpg              │  ├─ file_size             │
│  │  │  └─ ...                          │  ├─ mime_type             │
│  │  └─ {userId}/                      │  ├─ verification_status   │
│  │     └─ ...                          │  └─ created_at            │
│  └─ Total: 1000s of user directories  └─ Indexed on: user_id      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Upload Flow
```
User Taps Upload
       │
       ↓
Modal Opens (DocumentUploadModal.tsx)
       │
       ├─ Select Type: identity/address/bank/pan/aadhaar/other
       ├─ Enter Name: "My Passport"
       └─ Pick File: Select PDF or image
       │
       ↓
User Clicks Upload Button
       │
       ├─ Validate: Type, Name, File (Frontend)
       ├─ Create FormData with file
       └─ Get Bearer Token from AsyncStorage
       │
       ↓
Send POST /api/v1/users/documents
       │
       ├─ Header: Authorization: Bearer TOKEN
       ├─ Header: Accept: application/json
       └─ Body: FormData (multipart/form-data)
       │
       ↓
Backend Receives Request
       │
       ├─ Authenticate: Check Bearer token
       ├─ Multer: Process file upload
       ├─ Validate:
       │  ├─ document_type ✓
       │  ├─ document_name ✓
       │  ├─ file.size <= 10MB ✓
       │  └─ file.mime in [pdf, jpeg, png, gif] ✓
       └─ Error? Return 400 with message
       │
       ├─ Store: File in uploads/documents/{userId}/
       ├─ Insert: Metadata in user_documents table
       └─ Return: 201 with document object
       │
       ↓
Frontend Receives Response
       │
       ├─ Success? Show alert
       ├─ Add to documents list
       ├─ Reset form
       └─ Close modal
       │
       ↓
DocumentsScreen Refreshes
       │
       └─ New document appears in list with "pending" status
```

### Delete Flow
```
User Taps Delete Icon
       │
       └─ Confirmation Alert
       │
       ├─ Cancel? → Do nothing
       └─ Delete? → Continue
       │
       ↓
Send DELETE /api/v1/users/documents/{docId}
       │
       ├─ Header: Authorization: Bearer TOKEN
       └─ Body: Empty
       │
       ↓
Backend Receives Request
       │
       ├─ Authenticate: Check Bearer token
       ├─ Verify: User owns document
       ├─ Delete: Record from user_documents table
       ├─ Optional: Delete file from disk
       └─ Return: 200 with success message
       │
       ↓
Frontend Receives Response
       │
       ├─ Success? Show alert
       ├─ Remove from list
       └─ Update UI
```

## Component Hierarchy

```
App
└─ ProfileNavigator
   └─ ProfileStackNavigator
      └─ DocumentsScreen (screens/profile/DocumentsScreen.tsx)
         ├─ ScrollView
         │  ├─ Header
         │  ├─ DocumentList
         │  │  └─ DocumentCard (repeated for each document)
         │  └─ UploadButton
         │
         └─ DocumentUploadModal (components/modals/DocumentUploadModal.tsx)
            ├─ Header
            ├─ ScrollView
            │  ├─ DocumentTypeSelector
            │  ├─ DocumentNameInput
            │  ├─ FilePicker
            │  └─ FileDetails
            └─ Footer (Cancel / Upload buttons)
```

## State Management

### DocumentsScreen State
```typescript
const [loading, setLoading] = useState(true)
const [documents, setDocuments] = useState<Document[]>([])
const [uploadModalVisible, setUploadModalVisible] = useState(false)
```

### DocumentUploadModal State
```typescript
const [selectedType, setSelectedType] = useState<DocumentType>('identity')
const [documentName, setDocumentName] = useState('')
const [selectedFile, setSelectedFile] = useState<any>(null)
const [loading, setLoading] = useState(false)
```

## API Request/Response Examples

### Upload Request
```http
POST /api/v1/users/documents HTTP/1.1
Host: 10.251.149.193:3000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
Accept: application/json

------WebKitFormBoundary...
Content-Disposition: form-data; name="document_type"

identity
------WebKitFormBoundary...
Content-Disposition: form-data; name="document_name"

My Passport
------WebKitFormBoundary...
Content-Disposition: form-data; name="document"; filename="passport.pdf"
Content-Type: application/pdf

[Binary PDF data...]
------WebKitFormBoundary...--
```

### Upload Response
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "document_type": "identity",
    "document_name": "My Passport",
    "file_size": 2048000,
    "verification_status": "pending",
    "created_at": "2026-01-16T06:00:00Z"
  }
}
```

## File Storage Structure

```
backend/
└─ uploads/
   └─ documents/
      ├─ 550e8400-e29b-41d4-a716-446655440000/ (user1)
      │  ├─ 1642345600000-12345-my-passport.pdf
      │  ├─ 1642345700000-67890-my-address.jpg
      │  └─ 1642345800000-11111-pan-card.png
      │
      ├─ 660e8400-e29b-41d4-a716-446655440001/ (user2)
      │  ├─ 1642346600000-22222-utility-bill.pdf
      │  └─ 1642346700000-33333-aadhaar.jpg
      │
      └─ ...
```

## Security Flow

```
User Login
    ↓
JWT Token Generated
    ↓
Token Stored in AsyncStorage
    ↓
Upload Request Made
    ├─ Get token from AsyncStorage
    ├─ Add to Authorization header
    └─ Send with FormData
    ↓
Backend Receives Request
    ├─ Extract Bearer token
    ├─ Verify signature & expiry
    ├─ Get userId from token
    └─ Use userId to:
       ├─ Create user-specific directory
       ├─ Set user_id in database record
       └─ Prevent cross-user access
```

## Error Handling Flow

```
User Uploads File
    │
    ├─ Frontend Validation
    │  ├─ No file? → "Please select a document"
    │  ├─ No name? → "Please enter a document name"
    │  └─ Invalid type? → "Invalid document type"
    │
    └─ Backend Validation
       ├─ Auth missing? → 401 Unauthorized
       ├─ Invalid type? → 400 Bad Request
       ├─ File missing? → 400 Bad Request
       ├─ Size > 10MB? → 413 Payload Too Large
       ├─ Invalid MIME? → 400 Bad Request
       └─ DB error? → 500 Internal Server Error
```

---

This architecture provides:
- ✅ Secure file upload with authentication
- ✅ Proper separation of concerns
- ✅ Scalable file storage structure
- ✅ Comprehensive validation
- ✅ Clear error handling
- ✅ User isolation

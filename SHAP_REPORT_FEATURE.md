# SHAP Report Feature Implementation

## Overview
Added comprehensive SHAP (SHapley Additive exPlanations) report viewing and PDF download functionality for both users and admins.

## Features Implemented

### 1. User Dashboard
- **Location**: `frontend/src/pages/Dashboard.tsx`
- **Feature**: "SHAP Report" button next to each application with a credit score
- **Functionality**: 
  - Click to view interactive SHAP report in a modal
  - Print report directly from browser
  - Download report as PDF

### 2. Admin Panel
- **Location**: `frontend/src/pages/AdminApplications.tsx`
- **Feature**: "SHAP" button in the actions column for each application
- **Functionality**:
  - Same viewing, printing, and PDF download capabilities as users
  - Admin-specific API endpoint for secure access

### 3. SHAP Report Component
- **Location**: `frontend/src/components/ShapReport.tsx`
- **Features**:
  - **Credit Score Summary**: Displays score, risk category, and default probability
  - **SHAP Explanation**: Clear explanation of what SHAP values mean
  - **Positive Factors**: Green-highlighted features that improved the score
  - **Negative Factors**: Red-highlighted features that reduced the score
  - **Recommendations**: Actionable advice to improve credit score
  - **Print Button**: Opens browser print dialog
  - **Download PDF Button**: Generates and downloads professional PDF report

### 4. PDF Generation Service
- **Location**: `backend/app/services/pdf_service.py`
- **Technology**: ReportLab library
- **Features**:
  - Professional PDF layout with branding
  - Color-coded positive/negative factors
  - Tables with proper formatting
  - Recommendations section
  - Footer with model version and copyright

### 5. API Endpoints

#### User Endpoint
```
GET /api/v1/applications/{application_id}/shap-report/pdf
```
- Requires user authentication (JWT token)
- User can only download their own reports

#### Admin Endpoint
```
GET /api/v1/admin/applications/{application_id}/shap-report/pdf
```
- Requires admin authentication
- Admin can download any application's report

## Technical Details

### Frontend Components
1. **ShapReport.tsx**: Reusable modal component for displaying SHAP data
2. **Print Styles**: Custom CSS for print-friendly output
3. **PDF Download**: Fetch API to download PDF from backend

### Backend Services
1. **pdf_service.py**: Generates PDF using ReportLab
2. **applications.py**: User endpoint for PDF download
3. **admin_applications.py**: Admin endpoint for PDF download

### Dependencies Added
- **Backend**: `reportlab==4.0.7` (already installed)
- **Frontend**: No new dependencies (uses native browser APIs)

## How It Works

### User Flow
1. User submits credit application
2. AI model generates credit score with SHAP explanations
3. User sees "SHAP Report" button on dashboard
4. Click button → Modal opens with detailed SHAP analysis
5. User can:
   - View interactive report
   - Click "Print" → Browser print dialog opens
   - Click "Download PDF" → Professional PDF downloads

### Admin Flow
1. Admin views applications list
2. Each application with a score shows "SHAP" button
3. Click button → Same modal as users
4. Admin can print or download PDF for any application

### PDF Generation
1. Frontend sends request to backend with auth token
2. Backend validates authentication and authorization
3. Backend fetches application and credit score data
4. ReportLab generates professional PDF with:
   - Header with application details
   - Credit score summary table
   - SHAP explanation text
   - Positive factors table (green)
   - Negative factors table (red)
   - Recommendations list
   - Footer with model version
5. PDF returned as binary response
6. Frontend triggers download

## Feature Highlights

### Explainability
- Clear explanation of SHAP values for non-technical users
- Visual separation of positive vs negative factors
- Impact magnitude shown for each feature

### Actionable Insights
- Top 3 recommendations based on negative factors
- Specific advice for each feature (e.g., "Set up automatic payments")

### Professional Output
- Print-friendly layout
- High-quality PDF with proper formatting
- Color-coded for easy understanding
- Branded with Saral Credit logo and copyright

### Security
- User can only access their own reports
- Admin has access to all reports
- JWT token authentication required
- Authorization checks on backend

## Files Modified/Created

### Created
- `frontend/src/components/ShapReport.tsx`
- `frontend/src/styles/print.css`
- `backend/app/services/pdf_service.py`
- `SHAP_REPORT_FEATURE.md`

### Modified
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/AdminApplications.tsx`
- `frontend/index.html`
- `backend/app/api/applications.py`
- `backend/app/api/admin_applications.py`
- `backend/requirements.txt`

## Testing

### To Test User Flow
1. Register/login as a user
2. Submit a credit application
3. Wait for credit score generation
4. Go to dashboard
5. Click "SHAP Report" button
6. Verify modal opens with SHAP data
7. Click "Print" and verify print preview
8. Click "Download PDF" and verify PDF downloads

### To Test Admin Flow
1. Login as admin (see admin credentials in backend/scripts/create_admin.py)
2. Go to Applications page
3. Find application with credit score
4. Click "SHAP" button
5. Verify modal opens
6. Test print and PDF download

## Future Enhancements
- Add SHAP waterfall chart visualization
- Email SHAP report to user
- Compare SHAP reports across multiple applications
- Add SHAP summary statistics to admin dashboard
- Export SHAP data as CSV for analysis

## Notes
- PDF generation requires reportlab library (already installed)
- Print functionality uses browser's native print dialog
- SHAP data is stored in database when credit score is generated
- No additional API calls needed for viewing report (data already loaded)

# 広聴AI管理画面 (Kouchou-AI Admin Interface) - Comprehensive Test Plan

## Application Overview

The 広聴AI管理画面 (Kouchou-AI Admin Interface) is a Next.js-based administrative interface for creating and managing broadlistening reports. The application is accessible at http://localhost:4000 and provides comprehensive functionality for:

- **Report Management**: View, create, edit, and delete reports with visibility controls (public, unlisted, private)
- **Report Creation**: Multi-step wizard for creating new reports with CSV or Google Spreadsheet input
- **AI Configuration**: Configure AI providers (OpenAI, Azure OpenAI, Local LLM), models, and processing parameters
- **Data Input**: Support for CSV file upload and Google Spreadsheet integration
- **Cluster Configuration**: Set hierarchical clustering parameters for opinion grouping
- **Prompt Customization**: Customize AI prompts for extraction, labeling, and overview generation
- **Build Management**: Download static builds of reports

## Application Architecture

### Key Pages

1. **Homepage** (`/`) - Report list and management dashboard
   - URL: http://localhost:4000
   - Displays all reports with statistics
   - Shows visibility counts (public, unlisted, private)
   - Report cards with metadata (creation date, name, comment count, opinion count, opinion group count)
   - Navigation to report creation page

2. **Report Creation Page** (`/create`) - Multi-step form for new reports
   - URL: http://localhost:4000/create
   - Basic information section (title, description, ID)
   - Data input section (CSV file or Google Spreadsheet)
   - AI settings section (provider, model, workers, advanced options)
   - Prompt customization options
   - Validation and submission

### Key Components

- **Header**: Logo and "管理者画面" (Administrator Screen) warning indicator
- **PageContent**: Report management dashboard with statistics and report cards
- **BasicInfoSection**: Title, description, and ID input fields
- **CsvFileTab**: CSV file upload and column selection
- **SpreadsheetTab**: Google Spreadsheet URL input and import functionality
- **AISettingsSection**: AI provider, model, and configuration options
- **ReportCardList**: Grid display of reports with operations (view, edit, delete, download, visibility toggle)
- **Empty**: Placeholder screen when no reports exist

## Test Scenarios

### Seed File
All tests assume a fresh browser state. The seed file is located at: `/Users/nishio/kouchou-ai/test/e2e/seed.spec.ts`

---

## 1. Homepage and Navigation

### 1.1 Homepage Load - Empty State
**Steps:**
1. Navigate to http://localhost:4000
2. Wait for page to fully load

**Expected Results:**
- Page loads successfully without errors
- Header displays with logo image at `/images/logo.svg`
- Header shows warning alert with "管理者画面" title
- Alert description reads "このページはレポート作成者向けの管理画面です"
- Empty state is displayed with text "レポートが0件です"
- Empty state shows explanation message about report creation
- "新規作成" button is visible with Plus icon
- Empty state image `/images/report-empty.png` is displayed

### 1.2 Homepage Load - With Reports
**Prerequisites:** At least one report exists in the system

**Steps:**
1. Navigate to http://localhost:4000
2. Wait for page to fully load

**Expected Results:**
- Page loads successfully
- "レポート管理" heading is displayed
- Three visibility count boxes are shown (public, unlisted, private)
- Each count box displays an icon (Eye, LockKeyhole, EyeClosedIcon) and count number
- "新規作成" button appears in the top right
- Report list grid is displayed with column headers:
  - 作成日時 (Creation Date)
  - レポート名 (Report Name)
  - コメント (Comments)
  - 意見 (Opinions)
  - 意見グループ (Opinion Groups)
- At least one report card is visible in the grid

### 1.3 Navigation to Report Creation
**Steps:**
1. Navigate to http://localhost:4000
2. Click the "新規作成" button (either in empty state or with reports)

**Expected Results:**
- URL changes to http://localhost:4000/create
- Page redirects to report creation page
- "新しいレポートを作成する" heading is displayed

---

## 2. Report Creation - Basic Information

### 2.1 Display Basic Information Form
**Steps:**
1. Navigate to http://localhost:4000/create
2. Observe the basic information section

**Expected Results:**
- Three form fields are visible:
  - "タイトル" (Title) field
  - "調査概要" (Survey Overview) field
  - "ID" field
- Each field has appropriate placeholder text:
  - Title: "例：人類が人工知能を開発・展開する上で、最優先すべき課題は何でしょうか？"
  - Overview: "例：このAI生成レポートは、パブリックコメントにおいて寄せられた意見に基づいています。"
  - ID: "例：example"
- Helper text is displayed under each field
- ID field helper text: "英字小文字と数字とハイフンのみ(URLで利用されます)"

### 2.2 Title Input Validation
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "タイトル" input field
3. Type "テストレポート"
4. Tab to next field

**Expected Results:**
- Text appears in the title field as typed
- No validation errors are shown
- Field accepts Japanese characters, spaces, and special characters

### 2.3 Survey Overview Input
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "調査概要" input field
3. Type "これはテスト用の調査です。2025年10月に実施されました。"
4. Tab to next field

**Expected Results:**
- Text appears in the overview field as typed
- No validation errors are shown
- Field accepts multi-byte characters and punctuation

### 2.4 Valid ID Input
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "ID" input field
3. Type "test-report-2025"
4. Tab to next field

**Expected Results:**
- Text appears in the ID field as typed
- No error border (red) appears on the field
- No validation error message is displayed
- Field accepts lowercase letters, numbers, and hyphens

### 2.5 Invalid ID Input - Uppercase Letters
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "ID" input field
3. Type "TestReport"
4. Tab to next field

**Expected Results:**
- Field border turns red (error state)
- Error message appears below field (text color red.500)
- Error message indicates invalid characters
- Helper text remains visible

### 2.6 Invalid ID Input - Special Characters
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "ID" input field
3. Type "test_report!@#"
4. Tab to next field

**Expected Results:**
- Field border turns red (error state)
- Error message appears below field
- Error message indicates invalid characters (only lowercase, numbers, and hyphens allowed)

### 2.7 Invalid ID Input - Japanese Characters
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click in the "ID" input field
3. Type "テストレポート"
4. Tab to next field

**Expected Results:**
- Field border turns red (error state)
- Error message appears indicating invalid characters

### 2.8 Empty Required Fields
**Steps:**
1. Navigate to http://localhost:4000/create
2. Leave all basic information fields empty
3. Scroll down to "レポート作成を開始" button
4. Click the button

**Expected Results:**
- Toast notification appears with type "error"
- Toast title: "入力エラー"
- Toast description contains validation error message
- Form does not submit
- User remains on the creation page

---

## 3. Report Creation - Data Input (CSV)

### 3.1 Display CSV Tab Interface
**Steps:**
1. Navigate to http://localhost:4000/create
2. Observe the "入力データ" (Input Data) section

**Expected Results:**
- Two tabs are visible: "CSVファイル" and "Googleスプレッドシート"
- "CSVファイル" tab is selected by default (variant: "enclosed")
- Tab indicator shows active tab
- CSV file upload area is visible

### 3.2 Switch Between Tabs
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click on "Googleスプレッドシート" tab
3. Click on "CSVファイル" tab

**Expected Results:**
- Tab switches to "Googleスプレッドシート" showing spreadsheet URL input
- Clicking "CSVファイル" tab switches back to CSV interface
- Tab indicator moves to show active tab
- Content area updates to show appropriate interface

### 3.3 CSV File Upload - Valid File
**Steps:**
1. Navigate to http://localhost:4000/create
2. Prepare a valid CSV file with columns: id, comment, source, url
3. Click on CSV file upload area or browse button
4. Select the CSV file
5. Confirm upload

**Expected Results:**
- File selection dialog opens
- After selection, file is uploaded
- Column selection dropdowns appear
- "コメントカラム選択" (Comment Column Selection) dropdown is populated with CSV columns
- "属性カラム選択" (Attribute Column Selection) multi-select is available
- Recommended cluster settings are calculated based on comment count

### 3.4 CSV Column Selection - Comment Column
**Steps:**
1. Navigate to http://localhost:4000/create
2. Upload a valid CSV file with multiple columns
3. Locate "コメントカラム選択" dropdown
4. Click and select "comment" column
5. Verify selection

**Expected Results:**
- Dropdown opens showing all CSV columns
- "comment" column can be selected
- Selected column is displayed in the dropdown
- Selection persists when clicking elsewhere

### 3.5 CSV Column Selection - Attribute Columns
**Steps:**
1. Navigate to http://localhost:4000/create
2. Upload a valid CSV file with multiple columns (e.g., id, comment, age, gender)
3. Locate "属性カラム選択" multi-select
4. Select multiple columns (e.g., "age" and "gender")
5. Verify selections

**Expected Results:**
- Multi-select opens showing available columns
- Multiple columns can be selected
- Selected columns are displayed as tags/chips
- Attribute columns can be deselected by clicking remove icon

### 3.6 CSV File Upload - Invalid Format
**Steps:**
1. Navigate to http://localhost:4000/create
2. Prepare a non-CSV file (e.g., .txt, .xlsx, .pdf)
3. Attempt to upload the file

**Expected Results:**
- File type validation occurs
- Error toast notification appears with type "error"
- Error message indicates invalid file format
- File is not accepted
- CSV upload area remains empty

### 3.7 CSV File Upload - Empty File
**Steps:**
1. Navigate to http://localhost:4000/create
2. Create an empty CSV file (0 bytes or header only)
3. Upload the empty CSV file

**Expected Results:**
- File uploads successfully
- Error toast appears: "データの読み込みに失敗しました"
- No column selection dropdowns appear
- User is prompted to upload a valid file with data

---

## 4. Report Creation - Data Input (Spreadsheet)

### 4.1 Display Spreadsheet Tab Interface
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click on "Googleスプレッドシート" tab

**Expected Results:**
- Spreadsheet URL input field is visible
- Input field has placeholder text for Google Spreadsheet URL
- Import button is visible
- Button is disabled until valid URL is entered

### 4.2 Spreadsheet URL Input - Valid Format
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click "Googleスプレッドシート" tab
3. Enter a valid Google Spreadsheet URL: "https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit"
4. Observe button state

**Expected Results:**
- URL appears in input field
- Import button becomes enabled
- No error message is displayed

### 4.3 Spreadsheet URL Input - Invalid Format
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click "Googleスプレッドシート" tab
3. Enter invalid URL: "http://example.com/test"
4. Attempt to import

**Expected Results:**
- Import button may be disabled based on URL validation
- If import is attempted, error toast appears
- Error message indicates invalid spreadsheet URL

### 4.4 Spreadsheet Import - Success
**Prerequisites:** Valid accessible Google Spreadsheet URL with public access

**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in basic info: Title "Test", ID "test-import-123"
3. Click "Googleスプレッドシート" tab
4. Enter valid public spreadsheet URL
5. Click import button
6. Wait for import to complete

**Expected Results:**
- Loading indicator appears during import
- Success toast notification appears
- Column selection dropdowns become available
- Spreadsheet data preview may be shown
- Comment and attribute column selectors are populated
- Import button becomes "Clear Data" button

### 4.5 Spreadsheet Import - Clear Data
**Prerequisites:** Spreadsheet data has been imported

**Steps:**
1. Navigate to http://localhost:4000/create after successful import
2. Locate "Clear Data" or similar button
3. Click the button

**Expected Results:**
- Imported data is cleared
- Column selection dropdowns disappear
- URL input field is cleared or reset
- Import button returns to initial state
- User can import a new spreadsheet

### 4.6 Spreadsheet Import - Private/Unauthorized
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click "Googleスプレッドシート" tab
3. Enter URL of private spreadsheet (no public access)
4. Click import button
5. Wait for response

**Expected Results:**
- Import fails
- Error toast notification appears
- Error message indicates access permission issue
- No data is imported
- User remains on creation page

---

## 5. Report Creation - AI Settings

### 5.1 Display AI Settings Section
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click "レポート生成設定" button
3. Observe expanded section

**Expected Results:**
- AI settings section expands and becomes visible
- Provider selection dropdown is displayed
- Model selection dropdown is displayed
- Workers number input with increment/decrement buttons is shown
- Additional options (パブコメモード, 引用元リンク有効化, etc.) are visible
- Prompt customization section may be visible

### 5.2 Collapse/Expand AI Settings
**Steps:**
1. Navigate to http://localhost:4000/create
2. Click "レポート生成設定" button to expand
3. Click the button again to collapse

**Expected Results:**
- First click: Section expands with animation
- Second click: Section collapses with animation
- Button remains accessible at all times
- Form state is preserved when collapsing/expanding

### 5.3 AI Provider Selection - OpenAI
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Click provider dropdown
4. Select "openai"

**Expected Results:**
- Dropdown opens showing available providers (openai, azure_openai, local)
- "openai" option can be selected
- Model dropdown updates to show OpenAI-compatible models
- Model options include GPT-4, GPT-3.5-turbo variants
- Provider description text appears explaining OpenAI option

### 5.4 AI Provider Selection - Azure OpenAI
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Select "azure_openai" from provider dropdown

**Expected Results:**
- Provider changes to Azure OpenAI
- Model dropdown updates to show Azure OpenAI models
- Additional connection settings may appear (endpoint, API key fields)
- Provider description explains Azure OpenAI usage

### 5.5 AI Provider Selection - Local LLM
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Select "local" from provider dropdown

**Expected Results:**
- Provider changes to Local LLM
- Model dropdown updates to show local models
- "ローカルLLMアドレス" (Local LLM Address) input field appears
- Default address may be pre-filled (e.g., "http://localhost:11434")
- "モデル取得" (Fetch Models) button appears
- Warning text about local LLM setup may be displayed

### 5.6 Model Selection
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Ensure provider is set to "openai"
4. Click model dropdown
5. Select a specific model (e.g., "gpt-4o-mini")

**Expected Results:**
- Model dropdown shows available models for selected provider
- Models include: gpt-4o, gpt-4o-mini, gpt-3.5-turbo variants
- Model can be selected
- Model description appears explaining the model capabilities and costs
- Selection persists

### 5.7 Fetch Local LLM Models
**Prerequisites:** Local LLM server running at specified address

**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Select "local" provider
4. Enter local LLM address: "http://localhost:11434"
5. Click "モデル取得" button

**Expected Results:**
- Button shows loading state
- Request is made to local LLM endpoint
- Available models are fetched and populate model dropdown
- Success feedback is shown
- If fetch fails, error toast appears with connection issue

### 5.8 Workers Configuration - Increase
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Locate workers number input (default may be 2 or 4)
4. Click increment button (+) multiple times

**Expected Results:**
- Worker count increases by 1 with each click
- Number is displayed in input field
- Maximum limit may exist (e.g., 10 or 20)
- Button may become disabled at maximum

### 5.9 Workers Configuration - Decrease
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Click decrement button (-) multiple times

**Expected Results:**
- Worker count decreases by 1 with each click
- Minimum value is enforced (likely 1)
- Decrement button becomes disabled at minimum
- Error prevention at minimum value

### 5.10 Workers Configuration - Manual Input
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Click in workers number input field
4. Clear existing value
5. Type "8"
6. Tab to next field

**Expected Results:**
- Input field accepts numeric input
- Non-numeric characters are rejected or filtered
- Valid number (8) is accepted
- Value is used in subsequent processing

### 5.11 Workers Configuration - Invalid Input
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Try to input "0" or negative number in workers field

**Expected Results:**
- Value is rejected or clamped to minimum (1)
- Error feedback may appear
- Field reverts to minimum valid value
- Form validation prevents invalid submission

### 5.12 Enable Pubcom Mode
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Locate "パブコメモード" checkbox
4. Click to enable

**Expected Results:**
- Checkbox becomes checked
- Setting is saved to form state
- Helper text or description explains pubcom mode functionality
- Mode affects report generation parameters

### 5.13 Enable Source Link
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Locate "引用元リンク有効化" checkbox
4. Click to enable

**Expected Results:**
- Checkbox becomes checked
- Setting enables source links in generated reports
- Helper text explains that source URLs will be included in reports

### 5.14 User API Key Input
**Prerequisites:** User wants to use their own API key

**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Locate "APIキー" or user API key input field
4. Enter a test API key: "sk-test-1234567890abcdef"
5. Tab to next field

**Expected Results:**
- Input field accepts text input
- Input may be masked for security (type="password")
- Helper text explains this overrides server-side API key
- API key is stored securely in form state

### 5.15 Cluster Settings - Default Values
**Steps:**
1. Navigate to http://localhost:4000/create
2. Upload CSV with 1000 comments
3. Open "レポート生成設定" section (may be under advanced settings)

**Expected Results:**
- Cluster Level 1 (第一層) shows recommended value (e.g., 10)
- Cluster Level 2 (第二層) shows recommended value (e.g., 100)
- Values are calculated based on cube root of comment count
- Helper text explains cluster number recommendations

### 5.16 Cluster Settings - Manual Override
**Steps:**
1. Navigate to http://localhost:4000/create
2. Upload CSV file
3. Access cluster settings (may be in AI settings or separate section)
4. Change Cluster Level 1 to 15
5. Change Cluster Level 2 to 225

**Expected Results:**
- Custom values are accepted
- Values override recommended defaults
- Warning may appear if values are unconventional
- Custom values are used in report generation

### 5.17 Prompt Customization - View Defaults
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open "レポート生成設定" section
3. Locate prompt customization area (may be collapsible)
4. Expand prompt sections

**Expected Results:**
- Extraction prompt is visible (used for extracting opinions from comments)
- Labeling prompt section may be visible
- Overview prompt section may be visible
- Default prompt templates are pre-filled
- Each prompt has explanation of its purpose

### 5.18 Prompt Customization - Edit Extraction Prompt
**Steps:**
1. Navigate to http://localhost:4000/create
2. Open prompt customization section
3. Locate extraction prompt text area
4. Modify the prompt text
5. Save or apply changes

**Expected Results:**
- Text area is editable
- Changes are preserved in form state
- Character count or limit may be displayed
- Modified prompt will be used during report generation
- Reset button may be available to restore defaults

---

## 6. Report Creation - Validation and Submission

### 6.1 Submit with All Required Fields Valid
**Prerequisites:** Valid data in all required fields

**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in Title: "Valid Test Report"
3. Fill in Survey Overview: "Test survey conducted in October 2025"
4. Fill in ID: "valid-test-report"
5. Upload valid CSV file with comments
6. Select comment column
7. Set AI provider to "openai"
8. Select model "gpt-4o-mini"
9. Scroll to bottom
10. Click "レポート作成を開始" button

**Expected Results:**
- Form validation passes
- Button shows loading state during submission
- Success toast appears: "レポート作成を開始しました"
- User is redirected to homepage (/)
- New report appears in report list with status "processing" or "pending"

### 6.2 Submit with Missing Title
**Steps:**
1. Navigate to http://localhost:4000/create
2. Leave Title field empty
3. Fill in Survey Overview: "Test"
4. Fill in ID: "test-no-title"
5. Upload CSV and configure settings
6. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears: "入力エラー"
- Description indicates title is required
- Form does not submit
- User remains on creation page
- Focus may move to title field

### 6.3 Submit with Missing ID
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in Title: "Test Report"
3. Fill in Survey Overview: "Test"
4. Leave ID field empty
5. Upload CSV and configure settings
6. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears: "入力エラー"
- Description indicates ID is required
- Form does not submit
- User remains on creation page

### 6.4 Submit with No Data Input
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in all basic information fields
3. Do NOT upload CSV or import spreadsheet
4. Configure AI settings
5. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears
- Description indicates input data is required
- Message prompts user to upload CSV or import spreadsheet
- Form does not submit

### 6.5 Submit with Missing Comment Column Selection
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in basic information
3. Upload CSV file
4. Do NOT select a comment column
5. Configure AI settings
6. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears
- Description indicates comment column must be selected
- Form does not submit

### 6.6 Submit with No AI Provider Selected
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in basic information
3. Upload CSV and select comment column
4. Clear or skip AI provider selection
5. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears: "入力エラー"
- Description indicates AI provider must be selected
- Form does not submit

### 6.7 Submit with No Model Selected
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in basic information
3. Upload CSV and select comment column
4. Select AI provider but no model
5. Click "レポート作成を開始" button

**Expected Results:**
- Form validation fails
- Error toast appears
- Description indicates model must be selected
- Form does not submit

### 6.8 Submit with Comments Less Than Cluster Count
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in basic information with ID "small-dataset"
3. Upload CSV with only 10 comments
4. Select comment column
5. Set cluster level 2 to 50 (more than comment count)
6. Click "レポート作成を開始" button

**Expected Results:**
- Warning confirmation dialog appears
- Dialog message: "csvファイルの行数 (10) が設定された意見グループ数 (50) を下回っています。このまま続けますか？"
- Dialog explains potential processing errors
- Dialog suggests adjusting cluster settings
- User can choose to proceed or cancel
- If proceed: submission continues
- If cancel: returns to form

### 6.9 Submit with API Error
**Prerequisites:** Backend API is offline or returns error

**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in all required fields correctly
3. Click "レポート作成を開始" button
4. Wait for API response

**Expected Results:**
- Submission is attempted
- Error toast appears: "レポート作成に失敗しました"
- Error description shows API error message
- Button returns to normal state (not loading)
- User remains on creation page
- Form data is preserved

### 6.10 Submit During Processing
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in all required fields
3. Click "レポート作成を開始" button
4. Immediately try to click the button again

**Expected Results:**
- Button enters loading state after first click
- Button is disabled during processing
- Second click has no effect
- Duplicate submission is prevented
- User must wait for first submission to complete

### 6.11 API Cost Warning Acknowledgment
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in all fields with paid AI provider (OpenAI or Azure)
3. Scroll to bottom
4. Observe warning text above submit button

**Expected Results:**
- Warning text is visible: "有料のAIプロバイダーの場合は作成する度にAPI利用料がかかります。"
- Text color is secondary/muted (font.secondary)
- Text size is small (body/sm)
- Warning remains visible before and during submission

---

## 7. Report Management Operations

### 7.1 View Report List with Multiple Reports
**Prerequisites:** At least 3 reports exist with different visibility settings

**Steps:**
1. Navigate to http://localhost:4000
2. Observe the report list

**Expected Results:**
- All reports are displayed in grid format
- Each report card shows:
  - Creation date/time (作成日時)
  - Report name (レポート名)
  - Comment count (コメント)
  - Opinion count (意見)
  - Opinion group count (意見グループ)
  - Visibility indicator icon
  - Action buttons (view, edit, delete, download)
- Reports are sorted (likely by creation date, newest first)
- Visibility statistics are correct in count boxes

### 7.2 Filter/Sort Reports
**Note:** This feature may not be implemented based on code analysis

**Steps:**
1. Navigate to http://localhost:4000
2. Look for sort or filter controls
3. Attempt to sort by date, name, or visibility

**Expected Results:**
- If feature exists: Reports reorder according to selected criteria
- If feature does not exist: No filter/sort controls are visible

### 7.3 View Report Details
**Prerequisites:** At least one completed report exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate a report card
3. Click on report name or view button

**Expected Results:**
- User is redirected to report detail page (likely on client app, port 3000)
- URL format: http://localhost:3000/report/{report-id}
- Report displays with full visualizations and data
- User can navigate back to admin interface

### 7.4 Edit Report Metadata
**Note:** Edit functionality may be limited based on code structure

**Prerequisites:** At least one report exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate a report card
3. Click edit button (if available)

**Expected Results:**
- If edit page exists: User is redirected to edit form
- Edit form pre-fills with existing report data
- User can modify title, description, visibility
- Save button updates report metadata
- If edit not available: Edit button may not be visible

### 7.5 Delete Report - Confirmation
**Prerequisites:** At least one report exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate a report card
3. Click delete button (likely trash icon)

**Expected Results:**
- Confirmation dialog appears
- Dialog message asks: "このレポートを削除しますか？" or similar
- Dialog shows report name being deleted
- Dialog warns about permanent deletion
- "Cancel" and "Delete" buttons are present
- Delete button may be red/warning color

### 7.6 Delete Report - Execute
**Prerequisites:** Delete confirmation dialog is open

**Steps:**
1. Open delete confirmation dialog (see 7.5)
2. Click "Delete" or confirmation button
3. Wait for deletion to complete

**Expected Results:**
- Loading indicator may appear
- API request is made to delete report
- Success toast appears: "レポートを削除しました" or similar
- Report card is removed from list
- Report count statistics update
- Page refreshes or updates automatically

### 7.7 Delete Report - Cancel
**Prerequisites:** Delete confirmation dialog is open

**Steps:**
1. Open delete confirmation dialog (see 7.5)
2. Click "Cancel" button

**Expected Results:**
- Dialog closes
- No deletion occurs
- Report remains in list
- User returns to normal view

### 7.8 Change Report Visibility - Public
**Prerequisites:** Report with "unlisted" or "private" visibility exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate report with non-public visibility
3. Click visibility toggle button or menu
4. Select "public" option

**Expected Results:**
- Report visibility changes to "public"
- Visibility icon updates to Eye icon
- Public count increases by 1
- Previous visibility count decreases by 1
- Success feedback may appear
- Report becomes accessible at public URL

### 7.9 Change Report Visibility - Unlisted
**Prerequisites:** Report with "public" or "private" visibility exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate report with different visibility
3. Click visibility toggle
4. Select "unlisted" option

**Expected Results:**
- Report visibility changes to "unlisted"
- Visibility icon updates to LockKeyhole icon
- Unlisted count increases by 1
- Previous visibility count decreases by 1
- Report accessible only via direct URL

### 7.10 Change Report Visibility - Private
**Prerequisites:** Report with "public" or "unlisted" visibility exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate report with different visibility
3. Click visibility toggle
4. Select "private" option

**Expected Results:**
- Report visibility changes to "private"
- Visibility icon updates to EyeClosedIcon icon
- Private count increases by 1
- Previous visibility count decreases by 1
- Report not accessible via public URL

### 7.11 Download Report Build
**Prerequisites:** At least one completed report exists

**Steps:**
1. Navigate to http://localhost:4000
2. Locate report card
3. Click download button (likely download icon)

**Expected Results:**
- Download initiation feedback appears
- Browser download dialog opens
- Report data is downloaded (likely ZIP or JSON format)
- Download completes successfully
- File contains report configuration and/or results

### 7.12 Bulk Build Download
**Prerequisites:** Multiple reports exist

**Steps:**
1. Navigate to http://localhost:4000
2. Scroll to bottom of report list
3. Locate "Build Download" button (BuildDownloadButton component)
4. Click the button

**Expected Results:**
- Build preparation begins
- Progress indicator may appear
- ZIP file containing multiple reports is generated
- Download begins automatically
- Success notification appears

---

## 8. Error Handling and Edge Cases

### 8.1 Network Error During Page Load
**Prerequisites:** Simulate network error or disconnect internet

**Steps:**
1. Disconnect network or use browser dev tools to simulate offline
2. Navigate to http://localhost:4000
3. Wait for timeout

**Expected Results:**
- Page attempts to load
- After timeout, error message appears
- Error heading: "レポートの取得に失敗しました"
- Page displays gracefully without crash
- User can retry when connection restored

### 8.2 API Server Offline
**Prerequisites:** Backend API server (port 8000) is not running

**Steps:**
1. Ensure API server is stopped
2. Navigate to http://localhost:4000
3. Observe behavior

**Expected Results:**
- Page loads frontend successfully
- API request for reports fails
- Error message appears: "レポートの取得に失敗しました"
- Header and navigation remain functional
- User can navigate to /create page

### 8.3 Session Timeout During Form Fill
**Prerequisites:** Long form session or simulated timeout

**Steps:**
1. Navigate to http://localhost:4000/create
2. Begin filling form
3. Wait extended period (30+ minutes)
4. Attempt to submit

**Expected Results:**
- If session expires: Error appears indicating session timeout
- User may need to refresh and re-enter data
- Best practice: Form data preserved in browser storage
- Warning message advises user to refresh

### 8.4 Browser Back Button After Submission
**Steps:**
1. Navigate to http://localhost:4000/create
2. Complete form and submit successfully
3. Redirected to homepage
4. Click browser back button

**Expected Results:**
- Browser navigates back to creation page
- Form is reset to empty state (prevents duplicate submission)
- OR form shows previously entered data
- Warning may appear about form resubmission
- Duplicate submission is prevented

### 8.5 Refresh During Report Creation
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill form partially
3. Press browser refresh (F5 or Cmd+R)

**Expected Results:**
- Browser prompts about form resubmission (if POST was made)
- Page reloads
- Form resets to empty state (likely no form data persistence)
- User must re-enter data
- No partial submission occurs

### 8.6 Multiple Browser Tabs/Windows
**Steps:**
1. Open http://localhost:4000 in Tab 1
2. Open http://localhost:4000 in Tab 2
3. Create report in Tab 1
4. Switch to Tab 2 and refresh

**Expected Results:**
- Both tabs function independently
- New report from Tab 1 appears in Tab 2 after refresh
- No conflicts between tabs
- Each tab maintains separate form state

### 8.7 Very Large CSV File Upload
**Steps:**
1. Navigate to http://localhost:4000/create
2. Prepare CSV file with 50,000+ rows
3. Attempt to upload

**Expected Results:**
- Upload may take significant time
- Progress indicator appears
- File size validation may reject extremely large files
- If accepted: Processing time warning may appear
- If rejected: Error message about file size limit

### 8.8 CSV with Special Characters
**Steps:**
1. Navigate to http://localhost:4000/create
2. Upload CSV containing:
   - Multi-byte Japanese characters
   - Emojis
   - Special symbols (©, ®, ™)
   - Line breaks within cells
3. Select comment column with special characters
4. Submit report

**Expected Results:**
- CSV parsing handles special characters correctly
- Multi-byte characters display properly
- Emojis are preserved
- Line breaks are handled
- No encoding errors occur
- Report generation processes special characters correctly

### 8.9 Duplicate Report ID
**Prerequisites:** Report with ID "existing-report" already exists

**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill in Title: "Duplicate Test"
3. Fill in ID: "existing-report"
4. Complete form
5. Attempt to submit

**Expected Results:**
- Validation detects duplicate ID
- Error toast appears: "このIDは既に使用されています" or similar
- Form does not submit
- User must choose different ID
- Red border may appear on ID field

### 8.10 Console Errors Check
**Steps:**
1. Open browser developer console
2. Navigate to http://localhost:4000
3. Navigate to http://localhost:4000/create
4. Interact with form elements
5. Observe console for errors

**Expected Results:**
- No JavaScript errors appear in console
- No React warnings about keys or props
- No network errors (except expected API failures if server down)
- Console may show info logs for development
- Application functions without console errors

---

## 9. Accessibility and UX

### 9.1 Keyboard Navigation - Homepage
**Steps:**
1. Navigate to http://localhost:4000
2. Use Tab key to navigate through interactive elements
3. Use Enter/Space to activate buttons
4. Navigate entire page using only keyboard

**Expected Results:**
- Tab order is logical (top to bottom, left to right)
- Focus indicators are visible on focused elements
- All buttons and links are keyboard accessible
- Enter/Space activates buttons and links
- "新規作成" button can be activated via keyboard
- Report cards are keyboard navigable

### 9.2 Keyboard Navigation - Creation Form
**Steps:**
1. Navigate to http://localhost:4000/create
2. Tab through all form fields
3. Use arrow keys in dropdowns
4. Use keyboard to navigate tabs (CSV vs Spreadsheet)

**Expected Results:**
- Tab order follows visual layout
- Form fields receive focus in logical order
- Dropdowns can be navigated with arrow keys
- Tabs can be switched with arrow keys
- Space/Enter activates buttons
- Form can be completely filled using keyboard only

### 9.3 Screen Reader Compatibility
**Prerequisites:** Screen reader software (NVDA, JAWS, VoiceOver)

**Steps:**
1. Enable screen reader
2. Navigate to http://localhost:4000
3. Navigate through page structure
4. Listen to field labels and descriptions

**Expected Results:**
- Page structure is announced correctly
- Headings are properly labeled (h1, h2, etc.)
- Form fields have associated labels
- Button purposes are announced
- Error messages are announced
- ARIA labels are present where needed
- Images have alt text

### 9.4 Form Field Labels and Help Text
**Steps:**
1. Navigate to http://localhost:4000/create
2. Observe all form fields
3. Check for labels and helper text

**Expected Results:**
- Every field has visible label
- Labels are descriptive (タイトル, 調査概要, ID)
- Helper text provides additional context
- Placeholder text gives examples
- Required fields are indicated (if applicable)
- Error messages are clear and actionable

### 9.5 Responsive Design - Mobile View
**Steps:**
1. Open http://localhost:4000 in browser
2. Resize window to mobile width (375px)
3. Navigate to creation page
4. Interact with form elements

**Expected Results:**
- Layout adapts to narrow width
- Form fields stack vertically
- Buttons remain accessible
- Text remains readable
- No horizontal scrolling required
- Touch targets are appropriately sized
- Navigation remains usable

### 9.6 Responsive Design - Tablet View
**Steps:**
1. Open http://localhost:4000
2. Resize to tablet width (768px)
3. Test all interactions

**Expected Results:**
- Layout adjusts for medium width
- Report cards may adjust column count
- Form layout remains usable
- All features remain accessible
- Typography scales appropriately

### 9.7 Loading States and Feedback
**Steps:**
1. Navigate to http://localhost:4000/create
2. Fill form and submit
3. Observe loading indicators
4. Try uploading large CSV
5. Try importing spreadsheet

**Expected Results:**
- Submit button shows loading state (spinner, text change)
- File upload shows progress
- Spreadsheet import shows loading indicator
- User knows when system is processing
- Loading states prevent duplicate actions
- User can't interact with disabled elements

### 9.8 Error Message Clarity
**Steps:**
1. Navigate to http://localhost:4000/create
2. Trigger various validation errors
3. Read error messages

**Expected Results:**
- Error messages are in Japanese
- Messages clearly state what's wrong
- Messages suggest how to fix the error
- Messages are specific, not generic
- Error toast notifications are readable
- Error styling is consistent (red, warning icons)

### 9.9 Success Feedback
**Steps:**
1. Successfully create a report
2. Successfully change report visibility
3. Successfully delete a report

**Expected Results:**
- Success toast notifications appear
- Messages confirm action completed
- Toast color indicates success (green/success theme)
- Toast duration is appropriate (5 seconds)
- User clearly knows action succeeded
- Page updates reflect successful action

### 9.10 Browser Compatibility
**Steps:**
1. Open http://localhost:4000 in Chrome
2. Open http://localhost:4000 in Firefox
3. Open http://localhost:4000 in Safari
4. Open http://localhost:4000 in Edge
5. Test core functionality in each browser

**Expected Results:**
- Application loads in all modern browsers
- Layout renders consistently
- Form interactions work in all browsers
- CSS styling is consistent
- JavaScript functionality works
- No browser-specific errors
- Polyfills handle older browser features

---

## 10. Integration and Data Flow

### 10.1 End-to-End Report Creation Flow
**Steps:**
1. Navigate to http://localhost:4000
2. Click "新規作成"
3. Fill Title: "E2E Test Report"
4. Fill Survey Overview: "End-to-end test survey"
5. Fill ID: "e2e-test-report"
6. Upload valid CSV with 100 comments
7. Select comment column
8. Select one attribute column
9. Open AI settings
10. Verify provider: openai, model: gpt-4o-mini
11. Accept default workers: 4
12. Click "レポート作成を開始"
13. Wait for redirect to homepage
14. Verify new report appears in list

**Expected Results:**
- Complete flow executes without errors
- Each step transitions smoothly
- All data is captured correctly
- API request is made with correct payload
- Report appears in list with "processing" status
- User can view report once processing completes

### 10.2 Report Status Tracking
**Prerequisites:** Report creation in progress

**Steps:**
1. Create new report (see 10.1)
2. Return to homepage
3. Observe report status
4. Refresh page periodically
5. Monitor status changes

**Expected Results:**
- Report initially shows "processing" or "pending" status
- Status indicator (icon, badge, or text) is visible
- Status updates as processing progresses
- Final status shows "completed" or "ready"
- If error occurs: Status shows "failed" with error indicator
- User can click to view details or error messages

### 10.3 API Request Payload Validation
**Prerequisites:** Browser dev tools open

**Steps:**
1. Open Network tab in browser dev tools
2. Navigate to http://localhost:4000/create
3. Fill and submit form
4. Observe POST request to /admin/reports or similar

**Expected Results:**
- POST request is made to correct endpoint
- Request headers include API key
- Content-Type is application/json
- Request body includes:
  - input (ID)
  - question (title)
  - intro (overview)
  - comments array
  - cluster settings [lv1, lv2]
  - provider
  - model
  - workers
  - prompt settings
  - other configuration
- Request structure matches API schema

### 10.4 Homepage Data Refresh
**Steps:**
1. Navigate to http://localhost:4000
2. Note report count and list
3. In another tab, create new report
4. Return to first tab
5. Refresh page

**Expected Results:**
- Page fetches latest reports
- New report appears in list
- Statistics update correctly
- No cache issues prevent data refresh
- fetch with cache: "no-store" ensures fresh data

### 10.5 Cross-Service Navigation
**Steps:**
1. Navigate to admin interface: http://localhost:4000
2. Click on a completed report to view it
3. Verify navigation to client app: http://localhost:3000
4. Note report ID in URL
5. Return to admin interface

**Expected Results:**
- Report links correctly to client viewing app
- URL format: http://localhost:3000/report/{report-id}
- Report displays with full visualizations
- Browser back button returns to admin interface
- No navigation errors occur

---

## Test Environment Setup

### Prerequisites
- Docker and Docker Compose installed
- Ports 3000, 4000, 8000 available
- OpenAI API key configured in .env file
- Sufficient disk space for Docker images and data

### Starting the Application
```bash
# From repository root
cp .env.example .env
# Edit .env and add OPENAI_API_KEY and other required variables
docker compose up
```

### Accessing the Application
- Admin Interface: http://localhost:4000
- Client Interface: http://localhost:3000 (for viewing reports)
- API Server: http://localhost:8000 (backend)

### Test Data Preparation
Create sample CSV files with various characteristics:
- Small file: 10 rows
- Medium file: 100 rows
- Large file: 1000 rows
- File with special characters
- File with multiple columns for attributes
- Invalid CSV files for negative testing

### Playwright Configuration
Tests should be located in: `/Users/nishio/kouchou-ai/test/e2e/`

Use the seed file: `/Users/nishio/kouchou-ai/test/e2e/seed.spec.ts`

Configure Playwright to:
- Run tests on Chromium, Firefox, and WebKit
- Use baseURL: http://localhost:4000
- Set appropriate timeouts for API operations
- Take screenshots on failure
- Record videos for failed tests
- Use parallel execution for independent tests

---

## Notes for Test Implementation

1. **Async Operations**: Many operations involve API calls and processing. Use appropriate waits and timeout configurations.

2. **API Dependency**: Tests require running backend API. Consider mocking for unit tests, but integration tests need real API.

3. **Data Cleanup**: Implement cleanup after tests to remove test reports and data.

4. **Test Independence**: Each test should be independent and not rely on state from other tests.

5. **Environment Variables**: Tests may need to set/override environment variables for different configurations.

6. **Authentication**: Currently no authentication visible in code, but may be added in future.

7. **File Handling**: CSV upload tests need actual test files in accessible location.

8. **Timing Issues**: AI processing can take minutes. Either mock for fast tests or use separate integration tests.

9. **Localization**: All text is in Japanese. Tests should verify exact Japanese strings.

10. **Browser State**: Tests should start with fresh browser context to ensure clean slate.

---

## Summary

This comprehensive test plan covers:
- **80+ test scenarios** across 10 major functional areas
- **Homepage and navigation** (12 scenarios)
- **Report creation with basic information** (8 scenarios)
- **CSV data input** (7 scenarios)
- **Spreadsheet integration** (6 scenarios)
- **AI settings and configuration** (18 scenarios)
- **Form validation and submission** (11 scenarios)
- **Report management operations** (12 scenarios)
- **Error handling and edge cases** (10 scenarios)
- **Accessibility and UX** (10 scenarios)
- **Integration and data flow** (5 scenarios)

Each scenario includes:
- Clear step-by-step instructions
- Expected results for verification
- Prerequisites where applicable
- Error conditions and edge cases

The test plan is designed for Playwright implementation and follows best practices for E2E testing, including proper setup, cleanup, and independence between tests.

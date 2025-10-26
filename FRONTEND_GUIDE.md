# Frontend Dashboard Guide - Multi-Agent Orchestration UI

## Dashboard Overview

The React frontend provides an intuitive interface for running brand reputation analysis with two distinct modes:

### Dashboard URL
```
http://localhost:3000
```

---

## User Interface Layout

### Left Panel - Control Center (1/3 Width)
**Run Brand Analysis Card**
- Tabbed interface selector (Quick Analysis | Full Orchestration)
- Brand name text input (default: "Acme Corp")
- Max articles slider (3-25, default: 10)
- Days to look back slider (1-30, default: 7)
- Submit button (Analyze Brand | Run Orchestration)
- Error alert display

### Main Panel - Results Display (2/3 Width)
**Tabbed Results View**
- Tab 1: Quick Analysis mode results
- Tab 2: Full Orchestration mode results

---

## Mode 1: Quick Analysis Tab

### Sentiment Overview Section
**Left Side - Pie Chart:**
- Inner donut chart showing sentiment distribution
- Color-coded segments:
  - Green: Positive sentiment
  - Blue: Neutral sentiment
  - Red: Negative sentiment
- Interactive legend below chart

**Right Side - Summary Statistics:**
- Brand name display
- Analysis timestamp
- Timeframe indicator
- Average sentiment score chip (with trend icon)
- Sentiment breakdown chips:
  - Green "Positive: X"
  - Blue "Neutral: X"
  - Red "Negative: X"

### Key Insights Section
**Lower Left Grid Item:**
- Typography header: "Key Insights"
- Icon + text pairs for each insight
- Displays notable patterns from analysis
- Shows empty state if no insights found

### Recommended Next Steps Section
**Lower Right Grid Item:**
- Typography header: "Recommended Next Steps"
- Action items with trending icon
- Suggested monitoring actions
- Priority recommendations

### Latest Articles Section
**Full Width Grid Item:**
- Header with article count
- Keyword chips showing top topics
- Article cards (scrollable list):
  - Article title (clickable)
  - Source and publication date
  - Excerpt text preview
  - Keyword chips (first 4)
  - Sentiment badge (color-coded)
  - Sentiment score display
  - External link button

---

## Mode 2: Full Orchestration Tab

### Workflow Execution Summary Card
**Top Section:**
- Workflow ID display
- Success/Failed status chip
- Execution time display
- Completed steps chips (green with checkmarks)
- Failed steps chips (if any)

### Sentiment Analysis Results Grid

**Left Side - Pie Chart (Same as Quick Analysis):**
- Donut chart of sentiment distribution
- Legend with counts

**Right Side - Detailed Breakdown:**
- "Sentiment Analysis Agent Results" header
- Average Sentiment Score (large display)
- Breakdown table:
  - Positive count
  - Neutral count
  - Negative count

### Risk Assessment & Crisis Analysis Card

**Crisis Score Display:**
- "Crisis Score" label
- Numeric score (0.12 / 1.00)
- Linear progress bar:
  - Green fill if score < 0.6
  - Red fill if score > 0.6
- Height: 8px, rounded corners

**Crisis Level Chip:**
- Color-coded:
  - Green: "low"
  - Orange: "moderate"
  - Red: "severe"

**Additional Metrics:**
- Negative Sentiment Ratio percentage
- Crisis indicators found count
- Immediate attention flag

### Response Generation Agent Recommendations Card

**Header:**
- "Response Generation Agent - Recommendations"

**Content List:**
- Info icon + recommendation text pairs
- One recommendation per line
- Examples:
  - "📊 Analyzed 10 recent articles - sentiment trend is positive"
  - "🔑 Top topics: stocks, openai, ethernet, open, broadcom"
  - "✅ Continue regular monitoring - no critical issues detected"

### Next Actions Card

**Header:**
- "Next Actions"

**Content List:**
- Timeline icon + action text pairs
- Prioritized action items
- Examples:
  - "Review detailed sentiment breakdown below"
  - "Track key metrics in next 24-hour cycle"

### Analyzed Articles Section (Full Width)
**Article Grid:**
- Same layout as Quick Analysis mode
- All 10 analyzed articles displayed
- Sortable/filterable (implementation-ready)

---

## Interactive Elements

### Form Inputs
```
Brand Name Input Field
├─ Text input with validation
├─ Placeholder: "Enter brand name"
├─ Required: true
├─ Min length: 2, Max: 80

Articles to Fetch
├─ Number input with spinner
├─ Range: 3-25
├─ Default: 10
├─ Step: 1

Days to Look Back
├─ Number input with spinner
├─ Range: 1-30
├─ Default: 7
├─ Step: 1
```

### Submit Button States
```
Normal State
├─ Label: "Analyze Brand" (Quick mode)
│  or "Run Orchestration" (Full mode)
├─ Color: Primary (blue)
├─ Enabled: true

Loading State
├─ Label: "Analyzing…"
├─ Disabled: true
├─ Shows spinner
├─ Cursor: not-allowed
```

### Error Handling
```
Error Alert
├─ Type: Alert component
├─ Severity: "error" (red background)
├─ Message: Error description
├─ Dismissible: true
├─ Position: Below form inputs
```

---

## Response Data Flow

```
User Input (Brand Name)
        ↓
Form Validation
        ↓
HTTP POST Request
        ↓
Backend Processing
├─ Data Collection Agent fetches from NewsAPI
├─ Sentiment Analysis Agent processes articles
└─ Response Generation Agent creates recommendations
        ↓
JSON Response Received
        ↓
React Component State Update
        ↓
UI Renders Results
├─ Charts re-render with new data
├─ Article cards populate
└─ Metrics display updates
```

---

## Material-UI Components Used

### Layout
- `Box` - Flex containers and spacing
- `Grid` - Responsive grid layout (12-column)
- `Paper` - Card/panel backgrounds with elevation
- `Stack` - Direction-based layout (row/column)

### Input
- `TextField` - Text and number inputs
- `Button` - Submit and action buttons
- `Tabs` - Mode selection tabs
- `Tab` - Individual tab items

### Display
- `Typography` - Text with semantic meaning
- `Chip` - Compact data display badges
- `LinearProgress` - Crisis score visualization
- `Card` - Information containers
- `CardContent` - Card content wrapper

### Feedback
- `Alert` - Error messages
- `CircularProgress` - Loading spinner

### Icons (Material Design Icons)
- `LaunchIcon` - External link indicator
- `TrendingUpIcon` - Positive trend
- `TrendingDownIcon` - Negative trend
- `InfoIcon` - Information marker
- `ArticleIcon` - Article indicator
- `SchemaIcon` - Orchestration/network
- `TimelineIcon` - Sequential action
- `CheckCircleIcon` - Completed state
- `ErrorIcon` - Error state

---

## Responsive Behavior

### Mobile (xs: 0-600px)
- Single column layout
- Full-width inputs
- Stacked cards
- Vertical article layout
- Smaller charts

### Tablet (sm: 600-900px)
- Two-column grid for some sections
- Side-by-side article info

### Desktop (md: 900px+)
- Three-column sections possible
- Side-by-side panels
- Horizontal article layout with sentiment on right
- Large charts and detailed metrics

---

## Performance Optimizations

1. **React Query**: Caches analysis results to prevent duplicate requests
2. **useMemo**: Sentiment breakdown data memoized to prevent unnecessary recalculations
3. **Lazy Charts**: Recharts renders on-demand for visible sections
4. **Conditional Rendering**: Articles only displayed when analysis complete

---

## Accessibility Features

- Semantic HTML structure
- ARIA labels on tabs
- Color contrast compliant (WCAG AA)
- Keyboard navigation support
- Screen reader friendly
- Focus management

---

## Example Usage Scenario

### Step 1: Load Dashboard
```
User opens http://localhost:3000
↓
Dashboard loads with empty state
↓
Default brand "Acme Corp" displayed
```

### Step 2: Select Full Orchestration
```
User clicks "Full Orchestration" tab
↓
Tab switches to orchestration mode
↓
Form remains visible on left
```

### Step 3: Enter Brand Name
```
User clears default and enters "NVIDIA"
↓
Brand name updates to "NVIDIA"
```

### Step 4: Submit Analysis
```
User clicks "Run Orchestration" button
↓
Button shows "Analyzing…" state
↓
Loading spinner appears in main panel
```

### Step 5: View Results
```
Results load after ~0.3 seconds
↓
Workflow ID displays
↓
Crisis score gauge shows 0.12 (LOW)
↓
Pie chart renders sentiment distribution
↓
Articles list populates
↓
Recommendations display
```

### Step 6: Explore Articles
```
User scrolls through articles
↓
User clicks external link button
↓
Article opens in new tab
```

---

## API Integration Points

### Quick Analysis Endpoint
```
POST /api/v1/analytics/brand-analysis
Content-Type: application/json

{
  "brand_name": "NVIDIA",
  "max_articles": 10,
  "days_back": 7
}

Response: BrandAnalysisResponse
├─ articles[]
├─ summary
│  ├─ total_articles
│  ├─ positive
│  ├─ neutral
│  ├─ negative
│  ├─ average_sentiment_score
│  ├─ top_keywords[]
│  ├─ insights[]
│  └─ recommendations[]
└─ timeframe_days
```

### Full Orchestration Endpoint
```
POST /api/v1/analytics/brand-analysis-orchestrated
Content-Type: application/json

{
  "brand_name": "NVIDIA",
  "max_articles": 10,
  "days_back": 7
}

Response: FullOrchestrationResponse
├─ success
├─ workflow_id
├─ execution_time_seconds
├─ steps_completed[]
├─ articles[]
├─ summary
├─ agent_results
│  ├─ data_collection_agent
│  ├─ sentiment_analysis_agent
│  └─ response_generation_agent
├─ risk_assessments
│  ├─ crisis_score
│  ├─ crisis_level
│  └─ negative_sentiment_ratio
├─ recommendations[]
└─ next_actions[]
```

---

## Theming

**Color Palette:**
- Primary (Blue): #1976d2
- Success (Green): #2e7d32
- Error (Red): #c62828
- Warning (Orange): #f57c00
- Info (Light Blue): #0288d1
- Text Primary: #212121
- Text Secondary: #757575
- Background: #ffffff
- Surface: #f5f5f5

**Typography:**
- Headings: Roboto Bold
- Body: Roboto Regular
- Code: Roboto Mono

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

**Dashboard is fully responsive and optimized for all screen sizes!** 📱💻🖥️

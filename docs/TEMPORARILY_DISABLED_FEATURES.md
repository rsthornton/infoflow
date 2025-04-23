# Temporarily Disabled Features

This document details features that have been temporarily disabled in the InfoFlow application and provides instructions for re-enabling them.

## Disabled Features

As of April 13, 2025, the following features have been temporarily disabled:

1. **Guided Scenarios**
   - Web UI access at `/guided-scenarios`
   - API endpoints at `/api/scenarios` and `/api/scenarios/<scenario_id>`
   - Navigation menu link

2. **Metrics Dashboard**
   - Web UI access at `/metrics-dashboard` 
   - API endpoint at `/api/metrics-dashboard/<run_id>`
   - Navigation menu link

## Implementation Details

The features were disabled with the following changes:

1. **Route Handlers**: Modified to return friendly error messages
   - File: `/infoflow/web/routes.py`
   - Changes: Return "temporarily unavailable" message using the error template
   - Original code is preserved as comments with "Uncomment to re-enable" instructions

2. **Navigation Menu**: Hidden from the UI
   - File: `/infoflow/web/templates/base.html`
   - Changes: Navigation links commented out using HTML comments

3. **API Endpoints**: Modified to return appropriate error responses
   - File: `/infoflow/web/routes.py`
   - Changes: Return HTTP 503 Service Unavailable with error message
   - Original code is preserved as comments

## Re-enabling the Features

To restore these features, follow these steps:

### 1. Restore Route Handlers

Edit `/infoflow/web/routes.py` and:

1. For the **Guided Scenarios** handlers:
   - Find the functions `guided_scenarios()` and `view_scenario()`
   - Comment out the temporary error return statement
   - Uncomment the original code that was commented out

2. For the **Metrics Dashboard** handler:
   - Find the function `metrics_dashboard()`
   - Comment out the temporary error return statement
   - Uncomment the original code block that was commented out with triple quotes (`"""`)

3. For the **API Endpoints**:
   - Find the functions `api_list_scenarios()`, `api_get_scenario()`, and `generate_metrics_charts()`
   - Comment out the temporary error return statements
   - Uncomment the original code that was commented out

### 2. Restore Navigation Links

Edit `/infoflow/web/templates/base.html` and:

1. Find the navigation menu section
2. Remove the HTML comment markers (`<!-- -->`) around:
   - The Guided Scenarios navigation link
   - The Metrics Dashboard navigation link

## Example: Re-enabling Guided Scenarios

From this:
```python
@bp.route("/guided-scenarios")
def guided_scenarios():
    """Render the guided scenarios page."""
    # Temporarily disabled
    return render_template("error.html", message="Guided scenarios are temporarily unavailable.")
    # Uncomment to re-enable:
    # scenarios = list_scenarios()
    # return render_template("guided_scenarios.html", scenarios=scenarios)
```

To this:
```python
@bp.route("/guided-scenarios")
def guided_scenarios():
    """Render the guided scenarios page."""
    # Temporarily disabled
    # return render_template("error.html", message="Guided scenarios are temporarily unavailable.")
    # Uncomment to re-enable:
    scenarios = list_scenarios()
    return render_template("guided_scenarios.html", scenarios=scenarios)
```

## Verification After Re-enabling

After re-enabling these features, it's recommended to:

1. Restart the Flask server
2. Verify the navigation links appear in the UI
3. Test each feature to ensure it functions correctly:
   - Access the Guided Scenarios page
   - Access the Metrics Dashboard
   - Test relevant API endpoints

If any issues are encountered, check for remaining commented code or indentation errors in the affected files.
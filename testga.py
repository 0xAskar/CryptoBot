import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cedar-shape-448919-t2-87c5269d5fba.json'

# Initialize client
client = BetaAnalyticsDataClient()

# Google Analytics property ID (GA4 property)
property_id = "423666009"

# Define request with valid dimensions and metrics
request_api = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[
        Dimension(name="dateHourMinute"),
        Dimension(name="eventName"),
        Dimension(name="pagePath"),
        Dimension(name="fullPageUrl"),
        Dimension(name="pageLocation"),
        Dimension(name="pageReferrer"),
        Dimension(name="country"),
    ],
    metrics=[
        Metric(name="eventCount"),
        Metric(name="activeUsers"),
        Metric(name="engagedSessions"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration"),
    ],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
)

# Execute the request
response = client.run_report(request_api)

# Sort response rows by dateHourMinute
sorted_rows = sorted(response.rows, 
                    key=lambda row: row.dimension_values[0].value)  # Just sort by dateHourMinute

# Print results
for i, row in enumerate(sorted_rows, 1):
    print(f"#####")
    print(f"link index: {i}")
    print(f"when: {row.dimension_values[0].value}")
    print(f"full url: {row.dimension_values[3].value}")
    print(f"country: {row.dimension_values[6].value}")
    print(f"#####\n")
print(f'TOTAL ROWS: {len(response.rows)}')
"""Constants for the Marginal Child application."""

# PolicyEngine app-v2 design tokens
COLORS = {
    "primary": "#319795",  # Teal-500
    "secondary": "#026AA2",  # Blue-700
    "gray_400": "#9CA3AF",
    "gray_700": "#344054",
    "teal_300": "#4FD1C5",
    "teal_500": "#319795",
    "gradient": ["#9CA3AF", "#81E6D9", "#4FD1C5", "#319795"],  # Gray to teal
}

# Font
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

# Logo
LOGO_URL = "https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/teal.png"

# Calculation parameters
MAX_CHILDREN = 4
INCOME_MIN = 0
INCOME_MAX = 500000
INCOME_STEP = 1000
DEFAULT_CHILD_AGE = 10
DEFAULT_ADULT_AGE = 30

# US States
US_STATES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]

DEFAULT_STATE_INDEX = 43  # Texas

# UK Regions (ITL1)
UK_REGIONS = [
    ("LONDON", "London"),
    ("SOUTH_EAST", "South East"),
    ("SOUTH_WEST", "South West"),
    ("EAST_OF_ENGLAND", "East of England"),
    ("WEST_MIDLANDS", "West Midlands"),
    ("EAST_MIDLANDS", "East Midlands"),
    ("YORKSHIRE", "Yorkshire and the Humber"),
    ("NORTH_WEST", "North West"),
    ("NORTH_EAST", "North East"),
    ("SCOTLAND", "Scotland"),
    ("WALES", "Wales"),
    ("NORTHERN_IRELAND", "Northern Ireland"),
]

DEFAULT_REGION_INDEX = 0  # London

# UK-specific constants
UK_INCOME_MAX = 200000  # £200k max for UK
UK_DEFAULT_RENT = 12000  # £1k/month
UK_DEFAULT_CHILDCARE_PER_CHILD = 12000  # £1,000/month for under-5s full-time nursery
UK_CHILD_AGES = [1, 3, 5]  # Young children needing full-time childcare
UK_PARENT_AGE = 35

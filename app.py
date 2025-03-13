import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import re

# Load data
questions_df = pd.read_excel('Questions.xlsx')
numeric_df = pd.read_excel('Chat Data Numeric.xlsx')
text_df = pd.read_excel('Chat Data Text.xlsx')

# Create a mapping of question IDs to their text
question_mapping = dict(zip(questions_df['Question_ID'], questions_df['Question_Text']))

# Function to analyze text responses and classify as Yes or No
def analyze_text_response(text, question_id):
    if pd.isna(text) or not isinstance(text, str):
        return None, None
    
    text = text.lower().strip()
    
    # Define yes/no patterns
    yes_patterns = [
        r'\byes\b', r'\byeah\b', r'\bep\b', r'\bsure\b', r'\bdefinitely\b', 
        r'\babsolutely\b', r'\bagree\b', r'\bwould\b', r'\bpositive\b', r'\baffirmative\b',
        r'\bi think so\b', r'\bi would\b', r'\bi do\b', r'\bi believe so\b'
    ]
    
    no_patterns = [
        r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bnever\b', r'\bdisagree\b', 
        r'\bwouldn\'t\b', r'\bwould not\b', r'\bnegative\b', r'\bnot\b', 
        r'\bi don\'t\b', r'\bi do not\b', r'\bi wouldn\'t\b', r'\bi would not\b'
    ]
    
    # Question-specific context analysis
    if question_id == 'Q8':  # Is curry a soup?
        # Additional context for curry question
        yes_contexts = [
            r'is a soup', r'type of soup', r'soup-like', r'similar to soup', 
            r'considered a soup', r'classified as soup', r'soup category'
        ]
        no_contexts = [
            r'not a soup', r'isn\'t a soup', r'is not a soup', r'different from soup',
            r'stew', r'sauce', r'dish', r'not soup', r'wouldn\'t classify'
        ]
    elif question_id == 'Q9':  # Is pizza crust-to-crust a sandwich?
        # Additional context for pizza sandwich question
        yes_contexts = [
            r'is a sandwich', r'sandwich-like', r'would be a sandwich', 
            r'technically a sandwich', r'fits the definition', r'meets the criteria'
        ]
        no_contexts = [
            r'not a sandwich', r'isn\'t a sandwich', r'is not a sandwich', 
            r'wouldn\'t be a sandwich', r'would not be a sandwich', r'just pizza'
        ]
    else:
        yes_contexts = []
        no_contexts = []
    
    # Check for direct yes/no answers
    is_yes = any(re.search(pattern, text) for pattern in yes_patterns)
    is_no = any(re.search(pattern, text) for pattern in no_patterns)
    
    # Check for contextual clues
    context_yes = any(re.search(pattern, text) for pattern in yes_contexts)
    context_no = any(re.search(pattern, text) for pattern in no_contexts)
    
    # Determine the final classification
    if (is_yes and not is_no) or (context_yes and not context_no):
        return "Yes", "✅"
    elif (is_no and not is_yes) or (context_no and not context_yes):
        return "No", "❌"
    elif "it depends" in text or "depends" in text:
        return "It depends", "🤔"
    else:
        # For ambiguous responses, do a more detailed analysis
        if question_id == 'Q8':
            if any(word in text for word in ['stew', 'sauce', 'dish', 'not liquid enough']):
                return "No", "❌"
            elif any(word in text for word in ['liquid', 'broth', 'bowl']):
                return "Yes", "✅"
        elif question_id == 'Q9':
            if any(word in text for word in ['bread', 'filling', 'between']):
                return "Yes", "✅"
            elif any(word in text for word in ['still pizza', 'just pizza', 'not bread']):
                return "No", "❌"
        
        # If still ambiguous, make a best guess based on the overall tone
        yes_score = sum(1 for pattern in yes_patterns + yes_contexts if re.search(pattern, text))
        no_score = sum(1 for pattern in no_patterns + no_contexts if re.search(pattern, text))
        
        if yes_score > no_score:
            return "Yes", "✅"
        elif no_score > yes_score:
            return "No", "❌"
        else:
            return "Ambiguous", "❓"

# Process text responses for Q8 and Q9
for question_id in ['Q8', 'Q9']:
    text_column = f"{question_id}_text"
    if text_column in text_df.columns:
        # Create new columns for classification and emoji
        classification_column = f"{question_id}_classification"
        emoji_column = f"{question_id}_emoji"
        
        # Apply the analysis function to each text response
        classifications = []
        emojis = []
        
        for text in text_df[text_column]:
            classification, emoji = analyze_text_response(text, question_id)
            classifications.append(classification)
            emojis.append(emoji)
        
        text_df[classification_column] = classifications
        text_df[emoji_column] = emojis

# Create a mapping for demographic variables
demographic_mappings = {
    'GENDER': {
        1: 'Male',
        2: 'Female',
        'Male': 'Male',
        'Female': 'Female'
    },
    'REGION': {
        1: 'ATL',
        2: 'QC',
        3: 'ON',
        4: 'MB',
        5: 'SK',
        6: 'AB',
        7: 'BC',
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'ON': 'Ontario',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'ATL': 'Atlantic Provinces'
    },
    'REGION_DISPLAY': {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'ON': 'Ontario',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'ATL': 'Atlantic Provinces'
    },
    'EDUCATION': {
        1: 'Elementary/High School (Partial)',
        2: 'High School Graduate',
        3: 'College/Trade School (Partial)',
        4: 'College/Trade School Graduate',
        5: 'University (Partial)',
        6: 'Bachelor\'s Degree',
        7: 'Graduate Degree (Master\'s/PhD)',
        'Some elementary or high school': 'Elementary/High School (Partial)',
        'High school graduate': 'High School Graduate',
        'Some college/trade school': 'College/Trade School (Partial)',
        'Graduated from college/trade school': 'College/Trade School Graduate',
        'Some university': 'University (Partial)',
        'University undergraduate degree, such as a bachelor\'s degree': 'Bachelor\'s Degree',
        'University graduate degree, such as a master\'s or PhD': 'Graduate Degree (Master\'s/PhD)'
    },
    'EDUCATION_ORDER': [
        'Elementary/High School (Partial)',
        'High School Graduate',
        'College/Trade School (Partial)',
        'College/Trade School Graduate',
        'University (Partial)',
        'Bachelor\'s Degree',
        'Graduate Degree (Master\'s/PhD)'
    ],
    'HHINCOME': {
        1: 'Under $25,000',
        2: '$25,000 to less than $50,000',
        3: '$50,000 to less than $100,000',
        4: '$100,000 to less than $150,000',
        5: '$150,000 to less than $200,000',
        6: 'Over $200,000',
        7: 'Don\'t know / Rather not say',
        'Under $25,000': 'Under $25,000',
        '$25,000 to less than $50,000': '$25,000 to less than $50,000',
        '$50,000 to less than $100,000': '$50,000 to less than $100,000',
        '$100,000 to less than $150,000': '$100,000 to less than $150,000',
        '$150,000 to less than $200,000': '$150,000 to less than $200,000',
        'Over $200,000': 'Over $200,000',
        'Don\'t know / Rather not say': 'Don\'t know / Rather not say'
    },
    'HHINCOME_ORDER': [
        'Under $25,000',
        '$25,000 to less than $50,000',
        '$50,000 to less than $100,000',
        '$100,000 to less than $150,000',
        '$150,000 to less than $200,000',
        'Over $200,000',
        'Don\'t know / Rather not say'
    ],
    'AGE_GROUP_ORDER': [
        'Under 18',
        '18-24',
        '25-29',
        '30-34',
        '35-39',
        '40-44',
        '45-49',
        '50-54',
        '55-59',
        '60-64',
        '65-69',
        '70-74',
        '75+'
    ],
    'ETHNICITYROLL23': {
        1: 'First Nations',
        2: 'White',
        3: 'South Asian',
        4: 'Chinese',
        5: 'Black',
        6: 'Filipino',
        7: 'Arab/West Asian',
        8: 'Latin American',
        9: 'Southeast Asian',
        10: 'East Asian',
        11: 'Multiple visible minorities',
        'White': 'White',
        'Black': 'Black',
        'Chinese': 'Chinese',
        'South Asian': 'South Asian',
        'East Asian': 'East Asian',
        'Southeast Asian': 'Southeast Asian',
        'Filipino': 'Filipino',
        'Latin American': 'Latin American',
        'Arab/West Asian': 'Arab/West Asian',
        'First Nations': 'First Nations',
        'Multiple visible minorities': 'Multiple visible minorities'
    },
    'PMARITALSTATUS': {
        1: 'Single, never married',
        2: 'Married',
        3: 'Common law',
        4: 'Separated',
        5: 'Widowed',
        6: 'Divorced',
        'Married': 'Married',
        'Single, never married': 'Single, never married',
        'Divorced': 'Divorced',
        'Separated': 'Separated',
        'Widowed': 'Widowed',
        'Common law': 'Common law'
    }
}

# Convert text demographic values to be consistent with numeric_df
for col in ['GENDER', 'REGION', 'EDUCATION', 'HHINCOME', 'ETHNICITYROLL23', 'PMARITALSTATUS']:
    if col in text_df.columns:
        text_df[col] = text_df[col].map(lambda x: demographic_mappings[col].get(x, x))

# Convert numeric demographic codes to text labels in numeric_df
for col in ['GENDER', 'REGION', 'EDUCATION', 'HHINCOME', 'ETHNICITYROLL23', 'PMARITALSTATUS']:
    if col in numeric_df.columns:
        numeric_df[col] = numeric_df[col].map(lambda x: demographic_mappings[col].get(x, x))

# Create age groups
numeric_df['AGE_GROUP'] = pd.cut(
    numeric_df['AGE'], 
    bins=[0, 18, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 100],
    labels=['Under 18', '18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75+']
)

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP])
server = app.server

# Custom CSS for better styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Survey Data Visualization Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .dashboard-container {
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .filter-card {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                height: 100%;
            }
            .dashboard-title {
                color: #2C3E50;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .dashboard-subtitle {
                color: #7b8a8b;
                margin-bottom: 25px;
            }
            .section-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #2C3E50;
                border-bottom: 2px solid #18BC9C;
                padding-bottom: 8px;
                margin-bottom: 15px;
            }
            .filter-label {
                font-weight: 500;
                color: #2C3E50;
                margin-bottom: 5px;
            }
            .apply-button {
                background-color: #18BC9C;
                border-color: #18BC9C;
                font-weight: 500;
                transition: all 0.3s;
            }
            .apply-button:hover {
                background-color: #128f76;
                border-color: #128f76;
            }
            .question-box {
                background-color: #f8f9fa;
                border-left: 4px solid #18BC9C;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .dash-dropdown {
                border-radius: 4px;
            }
            .response-card {
                border-radius: 8px;
                margin-bottom: 10px;
                transition: all 0.2s;
            }
            .response-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            /* Custom styles for dropdown menus */
            .Select-menu-outer {
                max-height: 400px !important;
            }
            .Select-menu {
                max-height: 398px !important;
            }
            .Select-option {
                padding: 12px 12px !important;
                border-bottom: 1px solid #f0f0f0;
            }
            .Select-option:hover {
                background-color: #f8f9fa !important;
            }
            .Select-value-label {
                font-size: 14px !important;
                line-height: 1.5 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Survey Data Visualization Dashboard", className="dashboard-title text-center my-4"),
            html.P("Explore and analyze survey responses with interactive visualizations", className="dashboard-subtitle text-center mb-4")
        ])
    ]),
    
    dbc.Row([
        # Left sidebar for filters
        dbc.Col([
            html.Div([
                html.H4("Filters", className="section-title"),
                
                html.Div([
                    html.H5("Question Selection", className="filter-label mt-3"),
                    dcc.Dropdown(
                        id='question-dropdown',
                        options=[
                            {'label': 'Q1: Is a hot dog a sandwich?', 'value': 'Q1'},
                            {'label': 'Q2: Does a ripped hot dog bun become a sandwich?', 'value': 'Q2'},
                            {'label': 'Q3: Minimum ingredients for a sandwich', 'value': 'Q3'},
                            {'label': 'Q4: When is a taco considered a sandwich?', 'value': 'Q4'},
                            {'label': 'Q5: Most important characteristic of soup', 'value': 'Q5'},
                            {'label': 'Q6: Is cereal with milk a type of soup?', 'value': 'Q6'},
                            {'label': 'Q7: Open-faced vs. regular sandwich preference', 'value': 'Q7'},
                            {'label': 'Q8: Is curry a soup?', 'value': 'Q8'},
                            {'label': 'Q9: Is folded pizza a sandwich?', 'value': 'Q9'},
                            {'label': 'Q10: Importance of chef\'s intent for sandwiches', 'value': 'Q10'}
                        ],
                        value='Q1',
                        clearable=False,
                        className="mb-3",
                        style={'lineHeight': '1.5', 'fontSize': '14px'}
                    ),
                    
                    html.H5("Demographics", className="filter-label mt-3"),
                    
                    html.Label("Age Group", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='age-group-dropdown',
                        options=[{'label': age_group, 'value': age_group} 
                                for age_group in sorted(numeric_df['AGE_GROUP'].unique()) if pd.notna(age_group)],
                        multi=True,
                        placeholder="Select age groups...",
                        className="mb-2"
                    ),
                    
                    html.Label("Gender", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='gender-dropdown',
                        options=[{'label': gender, 'value': gender} 
                                for gender in sorted(numeric_df['GENDER'].unique()) if pd.notna(gender)],
                        multi=True,
                        placeholder="Select genders...",
                        className="mb-2"
                    ),
                    
                    html.Label("Region", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='region-dropdown',
                        options=[{'label': demographic_mappings['REGION_DISPLAY'].get(region, region), 'value': region} 
                                for region in sorted(numeric_df['REGION'].unique()) if pd.notna(region)],
                        multi=True,
                        placeholder="Select regions...",
                        className="mb-2"
                    ),
                    
                    html.Label("Education", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='education-dropdown',
                        options=[{'label': education, 'value': education} 
                                for education in demographic_mappings['EDUCATION_ORDER'] 
                                if education in numeric_df['EDUCATION'].unique()],
                        multi=True,
                        placeholder="Select education levels...",
                        className="mb-2"
                    ),
                    
                    html.Label("Household Income", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='income-dropdown',
                        options=[{'label': income, 'value': income} 
                                for income in demographic_mappings['HHINCOME_ORDER'] 
                                if income in numeric_df['HHINCOME'].unique()],
                        multi=True,
                        placeholder="Select income ranges...",
                        className="mb-2"
                    ),
                    
                    html.Label("Ethnicity", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='ethnicity-dropdown',
                        options=[{'label': ethnicity, 'value': ethnicity} 
                                for ethnicity in sorted(numeric_df['ETHNICITYROLL23'].unique()) if pd.notna(ethnicity)],
                        multi=True,
                        placeholder="Select ethnicities...",
                        className="mb-2"
                    ),
                    
                    html.Label("Marital Status", className="filter-label mt-2"),
                    dcc.Dropdown(
                        id='marital-dropdown',
                        options=[{'label': status, 'value': status} 
                                for status in sorted(numeric_df['PMARITALSTATUS'].unique()) if pd.notna(status)],
                        multi=True,
                        placeholder="Select marital statuses...",
                        className="mb-3"
                    ),
                    
                    html.Button(
                        [html.I(className="bi bi-funnel me-2"), "Apply Filters"], 
                        id='apply-button', 
                        className="btn btn-primary apply-button mt-3 w-100"
                    )
                ])
            ], className="filter-card")
        ], width=3, className="mb-4"),
        
        # Right side for visualization
        dbc.Col([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4("Visualization Options", className="section-title"),
                        html.Label("Chart Type", className="filter-label"),
                        dcc.Dropdown(
                            id='chart-type-dropdown',
                            options=[
                                {'label': 'Bar Chart', 'value': 'bar'},
                                {'label': 'Pie Chart', 'value': 'pie'},
                                {'label': 'Donut Chart', 'value': 'donut'},
                                {'label': 'Horizontal Bar Chart', 'value': 'hbar'},
                                {'label': 'Stacked Bar Chart', 'value': 'stacked_bar'}
                            ],
                            value='bar',
                            clearable=False
                        )
                    ], width=6),
                    
                    dbc.Col([
                        html.H4("Secondary Filter", className="section-title"),
                        html.Label("Group By", className="filter-label"),
                        dcc.Dropdown(
                            id='group-by-dropdown',
                            options=[
                                {'label': 'None', 'value': 'none'},
                                {'label': 'Age Group', 'value': 'AGE_GROUP'},
                                {'label': 'Gender', 'value': 'GENDER'},
                                {'label': 'Region', 'value': 'REGION'},
                                {'label': 'Education', 'value': 'EDUCATION'},
                                {'label': 'Income', 'value': 'HHINCOME'},
                                {'label': 'Ethnicity', 'value': 'ETHNICITYROLL23'},
                                {'label': 'Marital Status', 'value': 'PMARITALSTATUS'}
                            ],
                            value='none',
                            clearable=False
                        )
                    ], width=6)
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        html.Div(id='question-text', className="question-box")
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='visualization-graph', style={'height': '50vh'}, className="shadow-sm")
                    ])
                ]),
                
                # Text responses section
                dbc.Row([
                    dbc.Col([
                        html.Div(id='text-responses-section', className="mt-4")
                    ])
                ])
            ], className="dashboard-container")
        ], width=9)
    ])
], fluid=True, className="px-4 py-3")

# Define callback to update the question text
@app.callback(
    Output('question-text', 'children'),
    Input('question-dropdown', 'value')
)
def update_question_text(question_id):
    if question_id in question_mapping:
        question_text = question_mapping[question_id]
        
        # Format the question display based on question ID
        if question_id == 'Q1':
            return html.Div([
                html.H5("Question 1:", className="mb-2 fw-bold"),
                html.P("Is a hot dog a sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("Yes"),
                    html.Li("No"),
                    html.Li("It depends"),
                    html.Li("I refuse to answer")
                ], className="ms-4")
            ])
        elif question_id == 'Q2':
            return html.Div([
                html.H5("Question 2:", className="mb-2 fw-bold"),
                html.P("If the bottom of a hot dog bun rips, does it become a sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("Yes"),
                    html.Li("No")
                ], className="ms-4")
            ])
        elif question_id == 'Q3':
            return html.Div([
                html.H5("Question 3:", className="mb-2 fw-bold"),
                html.P("What is the minimum number of ingredients required for something to be considered a sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("0 (bread is a sandwich by itself)"),
                    html.Li("1 (e.g. buttered toast)"),
                    html.Li("2 (e.g. PB&J)"),
                    html.Li("3 or more")
                ], className="ms-4")
            ])
        elif question_id == 'Q4':
            return html.Div([
                html.H5("Question 4:", className="mb-2 fw-bold"),
                html.P("Is a taco more likely to be considered a sandwich in which of the following scenarios?", className="mb-3"),
                html.Ul([
                    html.Li("Hard shell"),
                    html.Li("Soft shell"),
                    html.Li("Only if the bottom cracks or rips"),
                    html.Li("Under no conditions should a taco be considered a sandwich")
                ], className="ms-4")
            ])
        elif question_id == 'Q5':
            return html.Div([
                html.H5("Question 5:", className="mb-2 fw-bold"),
                html.P("What is the most important characteristic for something to be considered soup?", className="mb-3"),
                html.Ul([
                    html.Li("The broth"),
                    html.Li("The consistency"),
                    html.Li("The way it's served"),
                    html.Li("The primary flavour profile"),
                    html.Li("Something else")
                ], className="ms-4")
            ])
        elif question_id == 'Q6':
            return html.Div([
                html.H5("Question 6:", className="mb-2 fw-bold"),
                html.P("Is cereal with milk a type of soup?", className="mb-3"),
                html.Ul([
                    html.Li("Yes"),
                    html.Li("No"),
                    html.Li("It depends")
                ], className="ms-4")
            ])
        elif question_id == 'Q7':
            return html.Div([
                html.H5("Question 7:", className="mb-2 fw-bold"),
                html.P("How likely are you to order an open-faced sandwich compared to a regular sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("Much more"),
                    html.Li("A little more"),
                    html.Li("It makes no difference"),
                    html.Li("A little less"),
                    html.Li("Much less")
                ], className="ms-4")
            ])
        elif question_id == 'Q8':
            return html.Div([
                html.H5("Question 8:", className="mb-2 fw-bold"),
                html.P("Is curry a soup?", className="mb-3"),
                html.Ul([
                    html.Li("Yes"),
                    html.Li("No"),
                    html.Li("It depends")
                ], className="ms-4")
            ])
        elif question_id == 'Q9':
            return html.Div([
                html.H5("Question 9:", className="mb-2 fw-bold"),
                html.P("Is a pizza folded crust-to-crust a sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("Yes"),
                    html.Li("No"),
                    html.Li("It depends")
                ], className="ms-4")
            ])
        elif question_id == 'Q10':
            return html.Div([
                html.H5("Question 10:", className="mb-2 fw-bold"),
                html.P("How important is the chef's intent when determining if something is a sandwich?", className="mb-3"),
                html.Ul([
                    html.Li("0 - Not at all"),
                    html.Li("1"),
                    html.Li("2"),
                    html.Li("3"),
                    html.Li("4"),
                    html.Li("5 - It's the only thing that matters")
                ], className="ms-4")
            ])
        else:
            return f"Question: {question_text}"
    return "Select a question"

# Define callback to update the text responses section
@app.callback(
    Output('text-responses-section', 'children'),
    [Input('apply-button', 'n_clicks'),
     Input('question-dropdown', 'value')],
    [State('age-group-dropdown', 'value'),
     State('gender-dropdown', 'value'),
     State('region-dropdown', 'value'),
     State('education-dropdown', 'value'),
     State('income-dropdown', 'value'),
     State('ethnicity-dropdown', 'value'),
     State('marital-dropdown', 'value')]
)
def update_text_responses(n_clicks, question_id, age_groups, genders, regions, educations, incomes, ethnicities, marital_statuses):
    # Only show text responses for Q8 and Q9
    if question_id not in ['Q8', 'Q9']:
        return html.Div()
    
    # Get the text column for the selected question
    text_column = f"{question_id}_text"
    classification_column = f"{question_id}_classification"
    emoji_column = f"{question_id}_emoji"
    
    if text_column not in text_df.columns:
        return html.Div([
            html.H4("Text Responses", className="section-title mt-3"),
            html.P("No text responses available for this question.", className="text-muted")
        ])
    
    # Start with the full dataset
    filtered_df = text_df.copy()
    
    # Apply demographic filters if they are selected
    if age_groups and len(age_groups) > 0:
        # Create age groups in text_df
        filtered_df['AGE_GROUP'] = pd.cut(
            filtered_df['AGE'], 
            bins=[0, 18, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 100],
            labels=['Under 18', '18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75+']
        )
        filtered_df = filtered_df[filtered_df['AGE_GROUP'].isin(age_groups)]
    
    if genders and len(genders) > 0:
        filtered_df = filtered_df[filtered_df['GENDER'].isin(genders)]
    
    if regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df['REGION'].isin(regions)]
    
    if educations and len(educations) > 0:
        filtered_df = filtered_df[filtered_df['EDUCATION'].isin(educations)]
    
    if incomes and len(incomes) > 0:
        filtered_df = filtered_df[filtered_df['HHINCOME'].isin(incomes)]
    
    if ethnicities and len(ethnicities) > 0:
        filtered_df = filtered_df[filtered_df['ETHNICITYROLL23'].isin(ethnicities)]
    
    if marital_statuses and len(marital_statuses) > 0:
        filtered_df = filtered_df[filtered_df['PMARITALSTATUS'].isin(marital_statuses)]
    
    # Get text responses with classifications and emojis
    responses_df = filtered_df[[text_column, classification_column, emoji_column]].dropna(subset=[text_column])
    
    if responses_df.empty:
        return html.Div([
            html.H4("Text Responses", className="section-title mt-3"),
            html.P("No text responses available for the selected filters.", className="text-muted")
        ])
    
    # Create a summary of Yes/No responses
    yes_count = sum(responses_df[classification_column] == "Yes")
    no_count = sum(responses_df[classification_column] == "No")
    depends_count = sum(responses_df[classification_column] == "It depends")
    ambiguous_count = sum(responses_df[classification_column] == "Ambiguous")
    other_count = len(responses_df) - yes_count - no_count - depends_count - ambiguous_count
    
    # Create a summary table with improved styling
    summary_table = html.Div([
        html.Div([
            html.Div([
                html.Div("Response Type", className="fw-bold", style={'flex': '40%', 'textAlign': 'left'}),
                html.Div("Count", className="fw-bold", style={'flex': '30%', 'textAlign': 'center'}),
                html.Div("Percentage", className="fw-bold", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#f2f2f2', 'borderRadius': '6px 6px 0 0'}),
            
            html.Div([
                html.Div([html.Span("Yes "), html.Span("✅", style={'fontSize': '1.2em'})], style={'flex': '40%'}),
                html.Div(yes_count, style={'flex': '30%', 'textAlign': 'center'}),
                html.Div(f"{yes_count / len(responses_df) * 100:.1f}%", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#e6ffe6'}),
            
            html.Div([
                html.Div([html.Span("No "), html.Span("❌", style={'fontSize': '1.2em'})], style={'flex': '40%'}),
                html.Div(no_count, style={'flex': '30%', 'textAlign': 'center'}),
                html.Div(f"{no_count / len(responses_df) * 100:.1f}%", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#ffe6e6'}),
            
            html.Div([
                html.Div([html.Span("It depends "), html.Span("🤔", style={'fontSize': '1.2em'})], style={'flex': '40%'}),
                html.Div(depends_count, style={'flex': '30%', 'textAlign': 'center'}),
                html.Div(f"{depends_count / len(responses_df) * 100:.1f}%", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#fff9e6'}),
            
            html.Div([
                html.Div([html.Span("Ambiguous "), html.Span("❓", style={'fontSize': '1.2em'})], style={'flex': '40%'}),
                html.Div(ambiguous_count, style={'flex': '30%', 'textAlign': 'center'}),
                html.Div(f"{ambiguous_count / len(responses_df) * 100:.1f}%", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#f2f2f2'}),
            
            html.Div([
                html.Div([html.Span("Other "), html.Span("⚪", style={'fontSize': '1.2em'})], style={'flex': '40%'}),
                html.Div(other_count, style={'flex': '30%', 'textAlign': 'center'}),
                html.Div(f"{other_count / len(responses_df) * 100:.1f}%", style={'flex': '30%', 'textAlign': 'center'})
            ], className="d-flex p-2", style={'backgroundColor': '#f9f9f9', 'borderRadius': '0 0 6px 6px'})
        ], className="mb-4", style={'border': '1px solid #ddd', 'borderRadius': '6px', 'overflow': 'hidden'})
    ])
    
    # Create a list of text responses with classification badges
    list_items = []
    for _, row in responses_df.iterrows():
        response = row[text_column]
        classification = row[classification_column]
        emoji = row[emoji_column]
        
        # Choose badge color based on classification
        badge_color = {
            'Yes': 'success',
            'No': 'danger',
            'It depends': 'warning',
            'Ambiguous': 'secondary',
            None: 'light'
        }.get(classification, 'info')
        
        list_items.append(
            html.Div([
                html.Div([
                    html.Span(f"{emoji} ", className="me-2", style={'fontSize': '1.2em'}),
                    html.Span(response, className="text-wrap"),
                    html.Span(" "),
                    dbc.Badge(classification, color=badge_color, className="ms-2")
                ], className="p-3")
            ], className="response-card mb-2", style={'backgroundColor': 'white', 'border': '1px solid #eee'})
        )
    
    # Show all responses in a scrollable container with improved styling
    return html.Div([
        html.Div([
            html.H4("AI Analysis of Text Responses", className="section-title mt-3 mb-4"),
            html.Div([
                html.H5("Summary", className="filter-label mb-3"),
                summary_table,
                html.H5(f"Individual Responses ({len(list_items)})", className="filter-label mb-3"),
                html.Div([
                    html.Div(list_items)
                ], style={'maxHeight': '500px', 'overflowY': 'auto', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '6px'})
            ])
        ], className="dashboard-container")
    ])

# Define callback to update the visualization
@app.callback(
    Output('visualization-graph', 'figure'),
    Input('apply-button', 'n_clicks'),
    State('question-dropdown', 'value'),
    State('age-group-dropdown', 'value'),
    State('gender-dropdown', 'value'),
    State('region-dropdown', 'value'),
    State('education-dropdown', 'value'),
    State('income-dropdown', 'value'),
    State('ethnicity-dropdown', 'value'),
    State('marital-dropdown', 'value'),
    State('chart-type-dropdown', 'value'),
    State('group-by-dropdown', 'value')
)
def update_visualization(n_clicks, question_id, age_groups, genders, regions, educations, incomes, ethnicities, marital_statuses, chart_type, group_by):
    # Start with the full dataset
    filtered_df = numeric_df.copy()
    
    # Apply demographic filters if they are selected
    if age_groups and len(age_groups) > 0:
        filtered_df = filtered_df[filtered_df['AGE_GROUP'].isin(age_groups)]
    
    if genders and len(genders) > 0:
        filtered_df = filtered_df[filtered_df['GENDER'].isin(genders)]
    
    if regions and len(regions) > 0:
        # For numeric_df, we need to map region codes to region names for filtering
        filtered_df = filtered_df[filtered_df['REGION'].isin(regions)]
    
    if educations and len(educations) > 0:
        filtered_df = filtered_df[filtered_df['EDUCATION'].isin(educations)]
    
    if incomes and len(incomes) > 0:
        filtered_df = filtered_df[filtered_df['HHINCOME'].isin(incomes)]
    
    if ethnicities and len(ethnicities) > 0:
        filtered_df = filtered_df[filtered_df['ETHNICITYROLL23'].isin(ethnicities)]
    
    if marital_statuses and len(marital_statuses) > 0:
        filtered_df = filtered_df[filtered_df['PMARITALSTATUS'].isin(marital_statuses)]
    
    # For Q8 and Q9, use the AI classification results
    if question_id in ['Q8', 'Q9']:
        # Get the filtered text data with classifications
        filtered_text_df = text_df.copy()
        
        # Apply the same demographic filters
        if age_groups and len(age_groups) > 0:
            filtered_text_df['AGE_GROUP'] = pd.cut(
                filtered_text_df['AGE'], 
                bins=[0, 18, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 100],
                labels=['Under 18', '18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75+']
            )
            filtered_text_df = filtered_text_df[filtered_text_df['AGE_GROUP'].isin(age_groups)]
        
        if genders and len(genders) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['GENDER'].isin(genders)]
        
        if regions and len(regions) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['REGION'].isin(regions)]
        
        if educations and len(educations) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['EDUCATION'].isin(educations)]
        
        if incomes and len(incomes) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['HHINCOME'].isin(incomes)]
        
        if ethnicities and len(ethnicities) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['ETHNICITYROLL23'].isin(ethnicities)]
        
        if marital_statuses and len(marital_statuses) > 0:
            filtered_text_df = filtered_text_df[filtered_text_df['PMARITALSTATUS'].isin(marital_statuses)]
        
        classification_column = f"{question_id}_classification"
        
        if classification_column in filtered_text_df.columns:
            # Filter out rows with None or NaN classifications
            filtered_text_df = filtered_text_df.dropna(subset=[classification_column])
            
            # If there's no data after filtering, show an empty chart with a message
            if filtered_text_df.empty:
                return go.Figure().update_layout(
                    title=f"No data available for {question_id} with the selected filters",
                    xaxis_title="No data available",
                    yaxis_title="Count",
                    annotations=[{
                        'text': "No data available for the selected filters",
                        'showarrow': False,
                        'font': {'size': 16}
                    }]
                )
            
            if group_by != 'none':
                # Group by classification and the selected demographic
                if group_by == 'AGE_GROUP':
                    # Create age groups if not already created
                    if 'AGE_GROUP' not in filtered_text_df.columns:
                        filtered_text_df['AGE_GROUP'] = pd.cut(
                            filtered_text_df['AGE'], 
                            bins=[0, 18, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 100],
                            labels=['Under 18', '18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75+']
                        )
                    # For age group, use the ordered list from demographic_mappings
                    grouped_data = filtered_text_df.groupby([classification_column, group_by], observed=True).size().reset_index(name='count')
                    # Create a categorical type with the ordered age groups
                    age_order = pd.CategoricalDtype(categories=demographic_mappings['AGE_GROUP_ORDER'], ordered=True)
                    grouped_data[group_by] = pd.Categorical(grouped_data[group_by], categories=age_order.categories, ordered=True)
                    # Sort by the age order
                    grouped_data = grouped_data.sort_values(group_by)
                elif group_by == 'EDUCATION':
                    # For education, use the ordered list from demographic_mappings
                    grouped_data = filtered_text_df.groupby([classification_column, group_by], observed=True).size().reset_index(name='count')
                    # Create a categorical type with the ordered education levels
                    education_order = pd.CategoricalDtype(categories=demographic_mappings['EDUCATION_ORDER'], ordered=True)
                    grouped_data[group_by] = pd.Categorical(grouped_data[group_by], categories=education_order.categories, ordered=True)
                    # Sort by the education order
                    grouped_data = grouped_data.sort_values(group_by)
                elif group_by == 'HHINCOME':
                    # For income, use the ordered list from demographic_mappings
                    grouped_data = filtered_text_df.groupby([classification_column, group_by], observed=True).size().reset_index(name='count')
                    # Create a categorical type with the ordered income levels
                    income_order = pd.CategoricalDtype(categories=demographic_mappings['HHINCOME_ORDER'], ordered=True)
                    grouped_data[group_by] = pd.Categorical(grouped_data[group_by], categories=income_order.categories, ordered=True)
                    # Sort by the income order
                    grouped_data = grouped_data.sort_values(group_by)
                else:
                    # For other demographics, group by the values directly
                    grouped_data = filtered_text_df.groupby([classification_column, group_by], observed=True).size().reset_index(name='count')
                    # Use the display labels for regions if needed
                    if group_by == 'REGION':
                        grouped_data[group_by] = grouped_data[group_by].map(lambda x: demographic_mappings['REGION_DISPLAY'].get(x, x))
                
                # Create the visualization based on chart type
                if chart_type == 'bar':
                    fig = px.bar(grouped_data, x=classification_column, y='count', color=group_by,
                                barmode='group', title=f"AI Classification for {question_id}")
                elif chart_type == 'stacked_bar':
                    fig = px.bar(grouped_data, x=classification_column, y='count', color=group_by,
                                barmode='stack', title=f"AI Classification for {question_id}")
                elif chart_type == 'hbar':
                    fig = px.bar(grouped_data, y=classification_column, x='count', color=group_by,
                                barmode='group', orientation='h', title=f"AI Classification for {question_id}")
                else:  # pie or donut
                    # For pie/donut with grouping, we'll create a faceted plot
                    fig = px.pie(grouped_data, values='count', names=classification_column, facet_col=group_by,
                                title=f"AI Classification for {question_id}")
                    if chart_type == 'donut':
                        fig.update_traces(hole=0.4)
            else:
                # No grouping, just count by classification
                classification_counts = filtered_text_df[classification_column].value_counts().reset_index()
                classification_counts.columns = [classification_column, 'count']
                
                # Add emojis to the classification labels
                emoji_map = {'Yes': '✅ Yes', 'No': '❌ No', 'It depends': '🤔 It depends', 'Ambiguous': '❓ Ambiguous'}
                classification_counts[classification_column] = classification_counts[classification_column].map(
                    lambda x: emoji_map.get(x, x)
                )
                
                if chart_type == 'bar':
                    fig = px.bar(classification_counts, x=classification_column, y='count',
                                title=f"AI Classification for {question_id}")
                elif chart_type == 'hbar':
                    fig = px.bar(classification_counts, y=classification_column, x='count', orientation='h',
                                title=f"AI Classification for {question_id}")
                elif chart_type == 'pie':
                    fig = px.pie(classification_counts, values='count', names=classification_column,
                                title=f"AI Classification for {question_id}")
                elif chart_type == 'donut':
                    fig = px.pie(classification_counts, values='count', names=classification_column,
                                title=f"AI Classification for {question_id}", hole=0.4)
                else:  # stacked_bar (falls back to regular bar for no grouping)
                    fig = px.bar(classification_counts, x=classification_column, y='count',
                                title=f"AI Classification for {question_id}")
            
            # Update layout for better appearance
            fig.update_layout(
                title_x=0.5,
                margin=dict(l=50, r=50, t=80, b=50),
                legend_title_text='Legend',
                plot_bgcolor='rgba(0,0,0,0.05)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            return fig
    
    # For other questions, use the original visualization logic
    # Check if the question exists in the dataset
    if question_id not in filtered_df.columns:
        return go.Figure().update_layout(
            title=f"Question {question_id} data not found",
            xaxis_title="No data available",
            yaxis_title="Count"
        )
    
    # Create a mapping for answer values if needed
    answer_mapping = {}
    
    # For Q1 (Is a hot dog a sandwich?)
    if question_id == 'Q1':
        answer_mapping = {1: 'Yes', 2: 'No', 3: 'It depends', 4: 'I refuse to answer'}
    # For Q2 (If the bottom of a hot dog bun rips...)
    elif question_id == 'Q2':
        answer_mapping = {1: 'Yes', 2: 'No'}
    # For Q3 (Minimum number of ingredients...)
    elif question_id == 'Q3':
        answer_mapping = {1: '0 (bread is a sandwich by itself)', 2: '1 (e.g. buttered toast)', 
                         3: '2 (e.g. PB&J)', 4: '3 or more'}
    # For Q4 (Is a taco more likely to be considered a sandwich...)
    elif question_id == 'Q4':
        answer_mapping = {1: 'Hard shell', 2: 'Soft shell', 3: 'Only if the bottom cracks or rips', 
                         4: 'Under no conditions should a taco be considered a sandwich'}
    # For Q5 (Most important characteristic for soup...)
    elif question_id == 'Q5':
        answer_mapping = {1: 'The broth', 2: 'The consistency', 3: 'The way it\'s served', 
                         4: 'The primary flavour profile', 5: 'Something else'}
    # For Q6 (Is cereal with milk a type of soup?)
    elif question_id == 'Q6':
        answer_mapping = {1: 'Yes', 2: 'No', 3: 'It depends'}
    # For Q7 (Open-faced sandwich ordering likelihood...)
    elif question_id == 'Q7':
        answer_mapping = {1: 'Much more', 2: 'A little more', 3: 'It makes no difference', 
                         4: 'A little less', 5: 'Much less'}
    # For Q10 (Chef's intent importance...)
    elif question_id == 'Q10':
        answer_mapping = {1: '0 - Not at all', 2: '1', 3: '2', 4: '3', 5: '4', 6: '5 - It\'s the only thing that matters'}
    
    # Map the answer values to their text representations if available
    if answer_mapping:
        filtered_df['answer_text'] = filtered_df[question_id].map(answer_mapping)
    else:
        filtered_df['answer_text'] = filtered_df[question_id].astype(str)
    
    if group_by != 'none':
        # Group by answer and the selected demographic
        if group_by == 'AGE_GROUP':
            # For age group, we already have the labels
            grouped_data = filtered_df.groupby(['answer_text', group_by], observed=True).size().reset_index(name='count')
        elif group_by == 'EDUCATION':
            # For education, use the ordered list from demographic_mappings
            grouped_data = filtered_df.groupby(['answer_text', group_by], observed=True).size().reset_index(name='count')
            # Create a categorical type with the ordered education levels
            education_order = pd.CategoricalDtype(categories=demographic_mappings['EDUCATION_ORDER'], ordered=True)
            grouped_data[group_by] = pd.Categorical(grouped_data[group_by], categories=education_order.categories, ordered=True)
            # Sort by the education order
            grouped_data = grouped_data.sort_values(group_by)
        elif group_by == 'HHINCOME':
            # For income, use the ordered list from demographic_mappings
            grouped_data = filtered_df.groupby(['answer_text', group_by], observed=True).size().reset_index(name='count')
            # Create a categorical type with the ordered income levels
            income_order = pd.CategoricalDtype(categories=demographic_mappings['HHINCOME_ORDER'], ordered=True)
            grouped_data[group_by] = pd.Categorical(grouped_data[group_by], categories=income_order.categories, ordered=True)
            # Sort by the income order
            grouped_data = grouped_data.sort_values(group_by)
        else:
            # For other demographics, map the codes to labels
            grouped_data = filtered_df.groupby(['answer_text', group_by], observed=True).size().reset_index(name='count')
            # Map the demographic codes to their display labels
            if group_by in demographic_mappings:
                grouped_data[group_by] = grouped_data[group_by].map(lambda x: demographic_mappings[group_by].get(x, x))
        
        # Create the visualization based on chart type
        if chart_type == 'bar':
            fig = px.bar(grouped_data, x='answer_text', y='count', color=group_by,
                        barmode='group', title=f"Response Distribution for {question_id}")
        elif chart_type == 'stacked_bar':
            fig = px.bar(grouped_data, x='answer_text', y='count', color=group_by,
                        barmode='stack', title=f"Response Distribution for {question_id}")
        elif chart_type == 'hbar':
            fig = px.bar(grouped_data, y='answer_text', x='count', color=group_by,
                        barmode='group', orientation='h', title=f"Response Distribution for {question_id}")
        else:  # pie or donut
            # For pie/donut with grouping, we'll create a faceted plot
            fig = px.pie(grouped_data, values='count', names='answer_text', facet_col=group_by,
                        title=f"Response Distribution for {question_id}")
            if chart_type == 'donut':
                fig.update_traces(hole=0.4)
    else:
        # No grouping, just count by answer
        answer_counts = filtered_df['answer_text'].value_counts().reset_index()
        answer_counts.columns = ['answer_text', 'count']
        
        if chart_type == 'bar':
            fig = px.bar(answer_counts, x='answer_text', y='count',
                        title=f"Response Distribution for {question_id}")
        elif chart_type == 'hbar':
            fig = px.bar(answer_counts, y='answer_text', x='count', orientation='h',
                        title=f"Response Distribution for {question_id}")
        elif chart_type == 'pie':
            fig = px.pie(answer_counts, values='count', names='answer_text',
                        title=f"Response Distribution for {question_id}")
        elif chart_type == 'donut':
            fig = px.pie(answer_counts, values='count', names='answer_text',
                        title=f"Response Distribution for {question_id}", hole=0.4)
        else:  # stacked_bar (falls back to regular bar for no grouping)
            fig = px.bar(answer_counts, x='answer_text', y='count',
                        title=f"Response Distribution for {question_id}")
    
    # Update layout for better appearance
    fig.update_layout(
        title_x=0.5,
        margin=dict(l=50, r=50, t=80, b=50),
        legend_title_text='Legend',
        plot_bgcolor='rgba(0,0,0,0.05)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    # Debug information
    print("=== Numeric DataFrame Columns ===")
    print(numeric_df.columns.tolist())
    print("\n=== Text DataFrame Columns ===")
    print(text_df.columns.tolist())
    
    print("\n=== Numeric DataFrame Data Types ===")
    print(numeric_df.dtypes)
    print("\n=== Text DataFrame Data Types ===")
    print(text_df.dtypes)
    
    print("\n=== Sample of Numeric DataFrame ===")
    print(numeric_df[['AGE_GROUP', 'GENDER', 'REGION', 'EDUCATION', 'HHINCOME', 'ETHNICITYROLL23', 'PMARITALSTATUS']].head())
    
    print("\n=== Sample of Text DataFrame ===")
    print(text_df[['GENDER', 'REGION', 'EDUCATION', 'HHINCOME', 'ETHNICITYROLL23', 'PMARITALSTATUS']].head())
    
    app.run_server(debug=True) 
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load the dataset
df = pd.read_csv(r'C:\Users\anush\OneDrive\Desktop\Softrate Intern\SocialMedia_Influencer_data.csv')

# Data cleaning and preparation
df.dropna(inplace=True)
df['Post_Timestamp'] = pd.to_datetime(df['Post_Timestamp'], errors='coerce')
df['Engagement_Rate'] = (df['Likes'] + df['Comments'] + df['Shares']) / df['Followers']

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'], suppress_callback_exceptions=True)

# Define the layout components
header = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Analysis", href="/analysis")),
    ],
    brand="Influencer Impact Analysis",
    brand_href="/",
    color="primary",
    dark=True,
)

footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.P(
                "© 2024 Social Media Analytics, Inc.",
                className="text-center"
            )
        )
    ),
    fluid=True,
    className="mt-4"
)

home_page = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Welcome to the Social Media Influencer Impact Analysis", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "This application allows you to analyze the impact of social media influencers using various metrics. "
            "Navigate to the Analysis page to explore different visualizations and insights about the engagement rates, "
            "sentiment distribution, collaboration impact, and more."
        ), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Go to Analysis", color="primary", href="/analysis"), className="text-center mb-5")
    ]),
    dbc.Row([
        dbc.Col(html.Div([
            html.H3(""),
            html.Div([
                html.I(className="fas fa-calculator fa-2x"), # Icon
                html.H4("Calculate Brand Impact", className="ml-2")
            ], className="d-flex align-items-center mb-3"),
            html.Div([
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-tag")), # Category icon
                    dbc.Input(id='input-category', type='text', placeholder='Enter Category')
                ], className="mb-2"),
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-users")), # Followers icon
                    dbc.Input(id='input-followers', type='number', placeholder='Enter Number of Followers')
                ], className="mb-2"),
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-thumbs-up")), # Likes icon
                    dbc.Input(id='input-likes', type='number', placeholder='Enter Number of Likes')
                ], className="mb-2"),
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-comment")), # Comments icon
                    dbc.Input(id='input-comments', type='number', placeholder='Enter Number of Comments')
                ], className="mb-2"),
                dbc.InputGroup([
                    dbc.InputGroupText(html.I(className="fas fa-share")), # Shares icon
                    dbc.Input(id='input-shares', type='number', placeholder='Enter Number of Shares')
                ], className="mb-2"),
                dbc.Button("Calculate Brand Impact", id='calculate-button', color='primary', className="mt-3")
            ]),
            html.Div(id='brand-impact-output', className='mt-4') # Output container
        ]), width=12)
    ], className='mt-4') # Add spacing
], fluid=True)

analysis_page = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Analysis Dashboard", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col(html.Label("Select Analysis:"), width=2),
        dbc.Col(dcc.Dropdown(
            id='analysis-dropdown',
            options=[
                {'label': 'Descriptive Statistics', 'value': 'statistics'},
                {'label': 'Engagement Rate Distribution', 'value': 'engagement'},
                {'label': 'Sentiment Distribution', 'value': 'sentiment'},
                {'label': 'Collaboration Impact', 'value': 'collaboration'},
                {'label': 'Top Influencers by Engagement Rate', 'value': 'top_influencers'},
                {'label': 'Engagement Rate by Category', 'value': 'category_engagement'},
                {'label': 'Sentiment by Category', 'value': 'category_sentiment'}
            ],
            value='statistics',
            className="mb-4"
        ), width=10)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='output-div'), className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='analysis-graph', config={'displayModeBar': True}))
    ])
], fluid=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    header,
    html.Div(id='page-content'),
    footer
])

# Define the callback to update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/analysis':
        return analysis_page
    else:
        return home_page

@app.callback(
    [Output('analysis-graph', 'figure'), Output('output-div', 'children')],
    [Input('analysis-dropdown', 'value')]
)
def update_graph(selected_analysis):
    if selected_analysis == 'statistics':
        # Create dropdown and graph components for statistics
        stats_dropdown = dcc.Dropdown(
            id='stats-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='Influencer_ID',  # Default column
            className="mb-4"
        )

        stats_graph = dcc.Graph(id='stats-graph', config={'displayModeBar': True})

        # Return empty figure for analysis-graph and add dropdown and graph
        fig = go.Figure()
        stats_text = html.Div([
            html.H5("Descriptive Statistics"),
            stats_dropdown,
            stats_graph
        ])
        return fig, stats_text

    elif selected_analysis == 'engagement':
        fig = px.histogram(df, x='Engagement_Rate', nbins=20, title='Distribution of Engagement Rates')
        fig.update_layout(xaxis_title='Engagement Rate', yaxis_title='Frequency')
        return fig, {}

    elif selected_analysis == 'sentiment':
        sentiment_distribution = df['Sentiment_Score'].value_counts(normalize=True).reset_index()
        sentiment_distribution.columns = ['Sentiment', 'Proportion']
        fig = px.bar(sentiment_distribution, x='Sentiment', y='Proportion', title='Sentiment Distribution')
        fig.update_layout(xaxis_title='Sentiment', yaxis_title='Proportion')
        return fig, {}

    elif selected_analysis == 'collaboration':
        collab_engagement = df.groupby('Collaboration')['Engagement_Rate'].mean().reset_index()
        fig = px.bar(collab_engagement, x='Collaboration', y='Engagement_Rate', title='Engagement Rate for Collaborations')
        fig.update_layout(xaxis_title='Collaboration', yaxis_title='Average Engagement Rate')
        return fig, {}

    elif selected_analysis == 'top_influencers':
        top_influencers = df.groupby('Name')['Engagement_Rate'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top_influencers, x='Engagement_Rate', y='Name', orientation='h', title='Top 10 Influencers by Engagement Rate')
        fig.update_layout(xaxis_title='Engagement Rate', yaxis_title='Influencer')
        return fig, {}

    elif selected_analysis == 'category_engagement':
        engagement_by_category = df.groupby('Category')['Engagement_Rate'].mean().reset_index()
        fig = px.bar(engagement_by_category, x='Category', y='Engagement_Rate', title='Average Engagement Rate by Category')
        fig.update_layout(xaxis_title='Category', yaxis_title='Average Engagement Rate')
        return fig, {}

    elif selected_analysis == 'category_sentiment':
        sentiment_by_category = df.groupby('Category')['Sentiment_Score'].value_counts(normalize=True).unstack().fillna(0)
        fig = go.Figure()
        for sentiment in sentiment_by_category.columns:
            fig.add_trace(go.Bar(
                x=sentiment_by_category.index,
                y=sentiment_by_category[sentiment],
                name=str(sentiment)
            ))
        fig.update_layout(
            title='Sentiment Distribution by Category',
            xaxis=dict(title='Category'),
            yaxis=dict(title='Proportion'),
            barmode='stack'
        )
        return fig, {}

    # Default placeholder figure and message if the analysis type is not recognized
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode='text',
        text=['Please select a valid analysis type from the dropdown menu.'],
        textposition='bottom center'
    ))
    fig.update_layout(
        title='Invalid Analysis Type',
        xaxis_title='X-Axis',
        yaxis_title='Y-Axis',
        showlegend=False
    )
    return fig, html.P("Invalid analysis type selected. Please choose a valid option from the dropdown menu.")

@app.callback(
    Output('stats-graph', 'figure'),
    [Input('stats-dropdown', 'value')]
)
def update_stats_graph(selected_column):
    if selected_column not in df.columns:
        return go.Figure()

    # Calculate statistics for the selected column
    stats_df = df[selected_column].describe()

    # Create a bar plot for the statistics
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=stats_df.index,
        y=stats_df.values,
        text=stats_df.values,
        textposition='auto'
    ))

    fig.update_layout(
        title=f'Statistics for {selected_column}',
        xaxis_title='Statistic',
        yaxis_title='Value'
    )

    return fig

@app.callback(
    Output('brand-impact-output', 'children'),
    [Input('calculate-button', 'n_clicks')],
    [Input('input-category', 'value'),
     Input('input-followers', 'value'),
     Input('input-likes', 'value'),
     Input('input-comments', 'value'),
     Input('input-shares', 'value')]
)
def calculate_brand_impact(n_clicks, category, followers, likes, comments, shares):
    if not n_clicks:
        return ''

    try:
        followers = float(followers)
        likes = float(likes)
        comments = float(comments)
        shares = float(shares)
        
        # Ensure no division by zero
        if followers == 0:
            return "Followers cannot be zero."
        
        engagement_rate = (likes + comments + shares) / followers
        
        # Simple brand impact calculation
        brand_impact = engagement_rate * 100  # Placeholder formula
        
        return f"Brand Impact for category '{category}' is {brand_impact:.2f} based on the provided metrics."

    except ValueError:
        return "Please enter valid numerical values for the metrics."

if __name__ == '__main__':
    app.run_server(debug=True)

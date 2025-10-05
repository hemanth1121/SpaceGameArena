import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

# Add this import at the top with other imports
import base64
from pathlib import Path

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Constants
baseline_crew, baseline_contestants, baseline_spectators = 15, 12, 50
capex_phase1, capex_phase2_additional, capex_per_extra_person = 5.7e9, 1.4e9, 20e6
crew_cost_per, contestant_cost_per, spectator_transport_cost_per = 65e6, 65e6, 55e6
crew_salary_per, prize_pool_per_contestant, cargo_per_person, docked_vehicle_cost = 0.317e6, 1.667e6, 1.5e6, 44e6
sponsorship, broadcasting, vr_ar, merchandising, revenue_growth = 600e6, 550e6, 100e6, 200e6, 0.10

# Styling
SIDEBAR_STYLE = {
    'position': 'fixed', 'top': 0, 'bottom': 0, 'padding': '2rem 1rem',
    'background': 'linear-gradient(135deg, #1b2733, #2c3e50)', 'overflowY': 'auto',
    'boxShadow': '2px 0 10px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease', 'zIndex': 1000,
}

LEFT_SIDEBAR_STYLE = {**SIDEBAR_STYLE, 'left': 0, 'width': '280px'}
LEFT_SIDEBAR_COLLAPSED = {**LEFT_SIDEBAR_STYLE, 'left': '-280px'}
RIGHT_SIDEBAR_STYLE = {**SIDEBAR_STYLE, 'right': 0, 'width': '320px'}
RIGHT_SIDEBAR_COLLAPSED = {**RIGHT_SIDEBAR_STYLE, 'right': '-320px'}

CONTENT_STYLE = {
    'marginLeft': '300px', 'marginRight': '340px', 'padding': '2rem 1rem',
    'background': 'linear-gradient(135deg, #0f2027, #203a43, #2c5364)',
    'minHeight': '100vh', 'transition': 'all 0.3s ease',
}

TOGGLE_BUTTON_STYLE = {
    'position': 'fixed', 'top': '20px', 'background': 'linear-gradient(135deg, #1b2733, #2c3e50)',
    'color': 'white', 'border': 'none', 'padding': '10px 15px', 'cursor': 'pointer',
    'zIndex': 1001, 'borderRadius': '5px', 'fontSize': '20px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.3)',
}

# Tooltips
TOOLTIPS = {
    'crew-count': "Total crew needed for operations (operations, medical, mission control, engineers).",
    'contestant-count': "Number of contestants per event. Transport & prize costs scale with this.",
    'include-spectators': "Adds a spectator deck and enables spectator transport & ticket revenue.",
    'spectator-count': "Number of spectators flown to the station per event (only applies if Spectators enabled).",
    'ticket-price': "Price per spectator in MILLIONS USD (includes transport, training, insurance, food, accommodation).",
    'scale-capex': "If enabled, CAPEX will increase for persons beyond baseline capacity (extra decks/space).",
    'use-amort': "When enabled, 'Net Profit (With Amortization)' subtracts an annual amortization amount each year.",
    'amort-years': "Annual amortization = total CAPEX / this number. Default 10 years gives 5.7B/10 = 570M.",
    'manual-amort': "Enter an explicit annual amortization amount instead of dividing CAPEX by amortization period.",
    'manual-amort-value': "Enter annual amortization (in MILLIONS USD). Example: 570 => $570M/year.",
    'total-capex': "Total upfront capital expenditure. Covers R&D, habitat, life support & integration.",
    'year1-opex': "Operating expenses in Year 1 (crew deployment, transport, salaries, cargo, prize pool).",
    'recurring-opex': "Annual recurring operating expenses from Year 2 onwards.",
    'year1-revenue': "Revenue in Year 1 = ticket revenue + sponsorship + broadcasting + VR/AR + merchandising.",
}

# Add this function after your constants and before the sidebar definitions
def encode_image(image_path):
    """Encode image to base64 for display"""
    try:
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return None

# Define your image path (modify 'your_image.png' to your actual image filename)
IMAGE_PATH = Path(__file__).parent / "one_page_finance.png"  # Change filename as needed
encoded_image = encode_image(IMAGE_PATH)

def create_input_with_tooltip(label, input_id, tooltip_text, input_component):
    return html.Div([
        dbc.Label([label, html.Span(" ℹ️", id=f"{input_id}-tooltip-icon", style={'cursor': 'pointer', 'marginLeft': '5px'})], 
                  className="text-white-50"),
        dbc.Tooltip(tooltip_text, target=f"{input_id}-tooltip-icon", placement="right"),
        input_component,
    ], className='mb-3')

# Left Sidebar
left_sidebar = html.Div([
    html.H3("⚙️ Parameters", className="text-white mb-4"),
    html.Div([
        create_input_with_tooltip("Crew Members", "crew-count", TOOLTIPS['crew-count'],
            dcc.Input(id='crew-count', type='number', value=15, min=1, max=50, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
        create_input_with_tooltip("Contestants", "contestant-count", TOOLTIPS['contestant-count'],
            dcc.Input(id='contestant-count', type='number', value=12, min=1, max=50, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
        html.Div([
            dbc.Checklist(id='include-spectators', options=[{'label': ' Enable Spectators (Phase 2)', 'value': 1}],
                         value=[], className='text-white', style={'fontSize': '0.9rem'}),
            html.Span(" ℹ️", id="include-spectators-tooltip-icon", style={'cursor': 'pointer', 'marginLeft': '5px', 'color': '#f0f0f0'}),
            dbc.Tooltip(TOOLTIPS['include-spectators'], target="include-spectators-tooltip-icon", placement="right"),
        ], className='mb-3'),
        create_input_with_tooltip("Spectators", "spectator-count", TOOLTIPS['spectator-count'],
            dcc.Input(id='spectator-count', type='number', value=0, min=0, max=200, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
        create_input_with_tooltip("Ticket Price / Spectator ($M)", "ticket-price", TOOLTIPS['ticket-price'],
            dcc.Input(id='ticket-price', type='number', value=60.0, step=0.5, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
        html.Div([
            dbc.Checklist(id='scale-capex', options=[{'label': ' Scale CAPEX for extra capacity', 'value': 1}],
                         value=[], className='text-white', style={'fontSize': '0.9rem'}),
            html.Span(" ℹ️", id="scale-capex-tooltip-icon", style={'cursor': 'pointer', 'marginLeft': '5px', 'color': '#f0f0f0'}),
            dbc.Tooltip(TOOLTIPS['scale-capex'], target="scale-capex-tooltip-icon", placement="right"),
        ], className='mb-3'),
        html.Hr(className='bg-secondary'),
        html.H5("CAPEX Amortization", className="text-white mb-3", style={'fontSize': '1rem'}),
        html.Div([
            dbc.Checklist(id='use-amort', options=[{'label': ' Amortize CAPEX', 'value': 1}],
                         value=[1], className='text-white', style={'fontSize': '0.9rem'}),
            html.Span(" ℹ️", id="use-amort-tooltip-icon", style={'cursor': 'pointer', 'marginLeft': '5px', 'color': '#f0f0f0'}),
            dbc.Tooltip(TOOLTIPS['use-amort'], target="use-amort-tooltip-icon", placement="right"),
        ], className='mb-3'),
        create_input_with_tooltip("Amortization Period (years)", "amort-years", TOOLTIPS['amort-years'],
            dcc.Input(id='amort-years', type='number', value=10, min=1, max=50, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
        html.Div([
            dbc.Checklist(id='manual-amort', options=[{'label': ' Manual override', 'value': 1}],
                         value=[], className='text-white', style={'fontSize': '0.9rem'}),
            html.Span(" ℹ️", id="manual-amort-tooltip-icon", style={'cursor': 'pointer', 'marginLeft': '5px', 'color': '#f0f0f0'}),
            dbc.Tooltip(TOOLTIPS['manual-amort'], target="manual-amort-tooltip-icon", placement="right"),
        ], className='mb-3'),
        create_input_with_tooltip("Manual Annual Amortization ($M)", "manual-amort-value", TOOLTIPS['manual-amort-value'],
            dcc.Input(id='manual-amort-value', type='number', value=570.0, step=1.0, className='form-control form-control-sm',
                     style={'background': '#2c3e50', 'color': 'white', 'border': '1px solid #4a5f7f'})),
    ], style={'background': 'rgba(255, 255, 255, 0.06)', 'borderRadius': '10px', 'padding': '15px'}),
], id='left-sidebar', style=LEFT_SIDEBAR_STYLE)

# Right Sidebar
# Right Sidebar
right_sidebar = html.Div([
    html.H4("📖 Space Game Arena – Concept Summary", className="text-white mb-4", style={'fontSize': '1.1rem'}),
    
    html.Div([
        html.H6("Core Assumptions", className="text-white mt-2 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li([html.Strong("Location:"), " Suborbital station (safer + cheaper vs. LEO)."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Mass:"), " ~300 t base module; expandable to ~400 t."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Usable Area:"), " ~9,500 sq ft across multiple decks."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Crew:"), " 15–17 (ops, coaches, medical, engineers, mission control)."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Transport:"), " SpaceX Starship-class for cargo; Crew Dragon for people."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Compliance:"), " Human-rated, NASA/FAA/ESA standards."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
        html.H6("Deck Layout (Modular Station Design)", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li([html.Strong("Deck A — Play Arena #1 (2,600 sq ft):"), " Physical, open competitions."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Deck B — Play Arena #2 (2,200 sq ft):"), " Puzzle/object-interaction games."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Deck C — Spectator & Media (2,000 sq ft, 40–80 seats):"), " Live viewing & broadcasting."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Deck D — Crew/Medical/Control (2,768 sq ft):"), " Quarters, medbay, operations."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
        html.H6("CAPEX (Upfront Investment)", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li([html.Strong("Without spectator module (~300 t):"), " ~$5.7B."], className="text-white-50 mb-1"),
            html.Li([html.Strong("With spectator module (~400 t):"), " ~$7.2B."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        html.P("Breakdown: R&D, habitat construction, life support, medical & ops, launches, regulatory/legal.", 
               className="text-white-50", style={'fontSize': '0.75rem', 'fontStyle': 'italic', 'marginLeft': '20px'}),
        
        html.H6("OPEX (Transport & Operations)", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li([html.Strong("Crew Deployment (one-time, 15 seats):"), " ~$975M."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Contestants (12 per year, 3-month stay):"), " ~$780M/year."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Cargo (food, supplies, spares):"), " ~$60M/year."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Docked safety vehicle (Crew Dragon):"), " ~$44M/year (amortized)."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Crew Salaries (15 people):"), " ~$15M/year."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Contestant Compensation:"), " ~$2.4M/year."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        html.P(
            [html.Strong("➡ Year 1 Total:"), " ~$1.87B (includes initial crew deployment)."], 
            style={
                'color': '#00ffff',            # bright cyan for vibrancy
                'fontSize': '0.85rem',         # slightly larger for readability
                'marginLeft': '20px',
                'marginTop': '8px',
                'fontWeight': '500'
            }
        ),
        html.P(
            [html.Strong("➡ Recurring Annual OPEX:"), " ~$902M."], 
            style={
                'color': '#00ffff',            # bright cyan for vibrancy
                'fontSize': '0.85rem',
                'marginLeft': '20px',
                'fontWeight': '500'
            }
        ),

        
        html.H6("Contestant Journey", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ol([
            html.Li([html.Strong("Earth → Suborbital Station"), " via Crew Dragon (12 contestants)."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Stay Duration:"), " ~3 months."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Gameplay Areas:"), html.Ul([
                html.Li("Deck A (physical games).", className="text-white-50"),
                html.Li("Deck B (puzzles & interaction).", className="text-white-50"),
                html.Li("Deck D (crew support & safety).", className="text-white-50"),
            ], style={'fontSize': '0.75rem', 'marginTop': '5px', 'paddingLeft': '20px'})], className="text-white-50 mb-1"),
            html.Li([html.Strong("Return to Earth"), " after contest."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
        html.H6("Audience Journey", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ol([
            html.Li([html.Strong("Ticket Purchase (Earth):"), " Online, TV, OTT platforms, YouTube."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Viewing Options:"), html.Ul([
                html.Li([html.Strong("Remote Streaming:"), " Live broadcast via TV, YouTube, OTT."], className="text-white-50"),
                html.Li([html.Strong("Onboard Viewing (Deck C):"), " Limited 40–80 seats, flown via Crew Dragon."], className="text-white-50"),
            ], style={'fontSize': '0.75rem', 'marginTop': '5px', 'paddingLeft': '20px'})], className="text-white-50 mb-1"),
            html.Li([html.Strong("Spectators Return"), " to Earth after live experience."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
        html.H6("Revenue Streams", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li("Broadcast Rights (TV & OTT).", className="text-white-50 mb-1"),
            html.Li("Advertising & Sponsorship.", className="text-white-50 mb-1"),
            html.Li("Ticket Sales (OTT/streaming).", className="text-white-50 mb-1"),
            html.Li("Onboard Spectator Seats (future expansion).", className="text-white-50 mb-1"),
            html.Li("Merchandise & Licensing.", className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
        html.H6("Financial Outlook (10-Year Model)", className="text-white mt-3 mb-2", style={'fontSize': '0.95rem', 'fontWeight': 'bold'}),
        html.Ul([
            html.Li([html.Strong("Revenue Growth:"), " +10% annually."], className="text-white-50 mb-1"),
            html.Li([html.Strong("Profitability:"), html.Ul([
                html.Li([html.Strong("With amortization (CAPEX spread):"), " Breakeven ~Year 7–8."], className="text-white-50"),
                html.Li([html.Strong("Without amortization:"), " Breakeven later (after CAPEX fully absorbed)."], className="text-white-50"),
            ], style={'fontSize': '0.75rem', 'marginTop': '5px', 'paddingLeft': '20px'})], className="text-white-50 mb-1"),
            html.Li([html.Strong("By Year 10:"), " Business turns profitable with strong recurring margins."], className="text-white-50 mb-1"),
        ], style={'fontSize': '0.8rem', 'paddingLeft': '20px'}),
        
    ], style={'background': 'rgba(255, 255, 255, 0.06)', 'borderRadius': '10px', 'padding': '15px'}),
], id='right-sidebar', style=RIGHT_SIDEBAR_STYLE)

# Toggle Buttons
left_toggle = html.Button("◀", id='left-toggle', style={**TOGGLE_BUTTON_STYLE, 'left': '290px'})
right_toggle = html.Button("▶", id='right-toggle', style={**TOGGLE_BUTTON_STYLE, 'right': '330px'})

# Main Content
content = html.Div([
    html.H1(
        "🚀 Space Game Arena: Play in Orbit",
        style={
            'color': '#00CED1',             # DarkTurquoise — vibrant but readable
            'fontSize': '3rem',             # larger font for visibility
            'fontWeight': '700',
            'textAlign': 'center',
            'marginBottom': '20px',
            'textShadow': '0 0 8px rgba(0, 206, 209, 0.6)'  # soft glow matching text color
        }
    ),

    html.H3(
        "📊 Key Financial Metrics",
        style={
            'color': '#FFA500',             # Orange — high contrast
            'fontSize': '2rem',             # larger font
            'fontWeight': '600',
            'textAlign': 'center',
            'marginBottom': '16px',
            'textShadow': '0 0 6px rgba(255, 165, 0, 0.5)'  # soft glow
        }
    ),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([
                html.H6(["Total CAPEX ", html.Span("ℹ️", id="total-capex-tooltip-icon", style={'cursor': 'pointer'})], 
                       className="text-white", style={'marginBottom': '8px'}),
                dbc.Tooltip(TOOLTIPS['total-capex'], target="total-capex-tooltip-icon", placement="top"),
                html.H4(id='metric-capex', className="text-white", style={'fontWeight': 'bold'})
            ])
        ])], style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'border': 'none'}), width=3),
        
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([
                html.H6(["Year 1 OPEX ", html.Span("ℹ️", id="year1-opex-tooltip-icon", style={'cursor': 'pointer'})], 
                       className="text-white", style={'marginBottom': '8px'}),
                dbc.Tooltip(TOOLTIPS['year1-opex'], target="year1-opex-tooltip-icon", placement="top"),
                html.H4(id='metric-year1-opex', className="text-white", style={'fontWeight': 'bold'})
            ])
        ])], style={'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'border': 'none'}), width=3),
        
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([
                html.H6(["Recurring OPEX ", html.Span("ℹ️", id="recurring-opex-tooltip-icon", style={'cursor': 'pointer'})], 
                       className="text-white", style={'marginBottom': '8px'}),
                dbc.Tooltip(TOOLTIPS['recurring-opex'], target="recurring-opex-tooltip-icon", placement="top"),
                html.H4(id='metric-recurring-opex', className="text-white", style={'fontWeight': 'bold'})
            ])
        ])], style={'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'border': 'none'}), width=3),
        
        dbc.Col(dbc.Card([dbc.CardBody([
            html.Div([
                html.H6(["Year 1 Revenue ", html.Span("ℹ️", id="year1-revenue-tooltip-icon", style={'cursor': 'pointer'})], 
                       className="text-white", style={'marginBottom': '8px'}),
                dbc.Tooltip(TOOLTIPS['year1-revenue'], target="year1-revenue-tooltip-icon", placement="top"),
                html.H4(id='metric-revenue', className="text-white", style={'fontWeight': 'bold'})
            ])
        ])], style={'background': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)', 'border': 'none'}), width=3),
    ], className="mb-4"),
    # ADD these lines right after the above line and BEFORE dcc.Graph:
html.Div([
    html.Img(
        src=encoded_image if encoded_image else "",
        style={
            'width': '100%',
            'maxWidth': '800px',
            'height': 'auto',
            'display': 'block',
            'margin': '0 auto 20px auto',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'
        }
    ) if encoded_image else html.Div(
        "Image not found",
        style={'textAlign': 'center', 'color': '#ff6b6b', 'marginBottom': '20px'}
    )
], style={'marginBottom': '20px'}),
    html.H3("📈 10-Year Trends", className="text-white mb-3"),
    dcc.Graph(id='profit-chart', style={'height': '500px'}),
    html.H3("📋 Projection Table", className="text-white mt-4 mb-3"),
    html.Div(id='projection-table'),
], id='main-content', style=CONTENT_STYLE)

# Layout
app.layout = html.Div([left_toggle, right_toggle, left_sidebar, content, right_sidebar,
                       dcc.Store(id='left-sidebar-state', data=True), dcc.Store(id='right-sidebar-state', data=True)])

# Sidebar toggle callbacks
@app.callback([Output('left-sidebar', 'style'), Output('left-toggle', 'children'), Output('left-toggle', 'style'), Output('left-sidebar-state', 'data')],
              [Input('left-toggle', 'n_clicks')], [State('left-sidebar-state', 'data')])
def toggle_left_sidebar(n_clicks, is_open):
    if n_clicks is None:
        return LEFT_SIDEBAR_STYLE, "◀", {**TOGGLE_BUTTON_STYLE, 'left': '290px'}, True
    is_open = not is_open
    return (LEFT_SIDEBAR_STYLE, "◀", {**TOGGLE_BUTTON_STYLE, 'left': '290px'}, True) if is_open else (LEFT_SIDEBAR_COLLAPSED, "▶", {**TOGGLE_BUTTON_STYLE, 'left': '10px'}, False)

@app.callback([Output('right-sidebar', 'style'), Output('right-toggle', 'children'), Output('right-toggle', 'style'), Output('right-sidebar-state', 'data')],
              [Input('right-toggle', 'n_clicks')], [State('right-sidebar-state', 'data')])
def toggle_right_sidebar(n_clicks, is_open):
    if n_clicks is None:
        return RIGHT_SIDEBAR_STYLE, "▶", {**TOGGLE_BUTTON_STYLE, 'right': '330px'}, True
    is_open = not is_open
    return (RIGHT_SIDEBAR_STYLE, "▶", {**TOGGLE_BUTTON_STYLE, 'right': '330px'}, True) if is_open else (RIGHT_SIDEBAR_COLLAPSED, "◀", {**TOGGLE_BUTTON_STYLE, 'right': '10px'}, False)

@app.callback(Output('main-content', 'style'), [Input('left-sidebar-state', 'data'), Input('right-sidebar-state', 'data')])
def adjust_content_margins(left_open, right_open):
    style = CONTENT_STYLE.copy()
    if not left_open:
        style['marginLeft'] = '20px'
    if not right_open:
        style['marginRight'] = '20px'
    return style

# Main calculation callback
@app.callback([Output('metric-capex', 'children'), Output('metric-year1-opex', 'children'), Output('metric-recurring-opex', 'children'),
               Output('metric-revenue', 'children'), Output('profit-chart', 'figure'), Output('projection-table', 'children')],
              [Input('crew-count', 'value'), Input('contestant-count', 'value'), Input('include-spectators', 'value'),
               Input('spectator-count', 'value'), Input('ticket-price', 'value'), Input('scale-capex', 'value'),
               Input('use-amort', 'value'), Input('amort-years', 'value'), Input('manual-amort', 'value'), Input('manual-amort-value', 'value')])
def update_dashboard(crew_count, contestant_count, include_spectators, spectator_count, ticket_price, scale_capex, use_amort, amort_years, manual_amort, manual_amort_M):
    crew_count = crew_count or 15
    contestant_count = contestant_count or 12
    spectator_count = spectator_count or 0
    ticket_price = ticket_price or 60.0
    amort_years = amort_years or 10
    manual_amort_M = manual_amort_M or 570.0
    
    include_spec = len(include_spectators) > 0
    scale_cap = len(scale_capex) > 0
    use_am = len(use_amort) > 0
    manual_am = len(manual_amort) > 0
    
    # CAPEX
    total_capex = capex_phase1 + (capex_phase2_additional if include_spec else 0)
    if scale_cap:
        extra_people = max(crew_count - baseline_crew, 0) + max(contestant_count - baseline_contestants, 0) + max(spectator_count - baseline_spectators, 0)
        total_capex += extra_people * capex_per_extra_person
    
    # OPEX
    year1_opex = (crew_count * crew_cost_per + contestant_count * contestant_cost_per + 
                  (spectator_count * spectator_transport_cost_per if include_spec else 0) +
                  crew_count * crew_salary_per + contestant_count * prize_pool_per_contestant +
                  (crew_count + contestant_count + (spectator_count if include_spec else 0)) * cargo_per_person + docked_vehicle_cost)
    
    annual_opex = (contestant_count * contestant_cost_per + 
                   (spectator_count * spectator_transport_cost_per if include_spec else 0) +
                   crew_count * crew_salary_per + contestant_count * prize_pool_per_contestant +
                   (crew_count + contestant_count + (spectator_count if include_spec else 0)) * cargo_per_person + docked_vehicle_cost)
    
    # Revenue
    ticket_revenue = spectator_count * ticket_price * 1e6 if include_spec else 0
    year1_revenue = ticket_revenue + sponsorship + broadcasting + vr_ar + merchandising
    
    years = list(range(1, 11))
    revenues = [year1_revenue * ((1 + revenue_growth) ** (i - 1)) for i in years]
    
    # Amortization
    annual_amortization = manual_amort_M * 1e6 if manual_am else (total_capex / amort_years if use_am else 0.0)
    
    # Profit
    net_no_amort = []
    for i, rev in enumerate(revenues, start=1):
        opex = year1_opex if i == 1 else annual_opex
        capex_this_year = total_capex if (i == 1 and not use_am) else 0.0
        net_no_amort.append(rev - opex - capex_this_year)
    
    # Convert to millions
    revenues_M = [r / 1e6 for r in revenues]
    net_no_amort_M = [n / 1e6 for n in net_no_amort]
    
    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=revenues_M, mode="lines+markers", name="Revenue ($M)", line=dict(color='#00d4ff')))
    fig.add_trace(go.Scatter(x=years, y=net_no_amort_M, mode="lines+markers", name="Net Profit (No Amort) ($M)", line=dict(color='#ff6b6b')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.3)',
                      font=dict(color='white'), xaxis=dict(title="Year", gridcolor='rgba(255,255,255,0.1)'),
                      yaxis=dict(title="Amount ($M)", gridcolor='rgba(255,255,255,0.1)'), legend=dict(bgcolor='rgba(0,0,0,0.5)'))
    
    # Table
    df = pd.DataFrame({"Year": years, "Revenue ($M)": [f"{v:,.0f}" for v in revenues_M],
                       "Net Profit (No Amort) ($M)": [f"{v:,.0f}" for v in net_no_amort_M]})
    
    table = dash_table.DataTable(data=df.to_dict('records'), columns=[{"name": i, "id": i} for i in df.columns],
                                 style_table={'overflowX': 'auto'},
                                 style_cell={'backgroundColor': 'rgba(0,0,0,0.3)', 'color': 'white',
                                           'border': '1px solid rgba(255,255,255,0.1)', 'textAlign': 'center', 'padding': '10px'},
                                 style_header={'backgroundColor': 'rgba(0,0,0,0.5)', 'fontWeight': 'bold',
                                             'border': '1px solid rgba(255,255,255,0.2)'})
    
    return f"${total_capex/1e9:.2f}B", f"${year1_opex/1e9:.2f}B", f"${annual_opex/1e9:.2f}B", f"${year1_revenue/1e9:.2f}B", fig, table

if __name__ == '__main__':
    app.run(debug=True, port=8050)

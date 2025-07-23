"""Stress detection visualizations for the dashboard."""
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc
import pandas as pd
from datetime import datetime, timedelta
from modules.visualizations import create_spotify_card, SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_WHITE, SPOTIFY_GRAY

# Define lighter colors for better text visibility
LIGHT_GRAY = '#B3B3B3'  # Much lighter than SPOTIFY_GRAY for better readability
MEDIUM_GRAY = '#9B9B9B'  # Medium gray for secondary text

def create_enhanced_stress_analysis_card(stress_data: dict) -> html.Div:
    """Create an enhanced stress analysis card with visualizations."""
    
    # Determine stress level color
    stress_score = stress_data.get('stress_score', 25)
    if stress_score >= 70:
        stress_color = '#FF6B6B'  # Red for high stress
        stress_icon = '🔴'
    elif stress_score >= 40:
        stress_color = '#FFD93D'  # Yellow for moderate stress
        stress_icon = '🟡'
    else:
        stress_color = SPOTIFY_GREEN  # Green for low stress
        stress_icon = '🟢'
    
    # Create stress timeline chart
    timeline_chart = create_stress_timeline_chart(stress_data.get('stress_timeline', []))
    
    # Create stress indicators breakdown
    indicators_breakdown = create_stress_indicators_breakdown(stress_data.get('stress_indicators', {}))
    
    return create_spotify_card(
        title="🧠 Advanced Stress Analysis",
        content=html.Div([
            # Main stress score display
            html.Div([
                html.Div([
                    html.H1([
                        stress_icon,
                        html.Span(f" {stress_score:.0f}", style={'marginLeft': '10px'})
                    ], style={
                        'color': stress_color,
                        'textAlign': 'center',
                        'fontSize': '3rem',
                        'fontWeight': 'bold',
                        'margin': '0'
                    }),
                    html.P(stress_data.get('stress_level', 'Low Stress Indicators'), 
                          style={
                              'textAlign': 'center', 
                              'color': 'rgba(255,255,255,0.8)',
                              'fontSize': '1.1rem',
                              'marginTop': '5px'
                          })
                ], style={'marginBottom': '20px'}),
                
                # Confidence indicator with data quality info
                html.Div([
                    html.Span("Analysis Confidence: ", style={'color': LIGHT_GRAY}),
                    html.Span(f"{stress_data.get('confidence', 20):.0f}%",
                             style={'color': SPOTIFY_WHITE, 'fontWeight': 'bold'}),
                    html.Div([
                        html.I(className="fas fa-info-circle", style={'marginRight': '5px'}),
                        html.Span("Based on research showing 75-85% accuracy in music-based stress detection",
                                 style={'fontSize': '0.8rem', 'color': LIGHT_GRAY})
                    ], style={'marginTop': '5px'})
                ], style={'textAlign': 'center', 'marginBottom': '20px'})
            ]),
            
            html.Hr(style={'margin': '20px 0', 'border': f'1px solid {stress_color}', 'opacity': '0.3'}),
            
            # Stress timeline with explanation
            html.Div([
                html.H5("📈 Stress Timeline (Last 30 Days)",
                       style={'color': SPOTIFY_GREEN, 'fontFamily': 'Orbitron, monospace', 'marginBottom': '10px'}),
                html.Div([
                    html.P([
                        html.Strong("Graph Explanation: ", style={'color': SPOTIFY_WHITE}),
                        html.Span("The solid green line shows your daily stress score (0-100) based on music patterns. ", style={'color': LIGHT_GRAY}),
                        html.Span("The dashed line shows average mood (valence) scaled to 0-100. ", style={'color': LIGHT_GRAY}),
                        html.Span("Higher stress scores indicate more agitated listening, repetitive behavior, and mood volatility.", style={'color': LIGHT_GRAY})
                    ], style={'fontSize': '0.85rem', 'marginBottom': '10px', 'lineHeight': '1.4'})
                ]),
                dcc.Graph(
                    figure=timeline_chart,
                    config={'displayModeBar': False},
                    style={'height': '250px'}
                )
            ], style={'marginBottom': '25px'}),
            
            # Stress indicators breakdown
            html.Div([
                html.H5("🔍 Stress Indicators", 
                       style={'color': SPOTIFY_GREEN, 'fontFamily': 'Orbitron, monospace', 'marginBottom': '15px'}),
                indicators_breakdown
            ], style={'marginBottom': '25px'}),
            
            # Personal triggers
            html.Div([
                html.H5("⚡ Personal Triggers", 
                       style={'color': SPOTIFY_GREEN, 'fontFamily': 'Orbitron, monospace', 'marginBottom': '15px'}),
                create_personal_triggers_display(stress_data.get('personal_triggers', []))
            ], style={'marginBottom': '25px'}),
            
            # Recommendations with scientific disclaimer
            html.Div([
                html.H5("💡 Evidence-Based Recommendations",
                       style={'color': SPOTIFY_GREEN, 'fontFamily': 'Orbitron, monospace', 'marginBottom': '15px'}),
                create_stress_recommendations_display(stress_data.get('recommendations', [])),

                # Scientific disclaimer
                html.Div([
                    html.Hr(style={'margin': '20px 0', 'border': '1px solid rgba(255,255,255,0.1)'}),
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px', 'color': '#FFD93D'}),
                        html.Span("Scientific Disclaimer", style={'fontWeight': 'bold', 'color': '#FFD93D'})
                    ]),
                    html.P(stress_data.get('scientific_disclaimer',
                          'This analysis is based on music listening patterns and should not replace professional mental health assessment.'),
                          style={'fontSize': '0.85rem', 'color': LIGHT_GRAY, 'marginTop': '8px', 'lineHeight': '1.4'})
                ], style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': 'rgba(255, 211, 61, 0.1)',
                         'borderRadius': '8px', 'border': '1px solid rgba(255, 211, 61, 0.3)'})
            ])
        ]),
        icon="fa-brain",
        card_type="glass"
    )

def create_stress_timeline_chart(timeline_data: list) -> go.Figure:
    """Create a stress timeline chart."""
    if not timeline_data:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for timeline analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(color=SPOTIFY_GRAY, size=14)
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=SPOTIFY_WHITE,
            height=250
        )
        return fig
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(timeline_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create the timeline chart
    fig = go.Figure()
    
    # Add stress score line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['stress_score'],
        mode='lines+markers',
        name='Stress Score',
        line=dict(color=SPOTIFY_GREEN, width=3),
        marker=dict(size=6, color=SPOTIFY_GREEN),
        hovertemplate='<b>%{x}</b><br>Stress Score: %{y:.0f}<extra></extra>'
    ))
    
    # Add mood line (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['avg_mood'] * 100,  # Scale to 0-100
        mode='lines',
        name='Average Mood',
        line=dict(color='rgba(255, 255, 255, 0.5)', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Mood: %{y:.0f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=SPOTIFY_WHITE,
        height=250,
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color=SPOTIFY_WHITE
        ),
        yaxis=dict(
            title='Stress Score',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color=SPOTIFY_WHITE,
            range=[0, 100]
        ),
        yaxis2=dict(
            title='Mood',
            overlaying='y',
            side='right',
            color='rgba(255,255,255,0.7)',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=SPOTIFY_WHITE)
        ),
        hovermode='x unified'
    )
    
    return fig

def create_stress_indicators_breakdown(indicators: dict) -> html.Div:
    """Create a breakdown of stress indicators."""
    if not indicators:
        return html.Div("No stress indicators detected", 
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})
    
    indicator_items = []
    
    # Agitated listening
    if 'agitated_listening' in indicators:
        agitated = indicators['agitated_listening']
        severity = agitated.get('severity', 'low')
        frequency = agitated.get('frequency', 0)
        
        color = {'high': '#FF6B6B', 'moderate': '#FFD93D', 'mild': '#FFA726', 'low': SPOTIFY_GREEN}[severity]
        
        indicator_items.append(
            html.Div([
                html.Div([
                    html.Span("🎵 Agitated Listening", style={'fontWeight': 'bold'}),
                    html.Span(f" ({frequency} instances)", style={'color': LIGHT_GRAY, 'fontSize': '0.9rem'})
                ]),
                html.Div(
                    severity.title(),
                    style={
                        'backgroundColor': color,
                        'color': SPOTIFY_BLACK,
                        'padding': '2px 8px',
                        'borderRadius': '12px',
                        'fontSize': '0.8rem',
                        'fontWeight': 'bold'
                    }
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '8px 0',
                'borderBottom': '1px solid rgba(255,255,255,0.1)'
            })
        )
    
    # Repetitive behavior - Research-based display
    if 'repetitive_behavior' in indicators:
        repetitive = indicators['repetitive_behavior']
        unique_tracks = repetitive.get('unique_repeated_tracks', 0)
        stress_tracks = repetitive.get('stress_repetitive_tracks', 0)
        happy_tracks = repetitive.get('happy_repetitive_tracks', 0)
        max_reps = repetitive.get('max_repetitions', 0)

        indicator_items.append(
            html.Div([
                html.Div([
                    html.Span("🔄 Repetitive Listening", style={'fontWeight': 'bold'}),
                    html.Span(f" ({unique_tracks} total: {stress_tracks} sad, {happy_tracks} happy)",
                             style={'color': LIGHT_GRAY, 'fontSize': '0.9rem'})
                ]),
                html.Div(
                    "Stress Rumination" if stress_tracks > 0 else "Healthy Pattern",
                    style={
                        'backgroundColor': '#FF6B6B' if stress_tracks > 0 else SPOTIFY_GREEN,
                        'color': SPOTIFY_WHITE if stress_tracks > 0 else SPOTIFY_BLACK,
                        'padding': '2px 8px',
                        'borderRadius': '12px',
                        'fontSize': '0.8rem',
                        'fontWeight': 'bold'
                    }
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '8px 0',
                'borderBottom': '1px solid rgba(255,255,255,0.1)'
            })
        )
    
    # Late night patterns
    if 'late_night_patterns' in indicators:
        late_night = indicators['late_night_patterns']
        frequency = late_night.get('frequency', 0)
        avg_mood = late_night.get('avg_mood', 0.5)
        
        indicator_items.append(
            html.Div([
                html.Div([
                    html.Span("🌙 Late Night Listening", style={'fontWeight': 'bold'}),
                    html.Span(f" ({frequency} sessions, mood: {avg_mood:.2f})",
                             style={'color': LIGHT_GRAY, 'fontSize': '0.9rem'})
                ]),
                html.Div(
                    "High" if frequency > 10 else "Moderate" if frequency > 5 else "Low",
                    style={
                        'backgroundColor': '#FF6B6B' if frequency > 10 else '#FFD93D' if frequency > 5 else SPOTIFY_GREEN,
                        'color': SPOTIFY_BLACK,
                        'padding': '2px 8px',
                        'borderRadius': '12px',
                        'fontSize': '0.8rem',
                        'fontWeight': 'bold'
                    }
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '8px 0',
                'borderBottom': '1px solid rgba(255,255,255,0.1)'
            })
        )
    
    # Mood volatility
    if 'mood_volatility' in indicators:
        volatility = indicators['mood_volatility']
        severity = volatility.get('severity', 'low')
        score = volatility.get('daily_volatility', 0)
        
        color = {'high': '#FF6B6B', 'moderate': '#FFD93D', 'mild': '#FFA726', 'low': SPOTIFY_GREEN}[severity]
        
        indicator_items.append(
            html.Div([
                html.Div([
                    html.Span("📊 Mood Volatility", style={'fontWeight': 'bold'}),
                    html.Span(f" (score: {score:.3f})",
                             style={'color': LIGHT_GRAY, 'fontSize': '0.9rem'})
                ]),
                html.Div(
                    severity.title(),
                    style={
                        'backgroundColor': color,
                        'color': SPOTIFY_BLACK,
                        'padding': '2px 8px',
                        'borderRadius': '12px',
                        'fontSize': '0.8rem',
                        'fontWeight': 'bold'
                    }
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '8px 0'
            })
        )
    
    return html.Div(indicator_items)

def create_personal_triggers_display(triggers: list) -> html.Div:
    """Create display for personal stress triggers."""
    if not triggers:
        return html.Div("No specific triggers identified yet", 
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '10px'})
    
    trigger_items = []
    for trigger in triggers[:3]:  # Limit to 3 triggers
        trigger_items.append(
            html.Div([
                html.Div([
                    html.Span("⚠️", style={'marginRight': '8px'}),
                    html.Span(trigger.get('trigger', ''), style={'fontWeight': 'bold'})
                ]),
                html.P(trigger.get('recommendation', ''),
                      style={'color': LIGHT_GRAY, 'fontSize': '0.9rem', 'margin': '5px 0 0 0'})
            ], style={
                'padding': '10px',
                'backgroundColor': 'rgba(255, 255, 255, 0.05)',
                'borderRadius': '8px',
                'marginBottom': '10px',
                'border': '1px solid rgba(255, 255, 255, 0.1)'
            })
        )
    
    return html.Div(trigger_items)

def create_stress_recommendations_display(recommendations: list) -> html.Div:
    """Create display for evidence-based stress management recommendations."""
    if not recommendations:
        return html.Div("No specific recommendations available",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '10px'})

    rec_items = []
    icons = {'calming': '🧘', 'sleep': '😴', 'stability': '⚖️', 'focus': '🎯', 'motivation': '⚡', 'general': '💡'}

    for rec in recommendations[:3]:  # Limit to 3 recommendations
        rec_type = rec.get('type', 'general')
        icon = icons.get(rec_type, '💡')
        confidence = rec.get('confidence', 0.5)

        # Confidence indicator color
        conf_color = '#1DB954' if confidence > 0.7 else '#FFD93D' if confidence > 0.4 else '#FF6B6B'

        rec_items.append(
            html.Div([
                html.Div([
                    html.Span(icon, style={'marginRight': '8px'}),
                    html.Span(rec.get('title', ''), style={'fontWeight': 'bold', 'color': SPOTIFY_GREEN}),
                    html.Span(f" ({confidence:.0%} confidence)",
                             style={'fontSize': '0.8rem', 'color': conf_color, 'marginLeft': '8px'})
                ]),
                html.P(rec.get('description', ''),
                      style={'color': SPOTIFY_WHITE, 'fontSize': '0.9rem', 'margin': '5px 0'}),
                # Evidence-based information
                html.P([
                    html.I(className="fas fa-flask", style={'marginRight': '5px', 'color': '#00D4FF'}),
                    rec.get('evidence', 'Based on music therapy research')
                ], style={'color': '#00D4FF', 'fontSize': '0.8rem', 'fontStyle': 'italic', 'margin': '5px 0'}),
                html.P(f"Action: {rec.get('action', 'Apply this technique during identified stress periods')}",
                      style={'color': LIGHT_GRAY, 'fontSize': '0.8rem', 'margin': '0'})
            ], style={
                'padding': '12px',
                'backgroundColor': 'rgba(29, 185, 84, 0.1)',
                'borderRadius': '8px',
                'marginBottom': '10px',
                'border': '1px solid rgba(29, 185, 84, 0.3)'
            })
        )

    return html.Div(rec_items)

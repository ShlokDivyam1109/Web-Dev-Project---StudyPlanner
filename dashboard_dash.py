from dash import Dash, dcc, html, Input, Output
from dash import State
import plotly.graph_objs as go
import pandas as pd
import flask
from datetime import datetime, timedelta

def init_dashboard(server, mydb, get_user_id_func):
    """Initialize and mount a Dash app onto the given Flask `server`.
    The Dash app will be available at /dashboard/ (url_base_pathname).
    It queries the provided `mydb` connection and uses `get_user_id_func` to
    map the logged-in session to a user_id.
    """
    # Include the main site stylesheet so topbar/sidebar styles match the Flask app
    dash_app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

    dash_app.layout = html.Div([
        # Topbar (matching original design) with app name left and controls on the right
        html.Div([
            html.Div("StudyPlanner", id='app-name', className="app-name", style={"fontWeight": "bold", "fontSize": "26px", "letterSpacing": "1px", "color": "#fff"}),
            html.Div([
                html.Button("Dark", id='dark-toggle', className='dark-toggle', style={"marginRight": "12px", "padding": "8px 12px", "borderRadius": "8px", "border": "none", "background": "rgba(255,255,255,0.12)", "color": "#fff", "cursor": "pointer", "fontWeight": "600"}),
                html.A("", id='user-info', href='/account', className="user-name-link", style={"color": "#fff", "fontWeight": "600", "fontSize": "14px", "textDecoration": "none"})
            ], style={"display": "flex", "alignItems": "center"})
    ], id='topbar', style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "background": "var(--topbar-gradient)", "padding": "18px 32px", "height": "70px", "boxShadow": "0 4px 12px rgba(0,0,0,0.15)", "marginBottom": 0}),

        html.Div([
            # Sidebar (matching original design)
            html.Div([
                html.Ul([
                    html.Li(html.A("Dashboard", href="/dashboard", style={"display": "block", "padding": "15px 20px", "color": "#ecf0f1", "textDecoration": "none", "borderLeft": "4px solid #667eea", "background": "#667eea", "fontWeight": "bold", "transition": "all 0.3s"})),
                    html.Li(html.A("To Do List", href="/todo", style={"display": "block", "padding": "15px 20px", "color": "#ecf0f1", "textDecoration": "none", "borderLeft": "4px solid transparent", "transition": "all 0.3s"})),
                    html.Li(html.A("Schedule", href="/schedule", style={"display": "block", "padding": "15px 20px", "color": "#ecf0f1", "textDecoration": "none", "borderLeft": "4px solid transparent", "transition": "all 0.3s"})),
                    html.Li(html.A("My Plans", href="/plans", style={"display": "block", "padding": "15px 20px", "color": "#ecf0f1", "textDecoration": "none", "borderLeft": "4px solid transparent", "transition": "all 0.3s"})),
                    html.Li(html.A("Account", href="/account", style={"display": "block", "padding": "15px 20px", "color": "#ecf0f1", "textDecoration": "none", "borderLeft": "4px solid transparent", "transition": "all 0.3s"})),
                    html.Li(html.A("Log Out", href="/logout", style={"display": "block", "padding": "15px 20px", "color": "#e74c3c", "textDecoration": "none", "borderLeft": "4px solid transparent", "transition": "all 0.3s", "borderTop": "1px solid #34495e", "marginTop": "20px", "paddingTop": "20px"}))
                ], style={"listStyle": "none", "padding": "20px 0", "margin": 0})
            ], id='sidebar', style={"width": "250px", "background": "var(--sidebar-bg)", "color": "white", "minHeight": "calc(100vh - 70px)", "boxShadow": "4px 0 10px rgba(0,0,0,0.1)", "overflowY": "auto"}),

            # Main content area
            html.Div([
                html.Div([
                    html.H1(id='greeting', style={"textAlign": "center", "marginBottom": "0.5em", "fontWeight": "bold", "fontSize": "32px"}),
                    html.H3(id='motivation', style={"textAlign": "center", "marginBottom": "1.5em", "fontStyle": "italic", "fontSize": "18px"}),
                ], style={"marginBottom": "1.5em"}),

                dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0),
                dcc.Store(id='theme-store', storage_type='local'),
                html.Div(id='theme-dummy', style={'display': 'none'}),

                # Horizontal bar graph for completion %
                dcc.Graph(id='completion-bar', style={"height": "340px", "marginBottom": "2em"}),

                # Progress bar for today's completion
                html.Div([
                        html.Div("Today's Progress", style={"fontWeight": "bold", "fontSize": "18px", "marginBottom": "0.5em"}),
                        html.Div(id='progress-bar-container', style={"width": "100%", "height": "36px", "background": "transparent", "borderRadius": "18px", "overflow": "hidden", "marginBottom": "0.5em"}),
                        html.Div(id='progress-bar-label', style={"fontSize": "16px", "color": "var(--primary)", "fontWeight": "bold"})
                ], style={"marginBottom": "2em"}),

                # Sunburst graph
                dcc.Graph(id='sunburst', style={"height": "420px", "marginBottom": "2em"}),

                # Top 2 tasks
                html.Div([
                    html.H3("Top 2 Most Important Tasks Today", style={"marginBottom": "1em"}),
                    html.Div(id='top-tasks-list'),
                    html.A("Go to To-Do List →", href="/todo", className='btn-primary', style={"display": "inline-block", "marginTop": "18px", "padding": "10px 24px", "textDecoration": "none", "borderRadius": "6px", "fontWeight": "bold"})
                ], style={"background": "linear-gradient(to right, #0fff0f, #000f00)", "padding": "24px", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)", "marginBottom": "2em"}),

                # Footer message
                html.Div("Keep hustling! 🚀", style={"textAlign": "center", "color": "var(--muted)", "marginTop": "2em", "fontSize": "18px"})
            ], id='main-content', style={"flex": 1, "padding": "40px 32px", "background": "var(--bg)", "overflowY": "auto"})
        ], style={"display": "flex", "width": "100%", "height": "calc(100vh - 70px)"})
    ], style={"height": "100vh", "margin": 0, "padding": 0})

    # Clientside callback: sync theme with localStorage and toggle when button clicked
    dash_app.clientside_callback(
        """
        function(n_clicks, current) {
            try {
                var stored = window.localStorage.getItem('studyplanner_dark');
                var cur = (current === 'dark') || (stored === '1');
                // If user clicked, toggle
                if (n_clicks && n_clicks > 0) {
                    var newVal = !cur;
                    window.localStorage.setItem('studyplanner_dark', newVal ? '1' : '0');
                    return newVal ? 'dark' : 'light';
                }
                return cur ? 'dark' : 'light';
            } catch(e) {
                return current || 'light';
            }
        }
        """,
        Output('theme-store', 'data'),
        Input('dark-toggle', 'n_clicks'),
        State('theme-store', 'data')
    )

    # Clientside callback: apply theme class to document.body and update UI styles when store updates
    dash_app.clientside_callback(
        """
        function(theme) {
            try {
                var isDark = (theme === 'dark');
                // body class
                if (isDark) {
                    document.body.classList.add('dark');
                } else {
                    document.body.classList.remove('dark');
                }

                // Button label and style
                var btnLabel = isDark ? 'Light' : 'Dark';
                var btnStyle = {
                    marginRight: '12px',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: 600
                };
                if (isDark) {
                    btnStyle.background = 'linear-gradient(to top, #0f1724, #0d9488)';
                    btnStyle.color = '#fff';
                } else {
                    btnStyle.background = 'rgba(255,255,255,0.12)';
                    btnStyle.color = '#fff';
                }

                // Topbar style
                var topbarStyle = {
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '18px 32px',
                    height: '70px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    marginBottom: 0
                };
                topbarStyle.background = 'linear-gradient(to right, #0f1724, #0d9488)';

                // Sidebar style
                var sidebarStyle = {
                    width: '250px',
                    color: 'white',
                    minHeight: 'calc(100vh - 70px)',
                    boxShadow: '4px 0 10px rgba(0,0,0,0.1)',
                    overflowY: 'auto'
                };
                sidebarStyle.background = isDark ? '#11171c' : '#2c3e50';

                // Main content style
                var mainStyle = {
                    flex: 1,
                    padding: '40px 32px',
                    overflowY: 'auto'
                };
                if (isDark) {
                    mainStyle.background = '#0b0f12';
                    mainStyle.color = '#e6eef8';
                } else {
                    mainStyle.background = '#f5f5f5';
                    mainStyle.color = '#222';
                }

                return ['', btnLabel, btnStyle, topbarStyle, sidebarStyle, mainStyle];
            } catch(e) {
                return ['', 'Dark', {marginRight: '12px'}, {}, {}, {}];
            }
        }
        """,
        [
            Output('theme-dummy', 'children'),
            Output('dark-toggle', 'children'),
            Output('dark-toggle', 'style'),
            Output('topbar', 'style'),
            Output('sidebar', 'style'),
            Output('main-content', 'style')
        ],
        Input('theme-store', 'data')
    )

    # Callback: update all graphs based on current session user and theme
    @dash_app.callback(
        Output('greeting', 'children'),
        Output('motivation', 'children'),
        Output('completion-bar', 'figure'),
        Output('progress-bar-container', 'children'),
        Output('progress-bar-label', 'children'),
        Output('sunburst', 'figure'),
        Output('top-tasks-list', 'children'),
        Output('user-info', 'children'),
        Input('refresh-interval', 'n_intervals'),
        Input('theme-store', 'data')
    )
    def update_dashboard(n, theme):
        user_email = flask.session.get('user_email')
        if not user_email:
            return (
                "Welcome!", "Please log in to see your dashboard.", go.Figure(), None, None, go.Figure(), [], 'Not logged in — please log into the main app.'
            )
        user_id = get_user_id_func(user_email)
        if not user_id:
            return (
                "Welcome!", "User not found.", go.Figure(), None, None, go.Figure(), [], 'User not found in DB.'
            )

        # Greeting and motivation
        greeting = f"Welcome, {user_email.split('@')[0].capitalize()}!"
        motivation = "\u201CThe secret of getting ahead is getting started.\u201D – Mark Twain"

    # --- Completion bar over last 7 days (dates on X axis, % on Y axis, stacked bars) ---
        today = datetime.now().date()
        cursor = mydb.cursor()
        start = today - timedelta(days=6)
        cursor.execute(
            "SELECT day_date, total_tasks, completed_tasks, pending_from_previous FROM Daily_Progress WHERE user_id = %s AND day_date BETWEEN %s AND %s ORDER BY day_date",
            (user_id, start, today)
        )
        rows = cursor.fetchall()
        if rows:
            df_days = pd.DataFrame(rows, columns=['day_date', 'total', 'completed', 'pending'])
            df_days['day_date'] = pd.to_datetime(df_days['day_date']).dt.date
            df_days['completed_pct'] = (df_days['completed'] / df_days['total']).fillna(0) * 100
            df_days['pending_pct'] = (df_days['pending'] / df_days['total']).fillna(0) * 100
        else:
            dates = [start + timedelta(days=i) for i in range(7)]
            df_days = pd.DataFrame({'day_date': dates, 'total': 0, 'completed': 0, 'pending': 0})
            df_days['completed_pct'] = 0
            df_days['pending_pct'] = 0

        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            x=df_days['day_date'],
            y=df_days['completed_pct'],
            name='Completed %',
            marker_color='#1f77b4',
            text=[f"{v:.1f}%" for v in df_days['completed_pct']],
            textposition='inside'
        ))
        bar_fig.add_trace(go.Bar(
            x=df_days['day_date'],
            y=df_days['pending_pct'],
            name='Pending %',
            marker_color='#ff7f0e',
            text=[f"{v:.1f}%" for v in df_days['pending_pct']],
            textposition='inside'
        ))
        # adapt plot colors based on theme
        if theme == 'dark':
            plot_bg = '#2d3643'
            paper_bg = '#2d3643'
            font_color = '#e6eef8'
        else:
            plot_bg = 'white'
            paper_bg = 'white'
            font_color = '#222'

        bar_fig.update_layout(
            barmode='stack',
            title='Completion % by Date (last 7 days)',
            xaxis_title='Date',
            yaxis_title='Percentage',
            yaxis=dict(range=[0, 100], color=font_color),
            xaxis=dict(color=font_color),
            margin=dict(l=60, r=30, t=60, b=60),
            plot_bgcolor=plot_bg,
            paper_bgcolor=paper_bg,
            font=dict(color=font_color)
        )

        # Get today's completion for the progress bar
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) FROM Study_Schedule WHERE user_id=%s AND due_date=%s", (user_id, today))
        total_today, completed_today = cursor.fetchone()
        total_today = total_today or 0
        completed_today = completed_today or 0

        # Progress bar for today's completion (render full themed container)
        pct_today = (completed_today / total_today * 100) if total_today else 0
        container_bg = '#e0e0e0' if theme != 'dark' else '#3a3f47'
        inner_bg = 'linear-gradient(to top, #0f1724, #0d9488)'
        progress_inner = html.Div(style={
            "width": f"{pct_today}%", "height": "100%", "background": inner_bg, "borderRadius": "18px", "transition": "width 0.3s"
        }) if pct_today > 0 else html.Div()
        progress_bar = html.Div(progress_inner, style={"width": "100%", "height": "36px", "background": container_bg, "borderRadius": "18px", "overflow": "hidden"})
        progress_label = f"{completed_today} / {total_today} tasks completed today ({pct_today:.1f}%)"

        # Sunburst: Category (Completed / Pending / Not Started) > Subject > Topic
        cursor.execute("SELECT subject, topic, status, due_date FROM Study_Schedule WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['subject', 'topic', 'status', 'due_date'])
        if not df.empty:
            # categorize each task
            today_date = datetime.now().date()
            def categorize(row):
                st = (row['status'] or '').lower()
                due = row['due_date']
                if st == 'completed':
                    return 'Completed'
                try:
                    if due and due < today_date:
                        return 'Pending'
                    else:
                        return 'Not Started'
                except Exception:
                    return 'Not Started'

            df['category'] = df.apply(categorize, axis=1)

            # aggregated counts
            cat_counts = df.groupby('category').size().to_dict()
            subj_counts = df.groupby(['category', 'subject']).size().to_dict()
            topic_counts = df.groupby(['category', 'subject', 'topic']).size().to_dict()

            labels = []
            parents = []
            values = []
            ids = []

            # add category nodes
            for cat, cnt in cat_counts.items():
                cid = f"cat::{cat}"
                ids.append(cid)
                labels.append(cat)
                parents.append("")
                values.append(int(cnt))

            # add subject nodes (child of category)
            for (cat, subj), cnt in subj_counts.items():
                sid = f"sub::{cat}::{subj}"
                ids.append(sid)
                labels.append(subj)
                parents.append(f"cat::{cat}")
                values.append(int(cnt))

            # add topic nodes (child of subject)
            for (cat, subj, topic), cnt in topic_counts.items():
                tid = f"top::{cat}::{subj}::{topic}"
                ids.append(tid)
                labels.append(topic)
                parents.append(f"sub::{cat}::{subj}")
                values.append(int(cnt))

            sunburst_fig = go.Figure(go.Sunburst(ids=ids, labels=labels, parents=parents, values=values, branchvalues='total', maxdepth=3))
            sunburst_fig.update_layout(margin=dict(t=40, l=0, r=0, b=0), title='Task Breakdown (Category > Subject > Topic)', plot_bgcolor=plot_bg, paper_bgcolor=paper_bg, font=dict(color=font_color))
        else:
            sunburst_fig = go.Figure()
            sunburst_fig.update_layout(title='No tasks found')

        # Top 2 most important not completed tasks of today (by weightage)
        cursor.execute("SELECT topic, subject, due_date, weightage, status FROM Study_Schedule WHERE user_id=%s AND due_date=%s AND status!='completed' ORDER BY weightage DESC LIMIT 2", (user_id, today))
        top_tasks = cursor.fetchall()
        top_tasks_list = []
        for i, (topic, subject, due_date, weightage, status) in enumerate(top_tasks, 1):
            # use CSS variables so color palette remains centralized
            card_bg = '#e0e0e0' if theme != 'dark' else '#3a3f47'
            text_color = 'var(--text)'
            top_tasks_list.append(html.Div([
                html.Strong(f"{i}. {topic} - {subject}", style={"color": text_color}), html.Br(),
                html.Small(f"Due: {due_date.strftime('%d %m %Y') if hasattr(due_date, 'strftime') else due_date} | Weightage: {weightage}% | Status: {status}", style={"color": text_color})
            ], style={"background": "transparent", "padding": "15px", "margin": "10px 0", "borderLeft": "4px solid var(--primary)", "borderRadius": "4px"}))

        # Fetch user's first name to show instead of email
        try:
            cursor.execute("SELECT First_Name FROM User_Data WHERE id = %s", (user_id,))
            name_row = cursor.fetchone()
            user_name = name_row[0] if name_row and name_row[0] else user_email.split('@')[0]
        except Exception:
            user_name = user_email.split('@')[0]
        cursor.close()
        # Return plain username as inner text of the account link in the topbar
        return greeting, motivation, bar_fig, progress_bar, progress_label, sunburst_fig, top_tasks_list, user_name

    return dash_app

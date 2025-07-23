import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import networkx as nx
from pyvis.network import Network

def show_live_analysis_in_placeholder(placeholder):
    """Display live analysis in a fixed placeholder to prevent stacking"""
    
    if not st.session_state.parsing_state.get('parsed_jobs'):
        with placeholder.container():
            st.info("🔍 No jobs parsed yet. Visualizations will appear as jobs are processed...")
        return
    
    config = st.session_state.get('parsing_config', {})
    df = pd.DataFrame(st.session_state.parsing_state['parsed_jobs'])
    
    # Generate unique key suffix using update counter and timestamp
    update_counter = st.session_state.parsing_state.get('update_counter', 0)
    unique_suffix = f"{update_counter}_{int(time.time() * 1000) % 10000}"
    
    # REPLACE all content in the placeholder
    with placeholder.container():
        st.markdown(f"**📊 {len(df)} Jobs Parsed So Far**")
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Jobs Parsed", len(df))
        with col2:
            unique_companies = df['company'].nunique() if 'company' in df.columns else 0
            st.metric("Companies", unique_companies)
        with col3:
            if 'min_experience' in df.columns:
                try:
                    exp_series = pd.to_numeric(df['min_experience'], errors='coerce')
                    avg_exp = exp_series.mean() if not exp_series.isna().all() else 0
                    st.metric("Avg Min Experience", f"{avg_exp:.1f} yrs")
                except:
                    st.metric("Avg Min Experience", "N/A")
            else:
                st.metric("Avg Min Experience", "N/A")
        with col4:
            if 'work_model' in df.columns:
                remote_count = len(df[df['work_model'].str.contains('Remote|remote', case=False, na=False)])
                st.metric("Remote Jobs", remote_count)
            else:
                st.metric("Remote Jobs", "N/A")
        
        # Live charts in columns for compact display
        col1, col2 = st.columns(2)
        
        with col1:
            # Top domains
            if 'domain' in df.columns and not df['domain'].isna().all():
                domain_counts = df['domain'].value_counts().head(config.get('max_categories_shown', 10))
                if not domain_counts.empty:
                    fig = px.bar(
                        x=domain_counts.values, 
                        y=domain_counts.index,
                        orientation='h',
                        title="Top Job Domains",
                        color=domain_counts.values,
                        color_continuous_scale=config.get('color_scheme', 'viridis')
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    if config.get('show_data_labels', True):
                        fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key=f"domains_{unique_suffix}")
                else:
                    st.info("No domain data available yet")
            else:
                st.info("No domain data available yet")
        
        with col2:
            # Top companies
            if 'company' in df.columns and not df['company'].isna().all():
                company_counts = df['company'].value_counts().head(config.get('max_categories_shown', 10))
                if not company_counts.empty:
                    fig = px.pie(
                        values=company_counts.values,
                        names=company_counts.index,
                        title="Top Companies"
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400),
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"companies_{unique_suffix}")
                else:
                    st.info("No company data available yet")
            else:
                st.info("No company data available yet")
        
        # Additional charts in second row
        col1, col2 = st.columns(2)
        
        with col1:
            # Experience distribution
            if 'min_experience' in df.columns:
                try:
                    exp_data = pd.to_numeric(df['min_experience'], errors='coerce').dropna()
                    if len(exp_data) > 0:
                        fig = px.histogram(
                            x=exp_data,
                            title="Experience Requirements",
                            nbins=min(15, int(exp_data.max()) + 1),
                            color_discrete_sequence=[config.get('color_scheme', 'viridis')]
                        )
                        fig.update_layout(
                            height=config.get('chart_height', 400) // 1.5,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"experience_{unique_suffix}")
                    else:
                        st.info("No valid experience data yet")
                except:
                    st.info("No valid experience data yet")
            else:
                st.info("No experience data available yet")
        
        with col2:
            # Locations
            if 'location' in df.columns and not df['location'].isna().all():
                location_counts = df['location'].value_counts().head(8)
                if not location_counts.empty:
                    fig = px.bar(
                        x=location_counts.values,
                        y=location_counts.index,
                        orientation='h',
                        title="Top Locations",
                        color=location_counts.values,
                        color_continuous_scale=config.get('color_scheme', 'plasma')
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400) // 1.5,
                        showlegend=False,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    if config.get('show_data_labels', True):
                        fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key=f"locations_{unique_suffix}")
                else:
                    st.info("No location data available yet")
            else:
                st.info("No location data available yet")
        
        # Latest parsed jobs preview
        if len(df) > 0:
            st.markdown("---")
            st.write(f"**🆕 Latest {config.get('max_preview_jobs', 5)} Parsed Jobs:**")
            
            display_cols = []
            for col in ['company', 'job_title', 'location', 'domain', 'min_experience']:
                if col in df.columns:
                    display_cols.append(col)
            
            if display_cols:
                latest_jobs = df[display_cols].tail(config.get('max_preview_jobs', 5))
                st.dataframe(latest_jobs, use_container_width=True, hide_index=True)


def show_final_analysis_results():
    """Display comprehensive analysis of parsed job data"""
    
    st.markdown("---")
    st.subheader("📊 Comprehensive Job Market Analysis")
    
    config = st.session_state.get('parsing_config', {})
    df = pd.DataFrame(st.session_state.parsing_state['parsed_jobs'])
    
    # Generate unique suffix for final analysis charts
    final_unique_suffix = f"final_{int(time.time() * 1000) % 10000}"
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(df))
    with col2:
        unique_companies = df['company'].nunique() if 'company' in df.columns else 0
        st.metric("Unique Companies", unique_companies)
    with col3:
        if 'min_experience' in df.columns:
            try:
                exp_series = pd.to_numeric(df['min_experience'], errors='coerce')
                avg_exp = exp_series.mean() if not exp_series.isna().all() else 0
                st.metric("Avg Min Experience", f"{avg_exp:.1f} yrs")
            except:
                st.metric("Avg Min Experience", "N/A")
        else:
            st.metric("Avg Min Experience", "N/A")
    with col4:
        if 'min_salary' in df.columns:
            try:
                salary_series = pd.to_numeric(df['min_salary'], errors='coerce')
                avg_salary = salary_series.mean() if not salary_series.isna().all() else 0
                st.metric("Avg Min Salary", f"${avg_salary:,.0f}")
            except:
                st.metric("Avg Min Salary", "N/A")
        else:
            st.metric("Avg Min Salary", "N/A")
    
    # Tab-based comprehensive analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Core Metrics", "🏢 Companies & Domains", "💰 Salaries & Experience", "🌐 Job Market Graph"])
    
    with tab1:
        # Row 1: Work models and experience
        col1, col2 = st.columns(2)
        
        with col1:
            # Work model distribution
            if 'work_model' in df.columns and not df['work_model'].isna().all():
                model_counts = df['work_model'].value_counts()
                if not model_counts.empty:
                    fig = px.pie(
                        values=model_counts.values,
                        names=model_counts.index,
                        title="Work Model Distribution",
                        hole=0.3
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400) // 1.2,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"work_model_{final_unique_suffix}")
                else:
                    st.info("No work model data available")
            else:
                st.info("No work model data available")
        
        with col2:
            # Experience distribution
            if 'min_experience' in df.columns:
                try:
                    exp_data = pd.to_numeric(df['min_experience'], errors='coerce').dropna()
                    if len(exp_data) > 0:
                        color_scheme = config.get('color_scheme', '#636EFA')
                        if color_scheme == 'viridis':  
                            color_scheme = '#636EFA'

                        fig = px.histogram(
                            exp_data,
                            title="Experience Requirements Distribution",
                            nbins=min(15, int(exp_data.max()) + 1),
                            color_discrete_sequence=[color_scheme]
                        )

                        fig.update_layout(
                            xaxis_title="Years of Experience",
                            yaxis_title="Number of Jobs",
                            height=config.get('chart_height', 400) // 1.2,
                            margin=dict(l=0, r=0, t=40, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"exp_dist_{final_unique_suffix}")
                    else:
                        st.info("No valid experience data")
                except:
                    st.info("No valid experience data")
            else:
                st.info("No experience data available")
        
        # Row 2: Education and locations
        col1, col2 = st.columns(2)
        
        with col1:
            # Education requirements
            if 'education' in df.columns and not df['education'].isna().all():
                edu_counts = df['education'].value_counts()
                if not edu_counts.empty:
                    fig = px.bar(
                        x=edu_counts.values,
                        y=edu_counts.index,
                        orientation='h',
                        title="Education Requirements",
                        color=edu_counts.values,
                        color_continuous_scale=config.get('color_scheme', 'plasma')
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400) // 1.5,
                        showlegend=False,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    if config.get('show_data_labels', True):
                        fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key=f"education_{final_unique_suffix}")
                else:
                    st.info("No education data available")
            else:
                st.info("No education data available")
        
        with col2:
            # Locations
            if 'location' in df.columns and not df['location'].isna().all():
                location_counts = df['location'].value_counts().head(10)
                if not location_counts.empty:
                    fig = px.bar(
                        x=location_counts.values,
                        y=location_counts.index,
                        orientation='h',
                        title="Top Job Locations",
                        color=location_counts.values,
                        color_continuous_scale=config.get('color_scheme', 'inferno')
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400) // 1.5,
                        showlegend=False,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    if config.get('show_data_labels', True):
                        fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key=f"locations_{final_unique_suffix}")
                else:
                    st.info("No location data available")
            else:
                st.info("No location data available")
    
    with tab2:
        # Company analysis
        st.subheader("Company Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies by job count
            if 'company' in df.columns and not df['company'].isna().all():
                company_counts = df['company'].value_counts().head(config.get('max_categories_shown', 10))
                if not company_counts.empty:
                    fig = px.bar(
                        x=company_counts.values,
                        y=company_counts.index,
                        orientation='h',
                        title="Top Companies by Job Count",
                        color=company_counts.values,
                        color_continuous_scale=config.get('color_scheme', 'viridis')
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    if config.get('show_data_labels', True):
                        fig.update_traces(texttemplate='%{x}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True, key=f"top_companies_{final_unique_suffix}")
                else:
                    st.info("No company data available")
            else:
                st.info("No company data available")
        
        with col2:
            # Top domains
            if 'domain' in df.columns and not df['domain'].isna().all():
                domain_counts = df['domain'].value_counts().head(config.get('max_categories_shown', 10))
                if not domain_counts.empty:
                    fig = px.pie(
                        values=domain_counts.values,
                        names=domain_counts.index,
                        title="Job Domain Distribution",
                        hole=0.3
                    )
                    fig.update_layout(
                        height=config.get('chart_height', 400),
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"domains_{final_unique_suffix}")
                else:
                    st.info("No domain data available")
            else:
                st.info("No domain data available")
        
        # Company size distribution
        if 'number_of_employeees' in df.columns and not df['number_of_employeees'].isna().all():
            st.subheader("Company Size Distribution")
            size_counts = df['number_of_employeees'].value_counts()
            if not size_counts.empty:
                fig = px.bar(
                    x=size_counts.index,
                    y=size_counts.values,
                    title="Company Size Distribution",
                    color=size_counts.values,
                    color_continuous_scale=config.get('color_scheme', 'plasma')
                )
                fig.update_layout(
                    xaxis_title="Company Size",
                    yaxis_title="Number of Jobs",
                    height=config.get('chart_height', 400) // 1.2,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"company_size_{final_unique_suffix}")
            else:
                st.info("No company size data available")
        else:
            st.info("No company size data available")
    
    with tab3:
        # Salary analysis
        st.subheader("Salary Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Min salary distribution
            if 'min_salary' in df.columns:
                try:
                    min_salaries = pd.to_numeric(df['min_salary'], errors='coerce').dropna()
                    if len(min_salaries) > 0:
                        fig = px.histogram(
                            min_salaries,
                            title="Minimum Salary Distribution",
                            nbins=20,
                            color_discrete_sequence=['#00CC96']
                        )
                        fig.update_layout(
                            xaxis_title="Minimum Salary",
                            yaxis_title="Number of Jobs",
                            height=config.get('chart_height', 400) // 1.2,
                            margin=dict(l=0, r=0, t=40, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"min_salary_{final_unique_suffix}")
                    else:
                        st.info("No min salary data available")
                except:
                    st.info("No min salary data available")
            else:
                st.info("No min salary data available")
        
        with col2:
            # Max salary distribution
            if 'max_salary' in df.columns:
                try:
                    max_salaries = pd.to_numeric(df['max_salary'], errors='coerce').dropna()
                    if len(max_salaries) > 0:
                        fig = px.histogram(
                            max_salaries,
                            title="Maximum Salary Distribution",
                            nbins=20,
                            color_discrete_sequence=['#EF553B']
                        )
                        fig.update_layout(
                            xaxis_title="Maximum Salary",
                            yaxis_title="Number of Jobs",
                            height=config.get('chart_height', 400) // 1.2,
                            margin=dict(l=0, r=0, t=40, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"max_salary_{final_unique_suffix}")
                    else:
                        st.info("No max salary data available")
                except:
                    st.info("No max salary data available")
            else:
                st.info("No max salary data available")
        
        # Experience vs Salary
        if 'min_experience' in df.columns and 'min_salary' in df.columns:
            try:
                exp_salary_df = df[['min_experience', 'min_salary']].copy()
                exp_salary_df['min_experience'] = pd.to_numeric(exp_salary_df['min_experience'], errors='coerce')
                exp_salary_df['min_salary'] = pd.to_numeric(exp_salary_df['min_salary'], errors='coerce')
                exp_salary_df = exp_salary_df.dropna()
                
                if len(exp_salary_df) > 0:
                    fig = px.scatter(
                        exp_salary_df,
                        x='min_experience',
                        y='min_salary',
                        title="Experience vs Minimum Salary",
                        trendline='ols',
                        color_discrete_sequence=['#636EFA']
                    )
                    fig.update_layout(
                        xaxis_title="Years of Experience",
                        yaxis_title="Minimum Salary",
                        height=config.get('chart_height', 400),
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"exp_vs_salary_{final_unique_suffix}")
                else:
                    st.info("Insufficient data for experience vs salary analysis")
            except:
                st.info("Could not generate experience vs salary analysis")
        else:
            st.info("Missing data for experience vs salary analysis")
    
    with tab4:
        st.subheader("Job Market Graph")
        if df.empty:
            st.info("No data available to build graph")
        else:
            G = nx.Graph()
            
            # Build sets for node categorization
            companies = set(df['company'].dropna().apply(str.strip).unique())
            jobs = set(df['job_title'].dropna().apply(str.strip).unique())
            domains = set(df['domain'].dropna().apply(str.strip).unique())
            skills = set()
            
            for _, row in df.iterrows():
                company = str(row.get('company', '')).strip()
                job = str(row.get('job_title', '')).strip()
                domain = str(row.get('domain', '')).strip()
                
                if company and job:
                    G.add_edge(company, job, relation="HAS_JOB")
                if job and domain:
                    G.add_edge(job, domain, relation="IN_DOMAIN")
                
                # Handle skills
                if 'domain_specific_skills' in row and pd.notna(row['domain_specific_skills']):
                    skill_str = row['domain_specific_skills']
                    if isinstance(skill_str, str):
                        skill_list = [s.strip() for s in skill_str.split(',')]
                    elif isinstance(skill_str, list):
                        skill_list = [str(s).strip() for s in skill_str]
                    else:
                        skill_list = []
                    
                    for skill in skill_list:
                        if skill:
                            skills.add(skill)
                            G.add_edge(job, skill, relation="REQUIRES_SKILL")
            
            # Create PyVis network
            net = Network(notebook=False, height='750px', width='100%', 
                          cdn_resources='remote', bgcolor='#ffffff', font_color='#333333')
            
            # Add nodes with color coding
            for node in G.nodes:
                if node in companies:
                    net.add_node(node, label=node, color="#1f77b4", shape="ellipse", size=30)  # Company: Blue
                elif node in jobs:
                    net.add_node(node, label=node, color="#2ca02c", shape="box", size=25)  # Job: Green
                elif node in domains:
                    net.add_node(node, label=node, color="#ff7f0e", shape="diamond", size=20)  # Domain: Orange
                else:
                    net.add_node(node, label=node, color="#9467bd", shape="dot", size=15)  # Skill: Purple
            
            # Add edges
            for u, v, data in G.edges(data=True):
                net.add_edge(u, v, label=data.get('relation', ''), color="#888888")
            
            # Configure physics
            net.repulsion(node_distance=200, central_gravity=0.3, 
                          spring_length=150, spring_strength=0.05)
            
            # Generate and display HTML
            net_html = net.generate_html()
            st.components.v1.html(net_html, height=800)
    
    # Full data table
    st.markdown("---")
    st.subheader("📋 Full Parsed Job Data")
    
    # Select columns to show
    all_columns = list(df.columns)
    default_columns = ['company', 'job_title', 'location', 'domain', 'min_experience', 'min_salary']
    visible_columns = st.multiselect(
        "Select columns to display",
        options=all_columns,
        default=default_columns
    )
    
    if visible_columns:
        st.dataframe(df[visible_columns], use_container_width=True, height=600)
    else:
        st.info("Select at least one column to display")
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        "💾 Download Full Dataset as CSV",
        data=csv,
        file_name=f"job_analysis_{int(time.time())}.csv",
        mime="text/csv",
        type="primary"
    )


def create_custom_chart(df, chart_type, x_col, y_col=None, color_col=None, title="Custom Chart", config=None):
    """
    Create custom charts based on user selection
    
    Args:
        df: DataFrame with job data
        chart_type: Type of chart ('bar', 'pie', 'scatter', 'histogram', 'box')
        x_col: Column for x-axis
        y_col: Column for y-axis (optional for some chart types)
        color_col: Column for color mapping (optional)
        title: Chart title
        config: Configuration dictionary from session state
    """
    
    if config is None:
        config = {}
    
    try:
        if chart_type == 'bar':
            if y_col:
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            else:
                # Count values for categorical data
                counts = df[x_col].value_counts()
                fig = px.bar(x=counts.index, y=counts.values, title=title)
                
        elif chart_type == 'pie':
            if y_col:
                fig = px.pie(df, names=x_col, values=y_col, title=title)
            else:
                counts = df[x_col].value_counts()
                fig = px.pie(names=counts.index, values=counts.values, title=title)
                
        elif chart_type == 'scatter':
            if not y_col:
                st.error("Scatter plot requires both X and Y columns")
                return None
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
            
        elif chart_type == 'histogram':
            fig = px.histogram(df, x=x_col, color=color_col, title=title)
            
        elif chart_type == 'box':
            fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
            
        else:
            st.error(f"Unsupported chart type: {chart_type}")
            return None
        
        # Apply configuration
        fig.update_layout(
            height=config.get('chart_height', 400),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        if config.get('color_scheme'):
            if hasattr(fig.data[0], 'marker'):
                fig.update_traces(marker_colorscale=config['color_scheme'])
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None


def show_interactive_chart_builder():
    """
    Interactive chart builder for custom visualizations
    """
    
    if not st.session_state.parsing_state.get('parsed_jobs'):
        st.info("No parsed job data available for chart builder")
        return
    
    df = pd.DataFrame(st.session_state.parsing_state['parsed_jobs'])
    config = st.session_state.get('parsing_config', {})
    
    st.subheader("🎨 Interactive Chart Builder")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ['bar', 'pie', 'scatter', 'histogram', 'box'],
            help="Select the type of chart to create"
        )
    
    with col2:
        x_column = st.selectbox(
            "X-Axis Column",
            options=df.columns.tolist(),
            help="Select column for X-axis"
        )
    
    with col3:
        y_column = st.selectbox(
            "Y-Axis Column (optional)",
            options=[None] + df.columns.tolist(),
            help="Select column for Y-axis (required for scatter and box plots)"
        )
    
    # Additional options
    col1, col2 = st.columns(2)
    
    with col1:
        color_column = st.selectbox(
            "Color Column (optional)",
            options=[None] + df.columns.tolist(),
            help="Select column for color mapping"
        )
    
    with col2:
        chart_title = st.text_input(
            "Chart Title",
            value=f"{chart_type.title()} Chart",
            help="Enter a title for your chart"
        )
    
    # Generate chart
    if st.button("🎯 Generate Chart", type="primary"):
        fig = create_custom_chart(
            df=df,
            chart_type=chart_type,
            x_col=x_column,
            y_col=y_column,
            color_col=color_column,
            title=chart_title,
            config=config
        )
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # Option to save chart
            if st.button("💾 Save Chart Configuration"):
                if 'saved_charts' not in st.session_state:
                    st.session_state.saved_charts = []
                
                chart_config = {
                    'type': chart_type,
                    'x_col': x_column,
                    'y_col': y_column,
                    'color_col': color_column,
                    'title': chart_title,
                    'created_at': time.time()
                }
                
                st.session_state.saved_charts.append(chart_config)
                st.success("Chart configuration saved!")


def show_saved_charts():
    """
    Display and manage saved chart configurations
    """
    
    if not st.session_state.get('saved_charts'):
        st.info("No saved charts available")
        return
    
    st.subheader("📁 Saved Charts")
    
    for i, chart_config in enumerate(st.session_state.saved_charts):
        with st.expander(f"Chart {i+1}: {chart_config['title']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type:** {chart_config['type']}")
                st.write(f"**X Column:** {chart_config['x_col']}")
                st.write(f"**Y Column:** {chart_config.get('y_col', 'None')}")
                st.write(f"**Color Column:** {chart_config.get('color_col', 'None')}")
            
            with col2:
                if st.button(f"🔄 Recreate Chart {i+1}"):
                    if st.session_state.parsing_state.get('parsed_jobs'):
                        df = pd.DataFrame(st.session_state.parsing_state['parsed_jobs'])
                        fig = create_custom_chart(
                            df=df,
                            chart_type=chart_config['type'],
                            x_col=chart_config['x_col'],
                            y_col=chart_config.get('y_col'),
                            color_col=chart_config.get('color_col'),
                            title=chart_config['title'],
                            config=st.session_state.get('parsing_config', {})
                        )
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("No job data available")
                
                if st.button(f"🗑️ Delete Chart {i+1}"):
                    st.session_state.saved_charts.pop(i)
                    st.rerun()
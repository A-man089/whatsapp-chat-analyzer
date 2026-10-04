import streamlit as st
from fontTools.diff import color
from plotly.express import timeline

import preprocessor, helper
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns


st.set_page_config(page_title="WhatsApp Chat Analytics", page_icon="", layout="wide")


st.markdown("""
    <style>
    /* Metric Card Custom Styling */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #21918C;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8B949E !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #5EC962 !important;
        font-size: 26px !important;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Whatsapp Chat Analytics")

# Single Unified File Uploader
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Export (.txt)", type=["txt"])

# Project Documentation Accordion
with st.sidebar.expander("About Project"):
    st.markdown("""
    **WhatsApp Analytics Suite**
    * **Tech Stack:** Python, Streamlit, Pandas, Plotly
    * **Theme:** Viridis Dark Mode (#0E1117)
    """)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    st.sidebar.divider()
    selected_user = st.sidebar.selectbox("Show analysis W.R.T", user_list)

    if st.sidebar.button("Generate Dashboard", use_container_width=True):
        
        title_prefix = "Group Overview" if selected_user == "Overall" else f"Overview for {selected_user}"
        st.title(f" {title_prefix}")

        total_msgs, total_words, active_days, avg_daily = helper.fetch_kpi_stats(selected_user, df)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.metric(label="Total Messages", value=f"{total_msgs:,}")
        with kpi2:
            st.metric(label="Total Words Sent", value=f"{total_words:,}")
        with kpi3:
            st.metric(label="Active Days", value=f"{active_days:,}")
        with kpi4:
            st.metric(label="Avg Msgs / Day", value=f"{avg_daily}")

        st.divider()

        # Followed by Monthly Timeline, Activity Maps, Heatmap, etc.








        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)

        if not timeline.empty:
            fig_timeline = px.line(
                timeline,
                x='time',
                y='message',
                markers=True,
                labels={'time': 'Month', 'message': 'Messages'}
            )

            # Apply gradient area glow, Viridis color, and custom hover tooltips
            fig_timeline.update_traces(
                line=dict(color='#5EC962', width=3),
                marker=dict(size=8, color='#5EC962', symbol='circle'),
                fill='tozeroy',
                fillcolor='rgba(94, 201, 98, 0.15)',  # Translucent Viridis green glow
                hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>'
            )

            fig_timeline.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    color='white',
                    title='',
                    tickangle=-45,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#262730',
                    color='white',
                    title='Total Messages',
                    zeroline=False
                ),
                margin=dict(l=10, r=20, t=10, b=10),
                height=350
            )

            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No timeline data available.")




        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)

        if not daily_timeline.empty:
            fig_daily = px.line(
                daily_timeline,
                x='only_date',
                y='message',
                labels={'only_date': 'Date', 'message': 'Messages'}
            )

            # Apply gradient area glow, Viridis accent color, and custom hover tooltips
            fig_daily.update_traces(
                line=dict(color='#21918C', width=2),  # Deep teal Viridis accent line
                fill='tozeroy',
                fillcolor='rgba(33, 145, 140, 0.15)',  # Translucent teal glow
                hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>'
            )

            fig_daily.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    color='white',
                    title='',
                    tickangle=-45,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#262730',
                    color='white',
                    title='Total Messages',
                    zeroline=False
                ),
                margin=dict(l=10, r=20, t=10, b=10),
                height=350
            )

            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No daily timeline data available.")

        # Weekly Activity Map
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        if not user_heatmap.empty:
            fig_heatmap = px.imshow(
                user_heatmap,
                labels=dict(x="Period", y="Day", color="Messages"),
                x=user_heatmap.columns,
                y=user_heatmap.index,
                color_continuous_scale="Viridis",
                aspect="auto"  
            )

            
            fig_heatmap.update_traces(
                hovertemplate="<b>Day:</b> %{y}<br><b>Period:</b> %{x}<br><b>Messages:</b> %{z}<extra></extra>",
                xgap=2,
                ygap=2
            )

          
            fig_heatmap.update_xaxes(constrain='domain')
            fig_heatmap.update_yaxes(scaleanchor=None)

            fig_heatmap.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                autosize=True,  
                coloraxis_colorbar=dict(
                    title=dict(text="Messages", font=dict(color="white", size=12)),
                    tickfont=dict(color="white", size=11),
                    len=0.85
                ),
                xaxis=dict(
                    showgrid=False,
                    color="white",
                    tickangle=-45,
                    tickfont=dict(size=10),
                    title=dict(text="Period", font=dict(color="white", size=12))
                ),
                yaxis=dict(
                    showgrid=False,
                    color="white",
                    tickfont=dict(size=11),
                    title=dict(text="Day", font=dict(color="white", size=12))
                ),
                margin=dict(l=0, r=0, t=20, b=10),
                height=380 
            )

            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No activity heatmap data available.")

      
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns([5, 5])

            with col1:
                
                x_names = [str(name) for name in x.index]

                fig_busy = px.bar(
                    x=x_names,
                    y=x.values,
                    text=x.values,
                    labels={'x': '', 'y': 'Messages'},
                    color=x.values,
                    color_continuous_scale='Viridis'
                )

                fig_busy.update_traces(
                    textposition='outside',
                    textfont=dict(color='white', size=11),
                    cliponaxis=False,
                    marker=dict(cornerradius=6),
                    hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>'
                )

                fig_busy.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False,
                    xaxis=dict(
                        type='category',  
                        showgrid=False,
                        color='white',
                        tickangle=-45,
                        tickfont=dict(size=11)
                    ),
                    yaxis=dict(showgrid=True, gridcolor='#262730', color='white', zeroline=False),
                    margin=dict(l=10, r=10, t=30, b=10),
                    height=380
                )
                st.plotly_chart(fig_busy, use_container_width=True)

            with col2:
               
                display_df = new_df.copy()

                if 'percent' in display_df.columns and 'count' in display_df.columns:
                    display_df = display_df.rename(columns={
                        'percent': 'User',
                        'count': 'Share (%)'
                    })
                elif len(display_df.columns) == 2:
                    display_df.columns = ['User', 'Share (%)']

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "User": st.column_config.TextColumn("User"),
                        "Share (%)": st.column_config.ProgressColumn(
                            "Share (%)",
                            format="%.2f%%",
                            min_value=0,
                            max_value=100
                        )

                    }
                )
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Export Table as CSV",
                    data=csv,
                    file_name=f"{selected_user}_busy_users.csv",
                    mime="text/csv",
                    key=f"download_{selected_user}_busy"
                )





        
        # Wordcloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)

        fig, ax = plt.subplots(figsize=(10, 5))

        # Make figure canvas background fully transparent
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

        # Render image
        ax.imshow(df_wc, interpolation='bilinear')

        # Hide axis lines, ticks, and tick numbers (0, 100, 200...)
        ax.axis('off')

        plt.tight_layout(pad=0)
        st.pyplot(fig)

        # Most Common Words or Symbols
        st.title('Most Common Words or Symbols')
        most_common_df = helper.most_common_words(selected_user, df)

        if not most_common_df.empty:
            # Ensure correct column naming whether helper returns a DataFrame with column names or positions
            words = most_common_df.iloc[:, 0].astype(str)
            counts = most_common_df.iloc[:, 1]

            fig_words = px.bar(
                x=counts,
                y=words,
                orientation='h',
                text=counts,
                labels={'x': 'Frequency', 'y': 'Words'},
                color=counts,
                # Vibrant Neon gradient (Cyan -> Electric Lime) matching the dark theme
                color_continuous_scale=['#00F5D4', '#70E000']
            )

            fig_words.update_traces(
                textposition='outside',
                textfont=dict(color='white', size=11),
                cliponaxis=False,
                marker=dict(cornerradius=6),
                hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
            )

            fig_words.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor='#262730', color='white', zeroline=False),
                yaxis=dict(type='category', showgrid=False, color='white', autorange='reversed'),
                # Keeps top word at the top
                margin=dict(l=10, r=40, t=10, b=10),
                height=550
            )

            st.plotly_chart(fig_words, use_container_width=True)
        else:
            st.info("No common words data available.")






        
        # Emoji analysis
        if selected_user == 'Overall':
            st.title("Emoji Analysis")
        else:
            display_name = "Your Profile" if selected_user == "You" else selected_user
            st.title(f"Emoji Analysis for {display_name}")

        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            col1, col2 = st.columns([5, 5])

            with col1:
                # Prepare table view without row index numbers
                display_emoji_df = emoji_df.copy()
                if len(display_emoji_df.columns) >= 2:
                    display_emoji_df.columns = ['Emoji', 'Count']

                st.dataframe(
                    display_emoji_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Emoji": st.column_config.TextColumn("Emoji"),
                        "Count": st.column_config.ProgressColumn(
                            "Count",
                            format="%d",
                            min_value=0,
                            max_value=int(display_emoji_df['Count'].max()) if not display_emoji_df.empty else 10
                        )
                    }
                )







                
                total_emojis = int(display_emoji_df['Count'].sum())
                top_emoji_char = display_emoji_df.iloc[0]['Emoji'] if not display_emoji_df.empty else "-"
                top_emoji_count = int(display_emoji_df.iloc[0]['Count']) if not display_emoji_df.empty else 0
                top_emoji_share = (top_emoji_count / total_emojis * 100) if total_emojis > 0 else 0

                st.markdown("---")
                m_col1, m_col2 = st.columns(2)

                with m_col1:
                    st.metric(
                        label="Total Emojis Used",
                        value=f"{total_emojis:,}"
                    )

                with m_col2:
                    st.metric(
                        label="Favorite Emoji",
                        value=f"{top_emoji_char}",
                        delta=f"{top_emoji_share:.1f}% share",
                        delta_color="normal"
                    )

            with col2:
                top_emojis = emoji_df.head(5).iloc[::-1].copy()
                top_emojis['Emoji'] = top_emojis['Emoji'].astype(str)

                fig_emoji = px.bar(
                    top_emojis,
                    x='Count',
                    y='Emoji',
                    orientation='h',
                    text='Count',
                    color='Count',
                    color_continuous_scale=['#00F5D4', '#70E000'],
                    labels={'Count': 'Usage', 'Emoji': ''}
                )

                fig_emoji.update_traces(
                    textposition='outside',
                    textfont=dict(color='white', size=12),
                    cliponaxis=False,
                    marker=dict(cornerradius=6),
                    hovertemplate='<b>Emoji:</b> %{y}<br><b>Count:</b> %{x}<extra></extra>'
                )





                
                num_items = len(top_emojis)
                calculated_height = 160 + (num_items * 40)

                fig_emoji.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=False, showticklabels=False, title=''),
                    yaxis=dict(
                        type='category',
                        showgrid=False,
                        title='',
                        tickfont=dict(size=20)
                    ),
                    margin=dict(l=10, r=40, t=10, b=10),
                    height=calculated_height
                )

                st.plotly_chart(fig_emoji, use_container_width=True)
        else:
            st.info("No emojis were used in this chat.")

#======================================================================
        # Response latency analysis
        if selected_user == 'Overall':
            st.title("Top Quickest Responders")
        else:
            display_name = "Your Profile" if selected_user == "You" else selected_user
            st.title(f"Response Speed for {display_name}")

        latency_df = helper.response_latency(selected_user, df)

        if not latency_df.empty:
            col1, col2 = st.columns([5, 5])

            with col1:
         
                display_latency_df = latency_df.rename(columns={'Avg_Response_Time_Mins': 'Median Delay (Mins)'}).copy()

                st.dataframe(
                    display_latency_df,
                    use_container_width=True,
                    hide_index=True, 
                    column_config={
                        "User": st.column_config.TextColumn("User"),
                        "Median Delay (Mins)": st.column_config.NumberColumn(
                            "Median Delay",
                            format="%.1f min",
                            alignment="left"
                        )
                    }
                )

            
                avg_delay = latency_df['Avg_Response_Time_Mins'].values[0] if not latency_df.empty else 0

                if avg_delay < 5:
                    badge = "Lightning Fast"
                elif avg_delay <= 15:
                    badge = "Active Responder"
                else:
                    badge = "Relaxed Pace"

                st.markdown("---")
                st.metric(
                    label="Average Delay Time",
                    value=f"{avg_delay:.1f} mins",
                    delta=badge,
                    delta_color="normal"
                )

            with col2:
                top_latency = latency_df.iloc[::-1].copy()
                top_latency['User'] = top_latency['User'].astype(str)

                fig_latency = px.bar(
                    top_latency,
                    x='Avg_Response_Time_Mins',
                    y='User',
                    orientation='h',
                    text='Avg_Response_Time_Mins',
                    color='Avg_Response_Time_Mins',
                    color_continuous_scale=['#00F5D4', '#70E000'],  # Vibrant neon theme
                    labels={'Avg_Response_Time_Mins': 'Median Delay (Minutes)', 'User': ''}
                )

                fig_latency.update_traces(
                    textposition='outside',
                    texttemplate='%{text:.1f} min',
                    textfont=dict(color='white', size=12),
                    cliponaxis=False,
                    marker=dict(cornerradius=6),
                    hovertemplate='<b>%{y}</b><br>Delay: %{x:.1f} mins<extra></extra>'
                )

                fig_latency.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=True, gridcolor='#262730', color='white', zeroline=False),
                    yaxis=dict(
                        type='category',  # Ensures user names render as discrete string categories
                        showgrid=False,
                        color='white',
                        tickfont=dict(size=12)
                    ),
                    margin=dict(l=10, r=60, t=10, b=10),
                    height=300 if len(latency_df) <= 2 else 380
                )

                st.plotly_chart(fig_latency, use_container_width=True)
        else:
            st.info("Insufficient message timing data to compute response latency.")




        
        st.title("Message Length vs. Volubility")

        volubility_df = helper.message_length_analysis(selected_user, df)

        if not volubility_df.empty:
            fig_scatter = px.scatter(
                volubility_df,
                x='total_messages',
                y='avg_words_per_message',
                size='total_messages',
                color='avg_words_per_message',
                hover_name='user',  # Clears text overlap by using mouse hover tooltips
                hover_data={
                    'total_messages': True,
                    'avg_words_per_message': ':.1f',
                    'user': False
                },
                color_continuous_scale='Viridis',
                labels={
                    'total_messages': 'Total Messages Sent',
                    'avg_words_per_message': 'Avg Words per Message'
                }
            )

           
            fig_scatter.update_traces(
                marker=dict(
                    sizemode='area',
                    sizeref=2 * max(volubility_df['total_messages']) / (30 ** 2),  # Standardized bubble scaling
                    sizemin=6,
                    opacity=0.85,
                    line=dict(width=1, color='white')
                )
            )

            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=True,  # Shows the Viridis colorbar scale
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Avg Words / Msg",
                        font=dict(color="white", size=12)
                    ),
                    tickfont=dict(color="white", size=11),
                    len=0.9
                ),
                xaxis=dict(showgrid=True, gridcolor='#262730', color='white', title='Total Messages Sent'),
                yaxis=dict(showgrid=True, gridcolor='#262730', color='white', title='Avg Words per Message'),
                margin=dict(l=10, r=20, t=20, b=10),
                height=450
            )

            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No volubility data available.")




        
        if selected_user != 'Overall':
            display_name = "Your Profile" if selected_user == "You" else selected_user
            st.title(f"Conversational Partners for {display_name}")

            replied_to_df, replied_by_df = helper.top_conversational_partners(selected_user, df)

            if not replied_to_df.empty or not replied_by_df.empty:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Who They Reply To Most")
                    if not replied_to_df.empty:
                        fig_to = px.bar(
                            replied_to_df.iloc[::-1],
                            x='Interactions',
                            y='Partner',
                            orientation='h',
                            text='Interactions',
                            color='Interactions',
                            color_continuous_scale='Viridis',
                            range_color=[0, max(replied_to_df['Interactions'].max(), 5)],
                            # Forces gradient scale even for 1s
                            labels={'Interactions': 'Replies Sent', 'Partner': ''}
                        )
                        fig_to.update_traces(
                            textposition='outside',
                            textfont=dict(color='white'),
                            cliponaxis=False
                        )
                        fig_to.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            coloraxis_showscale=False,
                            xaxis=dict(showgrid=False, color='white', dtick=1),
                            yaxis=dict(type='category', showgrid=False, color='white'),
                            margin=dict(l=10, r=50, t=10, b=10),
                            height=300
                        )
                        st.plotly_chart(fig_to, use_container_width=True)
                    else:
                        st.info("No reply data found.")

                with col2:
                    st.subheader("Who Replies To Them Most")
                    if not replied_by_df.empty:
                        fig_by = px.bar(
                            replied_by_df.iloc[::-1],
                            x='Interactions',
                            y='Partner',
                            orientation='h',
                            text='Interactions',
                            color='Interactions',
                            color_continuous_scale='Viridis',
                            range_color=[0, max(replied_by_df['Interactions'].max(), 5)],
                            # Forces gradient scale even for 1s
                            labels={'Interactions': 'Replies Received', 'Partner': ''}
                        )
                        fig_by.update_traces(
                            textposition='outside',
                            textfont=dict(color='white'),
                            cliponaxis=False
                        )
                        fig_by.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            coloraxis_showscale=False,
                            xaxis=dict(showgrid=False, color='white', dtick=1),
                            yaxis=dict(type='category', showgrid=False, color='white'),
                            margin=dict(l=10, r=50, t=10, b=10),
                            height=300
                        )
                        st.plotly_chart(fig_by, use_container_width=True)
                    else:
                        st.info("No incoming reply data found.")

                    

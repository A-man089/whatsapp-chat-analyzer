from urlextract import URLExtract
extract = URLExtract()
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
from collections import Counter
import emoji


def fetch_kpi_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    else:
        # Exclude system notifications for overall KPI calculations
        df = df[df['user'] != 'group_notification']

    total_messages = df.shape[0]
    total_words = df['message'].apply(lambda x: len(str(x).split())).sum()
    active_days = df['only_date'].nunique()

    avg_msgs_per_day = round(total_messages / active_days, 1) if active_days > 0 else 0

    return total_messages, total_words, active_days, avg_msgs_per_day







def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    #Fetch the number of messages
    num_messages = df.shape[0]

    # Fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch the number of media messages
    media_pattern = r'<.*?\bomitted\b.*?>|omitted'

    # FETCH THE NUMBER OF LINKS SHARED
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    num_media_messages = df[df['message'].str.contains(media_pattern, case=False, na=False)].shape[0]




    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df[df['user'] != 'group_notification']['user'].value_counts().head()
    df  = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df


def create_wordcloud(selected_user, df):
    # Your existing filtering / stop words logic here ...

    wc = WordCloud(
        width=1000,
        height=500,
        min_font_size=10,
        background_color='#0E1117',  # Matches Streamlit dark mode background
        colormap='viridis',  # Matches your Viridis dashboard theme
        collocations=False
    )

    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):

    with open('HINGLISH STOPWORDS.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in str(message).lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    if not emoji_df.empty:
        emoji_df.columns = ['Emoji', 'Count']

    return emoji_df


def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Pivot dataframe
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    # Clean up column names (e.g. '19-hour+1' -> '19:00 - 20:00')
    cleaned_columns = {}
    for col in user_heatmap.columns:
        col_str = str(col)
        if '-hour+1' in col_str:
            hour = int(col_str.split('-')[0])
            next_hour = (hour + 1) % 24
            cleaned_columns[col] = f"{hour:02d}:00 - {next_hour:02d}:00"
        else:
            cleaned_columns[col] = col_str

    user_heatmap = user_heatmap.rename(columns=cleaned_columns)

    return user_heatmap


def response_latency(selected_user, df):
    df_sorted = df.sort_values('date').copy()

    df_sorted['prev_user'] = df_sorted['user'].shift(1)
    df_sorted['prev_date'] = df_sorted['date'].shift(1)
    df_sorted['response_time'] = (df_sorted['date'] - df_sorted['prev_date']).dt.total_seconds() / 60.0

    replies = df_sorted[
        (df_sorted['user'] != df_sorted['prev_user']) &
        (df_sorted['user'] != 'group_notification') &
        (df_sorted['response_time'] <= 120) &
        (df_sorted['response_time'] > 0)
        ]

    if selected_user != 'Overall':
        replies = replies[replies['user'] == selected_user]

    if replies.empty:
        return pd.DataFrame(columns=['User', 'Avg_Response_Time_Mins'])

    latency_df = replies.groupby('user')['response_time'].median().reset_index()
    latency_df.columns = ['User', 'Avg_Response_Time_Mins']
    latency_df['Avg_Response_Time_Mins'] = latency_df['Avg_Response_Time_Mins'].round(1)

    # Force string type so Plotly treats phone numbers as text labels
    latency_df['User'] = latency_df['User'].astype(str)

    return latency_df.sort_values('Avg_Response_Time_Mins').head(10)


def message_length_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp['word_count'] = temp['message'].apply(lambda x: len(str(x).split()))

    volubility_df = temp.groupby('user').agg(
        total_messages=('message', 'count'),
        avg_words_per_message=('word_count', 'mean')
    ).reset_index()

    volubility_df['avg_words_per_message'] = volubility_df['avg_words_per_message'].round(1)

    # Ensure User column is string for clean tooltips
    volubility_df['user'] = volubility_df['user'].astype(str)

    return volubility_df


def top_conversational_partners(selected_user, df):
    # This feature only applies when an individual user is selected
    if selected_user == 'Overall':
        return pd.DataFrame(), pd.DataFrame()

    df_sorted = df.sort_values('date').copy()

    # Identify previous and next message senders and timestamps
    df_sorted['prev_user'] = df_sorted['user'].shift(1)
    df_sorted['prev_date'] = df_sorted['date'].shift(1)

    df_sorted['next_user'] = df_sorted['user'].shift(-1)
    df_sorted['next_date'] = df_sorted['date'].shift(-1)

    # Calculate time differences in minutes
    df_sorted['time_since_prev'] = (df_sorted['date'] - df_sorted['prev_date']).dt.total_seconds() / 60.0
    df_sorted['time_to_next'] = (df_sorted['next_date'] - df_sorted['date']).dt.total_seconds() / 60.0

    # Filter valid interactions (exclude self-replies, group notifications, and gaps > 60 mins)
    valid_interactions = df_sorted[df_sorted['user'] == selected_user]

    # 1. Who selected_user replies to
    replied_to = valid_interactions[
        (valid_interactions['prev_user'].notnull()) &
        (valid_interactions['prev_user'] != selected_user) &
        (valid_interactions['prev_user'] != 'group_notification') &
        (valid_interactions['time_since_prev'] <= 60)
        ]
    replied_to_df = replied_to['prev_user'].value_counts().reset_index()
    replied_to_df.columns = ['Partner', 'Interactions']
    replied_to_df['Partner'] = replied_to_df['Partner'].astype(str)

    # 2. Who replies to selected_user
    replied_by = valid_interactions[
        (valid_interactions['next_user'].notnull()) &
        (valid_interactions['next_user'] != selected_user) &
        (valid_interactions['next_user'] != 'group_notification') &
        (valid_interactions['time_to_next'] <= 60)
        ]
    replied_by_df = replied_by['next_user'].value_counts().reset_index()
    replied_by_df.columns = ['Partner', 'Interactions']
    replied_by_df['Partner'] = replied_by_df['Partner'].astype(str)

    return replied_to_df.head(5), replied_by_df.head(5)

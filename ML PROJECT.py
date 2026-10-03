import re
import pandas as pd

def preprocess(data):
    pattern = r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\](?:\s-\s|\s)'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date type
    # Cell 53
    # Clean trailing hyphens or spaces from date strings before parsing
    df['message_date'] = df['message_date'].str.extract(r'(\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\])')
    df['message_date'] = pd.to_datetime(df['message_date'], format='[%m/%d/%y, %I:%M:%S %p]')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []



    # Ensure we use user_message column if present
    source_column = 'user_message' if 'user_message' in df.columns else 'message'

    for message in df[source_column]:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    if 'user_message' in df.columns:
        df.drop(columns=['user_message'], inplace=True)

        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

    return df
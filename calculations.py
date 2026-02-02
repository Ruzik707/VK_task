import pandas as pd
import numpy as np

data = pd.read_excel('data.xlsx', index_col=0)

working_data = data.copy()
working_data['date'] = working_data['session_start'].dt.date
working_data['session_duration_in_minutes'] = (working_data['session_end'] - working_data['session_start']).dt.total_seconds() / 60

# 1
unique_users_per_day = working_data.groupby('date')['user_id'].nunique()

# 2
session_count_in_platforms = working_data.groupby('platform').count()['user_id']

# 3
mean_platforms_duration = working_data.groupby('platform')['session_duration_in_minutes'].mean().round(2)

# 4
data_notna_in_isnewuser = working_data[working_data['is_new_user'].notna()]
per_of_new_users_sessions = (data_notna_in_isnewuser['is_new_user'].sum() / len(data_notna_in_isnewuser)).round(4)

# 5
old_users = working_data[working_data['is_new_user'] == 0]
new_users = working_data[working_data['is_new_user'] == 1]

old_dur_median = old_users['session_duration_in_minutes'].median()
new_dur_median = new_users['session_duration_in_minutes'].median()

# 6
sum_dur_in_countries = working_data.groupby('country')['session_duration_in_minutes'].sum()
sum_dur_in_RU = sum_dur_in_countries['RU']

results = []

for date, count in unique_users_per_day.items():
    results.append({
        'Метрика': 'Уникальные пользователи в день',
        'Подраздел': date,
        'Значение': int(count),
        'Единица': 'пользователей'
    })

for platform, count in session_count_in_platforms.items():
    results.append({
        'Метрика': 'Количество сессий по платформам',
        'Подраздел': platform,
        'Значение': int(count),
        'Единица': 'сессий'
    })

for platform, duration in mean_platforms_duration.items():
    results.append({
        'Метрика': 'Средняя длительность сессии',
        'Подраздел': platform,
        'Значение': float(duration),
        'Единица': 'минут'
    })

results.append({
    'Метрика': 'Доля сессий новых пользователей',
    'Подраздел': 'Общая',
    'Значение': float(per_of_new_users_sessions),
    'Единица': '%',
    'Примечание': f'Рассчитано по {len(data_notna_in_isnewuser)} сессиям с известным статусом'
})

results.append({
    'Метрика': 'Медиана длительности сессий',
    'Подраздел': 'Новые пользователи',
    'Значение': float(new_dur_median),
    'Единица': 'минут'
})

results.append({
    'Метрика': 'Медиана длительности сессий',
    'Подраздел': 'Старые пользователи',
    'Значение': float(old_dur_median),
    'Единица': 'минут'
})

results.append({
    'Метрика': 'Суммарное время в стране RU',
    'Подраздел': 'Всего',
    'Значение': float(sum_dur_in_RU),
    'Единица': 'минут'
})

results_df = pd.DataFrame(results)

with pd.ExcelWriter('results_analysis.xlsx', engine='openpyxl') as writer:
    
    working_data.to_excel(writer, sheet_name='Исходные данные', index=False)
    results_df.to_excel(writer, sheet_name='Метрики', index=False)


    explanation = pd.DataFrame({
        'Метрика': [
            'Уникальные пользователи в деньё',
            'Количество сессий по платформам',
            'Средняя длительность сессии',
            'Доля сессий новых пользователей',
            'Медиана длительности сессий',
            'Суммарное время в стране RU'
        ],
        'Как считал': [
            'Группировка по дате + подсчет количества уникальных user_id',
            'Группировка по платформе + подсчет количества строк',
            'Группировка по платформе → среднее от столбца "session_duration_in_minutes"',
            'Сумма is_new_user=1 / количество строк не пустых is_new_user ',
            'Разделил данные на новых и старых (0) + подсчет медианы',
            'Группировка по стране + подсчет суммы сессий и выбор "RU" региона'
        ],
        'Обработка NULL': [
            'NULL в user_id исключены',
            'NULL в platform учтены как отдельная категория',
            'NULL в duration исключены',
            'NULL в is_new_user исключены из расчёта',
            'NULL в is_new_user исключены',
            'NULL в country не считаются за RU'
        ],
        'Интерпретация полученных результатов': [
            'Показывает ежедневную аудиторию сервиса. Рост числа - хороший показатель. Сравнение по дням выявляет пики активности',
            'Показывает нагрузку на инфраструктуру. Примерно у всех одинаково - нужно оптимизировать под все три операционные системы. ',
            'Показатель вовлеченности. IOS выше всех - возможно, игры лучше оптимизированы под Apple',
            'Высокий процент новых пользователей (~30%), но возможно это было в дни акций, скидок - нужно смотреть на другие дни (чем больше тем лучше)',
            'Нет особо большой разницы между новыми и старыми пользователями (31.5 и 32), все одинаково вовлечены в игру',
            'В сравнении с другими странами Россия лидирует. 21589 минут - это почти 360 часов игры за 3 дня!'
        ]
    })
    explanation.to_excel(writer, sheet_name='Объяснения', index=False)


#!/usr/bin/env python
# coding: utf-8

# <font color='blue'> Привет!)Ты проделал большую работу. Молодец, что пишешь много комментариев, это очень помогает понимать твои выводы.  Далее в файле ты можешь найти мои комменатрии, выделенные синим. Пожайлуста, постарайся учесть их в дальнейших проектах.</font>

# ## Исследование надёжности заёмщиков
# 
# Заказчик — кредитный отдел банка. Нужно разобраться, влияет ли семейное положение и количество детей клиента на факт погашения кредита в срок. Входные данные от банка — статистика о платёжеспособности клиентов.
# 
# Результаты исследования будут учтены при построении модели **кредитного скоринга** — специальной системы, которая оценивает способность потенциального заёмщика вернуть кредит банку.

# ### Шаг 1. Откройте файл с данными и изучите общую информацию. 

# In[51]:


import pandas as pd
import math
from datetime import datetime

df = pd.read_csv('/datasets/data.csv')

print ('Анализируем общую информацию по таблице:')
print (df.info())
print ('\nВизуально анализируем прочитанную таблицу:')
print (df.head())
print ('\nИщем логические несоответствия в данных:')
print ('\nВозраст клиента меньше 18:')
print (df[df['dob_years'] < 18]['dob_years'].value_counts())
print ('\nКоличество детей больше 10:')
print (df[df['children'] > 10]['children'].value_counts())
print ('\nОтрицательная зарплата:')
print (df[df['total_income'] < 0.0]['total_income'].value_counts())


# ### Вывод

# #### В таблице 21 525 записей.
# 
# #### Обнаруженные проблемы:
# 1. Есть пропуски в столбцах "days_employed" и "total_income".
# 2. Не все типы данных в столбцах соответствуют истине:
#    Столбец "days_employed" имеет тип float64, хотя, должен быть int64 - в стаже работы не учитываются "половинки" и "четвертинки" дней. Также в этом  столбце не может быть отрицательных значений.
# 3. Не все данные в столбцах имеют одинаковый вид:
#    Столбец "education" имеет запись об образовании "среднее" и "Среднее", что не одно и то же при поиске уникальных значений.
# 4. В столбцах типа "float", в которых хранится количество денег, должно быть округление до сотен, т.к. денюжки считаются до копеек.
# 5. Столбцы "education", "family_status" и "income_type" являются строковыми и содержат однотиповые значения - такой подход увеличивает время обработки данных, поэтому записи в этих столбцах нужно преобразовать в словари, заменив строковое значение на ID записи словаря.
# 6. В столбце "dob_years" (возраст клиента) присутстуют нули - насколько знаю, младенцам кредиты не дают, нужно исправить данные.
# 7. В столбце "children" присутствует значение "20" аж у 76 персон - вероятно, ошибка. Слишком много детей на одного человека.

# <font color='blue'> Отличные, очень подробные выводы.</font>

# ### Шаг 2. Предобработка данных

# ### Обработка пропусков

# In[56]:


print ('Проверяем количество пропусков для стажа работы:')
print (df['days_employed'].isna().sum())

print ('\nПроверяем количество пропусков для ежемесячного дохода:')
print (df['total_income'].isna().sum())

print ('\nПроверяем количество записей с нулями в годах')
print (df[df['dob_years'] == 0]['dob_years'].count())

print ('\nИщем визуально зависимости пропусков от данных:')
print (df[df['days_employed'].isna() | df['total_income'].isna()].head())

print ('\nСписок категорий с пропущенными значениями возраста:')
print (df[df['dob_years'] == 0]['income_type'].value_counts())

print ('\nИщем средние значения возраста для каждой категории:')
employee_age  = df[df['income_type'] == 'сотрудник']['dob_years'].median().astype(int)
companion_age = df[df['income_type'] == 'компаньон']['dob_years'].median().astype(int)
oldermen_age  = df[df['income_type'] == 'пенсионер']['dob_years'].median().astype(int)
employee_gov_age = df[df['income_type'] == 'госслужащий']['dob_years'].median().astype(int)
print (f'сотрудник: {employee_age}\nкомпаньон: {companion_age}\nпенсионер: {oldermen_age}\nгосслужащий: {employee_gov_age}')

df.loc[(df['income_type'] == 'сотрудник') & (df['dob_years'] == 0), 'dob_years'] = employee_age
df.loc[(df['income_type'] == 'компаньон') & (df['dob_years'] == 0), 'dob_years'] = companion_age
df.loc[(df['income_type'] == 'пенсионер') & (df['dob_years'] == 0), 'dob_years'] = oldermen_age
df.loc[(df['income_type'] == 'госслужащий') & (df['dob_years'] == 0), 'dob_years'] = employee_gov_age

print (df[df['dob_years'] == 0]['income_type'].count())

print ("\nУбираем дубли в уровне образование - по ним будем считать кол-во отработанных дней")
df.loc[(df['education'] == 'СРЕДНЕЕ') | (df['education'] == 'Среднее'), 'education'] = 'среднее'
df.loc[(df['education'] == 'ВЫСШЕЕ') | (df['education'] == 'Высшее'), 'education'] = 'высшее'
df.loc[(df['education'] == 'НЕОКОНЧЕННОЕ ВЫСШЕЕ') | (df['education'] == 'Неоконченное высшее'), 'education'] = 'неоконченное высшее'
df.loc[(df['education'] == 'УЧЕНАЯ СТЕПЕНЬ') | (df['education'] == 'Ученая степень'), 'education'] = 'ученая степень'
df.loc[(df['education'] == 'НАЧАЛЬНОЕ') | (df['education'] == 'Начальное'), 'education'] = 'начальное'

def get_age_type(age):
    """Разбиваем всех заемщиков на блоки по возрасту:"""
    if age < 30:
        return 'молодежь'
    if age < 50:
        return 'работяги'
    return 'пенсионеры'

def fill_total_income(df, income_type_list, age_type_list):
    """Заполняем пропущенные значения в ЗП, разбиваем по категориям работы и возрасту"""
    for income_type in income_type_list:
        for age_type in age_type_list:
            
            median = df.loc[
                (df['total_income'].notna()) 
                & (df['total_income'] > 0.0) 
                & (df['income_type'] == income_type) 
                & (df['age_type'] == age_type)
            ]['total_income'].median()
            
            if not math.isnan(median):
                df.loc[
                    (
                        (df['total_income'].isna() 
                         | (df['total_income'] == 0.0) 
                         | (df['total_income'] < 0.0))
                    ) 
                    & (df['income_type'] == income_type) 
                    & (df['age_type'] == age_type), 
                    'total_income'
                ] = median
    return df

def fill_days_employed(df, education_type_list, age_type_list):
    """Заполняем пропущенные значения в стаже работы, разбиваем по образованию и возрасту"""
    for education_type in education_type_list:
        for age_type in age_type_list:
            
            mean = df.loc[
                (df['days_employed'].notna()) 
                & (df['days_employed'] > 0.0) 
                & (df['education'] == education_type) 
                & (df['age_type'] == age_type)
            ]['days_employed'].mean()
            
            if not math.isnan(mean):
                df.loc[
                    (
                        df['days_employed'].isna() 
                        | (df['days_employed'] == 0.0) 
                        | (df['days_employed'] < 0.0)
                    ) 
                    & (df['education'] == education_type) 
                    & (df['age_type'] == age_type), 
                    'days_employed'
                ] = mean
            else:
                mean = df.loc[
                (df['days_employed'].notna()) 
                & (df['days_employed'] > 0.0) 
                & (df['age_type'] == age_type)
            ]['days_employed'].mean()
                if not math.isnan(mean):
                    df.loc[
                        (
                            df['days_employed'].isna() 
                            | (df['days_employed'] == 0.0) 
                            | (df['days_employed'] < 0.0)
                        ) 
                        & (df['age_type'] == age_type), 
                        'days_employed'
                    ] = mean
    return df

df['age_type'] = df['dob_years'].apply(get_age_type)
income_type_list    = df['income_type'].value_counts().index.tolist()
age_type_list       = df['age_type'].value_counts().index.tolist()
education_type_list = df['education'].value_counts().index.tolist()

df = fill_total_income(df, income_type_list, age_type_list)
df = fill_days_employed(df, education_type_list, age_type_list)

print ("\nПроверяем количество пропусков в уровне образования:")
print (df['education'].value_counts())

print ("\nПроверяем количество пропусков в столбце \"пол\":")
print (df['gender'].value_counts())
print ("\nЗаменяем значение \"XNA\" столбце \"пол\" на \"F\":")
df.loc[df['gender'] == "XNA", 'gender'] = "F"

print ("\nОбрабатываем последнюю незаполненную автоматически запись")
df.loc[(df['income_type'] == 'предприниматель') & (df['age_type'] == 'пенсионеры'), 'total_income'] = df[(df['total_income'].notna()) & (df['income_type'] == 'предприниматель')]['total_income'].median()
print ("\nПроверяем наличие пропусков в таблице:")
print (df.info())

print ("\nИщем тех, у кого слишком много или слишком мало детей")
print (df[(df['children'] < 0) | (df['children'] > 10)]['children'].value_counts())

print ("\nМеняем неверные значения:")
df.loc[df['children'] < 0, 'children'] = 0
df.loc[df['children'] == 20, 'children'] = 2


# ### Вывод

# Обнаруженные пропуски были в строках "dayes_employed" и "total_income" - видимо, не была получена информация о работодателе и/или люди умышленно пропустили этот пункт в заявке на кредит.
# 
# Чтобы заполнить пропуски данными, которые будут похожи на истину, нужно:
# 1. Разделить всех людей на группы по возрасту, ведь в зависимости от возраста кол-во отработанных дней и зп (у многих) повышается.
# 2. Разделить всех по уровню образования - очень часто уровень образования прямо влияет на должность и на зарплату.
# 3. Разделить всех по типу занятости - в каждой категории уровень зарплаты может варьироваться и медианное значение будет сильно отличаться.
# 
# Функция "**get_age**" разбивает на категории по возрасту всех записи.
# 
# Функция "**fill_total_income**" заполняет пропущенные значения по уровню ЗП. На вход подается DataFrame, список типа занятости и список возрастных категорий. В итоге для каждого типа занятости и для каждого возраста в этом типе находится медианное значение уровня ЗП. Медиана взята потому, что деньги неправльно считать средним - один человек с уровнем ЗП 100500 может сильно испортить статистику.
# 
# Функция "**fill_days_employed**" заполняет пропещенные значения количества отработанных дней. На вход подается DataFrame, список по типу образования и список по категориям возраста. Список по типу образования позволяет отсеить тех, кто учился дольше. Внутри этого списка данные разбиваются по возрастным категориям и среди них ищется среднее значение. В данной выборке среднее значение можно брать, так как точно не будет тех, кому больше 100 лет :)
# 
# Проверяем наличие пропусков - вуаля. 
# 
# В рамках этого задания найдено непонятное значение XNA в столбце с полом. Заменено на "F", так как девочек больше.
# 
# В рамках этого задания найдены непонятные числа в столбце "children". "-1" похоже на системную ошибку, а 20 на человеческую. Системную ошику заменили на 0, а 20 на 2 (дюди могли нажимать "0" по ошибке).
# 
# Все заполнено.

# <font color='blue'> Очень подробная работа, хотя она слегка излишня. Здесь достаточно было посмотреть, чем заполнять пропуски - 0, медианы или среднии или еще что и обмотивировать свой выбор.</font><br>
# <font color='green'>Данную часть решил оставить без изменений</font>

# ### Замена типа данных

# In[57]:


print ("\nЗаменяем тип данных в столбцах: \"days_employed\", \"total_income\"")
df['days_employed'] = df['days_employed'].astype(int)
print ("\nОкругляем ЗП до копеек")
df['total_income'] = df['total_income'].astype(int)
print ("\nПроверяем информацию: ")
print (df.info())


# ### Вывод

# В столбцах "days_employed" и "total_income" меняем тип данных с float64 на int64. Человек не может быть устроен пол дня с четвертинкой, а ЗП можно спокойно округлять до целых чисел - в дальнейшем сравнении и категоризации копейки ни на чтоне повлияют.
# Замена типа данных проводится методом "**astype**", которому передается значение нового типа данных.

# <font color='blue'> Здесь подразумевается только использование astype(). Вся остольная работа излишняя и л должна быть выполнена далее, например, введение словарей - это категоризация. Так читать проект очень сложно, хотя работа выглядит очень масштабно. </font><br><font color="green">Исправлено</font>

# ### Обработка дубликатов

# In[58]:


print ("\nИщем дубли среди данных: ")
print (df.duplicated().value_counts())

print ("\nПросматриваем дубли: ")
print (df[df.duplicated()].head())

print ("\nУдаляем дубликаты")
df = df.drop_duplicates().reset_index(drop=True)

print ("\nПроверяем, что дубликаты удалились: ")
print (df.duplicated().value_counts())


# ### Вывод

# Ищем дубли стандартным методом библиотеки "Pandas" "duplicated()" и подсчитываем уникальные значение методом "value_counts()". Как видно у нас 71 дубль - это значение, которым соответствует запись "True".
# 
# Просмотрим дубликаты - действительно, видно, что записи повторяются. Пример: строки с индексом **3290** и **5557**.
# 
# Дублей не много, можем смело их удалить методом "drop_duplicates" и пересборкой индекса методом "reset_index(drop=True)".
# 
# Проверяем наличи дублей теми же методами - записи "Ttrue" для метода поиска дублей нет, т.е. дублей 0.

# <font color='blue'> Так не понятно, что с дубликатами? Их 21525? Если этот метод не подходит, то какой подходит? Здесь надо вывести количество дубликатов, удалить дубликаты и вывести новое количество дубликатов, которое должно стать равно 0.</font><br><font color='green'>Исправлено</font>

# ### Лемматизация

# In[59]:


from pymystem3 import Mystem
from collections import Counter
m = Mystem()

purposes = df['purpose'].value_counts().index.tolist()
lem = m.lemmatize(','.join(purposes))
lem = Counter(lem).most_common()
print (lem)


# ### Вывод

# Выше выедены наиболее часто используемые леммы слов в графе "Цель кредита". Большинство вариантов связаны со следующими категориями:
# 
# - Недвижимость: [недвижимость, жилье, строительство, сделка, жилой, сдача, недвижимость, коммерческий, жилой]
# - Авто: [автомобиль, подержанный, сдача]
# - Свадьба: [свадьба, семья, сыграть]
# - Образование: [образование]

# <font color='blue'> Лемматизация выполнена хорошо - это самая сложная часть проекта.</font>

# ### Категоризация данных

# In[60]:


print ("\nСоздаем словари для замены одинаковых значений в строках")
family_status_list  = df['family_status'].value_counts().index.tolist()
gender_type_list    = df['gender'].value_counts().index.tolist()
purpose_type_list   = ['свадьба', 'авто', 'недвижимость', 'образование']

age_type_dict       = pd.DataFrame(age_type_list, columns=['age_type'])
income_type_dict    = pd.DataFrame(income_type_list, columns=['income_type'])
education_type_dict = pd.DataFrame(education_type_list, columns=['education_type'])
family_status_dict  = pd.DataFrame(family_status_list, columns=['family_status'])
gender_type_dict    = pd.DataFrame(gender_type_list, columns=['gender_type'])
purpose_type_dict   = pd.DataFrame(purpose_type_list, columns=['purpose_type'])

def get_dict_idx(value, current_df, column):
    """Выборка индекса словаря по значению поля"""
    return current_df[current_df[column] == value].index.values.astype(int)[0]

print (f"\n{datetime.now().strftime('%H:%M:%S')} Начало добавления столбцов по словарям... (процесс может выполняться минуту)")
df['income_type_idx'] = df['income_type'].apply(get_dict_idx, current_df=income_type_dict, column='income_type')
print (f"\n{datetime.now().strftime('%H:%M:%S')} Обработан словарь \"Тип занятости\"")

df['age_type_idx'] = df['age_type'].apply(get_dict_idx, current_df=age_type_dict, column='age_type')
print (f"\n{datetime.now().strftime('%H:%M:%S')} Обработан словарь \"Тип возраста\"")

df['education_type_idx'] = df['education'].apply(get_dict_idx, current_df=education_type_dict, column='education_type')
print (f"\n{datetime.now().strftime('%H:%M:%S')} Обработан словарь \"Уровень образования\"")

df['family_status_idx']  = df['family_status'].apply(get_dict_idx, current_df=family_status_dict, column='family_status')
print (f"\n{datetime.now().strftime('%H:%M:%S')} Обработан словарь \"Семейный статус\"")

df['gender_type_idx'] = df['gender'].apply(get_dict_idx, current_df=gender_type_dict, column='gender_type')
print (f"\n{datetime.now().strftime('%H:%M:%S')} Обработан словарь \"Пол\"")

df.loc[df['purpose'].str.contains('свадьб') | df['purpose'].str.contains('семь') | df['purpose'].str.contains('сыграть'), 'purpose_type_idx'] = 0
df.loc[df['purpose'].str.contains('автомобил') | df['purpose'].str.contains('подержа'), 'purpose_type_idx'] = 1
df.loc[df['purpose'].str.contains('недвижим') | df['purpose'].str.contains('жил') | df['purpose'].str.contains('строит') | df['purpose'].str.contains('коммерч'), 'purpose_type_idx'] = 2
df.loc[df['purpose'].str.contains('образован'), 'purpose_type_idx'] = 3
df['purpose_type_idx'] = df['purpose_type_idx'].astype(int)
print ("\nДобавлены значения словаря \"Цель кредита\"")
       
df.drop(columns=['income_type', 'age_type', 'education', 'family_status', 'gender', 'purpose'], inplace=True)
print (f"\n{datetime.now().strftime('%H:%M:%S')} Столбцы по словарям добавлены")
print ("\nУдалены столбцы со строковыми значениями")
print (df.info())
       
print ("\nРаспределяем всех по уровню дохода на 5 квантилей")       
income_level_list = ['Верхний', 'Четвертый', 'Средний', 'Второй', 'Нижний']
income_level_dict = pd.DataFrame(income_level_list, columns=['income_level'])
       
one_percent = int (df.shape[0] / 100)
level1 = int (one_percent * 80)
level2 = int (level1 - (one_percent * 20))
level3 = int (level2 - (one_percent * 20))
level4 = int (level3 - (one_percent * 20))

print ("\nСортируем всех по уровню дохода. Самые богатые внизу таблицы.")
df.sort_values("total_income", inplace=True)
df.reset_index(drop=True, inplace=True)

df['income_level_idx'] = 0
df.iloc[0:level4, df.columns.get_loc('income_level_idx')] = 4
df.iloc[level4:level3, df.columns.get_loc('income_level_idx')] = 3
df.iloc[level3:level2, df.columns.get_loc('income_level_idx')] = 2
df.iloc[level2:level1, df.columns.get_loc('income_level_idx')] = 1
print ("\nСмотрим среднее значение по каждому квантилю: ")
print (df.groupby('income_level_idx')['total_income'].mean())


# ### Вывод

# Добавили всевозможные категории и словари по этим категориям.
# Список категорий:
# 
# - Тип занятости
#   - сотрудник
#   - компаньон
#   - пенсионер
#   - госслужащий
# - Тип возраста
#   - молодежь
#   - работяги
#   - пенсионеры
# - Уровень образования
#   - среднее
#   - высшее
#   - неоконченное высшее
#   - начальное
#   - ученая степень 
# - Семейный статус
#   - женат / замужем
#   - гражданский брак
#   - Не женат / не замужем
#   - в разводе
#   - вдовец / вдова
# - Пол
#   - F
#   - M
# - Цель кредита
#   - Недвижимость
#   - Авто
#   - Образование
#   - Свадьба
#   
# В процессе выделения категорий и разбития на словари избавились от всех строковых столбцов в датасете.
# Сделана категоризация по уровню дохода. Все уровни разбиты на 5 стандратных квантилей - т.е. все отсортированы в порядке возрастания ЗП, и общее количество поровну разделено на 5 частей. head() - бедные, tail() - богатые. <br>
# --- P.S. Понятие "Квантиль" нагуглено на [этом сайте](https://economics.studio/ekonomicheskaya-teoriya/kolichestvennoe-opredelenie-neravenstva-86651.html) ---

# <font color='blue'> Технически категоризация выполнена хорошо. Однако:</font>
# 
# <font color='blue'> 1. не очень понятен выбор уровней отсечения для дохода, это лучше пояснять, обычно берут квантили. </font>
# 
# <font color='blue'> 2. делать категоризацию имеет смысл только для дохода и для целей кредита. Для других параметров нет смысла делать категории - это ограничивает данные. Например, ты хочешь посмотреть данные для 2 или 3 детей, возможно, там есть разница, а этих данных уже нет, они слиты в "дети есть" </font>
# 
# <font color='blue'> 3. для характеристик типа образование, семейное положение и.т.п - следует вводить словари, т.е. в датасэте оставить только коды, а описательную часть вынести в отдельные таблицы. Это сократить датасэт и упростит работу с ним. </font>
# 
# <font color='green'>Исправлено</font>

# ### Шаг 3. Ответьте на вопросы

# - Есть ли зависимость между наличием детей и возвратом кредита в срок?

# In[94]:


def get_percentage(row):
    percent = f"{(row[1] * 100 / (row[0] + row[1])):.2f}%"
    return (percent)

print ("\nПроверяем зависимость наличия детей и кредитной истории: \n")
pivot_table = df.pivot_table(index=['children'], columns='debt', values='total_income', aggfunc='count')
pivot_table.rename(columns={0:'Не_имел_задолженности',1:'Имел_задолженность'}, inplace=True)
pivot_table['Процент_должников'] = pivot_table.apply(get_percentage, axis=1)
print (pivot_table)

children_min_percent = 7.53
children_max_percent = 9.76


# ### Вывод

# Согласно вышеприведенным данным, процент должников среди бездетных клиентов намного ниже, чем у клиентов с детьми. Причем, не важно, детей много или мало - процент должников везде одинаковый.
# 
# #### Итог:
# 
# У бездетных семей шанс вернуть кредит в срок выше, чем у многодетных.

# - Влияет ли семейное положение на возврат кредита в срок?

# In[87]:


pivot_table = df.pivot_table(index=['family_status_id'], columns='debt', values='total_income', aggfunc='count').astype(int)
pivot_table.rename(columns={0:'Не_имел_задолженности',1:'Имел_задолженность'}, index=family_status_dict['family_status'], inplace=True)
pivot_table['Процент_должников'] = pivot_table.apply(get_percentage, axis=1)
print (pivot_table)

family_min_percent = 6.57
family_max_percent = 9.75


# ### Вывод

# Минимальный процент должников у людей не связанных узами брака.
# Максимальный процент должников среди вдовцов (у них горе, какой там кредит).

# - Есть ли зависимость между уровнем дохода и возвратом кредита в срок?

# In[88]:


pivot_table = df.pivot_table(index=['income_level_idx'], columns='debt', values='total_income', aggfunc='count').astype(int)
pivot_table.rename(columns={0:'Не_имел_задолженности',1:'Имел_задолженность'}, index=income_level_dict['income_level'], inplace=True)

pivot_table['Процент_должников'] = pivot_table.apply(get_percentage, axis=1)
print (pivot_table)

income_min_percent = 7.06
income_max_percent = 8.86


# ### Вывод

# Безусловно, у категории людей с высоким заработком самый низкий процент задолженности.
# 
# Самый низкий процент должников: Верхний квантиль.
# Самый высокий процент должников: Средний квантиль.
# 
# Интеерсно, что люди с самым низким уровнем дохода (Нижний квантиль) бывают должны банку не так часто, как другие квантили.
# Вероятно, на возврат кредита в срок влияет не только уровень заработка.

# - Как разные цели кредита влияют на его возврат в срок?

# In[89]:


pivot_table = df.pivot_table(index=['purpose_type_idx'], columns='debt', values='total_income', aggfunc='count').astype(int)
pivot_table.rename(columns={0:'Не_имел_задолженности',1:'Имел_задолженность'}, index=purpose_type_dict['purpose_type'], inplace=True)

pivot_table['Процент_должников'] = pivot_table.apply(get_percentage, axis=1)
print (pivot_table)

purpose_min_percent = 7.23
purpose_max_percent = 9.36


# ### Вывод

# Меньше всего должников среди тех, кто берет ипотеку на жилье. И дейстительно, если вы решили взять ипотеку, то, наверняка, подготовили стратегию возврата, разные варианты финансовых подушек6 либо, просто настроены пахать как кролик, чтобы купить уже эту квартирку.
# 
# Другой случай с кредитами на авто и образование - там сумму довольно небольшие, в сравнении с ипотекой на жилье, поэтому, о таком кредите легче забыть, можно пару раз не платить, чтобы потом одним платежом закрыть, либо сначала заработать денег с помощью авто или мозгов, и потом уже отдавать этим ваши кредиты.

# <font color='blue'> Отличный выводы, только не хватает цифр, процентов - это главная задача аналитика</font><br>
# <font color='green'>В каждую таблицу добавлены проценты для наглядного сравнения</font>

# ### Шаг 4. Общий вывод

# ## Влияет ли семейное положение и наличие детей на возврат кредита в срок?
# 
# ### Да, вляет.
# 
# В данной работе были произведены следующие работы:
# - Изучение данных
# - Первичная обработка данных
# - Категоризация данных
# - Были видвинуты гипотезы по возможным пропускам и некорректным данным
# - Были даны ответы на вопросы касательно способности вовремя возвращать кредит у разных категорий людей.
# 
# #### По результатам исследоватльского анализа, выявлена следующая закономерность:
# 
# - Лучше всего возвращают кредит
#   - Не женатые
#   - Бездетные
#   - С высоким уровнем заработка
#   - Берущие кредит на недвижимость
#   
# - Хуже всего возвращают кредит:
#   - Вдовцы
#   - Многодетные
#   - Со средним уровнем заработка
#   - Берущие кредит на образование или авто
#   
# Визуальное представление ниже:

# In[110]:


print ("Процент должников среди выделенных категорий. Максимальный и минимальный проценты.")
print (f"\nПо семейному статусу:\nНе женатые: {children_min_percent:}%\nВдовцы:     {children_max_percent}%")
print (f"\nПо наличию детей:\nБездетные:   {family_min_percent:}%\nМногодетные: {family_max_percent}%")
print (f"\nПо уровню заработка:\nВысокий уровень заработка: {income_min_percent:}%\nСредний уровень заработка: {income_max_percent}%")
print (f"\nПо целяем кредита:\nКредит на недвижимость:       {purpose_min_percent:}%\nКредит на образование или авто: {purpose_max_percent}%")


# <font color='blue'> В общих выводах лучше в кратце описать весь проект. В итогах тоже можно привести цифры, все-таки это выглядело бы удобнее для заказчика -- вдруг он сразу решит прочитать только итог, не читая предыдущих рассуждений?) </font><br>
# <font color='green'>Исправлено</font>

# ### Чек-лист готовности проекта
# 
# Поставьте 'x' в выполненных пунктах. Далее нажмите Shift+Enter.

# - [x]  открыт файл;
# - [x]  файл изучен;
# - [x]  определены пропущенные значения;
# - [x]  заполнены пропущенные значения;
# - [x]  есть пояснение какие пропущенные значения обнаружены;
# - [x]  описаны возможные причины появления пропусков в данных;
# - [x]  объяснено по какому принципу заполнены пропуски;
# - [x]  заменен вещественный тип данных на целочисленный;
# - [x]  есть пояснение какой метод используется для изменения типа данных и почему;
# - [ ]  удалены дубликаты;
# - [x]  есть пояснение какой метод используется для поиска и удаления дубликатов;
# - [x]  описаны возможные причины появления дубликатов в данных;
# - [x]  выделены леммы в значениях столбца с целями получения кредита;
# - [x]  описан процесс лемматизации;
# - [x]  данные категоризированы;
# - [x]  есть объяснение принципа категоризации данных;
# - [x]  есть ответ на вопрос "Есть ли зависимость между наличием детей и возвратом кредита в срок?";
# - [x]  есть ответ на вопрос "Есть ли зависимость между семейным положением и возвратом кредита в срок?";
# - [x]  есть ответ на вопрос "Есть ли зависимость между уровнем дохода и возвратом кредита в срок?";
# - [x]  есть ответ на вопрос "Как разные цели кредита влияют на его возврат в срок?";
# - [x]  в каждом этапе есть выводы;
# - [x]  есть общий вывод.

# <font color='blue'> В итоге, ты проделал хорошую работу. Постарайся доразобраться с работой с дубликатами. Также в первых двух частях проекта можно подсократить, оставить только нужное согласно заголовку раздела. </font><br>
# <font color='green'>Спасибо за замечания. Исправлено максимально все возможное :)</font>

# <font color='red'>Отлично, получилась прекрасная работа. Удачи в следующих проектах:)</font>

# In[ ]:





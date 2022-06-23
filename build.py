import re
import json
import hashlib

TASK_REGEX = r'@\s+\d+\s*\n([^@]+)'
ANSW_REGEX = r'^\s*(\w)\.\s*([^\n]+)'

EXCLUDE_LINES = [
    'Выполнен Баллов:',
    'ДО в Казанском',
    'Зкзамен по дисциплине',
    'https',
    'Поиск',
    'Портфолио',
    'Отметить вопрос',
    'Выполнен',
    'Отзыв',
    'р р р фр',
    'Текст вопроса',
    'Нет ответа',
    'Балл',
    'Баллов',
    'Сводка хранения данных',
    'Скачать мобильное приложение',
    'р р ду',
    'Стр.',
    'Снять флажок',
    'у ц д у',
    'Закончить обзор',
    'Сбросить тур для пользователя на этой странице',
    'р у ф р',
    'В Б 1 00 1 00',
    'е о е а а ,00',
    'о е а о ,00 з ,00',
    'Д р ц у',
    'Н Б 1 00',
    'Н б й б й',
    'Д р ру фр р',
    'р р р д д фр',
    'П й й б',
    'р р у рр у',
    'р у р',
    'о рос 38',
]

with open('obschiy.txt', 'r') as file:
    CONTENT = file.read()

with open('obschiy1.txt', 'r') as file:
    CONTENT += file.read()

CONTENT = CONTENT.replace('Вопрос', '@')

data = []

tasks = re.findall(TASK_REGEX, CONTENT)

def filter_lines(lines: list) -> list:
    filtered = []

    for line in lines:
        exclude = False

        for exc in EXCLUDE_LINES:
            if exc in line:
                exclude = True
        
        if exclude:
            continue
        
        filtered.append(line)

    return filtered


for task in tasks:
    taskData = { 'answers': {} }

    lines = filter_lines(task.split('\n'))

    answs = re.findall(ANSW_REGEX, '\n'.join(lines), re.MULTILINE)

    for answ in answs:
        taskData['answers'][answ[0]] = answ[1].split(';')[0].strip()

    for i, line in enumerate(lines):
        if 'Правильный ответ:' in line:
            taskData['correct'] = line.split(':', 1)[1].split(';')[0].strip()

    for key, answer in taskData['answers'].items():
        if answer == taskData['correct']:
            taskData['correct'] = key
            break

    if not len(taskData['answers']):
        continue

    question = ''

    for line in lines:
        if 'Выберите один ответ:' in line:
            break

        question += ' ' + line

    question = question[1:]

    if question[-1] == ':':
        question = question[:-1]

    if (a := question.split(': ')) and len(a) == 2 and a[0] == a[1]:
        question = a[0]
    
    if (not (l := len(question)) % 2) and (n := question[:int(l/2)]) == question[int(l/2):]:
        question = n

    taskData['question'] = question

    data.append(taskData)


uniqueTasks = {}

incorrect = []

compared = []

compared_log = []

for task in data:
    hash = hashlib.md5(''.join(task['question'].split(' ')).lower().encode()).hexdigest()

    if uniqueTasks.get(hash):
        continue

    task.update({'hash': hash})

    uniqueTasks.update({hash: task})

    if not task.get('correct') or len(task.get('correct')) > 1:
        if hash not in incorrect:
            incorrect.append(hash)

for h1, task1 in uniqueTasks.items():
    for h2, task2 in uniqueTasks.items():
        if task1['question'] in task2['question'] and h1 != h2:
            compared.append('compared: ' + h1 + ' - ' + h2)
            compared_log.append({h1: task1['question'], h2: task2['question']})

print('> Некорректные: ' + str(len(incorrect)))

if len(incorrect):
    print('\n'.join(incorrect))

print('> Найдены совпадения: ' + str(len(compared)))

if len(compared):
    print('\n'.join(compared))

print('> Всего: ' + str(len(uniqueTasks)))

with open('index.template.html', 'r') as file:
    index = file.read()

with open('index.html', 'w') as file:
    file.write(index.replace('[[[]]]', json.dumps(list(uniqueTasks.values()), ensure_ascii=False)))

with open('debug.json', 'w') as file:
    file.write(json.dumps(uniqueTasks, indent=4, ensure_ascii=False))

with open('compared_log.json', 'w') as file:
    file.write(json.dumps(compared_log, indent=4, ensure_ascii=False))
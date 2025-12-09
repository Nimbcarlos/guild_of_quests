# import json

# with open("data/quests.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     for q in data:
#         print("id:", q['id'])
#         print(q['name']['pt'], q['description']['pt'])
#         print("Tipo:", q['type'], "| dificuldade:", q['difficulty'])

from core.quest import Quest

q = Quest.load_quests(language='pt')
for i in q:
    print(i.id)
print(len(q))

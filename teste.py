import json

with open("data/quests.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for q in data:
        print(q['id'])

        # print("id:", q['id'],"\n",
        #       "Nome:", q['name']['pt'],"\n",
        #       q['description']['pt'],"\n",
        #       "Apartir do turno:", q['available_from_turn'],"\n",
        #       "Duração:", q['duration'],"\n",
        #       "Depende da quest:", q['required_quests'],"\n",
        #       "Nao pode ter completado a quesr id:", q['forbidden_quests'],"\n",
        #       "hero necessario/proibido para aparecer", q['required_heroes'], q['forbidden_heroes'])
        # print(q['name']['pt'], q['description']['pt'])
        # print("Tipo:", q['type'], "| dificuldade:", q['difficulty'])

# from core.quest import Quest

# q = Quest.load_quests(language='pt')
# for i in q:
#     print(i.id)
# print(len(q))

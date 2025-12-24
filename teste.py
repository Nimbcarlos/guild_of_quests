import os
import json

def update_quests():
    # Caminho para a pasta das quests
    folder_path = os.path.join('data', 'quests')
    
    # Verifica se a pasta existe
    if not os.path.exists(folder_path):
        print(f"Erro: A pasta {folder_path} não foi encontrada.")
        return

    count = 0
    # Percorre todos os arquivos na pasta
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # 1. Abre e lê o arquivo original
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # 2. Adiciona o campo max_heroes (se já não existir ou para sobrescrever)
                # Colocamos após o campo 'type' para manter a organização visual
                # Se preferir apenas adicionar ao final, use: data['max_heroes'] = 1
                
                # Criando um novo dicionário para garantir a ordem visual (Python 3.7+)
                new_data = {}
                for key, value in data.items():
                    new_data[key] = value
                    if key == "type":
                        new_data["max_heroes"] = 1
                
                # Caso a chave 'type' não exista por algum motivo, garante que max_heroes esteja lá
                if "max_heroes" not in new_data:
                    new_data["max_heroes"] = 1

                # 3. Salva o arquivo de volta com formatação
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(new_data, file, indent=2, ensure_ascii=False)
                
                print(f"Sucesso: {filename} atualizado.")
                count += 1
                
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

    print(f"\nTotal de {count} arquivos atualizados.")

if __name__ == "__main__":
    update_quests()
import os
import json
import time

def find_steam():
    home = os.path.expanduser("~")
    paths = [
        f"{home}/snap/steam/common/.local/share/Steam",
        f"{home}/.local/share/Steam",
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_game_name(steam_path, game_id):
    acf_file = f'{steam_path}/steamapps/appmanifest_{game_id}.acf'

    if os.path.exists(acf_file):
        try:
            with open(acf_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                if 'name' in line:
                    name = line.split('"')[3]
                    return name
        except:
            pass

    return f'Game {game_id}'


def convert(bytes_size):
    if bytes_size < 1024:
        bytes_size = f'{bytes_size:.2f} bytes'
    elif bytes_size < 1024**2:
        bytes_size = f'{bytes_size / 1024:.2f} Kb'  
    elif bytes_size < 1024**3:
        bytes_size = f'{bytes_size / 1024**2:.2f} Mb'
    elif bytes_size < 1024**4:
        bytes_size = f'{bytes_size / 1024**3:.2f} Gb'
    return bytes_size



def parse_content_log(steam_path):
    log_path = f"{steam_path}/logs/content_log.txt"

    if not os.path.exists(log_path):
        print('Файл логов не найден')
        return []
    
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    game_id = None
    download_rate = '0 Mbps'
    status = None
    progress_bar = 'Неизвестно'

    for line in reversed(lines[-100:]):
        line = line.strip()

        if 'Current download rate:' in line:
            words = line.split(':')
            download_rate = words[-1].strip()

        if 'update started : download' in line:
            words = line.split()
            for word in words:
                if '/' in word:                    
                    downloaded_bytes, needed_bytes = map(int, word[:-1].split('/'))
                    break
            downloaded = convert(downloaded_bytes)
            needed = convert(needed_bytes)
            progress_bar = f'{downloaded} / {needed}'

        if 'AppID' in line:
            words = line.split()
            for i, word in enumerate(words):
                if word == 'AppID':
                    game_id = int(words[i + 1])
                    
                    if 'update started : download' in line:
                        status = 'Скачивается'
                        break
                    elif 'scheduler finished' in line:
                        status = 'Остановлено'
                        break

        if game_id and status:
            break

    if game_id:
        return {
            'game_id': get_game_name(steam_path, game_id),
            'status': status,
            'download_rate': download_rate,
            'progress_bar': progress_bar
        }
    else:
        return None


def main():
    print('🔊 Мониторинг загрузок  Steam')
    print("=" * 50 + '\n')
    
    steam_path = find_steam()
  
    for minute in range(1, 6):
        print(f"\n💡 Check #{minute} ({time.strftime('%H:%M:%S')})")
        
        download = parse_content_log(steam_path)
        
        if not download:
            print("Нет активных загрузок")
        else:
            print(f"🎮 Game: {download['game_id']}")
            print(f"📊 Status: {download['status']}")
            print(f"📶 Download rate: {download['download_rate']}")
            print(f"🚀 Progress bar: {download['progress_bar']}")
        
        if minute < 5:
            print(f"\n⏳ Ожидание 60 секунд...")
            time.sleep(60)
    
    print("\n" + "=" * 50)
    print("✅ Мониторинг завершён")

if __name__ == "__main__":
    main()

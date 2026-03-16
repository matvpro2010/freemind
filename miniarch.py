#!/usr/bin/env python3
"""
MiniArch - Кроссплатформенная операционная среда на Python
Вдохновлена философией Arch Linux и свободного ПО
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import platform
import json
import importlib.util
from pathlib import Path

# Настройка терминала для кросс-платформенности
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-256color'

# Определяем платформу один раз для оптимизации
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

# Пытаемся импортировать psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    # Не выводим сообщение при импорте, только при вызове команд

class MiniArch:
    """Главный класс системы"""
    
    def __init__(self):
        self.version = "0.3.0"
        self.name = "MiniArch"
        self.commands = {}
        self.current_dir = os.path.expanduser("~")
        self.running = True
        self.has_terminal = sys.stdout.isatty()
        
        # Настройка путей для модулей
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.modules_path = os.path.join(self.base_path, "modules")
        self.loaded_modules = {}
        
        # Создаем папку modules если её нет
        os.makedirs(self.modules_path, exist_ok=True)
        for category in ['games', 'utils', 'system']:
            os.makedirs(os.path.join(self.modules_path, category), exist_ok=True)
        
        # Настройка цветов для Windows
        if IS_WINDOWS:
            os.system("color")
        
        self.init_commands()
        
    def init_commands(self):
        """Инициализация встроенных команд"""
        self.commands = {
            # Основные команды
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'clear': self.cmd_clear,
            'reboot': self.cmd_reboot,
            'shutdown': self.cmd_shutdown,
            
            # Файловые операции
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'mkdir': self.cmd_mkdir,
            'rm': self.cmd_rm,
            'del': self.cmd_rm,
            'cat': self.cmd_cat,
            'type': self.cmd_cat,
            'touch': self.cmd_touch,
            'edit': self.cmd_edit,
            
            # Системная информация
            'date': self.cmd_date,
            'time': self.cmd_date,
            'sysinfo': self.cmd_sysinfo,
            'info': self.cmd_sysinfo,
            'whoami': self.cmd_whoami,
            'ps': self.cmd_ps,
            'neofetch': self.cmd_neofetch,
            'fetch': self.cmd_neofetch,
            
            # Приложения
            'echo': self.cmd_echo,
            'calc': self.cmd_calc,
            'weather': self.cmd_weather,
            'gui': self.cmd_gui,
            
            # Модули
            'modules': self.cmd_modules,
            'module': self.cmd_module,
            
            # Платформозависимые
            'windows': self.cmd_windows,
            'linux': self.cmd_linux,
        }
        
    def colorize(self, text, color_code):
        """Добавляет цвет к тексту (кросс-платформенная версия)"""
        if not self.has_terminal:
            return text
            
        colors = {
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37',
        }
        
        if color_code in colors:
            # В Windows цвета работают по-другому
            if IS_WINDOWS:
                # Простая эмуляция цветов для Windows
                return text
            else:
                return f"\033[{colors[color_code]}m{text}\033[0m"
        return text
        
    def boot(self):
        """Загрузка системы"""
        self.clear_screen()
        self.show_boot_screen()
        time.sleep(1.5)
        self.clear_screen()
        self.main_loop()
        
    def show_boot_screen(self):
        """Показывает экран загрузки"""
        os_name = "Windows" if IS_WINDOWS else "Linux"
        boot_screen = f"""
╔══════════════════════════════════════════════════════════╗
║                    {self.name} v{self.version}                       ║
║              "Свобода. Простота. Контроль"               ║
╠══════════════════════════════════════════════════════════╣
║  Платформа: {os_name:<31} 		   ║
║  Загрузка ядра...                                        ║
║  Инициализация модулей...                                ║
║  Система готова к работе!                                ║
╚══════════════════════════════════════════════════════════╝
        """
        print(boot_screen)
        
    def clear_screen(self):
        """Очистка экрана (кросс-платформенная)"""
        os.system('cls' if IS_WINDOWS else 'clear')
        
    def get_prompt(self):
        """Формирует приглашение командной строки"""
        try:
            user = os.getlogin()
        except:
            user = 'user'
        
        host = platform.node()
        dir_name = os.path.basename(self.current_dir) or '/'
        
        prompt = f"{self.colorize(user, 'green')}@{self.colorize(host, 'cyan')} "
        prompt += f"{self.colorize(dir_name, 'blue')}$ "
        return prompt
        
    def main_loop(self):
        """Главный цикл системы"""
        print(f"\n{self.colorize('Добро пожаловать в ' + self.name + '!', 'yellow')}")
        print(f"{self.colorize('Введите help для списка команд', 'cyan')}\n")
        
        while self.running:
            try:
                command = input(self.get_prompt()).strip()
                if command:
                    self.execute_command(command)
            except KeyboardInterrupt:
                print("\nИспользуйте 'exit' для выхода")
            except EOFError:
                break
                
    def execute_command(self, command_line):
        """Выполнение команды"""
        parts = command_line.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
        else:
            self.execute_system_command(command_line)
            
    def execute_system_command(self, command):
        """Выполнение системной команды"""
        try:
            result = subprocess.run(command, shell=True, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{self.colorize(f'Ошибка: {result.stderr}', 'red')}")
        except Exception as e:
            print(f"{self.colorize(f'Команда не найдена: {command}', 'red')}")
    
    # ===== ОСНОВНЫЕ КОМАНДЫ =====
    
    def cmd_help(self, args):
        """Показывает справку"""
        print(f"\n{self.colorize('Доступные команды:', 'yellow')}")
        print("=" * 60)
        
        categories = {
            '📁 Файлы': ['ls', 'pwd', 'cd', 'mkdir', 'rm', 'cat', 'touch', 'edit'],
            '🖥️ Система': ['sysinfo', 'whoami', 'date', 'ps', 'neofetch'],
            '⚙️ Управление': ['clear', 'exit', 'reboot', 'shutdown'],
            '🎮 Приложения': ['calc', 'weather', 'gui', 'echo'],
            '🧩 Модули': ['modules', 'module'],
            '🔧 Платформа': ['windows', 'linux'],
        }
        
        for category, cmd_list in categories.items():
            print(f"\n{self.colorize(category, 'cyan')}")
            for cmd in sorted(cmd_list):
                if cmd in self.commands:
                    doc = self.commands[cmd].__doc__ or "Нет описания"
                    print(f"  {cmd:10} - {doc}")
        print()
    
    # ===== ФАЙЛОВЫЕ КОМАНДЫ =====
    
    def cmd_ls(self, args):
        """Показывает содержимое директории"""
        path = args[0] if args else self.current_dir
        show_all = '-a' in args or '/a' in args
        
        try:
            items = os.listdir(path)
            if not show_all:
                items = [i for i in items if not i.startswith('.')]
            
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    print(self.colorize(f"{item}/", 'blue'))
                elif os.access(full_path, os.X_OK):
                    print(self.colorize(f"{item}*", 'green'))
                else:
                    print(item)
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_pwd(self, args):
        """Показывает текущую директорию"""
        print(self.colorize(self.current_dir, 'cyan'))
    
    def cmd_cd(self, args):
        """Смена директории"""
        path = args[0] if args else os.path.expanduser("~")
        try:
            os.chdir(path)
            self.current_dir = os.getcwd()
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_mkdir(self, args):
        """Создает директорию"""
        if not args:
            print(f"{self.colorize('Укажите имя директории', 'red')}")
            return
        try:
            os.mkdir(args[0])
            print(f"Директория '{args[0]}' создана")
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_rm(self, args):
        """Удаляет файл или директорию"""
        if not args:
            print(f"{self.colorize('Укажите файл для удаления', 'red')}")
            return
        
        for path in args:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    print(f"Файл '{path}' удален")
                elif os.path.isdir(path):
                    os.rmdir(path)
                    print(f"Директория '{path}' удалена")
                else:
                    print(f"{self.colorize(f'{path} не найден', 'red')}")
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_cat(self, args):
        """Показывает содержимое файла"""
        if not args:
            print(f"{self.colorize('Укажите файл', 'red')}")
            return
        try:
            with open(args[0], 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_touch(self, args):
        """Создает пустой файл"""
        if not args:
            print(f"{self.colorize('Укажите имя файла', 'red')}")
            return
        for filename in args:
            try:
                with open(filename, 'a'):
                    os.utime(filename, None)
                print(f"Файл '{filename}' создан")
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def cmd_edit(self, args):
        """Простой текстовый редактор"""
        if not args:
            print(f"{self.colorize('Укажите файл для редактирования', 'red')}")
            return
        
        filename = args[0]
        lines = []
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                print(f"Редактирование {filename} (:wq для сохранения):")
            except:
                print(f"Не удалось прочитать {filename}")
                return
        else:
            print(f"Создание {filename} (:wq для сохранения):")
        
        new_lines = []
        line_num = 1
        
        for line in lines:
            print(f"{line_num:3d}| {line.rstrip()}")
            line_num += 1
        
        while True:
            try:
                user_input = input(f"{line_num:3d}| ")
                if user_input == ':wq':
                    break
                new_lines.append(user_input + '\n')
                line_num += 1
            except KeyboardInterrupt:
                print("\nСохранение...")
                break
        
        if new_lines:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"Файл {filename} сохранен")
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    # ===== СИСТЕМНЫЕ КОМАНДЫ =====
    
    def cmd_date(self, args):
        """Показывает дату и время"""
        now = datetime.now()
        print(f"{self.colorize('Дата:', 'yellow')} {now.strftime('%d.%m.%Y')}")
        print(f"{self.colorize('Время:', 'yellow')} {now.strftime('%H:%M:%S')}")
    
    def cmd_echo(self, args):
        """Выводит текст"""
        print(' '.join(args))
    
    def cmd_whoami(self, args):
        """Показывает имя пользователя"""
        try:
            print(os.getlogin())
        except:
            print('user')
    
    def cmd_clear(self, args):
        """Очищает экран"""
        self.clear_screen()
    
    def cmd_exit(self, args):
        """Выход из системы"""
        print(f"\n{self.colorize('Завершение сеанса...', 'yellow')}")
        self.running = False
    
    def cmd_reboot(self, args):
        """Перезагрузка системы"""
        print(f"\n{self.colorize('Перезагрузка...', 'yellow')}")
        time.sleep(1)
        self.clear_screen()
        self.boot()
    
    def cmd_shutdown(self, args):
        """Выключение системы"""
        print(f"\n{self.colorize('Выключение системы...', 'yellow')}")
        time.sleep(1)
        sys.exit(0)
    
    def cmd_sysinfo(self, args):
        """Информация о системе"""
        print(f"\n{self.colorize('=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===', 'yellow')}")
        print(f"ОС: {platform.system()} {platform.release()}")
        print(f"Хост: {platform.node()}")
        print(f"Пользователь: {self.cmd_whoami.__doc__}")
        print(f"Директория: {self.current_dir}")
        print(f"Python: {platform.python_version()}")
        
        if HAS_PSUTIL:
            try:
                print(f"\n{self.colorize('Аппаратное обеспечение:', 'yellow')}")
                print(f"CPU: {psutil.cpu_count()} ядер")
                print(f"CPU загрузка: {psutil.cpu_percent()}%")
                
                mem = psutil.virtual_memory()
                print(f"RAM: {mem.total / 1024**3:.1f}GB всего, {mem.percent}% используется")
                
                disk = psutil.disk_usage('/')
                print(f"Диск: {disk.total / 1024**3:.1f}GB всего, {disk.percent}% используется")
            except:
                pass
        else:
            print(f"\n{self.colorize('Установите psutil для полной информации', 'yellow')}")
        print()
    
    def cmd_ps(self, args):
        """Показывает процессы"""
        if not HAS_PSUTIL:
            print(f"{self.colorize('Установите psutil', 'yellow')}")
            return
        
        try:
            print(f"\n{'PID':>6} {'Имя':20} {'CPU%':>6} {'MEM%':>6}")
            print("-" * 40)
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    print(f"{info['pid']:6} {info['name'][:20]:20} "
                          f"{info['cpu_percent'] or 0:6.1f} {info['memory_percent'] or 0:6.1f}")
                except:
                    pass
        except:
            print("Информация о процессах недоступна")
    
    # ===== ПРИЛОЖЕНИЯ =====
    
    def cmd_calc(self, args):
        """Простой калькулятор"""
        print(f"\n{self.colorize('Калькулятор (q - выход)', 'yellow')}")
        while True:
            try:
                expr = input("calc> ").strip()
                if expr.lower() == 'q':
                    break
                result = eval(expr)
                print(f"= {result}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def cmd_weather(self, args):
        """Демо-погода"""
        print(f"\n{self.colorize('Погода:', 'yellow')}")
        print(f"Температура: +15°C")
        print(f"Влажность: 65%")
        print(f"Ветер: 3 м/с\n")
    
    def cmd_gui(self, args):
        """Текстовый оконный менеджер"""
        print(f"\n{self.colorize('Текстовый оконный менеджер', 'yellow')}")
        print("┌─────────────────────────────────┐")
        print("│  [Терминал]  [Монитор]  [Часы]  │")
        print("│                                 │")
        print("│  Нажмите Enter для выхода...    │")
        print("└─────────────────────────────────┘")
        input()
    
    # ===== ПЛАТФОРМОЗАВИСИМЫЕ КОМАНДЫ =====
    
    def cmd_windows(self, args):
        """Информация о Windows"""
        if IS_WINDOWS:
            print(f"\n{self.colorize('Windows:', 'yellow')}")
            print(f"Версия: {platform.version()}")
            print(f"Архитектура: {platform.machine()}")
        else:
            print("Эта команда доступна только в Windows")
    
    def cmd_linux(self, args):
        """Информация о Linux"""
        if IS_LINUX:
            print(f"\n{self.colorize('Linux:', 'yellow')}")
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            print(f"Дистрибутив: {line.split('=')[1].strip().strip('\"')}")
            except:
                print(f"Ядро: {platform.release()}")
        else:
            print("Эта команда доступна только в Linux")
    
    # ===== СИСТЕМА МОДУЛЕЙ =====
    
    def cmd_modules(self, args):
        """Показывает все модули"""
        print(f"\n{self.colorize('📦 ДОСТУПНЫЕ МОДУЛИ', 'yellow')}")
        print("=" * 50)
        
        if not os.path.exists(self.modules_path):
            print(f"{self.colorize('Папка modules не найдена', 'red')}")
            return
        
        categories = [d for d in os.listdir(self.modules_path) 
                     if os.path.isdir(os.path.join(self.modules_path, d))]
        
        if not categories:
            print("Нет установленных модулей")
            return
        
        for category in sorted(categories):
            print(f"\n{self.colorize(f'📁 {category.upper()}:', 'cyan')}")
            cat_path = os.path.join(self.modules_path, category)
            modules = [d for d in os.listdir(cat_path) 
                      if os.path.isdir(os.path.join(cat_path, d))]
            
            for module in sorted(modules):
                info = self.get_module_info(category, module)
                if info:
                    name = info.get('name', module)
                    version = info.get('version', '?')
                    desc = info.get('description', '')
                    print(f"  🧩 {name} v{version} - {desc[:40]}")
                else:
                    print(f"  🧩 {module}")
    
    def cmd_module(self, args):
        """Управление модулями: module [load|info|help] [имя]"""
        if not args:
            print("Использование: module [load|info|help] [имя]")
            return
        
        action = args[0].lower()
        if len(args) < 2:
            print(f"Укажите модуль для {action}")
            return
        
        module_name = args[1]
        
        if action == "load":
            self.load_module(module_name)
        elif action == "info":
            self.show_module_info(module_name)
        elif action == "help":
            self.show_module_help(module_name)
        elif action == "reload":
            self.reload_module(module_name)
        elif action == "unload":
            self.unload_module(module_name)
        else:
            print(f"Неизвестное действие: {action}")
    
    def get_module_info(self, category, module_name):
        """Получает информацию о модуле из meta.json"""
        meta_path = os.path.join(self.modules_path, category, module_name, "meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def parse_module_path(self, module_string):
        """Разбирает строку типа 'games.snake'"""
        parts = module_string.split('.')
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return None, parts[0]
        else:
            print(f"{self.colorize('Неправильный формат модуля', 'red')}")
            return None, None
    
    def find_module(self, module_name, category=None):
        """Ищет модуль в папках"""
        if category:
            path = os.path.join(self.modules_path, category, module_name)
            if os.path.exists(path):
                return category, module_name, path
        else:
            for cat in os.listdir(self.modules_path):
                cat_path = os.path.join(self.modules_path, cat)
                if os.path.isdir(cat_path):
                    mod_path = os.path.join(cat_path, module_name)
                    if os.path.exists(mod_path):
                        return cat, module_name, mod_path
        return None, None, None
    
    def load_module(self, module_string):
        """Загружает и запускает модуль"""
        category, module_name = self.parse_module_path(module_string)
        if not module_name:
            return
        
        found_cat, found_name, module_path = self.find_module(module_name, category)
        if not module_path:
            print(f"{self.colorize(f'Модуль {module_string} не найден', 'red')}")
            return
        
        module_key = f"{found_cat}.{found_name}"
        
        if module_key in self.loaded_modules:
            print(f"{self.colorize('Модуль уже загружен', 'yellow')}")
            return
        
        main_file = os.path.join(module_path, "main.py")
        if not os.path.exists(main_file):
            print(f"{self.colorize('В модуле нет main.py', 'red')}")
            return
        
        try:
            print(f"{self.colorize(f'Загрузка {module_key}...', 'cyan')}")
            spec = importlib.util.spec_from_file_location(module_key, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if not hasattr(module, 'run'):
                print(f"{self.colorize('В модуле нет функции run()', 'red')}")
                return
            
            self.loaded_modules[module_key] = {
                'module': module,
                'path': module_path,
                'category': found_cat,
                'name': found_name
            }
            
            print(f"{self.colorize('✅ Запуск...', 'green')}")
            print("-" * 40)
            module.run(self)
            
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
            if module_key in self.loaded_modules:
                del self.loaded_modules[module_key]
    
    def show_module_info(self, module_string):
        """Показывает информацию о модуле"""
        category, module_name = self.parse_module_path(module_string)
        found_cat, found_name, module_path = self.find_module(module_name, category)
        
        if not module_path:
            print(f"{self.colorize(f'Модуль {module_string} не найден', 'red')}")
            return
        
        info = self.get_module_info(found_cat, found_name)
        print(f"\n{self.colorize('📋 ИНФОРМАЦИЯ О МОДУЛЕ', 'yellow')}")
        print("=" * 50)
        
        if info:
            for key, value in info.items():
                print(f"{key.capitalize()}: {value}")
        else:
            print(f"Модуль: {found_cat}.{found_name}")
            print(f"Путь: {module_path}")
        
        module_key = f"{found_cat}.{found_name}"
        status = "✅ Загружен" if module_key in self.loaded_modules else "⏳ Не загружен"
        print(f"Статус: {status}\n")
    
    def show_module_help(self, module_string):
        """Показывает справку по модулю"""
        category, module_name = self.parse_module_path(module_string)
        found_cat, found_name, module_path = self.find_module(module_name, category)
        
        if not module_path:
            print(f"{self.colorize(f'Модуль {module_string} не найден', 'red')}")
            return
        
        main_file = os.path.join(module_path, "main.py")
        if not os.path.exists(main_file):
            print(f"{self.colorize('В модуле нет main.py', 'red')}")
            return
        
        try:
            spec = importlib.util.spec_from_file_location("temp", main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            print(f"\n{self.colorize('📖 СПРАВКА ПО МОДУЛЮ', 'yellow')}")
            print("=" * 50)
            
            if hasattr(module, 'help'):
                print(module.help())
            elif module.__doc__:
                print(module.__doc__)
            else:
                print("Нет справки по модулю")
            print()
            
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def reload_module(self, module_string):
        """Перезагружает модуль"""
        category, module_name = self.parse_module_path(module_string)
        module_key = f"{category}.{module_name}" if category else module_name
        
        if module_key not in self.loaded_modules:
            print(f"{self.colorize('Модуль не загружен', 'red')}")
            return
        
        try:
            del self.loaded_modules[module_key]
            print(f"{self.colorize('Перезагрузка...', 'yellow')}")
            self.load_module(module_string)
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
    
    def unload_module(self, module_string):
        """Выгружает модуль"""
        category, module_name = self.parse_module_path(module_string)
        module_key = f"{category}.{module_name}" if category else module_name
        
        if module_key in self.loaded_modules:
            del self.loaded_modules[module_key]
            print(f"{self.colorize(f'Модуль выгружен', 'green')}")
        else:
            print(f"{self.colorize('Модуль не загружен', 'red')}")
    
    def cmd_neofetch(self, args):
        """Показывает ASCII-логотип"""
        logo = f"""
{self.colorize('       ██╗██████╗ ███████╗███████╗', 'blue')}
{self.colorize('       ██║██╔══██╗██╔════╝██╔════╝', 'cyan')}
{self.colorize('       ██║██████╔╝█████╗  █████╗  ', 'green')}
{self.colorize('  ██   ██║██╔═══╝ ██╔══╝  ██╔══╝  ', 'yellow')}
{self.colorize('  ╚█████╔╝██║     ██║     ██║     ', 'red')}
{self.colorize('   ╚════╝ ╚═╝     ╚═╝     ╚═╝     ', 'magenta')}
{self.colorize('═══════════════════════════════════', 'white')}
{self.colorize('    OPEN KNOWLEDGE • FREE ACCESS   ', 'cyan')}
{self.colorize('═══════════════════════════════════', 'white')}

{self.colorize('Пользователь:', 'yellow')} {self.cmd_whoami([])}
{self.colorize('Система:', 'yellow')} {platform.system()} {platform.release()}
{self.colorize('Python:', 'yellow')} {platform.python_version()}
        """
        print(logo)

# ===== ВНЕШНИЕ ФУНКЦИИ =====

def main():
    """Главная функция"""
    arch = MiniArch()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("MiniArch - Операционная среда на Python")
            print("\nИспользование:")
            print("  python miniarch.py    - Запуск системы")
            print("  python miniarch.py demo - Демо-режим")
            return
        elif sys.argv[1] == 'demo':
            demo_mode()
            return
    
    try:
        arch.boot()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

def demo_mode():
    """Демонстрационный режим"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ MiniArch")
    print("="*60 + "\n")
    
    arch = MiniArch()
    arch.show_boot_screen()
    time.sleep(1)
    
    print(f"\n{arch.colorize('Доступные команды:', 'yellow')}")
    print("-" * 40)
    
    for i, cmd in enumerate(sorted(arch.commands.keys())[:15]):
        doc = arch.commands[cmd].__doc__ or "..."
        print(f"  {cmd:12} - {doc}")
    
    print("\n  ... и другие")
    print(f"\n{arch.colorize('Информация о системе:', 'yellow')}")
    print("-" * 40)
    arch.cmd_sysinfo([])
    
    print(f"\n{arch.colorize('ASCII-логотип:', 'yellow')}")
    print("-" * 40)
    arch.cmd_neofetch([])
    
    print(f"\n{arch.colorize('Для запуска полной версии:', 'yellow')}")
    print("  python miniarch.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

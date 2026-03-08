#!/usr/bin/env python3
"""
MiniArch - Простая операционная среда на Python
Вдохновлено Arch Linux (версия для Windows)
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import platform

# Пытаемся импортировать psutil, но не критично если его нет
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Для полной функциональности установите: pip install psutil")

class MiniArch:
    """Главный класс системы"""
    
    def __init__(self):
        self.version = "0.2.0"
        self.name = "MiniArch"
        self.commands = {}
        self.current_dir = os.path.expanduser("~")
        self.running = True
        self.init_commands()
        
        # Цвета для Windows
        if platform.system() == "Windows":
            os.system("color")
        
    def init_commands(self):
        """Инициализация встроенных команд"""
        self.commands = {
            'help': self.cmd_help,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,  # Windows compatibility
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'clear': self.cmd_clear,
            'cls': self.cmd_clear,  # Windows compatibility
            'date': self.cmd_date,
            'time': self.cmd_date,
            'echo': self.cmd_echo,
            'sysinfo': self.cmd_sysinfo,
            'info': self.cmd_sysinfo,
            'ps': self.cmd_ps,
            'whoami': self.cmd_whoami,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'reboot': self.cmd_reboot,
            'restart': self.cmd_reboot,
            'shutdown': self.cmd_shutdown,
            'mkdir': self.cmd_mkdir,
            'rm': self.cmd_rm,
            'del': self.cmd_rm,  # Windows compatibility
            'cat': self.cmd_cat,
            'type': self.cmd_cat,  # Windows compatibility
            'neofetch': self.cmd_neofetch,
            'fetch': self.cmd_neofetch,
            'edit': self.cmd_edit,
            'touch': self.cmd_touch,
            'weather': self.cmd_weather,
            'calc': self.cmd_calc,
            'gui': self.cmd_gui,
            'windows': self.cmd_windows,
            'modules': self.cmd_modules,
            'load': self.cmd_load,
            'install': self.cmd_install,
        }
        
    def colorize(self, text, color_code):
        """Добавляет цвет к тексту"""
        colors = {
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37',
        }
        if color_code in colors and platform.system() != "Windows":
            return f"\033[{colors[color_code]}m{text}\033[0m"
        return text
        
    def boot(self):
        """Загрузка системы"""
        self.clear_screen()
        self.show_boot_screen()
        time.sleep(2)
        self.clear_screen()
        self.main_loop()
        
    def show_boot_screen(self):
        """Показывает экран загрузки"""
        boot_screen = f"""
╔══════════════════════════════════════════════════════════╗
║                    {self.name} v{self.version}                      ║
║              "Простота - высшая мудрость"                         ║
╠══════════════════════════════════════════════════════════╣
║  Загрузка ядра...                                        ║
║  Инициализация модулей...                                ║
║  Запуск системных служб...                               ║
║  Система готова к работе!                                ║
╚══════════════════════════════════════════════════════════╝
        """
        print(boot_screen)
        
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_prompt(self):
        """Формирует приглашение командной строки"""
        user = os.getlogin() if hasattr(os, 'getlogin') else 'user'
        host = platform.node()
        dir_name = os.path.basename(self.current_dir) or '/'
        
        # Цветное приглашение
        prompt = f"{self.colorize(user, 'green')}@{self.colorize(host, 'cyan')} "
        prompt += f"{self.colorize(dir_name, 'blue')}$ "
        return prompt
        
    def main_loop(self):
        """Главный цикл системы"""
        print(f"\n{self.colorize('Добро пожаловать в ' + self.name + '!', 'yellow')}")
        print(f"{self.colorize('Введите help для списка команд', 'cyan')}\n")
        
        while self.running:
            try:
                # Показываем промпт
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
            # Попытка выполнить как системную команду
            self.execute_system_command(command_line)
            
    def execute_system_command(self, command):
        """Выполнение системной команды"""
        try:
            # Для Windows используем shell=True
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{self.colorize(f'Ошибка: {result.stderr}', 'red')}", file=sys.stderr)
        except Exception as e:
            print(f"{self.colorize(f'Команда не найдена: {command}', 'red')}")
            
    # Встроенные команды
    def cmd_help(self, args):
        """Показывает справку"""
        print(f"\n{self.colorize('Доступные команды:', 'yellow')}")
        print("-" * 50)
        
        # Группировка команд
        categories = {
            'Файлы': ['ls', 'dir', 'pwd', 'cd', 'mkdir', 'rm', 'del', 'cat', 'type', 'touch', 'edit'],
            'Система': ['sysinfo', 'info', 'ps', 'whoami', 'date', 'time', 'neofetch', 'fetch'],
            'Управление': ['clear', 'cls', 'exit', 'quit', 'reboot', 'restart', 'shutdown'],
            'Приложения': ['calc', 'weather', 'gui', 'windows', 'modules', 'load', 'install'],
            'Прочее': ['echo', 'help'],
        }
        
        for category, cmd_list in categories.items():
            print(f"\n{self.colorize(category + ':', 'cyan')}")
            for cmd in sorted(cmd_list):
                if cmd in self.commands:
                    doc = self.commands[cmd].__doc__ or "Нет описания"
                    print(f"  {cmd:12} - {doc}")
        print()
        
    def cmd_ls(self, args):
        """Показывает содержимое директории"""
        path = args[0] if args else self.current_dir
        show_all = '-a' in args or '/a' in args
        
        try:
            items = os.listdir(path)
            
            # Фильтрация скрытых файлов
            if not show_all:
                items = [i for i in items if not i.startswith('.')]
                
            # Сортировка
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            # Вывод с цветами
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    print(self.colorize(f"{item}/", 'blue'))
                elif os.path.isfile(full_path):
                    # Проверка на исполняемый файл
                    if os.access(full_path, os.X_OK):
                        print(self.colorize(f"{item}*", 'green'))
                    else:
                        print(item)
                else:
                    print(item)
                    
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
            
    def cmd_pwd(self, args):
        """Показывает текущую директорию"""
        print(self.colorize(self.current_dir, 'cyan'))
        
    def cmd_cd(self, args):
        """Смена директории"""
        if not args:
            path = os.path.expanduser("~")
        else:
            path = args[0]
            
        try:
            os.chdir(path)
            self.current_dir = os.getcwd()
        except Exception as e:
            print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
            
    def cmd_clear(self, args):
        """Очищает экран"""
        self.clear_screen()
        
    def cmd_date(self, args):
        """Показывает текущую дату и время"""
        now = datetime.now()
        print(f"{self.colorize('Дата:', 'yellow')} {now.strftime('%d.%m.%Y')}")
        print(f"{self.colorize('Время:', 'yellow')} {now.strftime('%H:%M:%S')}")
        
    def cmd_echo(self, args):
        """Выводит текст"""
        print(' '.join(args))
        
    def cmd_sysinfo(self, args):
        """Информация о системе"""
        print(f"\n{self.colorize('=== Системная информация ===', 'yellow')}")
        
        # Основная информация
        print(f"{self.colorize('ОС:', 'cyan')} {platform.system()} {platform.release()}")
        print(f"{self.colorize('Хост:', 'cyan')} {platform.node()}")
        print(f"{self.colorize('Пользователь:', 'cyan')} {os.getlogin() if hasattr(os, 'getlogin') else 'Unknown'}")
        print(f"{self.colorize('Текущая директория:', 'cyan')} {self.current_dir}")
        print(f"{self.colorize('Python:', 'cyan')} {platform.python_version()}")
        
        # Информация через psutil
        if HAS_PSUTIL:
            try:
                print(f"\n{self.colorize('Аппаратное обеспечение:', 'yellow')}")
                print(f"{self.colorize('CPU:', 'cyan')} {psutil.cpu_count()} ядер")
                print(f"{self.colorize('Использование CPU:', 'cyan')} {psutil.cpu_percent(interval=1)}%")
                
                memory = psutil.virtual_memory()
                print(f"{self.colorize('RAM:', 'cyan')} {memory.total / (1024**3):.1f}GB всего, "
                      f"{memory.used / (1024**3):.1f}GB используется ({memory.percent}%)")
                
                disk = psutil.disk_usage('/')
                print(f"{self.colorize('Диск:', 'cyan')} {disk.total / (1024**3):.1f}GB всего, "
                      f"{disk.used / (1024**3):.1f}GB используется ({disk.percent}%)")
            except:
                print(f"\n{self.colorize('(Установите psutil для полной информации)', 'yellow')}")
        else:
            print(f"\n{self.colorize('(Установите psutil для информации о железе)', 'yellow')}")
        print()
        
    def cmd_ps(self, args):
        """Показывает запущенные процессы"""
        if not HAS_PSUTIL:
            print(f"{self.colorize('Установите psutil для этой команды: pip install psutil', 'yellow')}")
            return
            
        try:
            print(f"\n{self.colorize('PID     Имя                   CPU%    MEM%', 'yellow')}")
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
            
    def cmd_whoami(self, args):
        """Показывает имя пользователя"""
        print(os.getlogin() if hasattr(os, 'getlogin') else 'user')
        
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
        self.running = False
        sys.exit(0)
        
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
                print(f"{self.colorize(f'Ошибка при удалении {path}: {e}', 'red')}")
                
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
            
    def cmd_edit(self, args):
        """Простой текстовый редактор"""
        if not args:
            print(f"{self.colorize('Укажите файл для редактирования', 'red')}")
            return
            
        filename = args[0]
        lines = []
        
        # Загрузка существующего файла
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                print(f"Редактирование {filename} (введите ':wq' для сохранения и выхода):")
            except:
                print(f"Не удалось прочитать {filename}")
                return
        else:
            print(f"Создание нового файла {filename} (введите ':wq' для сохранения и выхода):")
            
        # Редактирование
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
                print("\nСохранение и выход...")
                break
                
        # Сохранение
        if new_lines:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"Файл {filename} сохранен")
            except Exception as e:
                print(f"{self.colorize(f'Ошибка сохранения: {e}', 'red')}")
                
    def cmd_touch(self, args):
        """Создает пустой файл или обновляет время доступа"""
        if not args:
            print(f"{self.colorize('Укажите имя файла', 'red')}")
            return
            
        for filename in args:
            try:
                with open(filename, 'a'):
                    os.utime(filename, None)
                print(f"Файл '{filename}' создан/обновлен")
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
                
    def cmd_neofetch(self, args):
        """Показывает ASCII-логотип системы"""    
        arch_logo = f"""
        {self.colorize('       ██╗██████╗ ███████╗███████╗', 'blue')}
        {self.colorize('       ██║██╔══██╗██╔════╝██╔════╝', 'cyan')}
        {self.colorize('       ██║██████╔╝█████╗  █████╗  ', 'green')}
        {self.colorize('  ██   ██║██╔═══╝ ██╔══╝  ██╔══╝  ', 'yellow')}
        {self.colorize('  ╚█████╔╝██║     ██║     ██║     ', 'red')}
        {self.colorize('   ╚════╝ ╚═╝     ╚═╝     ╚═╝     ', 'magenta')}
        {self.colorize('═══════════════════════════════════', 'white')}
        {self.colorize('    OPEN KNOWLEDGE • FREE ACCESS   ', 'cyan')}
        {self.colorize('═══════════════════════════════════', 'white')}

        {self.colorize('Пользователь:', 'yellow')} {self.colorize(os.getlogin() if hasattr(os, 'getlogin') else 'user', 'green')}
        {self.colorize('Система:', 'yellow')} {self.colorize('FREE SOFTWARE', 'cyan')}
        {self.colorize('Знания:', 'yellow')} {self.colorize('Доступны каждому', 'blue')}
        {self.colorize('Интернет:', 'yellow')} {self.colorize('Свободный', 'magenta')}
        """
        print(arch_logo)
        
    def cmd_calc(self, args):
        """Простой калькулятор"""
        print(f"\n{self.colorize('Простой калькулятор', 'yellow')}")
        print("Введите выражение (например: 2 + 2) или 'q' для выхода")
        
        while True:
            try:
                expr = input("calc> ").strip()
                if expr.lower() == 'q':
                    break
                    
                result = eval(expr)
                print(f"{self.colorize('=', 'cyan')} {result}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{self.colorize(f'Ошибка: {e}', 'red')}")
                
    def cmd_weather(self, args):
        """Показывает погоду (демо)"""
        print(f"\n{self.colorize('Погода в Москве:', 'yellow')}")
        print(f"{self.colorize('Температура:', 'cyan')} +15°C")
        print(f"{self.colorize('Влажность:', 'cyan')} 65%")
        print(f"{self.colorize('Ветер:', 'cyan')} 3 м/с")
        print(f"{self.colorize('Описание:', 'cyan')} Облачно с прояснениями\n")
        
    def cmd_gui(self, args):
        """Запускает простой GUI"""
        print(f"\n{self.colorize('Запуск графического интерфейса...', 'yellow')}")
        print("┌─────────────────────────────────┐")
        print("│        Менеджер окон            │")
        print("├─────────────────────────────────┤")
        print("│  [Терминал]  [Монитор]  [Часы]  │")
        print("│                                 │")
        print("│  Welcome to MiniArch GUI        │")
        print("│  Это демо-версия оконного       │")
        print("│  менеджера в текстовом режиме   │")
        print("│                                 │")
        print("│  Нажмите Enter для выхода...    │")
        print("└─────────────────────────────────┘")
        input()
        
    def cmd_windows(self, args):
        """Показывает информацию о Windows"""
        if platform.system() == "Windows":
            print(f"\n{self.colorize('Информация о Windows:', 'yellow')}")
            print(f"Версия: {platform.version()}")
            print(f"Архитектура: {platform.machine()}")
            print(f"Процессор: {platform.processor()}")
        else:
            print("Эта команда доступна только в Windows")
    
    # НОВЫЕ КОМАНДЫ - модули
    def cmd_modules(self, args):
        """Показывает установленные модули"""
        print("📦 Модули пока не установлены")
        print("Эта функция в разработке")

    def cmd_load(self, args):
        """Загружает модуль"""
        print("📥 Загрузка модулей пока не работает")
    
    def cmd_install(self, args):
        """Устанавливает модуль"""
        print("🔧 Установка модулей пока не работает")

# ===== ЭТО КОНЕЦ КЛАССА MiniArch =====
# ВСЕ ЧТО НИЖЕ - ЭТО ВНЕШНИЕ ФУНКЦИИ (НЕ ВНУТРИ КЛАССА)

def main():
    """Главная функция"""
    # Создаем экземпляр системы
    arch = MiniArch()
    
    # Проверяем аргументы командной строки
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
            
    # Запускаем систему
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
    
    # Показываем загрузку
    arch.show_boot_screen()
    time.sleep(1)
    
    # Демонстрация команд
    print(f"\n{arch.colorize('Доступные команды:', 'yellow')}")
    print("-" * 40)
    
    # Показываем первые 15 команд
    for i, cmd in enumerate(sorted(arch.commands.keys())):
        if i < 15:
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

# Это запускает программу
if __name__ == "__main__":
    main()
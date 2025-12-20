# main.py - Основной загрузчик
import flet as ft
import importlib.util
import json
import os
import hashlib
from datetime import datetime
import urllib.request
import urllib.error
import ssl
import time
import threading

class GitHubAppLoader:
    def __init__(self, repo_owner, repo_name, app_file_path, branch="main", token=None):
        """
        Инициализация загрузчика приложений из GitHub
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.app_file_path = app_file_path
        self.branch = branch
        self.token = token
        
        # Настройки кэша
        self.cache_dir = "github_app_cache"
        self.cache_info_file = os.path.join(self.cache_dir, "cache_info.json")
        self.cache_code_file = os.path.join(self.cache_dir, "app_code.py")
        
        # Создаем папку для кэша
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Базовые настройки
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _get_headers(self):
        """Возвращает заголовки для запросов к GitHub"""
        headers = {
            "User-Agent": "Flet-GitHub-App-Loader/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def check_internet(self):
        """Проверяет доступность интернета"""
        try:
            with urllib.request.urlopen("https://github.com", 
                                       timeout=5, 
                                       context=self.ssl_context):
                return True
        except:
            return False
    
    def get_raw_file_url(self):
        """Возвращает raw URL файла на GitHub"""
        return f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{self.app_file_path}"
    
    def get_latest_commit_sha(self):
        """Получает SHA последнего коммита"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits/{self.branch}"
            request = urllib.request.Request(url, headers=self._get_headers())
            
            with urllib.request.urlopen(request, timeout=10, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('sha', '')
        except:
            return ""
    
    def download_app(self):
        """Скачивает приложение с GitHub или использует кэш"""
        
        # Проверяем интернет
        is_online = self.check_internet()
        
        # Если есть интернет - пытаемся скачать новую версию
        if is_online:
            try:
                print("🌐 Интернет доступен, проверяем обновления...")
                
                # Скачиваем новую версию
                print(f"🔄 Скачиваем новую версию с GitHub...")
                file_url = self.get_raw_file_url()
                
                request = urllib.request.Request(file_url, headers=self._get_headers())
                
                with urllib.request.urlopen(request, timeout=15, context=self.ssl_context) as response:
                    app_code = response.read().decode('utf-8')
                
                # Получаем SHA последнего коммита для кэша
                latest_sha = self.get_latest_commit_sha()
                
                # Сохраняем в кэш
                self.save_to_cache(app_code, latest_sha)
                
                # Получаем обновленную информацию о кэше
                cache_info = self.get_cache_info()
                
                print("✅ Новая версия успешно скачана и сохранена в кэш")
                return app_code, True, cache_info
                
            except Exception as e:
                print(f"⚠️ Ошибка при скачивании: {str(e)}")
                # Пробуем загрузить из кэша
                cached_code = self.load_from_cache()
                if cached_code:
                    print("📂 Используем кэшированную версию (после ошибки)")
                    return cached_code, False, self.get_cache_info()
                raise
        
        else:
            # Оффлайн режим
            print("📴 Нет интернета, используем кэш")
            cached_code = self.load_from_cache()
            if cached_code:
                return cached_code, False, self.get_cache_info()
            else:
                raise Exception("Нет интернета и кэшированной версии приложения")
    
    def save_to_cache(self, app_code, commit_sha):
        """Сохраняет код приложения в кэш"""
        try:
            # Сохраняем код
            with open(self.cache_code_file, "w", encoding="utf-8") as f:
                f.write(app_code)
            
            # Сохраняем информацию о кэше
            cache_info = {
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "branch": self.branch,
                "file_path": self.app_file_path,
                "commit_sha": commit_sha,
                "code_hash": hashlib.md5(app_code.encode()).hexdigest(),
                "size_bytes": len(app_code),
                "last_update": datetime.now().isoformat(),
                "cache_date": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
            
            with open(self.cache_info_file, "w", encoding="utf-8") as f:
                json.dump(cache_info, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Кэш сохранен: {len(app_code)} байт")
            
        except Exception as e:
            print(f"⚠️ Ошибка при сохранении кэша: {e}")
    
    def load_from_cache(self):
        """Загружает код приложения из кэша"""
        try:
            if os.path.exists(self.cache_code_file):
                with open(self.cache_code_file, "r", encoding="utf-8") as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке кэша: {e}")
            return None
    
    def get_cache_info(self):
        """Получает информацию о кэше"""
        try:
            if os.path.exists(self.cache_info_file):
                with open(self.cache_info_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except:
            return None
    
    def clear_cache(self):
        """Очищает кэш"""
        try:
            if os.path.exists(self.cache_code_file):
                os.remove(self.cache_code_file)
            if os.path.exists(self.cache_info_file):
                os.remove(self.cache_info_file)
            print("🗑️ Кэш очищен")
        except Exception as e:
            print(f"⚠️ Ошибка при очистке кэша: {e}")


class LoaderUI:
    """Пользовательский интерфейс загрузчика"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "GitHub App Loader"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        
        # Настройки GitHub репозитория
        self.repo_config = {
            "owner": "Arix89",
            "repo": "Loader", 
            "file": "app.py",
            "branch": "main",
            "token": None
        }
        
        self.loader = None
        
        # Автоматически запускаем загрузку при старте
        self.auto_load_app()
    
    def setup_ui(self, show_buttons=False):
        """Настраивает пользовательский интерфейс"""
        # Очищаем страницу
        self.page.clean()
        
        # Заголовок
        self.title = ft.Text(
            "🚀 GitHub App Loader",
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Информация о репозитории
        self.repo_info = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📂 Информация о репозитории", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Репозиторий: {self.repo_config['owner']}/{self.repo_config['repo']}"),
                    ft.Text(f"Файл: {self.repo_config['file']}"),
                    ft.Text(f"Ветка: {self.repo_config['branch']}"),
                ]),
                padding=15
            )
        )
        
        # Статус
        self.status_text = ft.Text("🔄 Автоматическая загрузка приложения...", size=16)
        self.status_icon = ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE)
        
        status_row = ft.Row([self.status_icon, self.status_text])
        
        # Кэш информация
        self.cache_info_text = ft.Text("", size=12, color=ft.Colors.GREY_400)
        
        # Прогресс бар
        self.progress_bar = ft.ProgressBar(width=400, visible=True)
        
        # Кнопки
        buttons_row = ft.Row([], alignment=ft.MainAxisAlignment.CENTER)
        
        if show_buttons:
            self.load_btn = ft.ElevatedButton(
                "🔄 Повторить загрузку",
                icon=ft.Icons.REFRESH,
                on_click=self.load_app,
                width=200
            )
            
            self.clear_cache_btn = ft.OutlinedButton(
                "🗑️ Очистить кэш",
                icon=ft.Icons.DELETE,
                on_click=self.clear_cache,
                width=200
            )
            
            buttons_row.controls = [self.load_btn, self.clear_cache_btn]
        
        # Собираем интерфейс
        self.page.add(
            ft.Column([
                self.title,
                ft.Divider(),
                self.repo_info,
                ft.Divider(height=20),
                status_row,
                self.cache_info_text,
                ft.Divider(height=10),
                self.progress_bar,
                ft.Divider(height=20),
                buttons_row
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # Обновляем страницу
        self.page.update()
    
    def update_status(self, message, icon=ft.Icons.INFO, color=ft.Colors.BLUE):
        """Обновляет статус в UI"""
        if hasattr(self, 'status_text'):
            self.status_text.value = message
            self.status_icon.name = icon
            self.status_icon.color = color
            self.page.update()
    
    def show_progress(self, show=True):
        """Показывает/скрывает прогресс бар"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.visible = show
            self.page.update()
    
    def auto_load_app(self):
        """Автоматически загружает приложение при старте"""
        # Сначала показываем базовый UI
        self.setup_ui(show_buttons=False)
        
        # Запускаем загрузку в отдельном потоке
        threading.Thread(target=self.load_app, daemon=True).start()
    
    def load_app(self, e=None):
        """Загружает и запускает приложение"""
        try:
            self.update_status("🔄 Инициализация загрузчика...", ft.Icons.SETTINGS, ft.Colors.BLUE)
            
            # Создаем загрузчик
            self.loader = GitHubAppLoader(
                repo_owner=self.repo_config["owner"],
                repo_name=self.repo_config["repo"],
                app_file_path=self.repo_config["file"],
                branch=self.repo_config["branch"],
                token=self.repo_config["token"]
            )
            
            # Проверяем интернет
            if not self.loader.check_internet():
                self.update_status("📶 Нет интернета, проверяем кэш...", ft.Icons.WIFI_OFF, ft.Colors.ORANGE)
                time.sleep(1)
            
            # Скачиваем приложение
            self.update_status("🌐 Подключаемся к GitHub...", ft.Icons.CLOUD_DOWNLOAD, ft.Colors.BLUE)
            
            app_code, is_fresh, cache_info = self.loader.download_app()
            
            # Обновляем информацию о кэше
            if cache_info and hasattr(self, 'cache_info_text'):
                last_update = datetime.fromisoformat(cache_info["last_update"]).strftime("%d.%m.%Y %H:%M")
                self.cache_info_text.value = f"💾 Кэш: {cache_info['size_bytes']} байт, обновлен: {last_update}"
            
            # Показываем статус загрузки
            if is_fresh:
                self.update_status("✅ Загружена новая версия!", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
            else:
                self.update_status("📂 Используем кэшированную версию", ft.Icons.ARCHIVE, ft.Colors.ORANGE)
            
            time.sleep(1)
            
            # Запускаем приложение
            self.update_status("🚀 Запускаем приложение...", ft.Icons.PLAY_ARROW, ft.Colors.GREEN)
            time.sleep(0.5)
            
            self.run_app(app_code)
            
        except Exception as ex:
            self.show_progress(False)
            self.update_status(f"❌ Ошибка: {str(ex)}", ft.Icons.ERROR, ft.Colors.RED)
            
            # Показываем кнопки для повторной попытки
            self.setup_ui(show_buttons=True)
            print(f"Ошибка: {ex}")
    
    def run_app(self, app_code):
        """Запускает загруженное приложение"""
        try:
            # Создаем модуль из кода
            spec = importlib.util.spec_from_loader("github_app", loader=None)
            module = importlib.util.module_from_spec(spec)
            
            # Выполняем код
            exec(app_code, module.__dict__)
            
            # Очищаем текущую страницу
            self.page.clean()
            
            # Запускаем main функцию из загруженного приложения
            if hasattr(module, 'main'):
                module.main(self.page)
            else:
                raise Exception("Функция main() не найдена в загруженном приложении")
                
        except Exception as ex:
            self.page.clean()
            self.page.add(ft.Text(f"Ошибка запуска приложения: {str(ex)}", color=ft.Colors.RED))
    
    def clear_cache(self, e=None):
        """Очищает кэш"""
        if self.loader:
            self.loader.clear_cache()
            self.cache_info_text.value = ""
            self.update_status("🗑️ Кэш очищен", ft.Icons.DELETE, ft.Colors.ORANGE)


def main(page: ft.Page):
    """Основная функция запуска загрузчика"""
    LoaderUI(page)

if __name__ == "__main__":
    ft.app(target=main)
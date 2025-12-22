# main_app.py - Пример приложения, которое будет загружаться с GitHub
import flet as ft
import random
from datetime import datetime

def main(page: ft.Page):
    page.title = "Мое приложение с GitHub"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Заголовок
    header = ft.Container(
        content=ft.Column([
            '''ft.Text(
                "🎉 Мое первое приложение с GitHub!",
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "✅ Успешно загружено и работает!",
                size=16,
                color=ft.Colors.GREEN,
                text_align=ft.TextAlign.CENTER
            ),'''
        ]),
        alignment=ft.alignment.center,
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
    )
    
    # Информационная панель
    info_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("📊 Информация о приложении", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(f"Версия: 1.0.0"),
                ft.Text(f"Дата загрузки: {datetime.now().strftime('%d.%m.%Y %H:%M')}"),
                ft.Text("Источник: GitHub Repository"),
                ft.Text("Статус: ✅ Активно"),
            ], spacing=5),
            padding=20,
        ),
        elevation=5,
    )
    
    # Счетчик
    counter_value = ft.Text("0", size=40, weight=ft.FontWeight.BOLD)
    
    def increment_counter(e):
        counter_value.value = str(int(counter_value.value) + 1)
        page.update()
    
    def decrement_counter(e):
        counter_value.value = str(int(counter_value.value) - 1)
        page.update()
    
    def reset_counter(e):
        counter_value.value = "0"
        page.update()
    
    counter_section = ft.Column([
        ft.Text("🔢 Счетчик", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([
            counter_value
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            ft.IconButton(ft.Icons.REMOVE, on_click=decrement_counter, bgcolor=ft.Colors.RED_100),
            ft.IconButton(ft.Icons.REFRESH, on_click=reset_counter, bgcolor=ft.Colors.GREY_100),
            ft.IconButton(ft.Icons.ADD, on_click=increment_counter, bgcolor=ft.Colors.GREEN_100),
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Генератор цитат
    quotes = [
        "Код пишется для людей, а не для машин.",
        "Лучше один раз написать, чем сто раз объяснять.",
        "Работающий код сегодня лучше идеального кода завтра.",
        "GitHub - это социальная сеть для разработчиков.",
        "Каждая проблема - это возможность научиться чему-то новому."
    ]
    
    quote_text = ft.Text(random.choice(quotes), size=16, text_align=ft.TextAlign.CENTER, italic=True)
    
    def new_quote(e):
        quote_text.value = random.choice(quotes)
        page.update()
    
    quote_section = ft.Column([
        ft.Text("💭 Случайная цитата", size=20, weight=ft.FontWeight.BOLD),
        quote_text,
        ft.ElevatedButton("Новая цитата", icon=ft.Icons.AUTORENEW, on_click=new_quote),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    # Кнопки действий
    def show_alert(e):
        dlg = ft.AlertDialog(
            title=ft.Text("🎊 Поздравляем!"),
            content=ft.Text("Приложение успешно работает из GitHub!"),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(dlg))]
        )
        page.open(dlg)
    
    action_buttons = ft.Row([
        ft.ElevatedButton("Показать alert", icon=ft.Icons.NOTIFICATIONS, on_click=show_alert),
        ft.ElevatedButton("Обновить страницу", icon=ft.Icons.REFRESH, 
                         on_click=lambda e: page.update()),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    # Футер
    footer = ft.Container(
        content=ft.Column([
            ft.Divider(),
            ft.Text(
                "📱 Приложение загружено с GitHub",
                size=12,
                color=ft.Colors.GREY_500,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "🔄 Автоматическое обновление при перезапуске",
                size=10,
                color=ft.Colors.GREY_400,
                text_align=ft.TextAlign.CENTER
            ),
        ]),
        padding=10,
    )
    
    # Собираем все вместе
    page.add(
        ft.Column([
            header,
            ft.Divider(height=20),
            info_card,
            ft.Divider(height=20),
            counter_section,
            ft.Divider(height=20),
            quote_section,
            ft.Divider(height=20),
            action_buttons,
            ft.Divider(height=30),
            footer
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    )

# Тестовая функция для проверки
def test():
    print("Приложение успешно загружено!")

if __name__ == "__main__":
    ft.app(target=main)
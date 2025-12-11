#!/usr/bin/env python3
"""
GUI для FreeCAD FastAPI сервера.
Запускается опционально, не влияет на работу сервера.
"""

import sys
import webbrowser
import threading
import time
from tkinter import Tk, Label, Button, Frame, messagebox, ttk
import requests
import logging

logger = logging.getLogger(__name__)

class FreeCADGUI:
    """GUI для управления FreeCAD FastAPI сервером."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FreeCAD API Gateway - GUI")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # URL сервера
        self.base_url = "http://localhost:8080"
        self.mcp_url = "http://localhost:9000/mcp"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса."""
        # Заголовок
        title_label = Label(
            self.root, 
            text="FreeCAD API Gateway", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=10)
        
        # Статус сервера
        self.status_frame = Frame(self.root, bg="#f0f0f0")
        self.status_frame.pack(pady=5)
        
        self.status_label = Label(
            self.status_frame,
            text="Проверка статуса сервера...",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.status_label.pack()
        
        # Прогресс бар
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(pady=5)
        self.progress.start()
        
        # Кнопки управления
        button_frame = Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        # Открыть Swagger
        swagger_btn = Button(
            button_frame,
            text="🌐 Открыть Swagger UI",
            command=self.open_swagger,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        swagger_btn.grid(row=0, column=0, padx=5)
        
        # Открыть MCP
        mcp_btn = Button(
            button_frame,
            text="🔗 Открыть MCP",
            command=self.open_mcp,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        mcp_btn.grid(row=0, column=1, padx=5)
        
        # Проверить статус
        status_btn = Button(
            button_frame,
            text="✅ Проверить статус",
            command=self.check_status,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        status_btn.grid(row=0, column=2, padx=5)
        
        # Разделитель
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        
        # Форма создания фигур
        self.create_shape_frame()
        
        # Разделитель
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        
        # Форма создания сборки
        self.create_assembly_frame()
        
        # Запускаем проверку статуса
        self.check_status_async()
        
    def create_shape_frame(self):
        """Создание формы для создания фигур."""
        frame = Frame(self.root, bg="#f0f0f0", relief="groove", bd=2)
        frame.pack(pady=5, padx=10, fill="x")
        
        Label(frame, text="Создание фигур", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        
        # Выбор типа фигуры
        shape_frame = Frame(frame, bg="#f0f0f0")
        shape_frame.pack(pady=5)
        
        Label(shape_frame, text="Тип фигуры:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        
        self.shape_var = ttk.Combobox(
            shape_frame,
            values=["cube", "sphere", "cylinder"],
            state="readonly",
            width=15
        )
        self.shape_var.set("cube")
        self.shape_var.grid(row=0, column=1, padx=5)
        
        # Размер
        Label(shape_frame, text="Размер (мм):", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        
        self.size_var = ttk.Entry(shape_frame, width=10)
        self.size_var.insert(0, "10")
        self.size_var.grid(row=0, column=3, padx=5)
        
        # Кнопка создания
        create_btn = Button(
            shape_frame,
            text="➕ Создать фигуру",
            command=self.create_shape,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=3
        )
        create_btn.grid(row=0, column=4, padx=5)
        
        # Результат
        self.shape_result = Label(frame, text="", bg="#f0f0f0", wraplength=500)
        self.shape_result.pack(pady=5)
        
    def create_assembly_frame(self):
        """Создание формы для создания сборки."""
        frame = Frame(self.root, bg="#f0f0f0", relief="groove", bd=2)
        frame.pack(pady=5, padx=10, fill="x")
        
        Label(frame, text="Создание сборки", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        
        # Имя сборки
        assembly_frame = Frame(frame, bg="#f0f0f0")
        assembly_frame.pack(pady=5)
        
        Label(assembly_frame, text="Имя сборки:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        
        self.assembly_name = ttk.Entry(assembly_frame, width=20)
        self.assembly_name.insert(0, "MyRobotAssembly")
        self.assembly_name.grid(row=0, column=1, padx=5)
        
        # Создавать детали
        self.create_parts_var = ttk.Checkbutton(
            assembly_frame,
            text="Создать стандартные детали",
            variable=self.create_parts_var
        )
        self.create_parts_var.grid(row=0, column=2, padx=5)
        
        # Кнопка создания
        create_btn = Button(
            assembly_frame,
            text="⚙️ Создать сборку",
            command=self.create_assembly,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=3
        )
        create_btn.grid(row=0, column=3, padx=5)
        
        # Результат
        self.assembly_result = Label(frame, text="", bg="#f0f0f0", wraplength=500)
        self.assembly_result.pack(pady=5)
        
    def check_status_async(self):
        """Асинхронная проверка статуса сервера."""
        def check():
            try:
                # Проверяем FastAPI
                response = requests.get(f"{self.base_url}/api/mcp/status", timeout=5)
                if response.status_code == 200:
                    self.update_status("✅ Сервер работает", "green")
                else:
                    self.update_status("⚠️ Сервер не отвечает", "orange")
            except requests.exceptions.ConnectionError:
                self.update_status("❌ Сервер не запущен", "red")
            except Exception as e:
                self.update_status(f"❌ Ошибка: {str(e)}", "red")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        
    def update_status(self, message, color):
        """Обновление статуса."""
        self.root.after(0, lambda: self._update_status_ui(message, color))
        
    def _update_status_ui(self, message, color):
        """Обновление статуса в UI потоке."""
        self.status_label.config(text=message, fg=color)
        self.progress.stop()
        self.progress.pack_forget()
        
    def check_status(self):
        """Ручная проверка статуса."""
        self.progress.pack(pady=5)
        self.progress.start()
        self.status_label.config(text="Проверка статуса...", fg="black")
        self.check_status_async()
        
    def open_swagger(self):
        """Открыть Swagger UI."""
        try:
            webbrowser.open(f"{self.base_url}/docs")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть Swagger: {e}")
            
    def open_mcp(self):
        """Открыть MCP."""
        try:
            webbrowser.open(self.mcp_url)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть MCP: {e}")
            
    def create_shape(self):
        """Создать фигуру."""
        try:
            shape_type = self.shape_var.get()
            size = float(self.size_var.get())
            
            if size <= 0:
                messagebox.showerror("Ошибка", "Размер должен быть положительным")
                return
                
            response = requests.get(
                f"{self.base_url}/api/cad/create-shape",
                params={"shape_type": shape_type, "size": size},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.shape_result.config(
                    text=f"✅ Успешно: {result['result']}",
                    fg="green"
                )
            else:
                self.shape_result.config(
                    text=f"❌ Ошибка: {response.text}",
                    fg="red"
                )
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный размер")
        except Exception as e:
            self.shape_result.config(
                text=f"❌ Ошибка: {str(e)}",
                fg="red"
            )
            
    def create_assembly(self):
        """Создать сборку."""
        try:
            assembly_name = self.assembly_name.get()
            if not assembly_name:
                messagebox.showerror("Ошибка", "Введите имя сборки")
                return
                
            response = requests.post(
                f"{self.base_url}/api/cad/create-assembly",
                params={
                    "assembly_name": assembly_name,
                    "create_default_parts": "true"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.assembly_result.config(
                    text=f"✅ Успешно: {result['message']}",
                    fg="green"
                )
            else:
                self.assembly_result.config(
                    text=f"❌ Ошибка: {response.text}",
                    fg="red"
                )
                
        except Exception as e:
            self.assembly_result.config(
                text=f"❌ Ошибка: {str(e)}",
                fg="red"
            )

def run_gui():
    """Запуск GUI в отдельном потоке."""
    try:
        root = Tk()
        app = FreeCADGUI(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Ошибка GUI: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить GUI: {e}")

if __name__ == "__main__":
    run_gui()
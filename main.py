import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class LightingCatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Справочник светильников (Вариант 28)")
        self.root.geometry("1000x650")
        self.db = []
        self.next_id = 1
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        btn_frame = ttk.Frame(self.root, padding="5")
        btn_frame.pack(fill=tk.X)
        buttons = [
            ("Импортировать JSON", self.import_json),
            ("Сохранить в JSON", self.save_json),
            ("Просмотр БД", self.refresh_tree),
            ("Вычисление значений", self.calculate_and_visualize),
            ("Очистить БД", self.clear_db)
        ]
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, command=cmd).grid(row=0, column=i, padx=5, pady=5)

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        columns = ("id", "name", "light_area", "cost", "room_area")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название светильника")
        self.tree.heading("light_area", text="Номинальная площадь (м²)")
        self.tree.heading("cost", text="Стоимость (руб)")
        self.tree.heading("room_area", text="Площадь аудитории (м²)")
        self.tree.column("id", width=40)
        self.tree.column("name", width=200)
        self.tree.column("light_area", width=150)
        self.tree.column("cost", width=100)
        self.tree.column("room_area", width=150)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_frame = ttk.LabelFrame(self.root, text="Поля ввода, поиска и управления записями", padding="10")
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        for i in range(8):
            bottom_frame.grid_columnconfigure(i, weight=1)

        fields = ["Название:", "Площадь лампы:", "Стоимость:", "Площадь аудитории:"]
        self.entries = []
        for i, label_text in enumerate(fields):
            ttk.Label(bottom_frame, text=label_text).grid(row=0, column=i * 2, padx=2, pady=2, sticky=tk.W)
            entry = ttk.Entry(bottom_frame, width=12)
            entry.grid(row=0, column=i * 2 + 1, padx=2, pady=2, sticky=tk.EW)
            self.entries.append(entry)

        ttk.Button(bottom_frame, text="Ввести запись", command=self.add_record).grid(row=1, column=0, columnspan=2,
                                                                                     pady=5, padx=2, sticky=tk.EW)
        ttk.Button(bottom_frame, text="Редактировать", command=self.edit_record).grid(row=1, column=2, columnspan=2,
                                                                                      pady=5, padx=2, sticky=tk.EW)
        ttk.Button(bottom_frame, text="Удалить запись", command=self.delete_record).grid(row=1, column=4, columnspan=2,
                                                                                         pady=5, padx=2, sticky=tk.EW)
        ttk.Button(bottom_frame, text="Перейти к записи (ID)", command=self.goto_record).grid(row=1, column=6,
                                                                                              columnspan=2, pady=5,
                                                                                              padx=2, sticky=tk.EW)

        ttk.Label(bottom_frame, text="Поиск по названию:").grid(row=2, column=0, columnspan=2, pady=5, padx=2,
                                                                sticky=tk.W)
        self.search_entry = ttk.Entry(bottom_frame, width=15)
        self.search_entry.grid(row=2, column=2, columnspan=2, pady=5, padx=2, sticky=tk.EW)
        ttk.Button(bottom_frame, text="Найти", command=self.search_records).grid(row=2, column=4, columnspan=2, pady=5,
                                                                                 padx=2, sticky=tk.EW)
        ttk.Button(bottom_frame, text="Сбросить поиск", command=self.refresh_tree).grid(row=2, column=6, columnspan=2,
                                                                                        pady=5, padx=2, sticky=tk.EW)
    def get_input_data(self):
        name = self.entries[0].get().strip()
        try:
            light_area = float(self.entries[1].get())
            cost = float(self.entries[2].get())
            room_area = float(self.entries[3].get())
            if not name: raise ValueError
            return name, light_area, cost, room_area
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные! Название не может быть пустым, остальные поля - числа.")
            return None

    def add_record(self):
        data = self.get_input_data()
        if data:
            name, light_area, cost, room_area = data
            record = {"id": self.next_id, "name": name, "light_area": light_area, "cost": cost, "room_area": room_area}
            self.db.append(record)
            self.next_id += 1
            self.clear_entries()
            self.refresh_tree()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования.")
            return
        data = self.get_input_data()
        if data:
            name, light_area, cost, room_area = data
            item_id = int(self.tree.item(selected[0])['values'][0])
            for record in self.db:
                if record['id'] == item_id:
                    record['name'] = name
                    record['light_area'] = light_area
                    record['cost'] = cost
                    record['room_area'] = room_area
                    break
            self.refresh_tree()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        item_id = int(self.tree.item(selected[0])['values'][0])
        self.db = [r for r in self.db if r['id'] != item_id]
        self.refresh_tree()

    def goto_record(self):
        target_id = simpledialog.askinteger("Переход", "Введите ID записи:")
        if target_id:
            for item in self.tree.get_children():
                if int(self.tree.item(item)['values'][0]) == target_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    values = self.tree.item(item)['values']
                    self.entries[0].delete(0, tk.END)
                    self.entries[0].insert(0, values[1])
                    for i in range(1, 4):
                        self.entries[i].delete(0, tk.END)
                        self.entries[i].insert(0, values[i+1])
                    return
            messagebox.showinfo("Информация", f"Запись с ID {target_id} не найдена.")

    def search_records(self):
        query = self.search_entry.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for record in self.db:
            if query in record['name'].lower():
                self.tree.insert("", tk.END, values=(record['id'], record['name'], record['light_area'], record['cost'], record['room_area']))

    def clear_db(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю базу данных?"):
            self.db = []
            self.next_id = 1
            self.refresh_tree()

    def import_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                max_id = max([record['id'] for record in imported_data], default=0)
                self.db = imported_data
                self.next_id = max_id + 1
                self.refresh_tree()
                messagebox.showinfo("Успех", "Данные успешно импортированы.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")

    def save_json(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.db, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "Данные успешно сохранены.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def calculate_and_visualize(self):
        if not self.db:
            messagebox.showwarning("Внимание", "База данных пуста. Нечего вычислять.")
            return
        results = []
        for item in self.db:
            if item['light_area'] > 0:
                lamps_needed = math.ceil(item['room_area'] / item['light_area'])
                total_cost = lamps_needed * item['cost']
            else:
                lamps_needed = 0
                total_cost = float('inf')
            results.append({'id': item['id'], 'name': item['name'], 'room_area': item['room_area'], 'lamps_needed': lamps_needed, 'total_cost': total_cost})

        valid_costs = [r['total_cost'] for r in results if r['total_cost'] != float('inf')]
        min_cost = min(valid_costs) if valid_costs else 0
        min_cost_records = [r for r in results if r['total_cost'] == min_cost]
        sorted_results = sorted(results, key=lambda x: x['total_cost'])

        res_window = tk.Toplevel(self.root)
        res_window.title("Результаты вычислений и визуализация")
        res_window.geometry("800x600")
        text_frame = ttk.Frame(res_window)
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        res_text = tk.Text(text_frame, height=8, width=80, font=("Arial", 10))
        res_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        res_text.insert(tk.END, f"=== МИНИМАЛЬНАЯ СТОИМОСТЬ ОСВЕЩЕНИЯ ===\n")
        res_text.insert(tk.END, f"Минимальная стоимость: {min_cost:.2f} руб.\n\n")
        res_text.insert(tk.END, "Варианты с минимальной стоимостью:\n")
        for r in min_cost_records:
            res_text.insert(tk.END, f"- Аудитория {r['room_area']} м² (Светильник: {r['name']}): нужно {r['lamps_needed']} шт.\n")
        res_text.insert(tk.END, f"\n=== РАСПРЕДЕЛЕНИЕ АУДИТОРИЙ ПО СТОИМОСТИ (от дешевой к дорогой) ===\n")
        for r in sorted_results:
            res_text.insert(tk.END, f"ID {r['id']} | {r['name']} | Аудитория: {r['room_area']} м² | Итог: {r['total_cost']:.2f} руб.\n")
        res_text.config(state=tk.DISABLED)

        chart_frame = ttk.Frame(res_window)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        names = [f"ID:{r['id']}" for r in sorted_results]
        costs = [r['total_cost'] for r in sorted_results]
        ax.bar(names, costs, color='skyblue', edgecolor='black')
        ax.set_title("Распределение аудиторий по стоимости освещения")
        ax.set_xlabel("Аудитории (ID записи)")
        ax.set_ylabel("Стоимость организации освещения (руб)")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for record in self.db:
            self.tree.insert("", tk.END, values=(record['id'], record['name'], record['light_area'], record['cost'], record['room_area']))

    def clear_entries(self):
        for entry in self.entries:
            entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = LightingCatalogApp(root)
    root.mainloop()
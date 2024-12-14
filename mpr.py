import tkinter as tk
from tkinter import font, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import time

class Job:
    def __init__(self, master, mpl_app):
        self.master = master
        self.master.title("MPR")
        self.master.geometry("1900x1210")
        self.mpl_app = mpl_app  

        self.label_font = font.Font(family="Pontiac", weight="bold", size=17)
        self.big_font = font.Font(family="SansSerif", size=16)
        self.result_font = font.Font(family="SansSerif", weight="bold", size=20) 
        self.n = 0
        self.m1 = []
        self.m2 = []
        self.id = []
        self.seqm1 = []
        self.seqm2 = []
        self.seq = []
        self.idlem1 = 0.0
        self.idlem2 = 0.0
        self.TTm1 = 0.0
        self.TTm2 = 0.0
        self.plotm1 = []
        self.plotm2 = []
        self.result_text = ""

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.page1 = ttk.Frame(self.notebook)
        self.notebook.add(self.page1, text="Input and Results")

        self.page2 = ttk.Frame(self.notebook)
        self.notebook.add(self.page2, text="Gantt Chart")

        self.title_label = tk.Label(self.page1, text="SCHEDULING N JOBS THROUGH 2 MACHINES", font=self.label_font,
                                    fg="black", bg="#CBC3E3")
        self.title_label.pack(side=tk.TOP, pady=20)

        self.input_panel = tk.Frame(self.page1, bg="#CBC3E3")
        self.input_panel.pack(side=tk.TOP, fill=tk.BOTH)

        self.input_panel_label = tk.Label(self.input_panel, text="Enter the number of jobs:", font=self.label_font,
                                          fg="black", bg="#CBC3E3")
        self.input_panel_label.pack(side=tk.LEFT)

        self.job_count_entry = tk.Entry(self.input_panel, font=self.big_font, bg="white")
        self.job_count_entry.pack(side=tk.LEFT)

        self.submit_button = tk.Button(self.input_panel, text="Submit", font=self.label_font, fg="black", bg="silver",
                                       command=self.submit_button_clicked)
        self.submit_button.pack(side=tk.LEFT,padx=20)

        self.clear_button = tk.Button(self.input_panel, text="Clear", font=self.label_font, bg="red", fg="white",
                                      command=self.clear_button_clicked)
        self.clear_button.pack(side=tk.LEFT,padx=20)

        self.show_gantt_button = tk.Button(self.input_panel, text="Show Gantt Chart", font=self.label_font, bg="silver",
                                            fg="Black", command=self.show_gantt_chart)
        self.show_gantt_button.pack(side=tk.RIGHT,padx=20)

        self.table_view = ttk.Treeview(self.page1, columns=("Job", "Processing Time A", "Processing Time B"),
                                       show="headings", height=20)
        self.table_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Pontiac", 20, "bold"))  

        for col in ("Job", "Processing Time A", "Processing Time B"):
            self.table_view.heading(col, text=col)

        for col in self.table_view["columns"]:
            self.table_view.column(col, width=250, anchor=tk.CENTER)

        style = ttk.Style()

        style.configure("Treeview", background="light yellow", foreground="black", rowheight=20,
                        fieldbackground="silver", font=("SansSerif", 14))  # Adjust font size of Treeview items
        style.map('Treeview', background=[('selected', 'blue')])

        self.result_panel = tk.Frame(self.page1, bg="#CBC3E3", padx=20, pady=20)
        self.result_panel.pack(side=tk.TOP, fill=tk.BOTH)

        self.result_textbox = tk.Text(self.result_panel, width=50, height=5, state='disabled', bg="white",
                                      font=self.result_font, padx=20, pady=20)
        self.result_textbox.pack()

        self.gantt_chart_title_label = tk.Label(self.page2, text="GANTT CHART", font=self.label_font, fg="black",
                                                 bg="#CBC3E3")
        self.gantt_chart_title_label.pack(side=tk.TOP, pady=20)

        self.plot_frame = tk.Frame(self.page2)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        self.mpl_app.create_canvas(self.plot_frame)

    def submit_button_clicked(self):
        try:
            self.n = int(self.job_count_entry.get())
            self.clear_button_clicked()  
            
            self.m1 = [0] * self.n
            self.m2 = [0] * self.n
            self.id = [0] * self.n
            self.plotm1 = []
            self.plotm2 = []

            for i in range(self.n):
                self.id[i] = i + 1
                m1_input = self.get_processing_time(f"Processing time for machine A for Job {i + 1}:")
                m2_input = self.get_processing_time(f"Processing time for machine B for Job {i + 1}:")

                if m1_input is None or m2_input is None:
                    messagebox.showerror("Error", "Please enter valid numeric values.")
                    return

                self.m1[i] = m1_input
                self.m2[i] = m2_input
                self.table_view.insert('', 'end', values=(self.id[i], self.m1[i], self.m2[i]))

            for j in range(self.n - 1):
                for i in range(self.n - 1 - j):
                    if min(self.m1[i], self.m2[i]) > min(self.m1[i + 1], self.m2[i + 1]):
                        self.m1[i], self.m1[i + 1] = self.m1[i + 1], self.m1[i]
                        self.m2[i], self.m2[i + 1] = self.m2[i + 1], self.m2[i]
                        self.id[i], self.id[i + 1] = self.id[i + 1], self.id[i]

            self.seqm1 = [0] * self.n
            self.seqm2 = [0] * self.n
            self.seq = [0] * self.n
            l, r = 0, self.n - 1

            for i in range(self.n):
                if self.m1[i] <= self.m2[i]:
                    self.seq[l] = self.id[i]
                    self.seqm1[l] = self.m1[i]
                    self.seqm2[l] = self.m2[i]
                    l += 1
                else:
                    self.seq[r] = self.id[i]
                    self.seqm1[r] = self.m1[i]
                    self.seqm2[r] = self.m2[i]
                    r -= 1

            self.idlem1 = 0.0
            self.idlem2 = 0.0
            self.TTm1 = 0.0
            self.TTm2 = 0.0

            for i in range(self.n):
                self.plotm1.append((self.TTm1, self.seqm1[i]))
                self.TTm1 += self.seqm1[i]
                if self.TTm1 > self.TTm2:
                    self.idlem2 += self.TTm1 - self.TTm2
                self.plotm2.append((max(self.TTm1, self.TTm2), self.seqm2[i]))
                self.TTm2 = max(self.TTm1, self.TTm2) + self.seqm2[i]

            self.idlem1 = self.TTm2 - self.TTm1
            self.result_text = (
                    "Optimal sequence of jobs: " + str(list(filter(None, self.seq))) + "\n"
            )
            if self.TTm2 > 0:  
                self.result_textbox.config(state='normal')
                self.result_textbox.delete(1.0, 'end')
                self.result_textbox.insert('end', self.result_text)
                self.result_textbox.config(state='disabled')
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")

    def clear_button_clicked(self):
        self.job_count_entry.delete(0, 'end')
        self.table_view.delete(*self.table_view.get_children())
        self.result_textbox.config(state='normal')
        self.result_textbox.delete(1.0, 'end')
        self.result_textbox.config(state='disabled')

    def get_processing_time(self, message):
        processing_time_var = tk.DoubleVar(value="")
        processing_time_window = tk.Toplevel(self.master)
        processing_time_window.title(message)

        root_x = self.master.winfo_rootx()
        root_y = self.master.winfo_rooty()
        root_width = self.master.winfo_width()
        root_height = self.master.winfo_height()

        window_width = 300
        window_height = 100
        x = root_x + root_width // 2 - window_width // 2
        y = root_y + root_height // 2 - window_height // 2

        processing_time_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        processing_time_label = tk.Label(processing_time_window, text=message)
        processing_time_label.pack()

        processing_time_entry = tk.Entry(processing_time_window, textvariable=processing_time_var)
        processing_time_entry.pack()
        processing_time_entry.focus_set()

        ok_button = tk.Button(processing_time_window, text="OK", command=processing_time_window.destroy)
        ok_button.pack()

        processing_time_window.grab_set()
        processing_time_window.wait_visibility()
        processing_time_window.wait_window()

        return float(processing_time_var.get())

    def show_gantt_chart(self):
        self.notebook.select(self.page2)
        if self.TTm2 > 0:  
            self.mpl_app.plot_gantt(self.plotm1, self.plotm2, self.TTm2, self.idlem1, self.idlem2, self.seq)
           

class Matplotlib:
    def __init__(self, master):
        self.master = master
        self.fig, self.gnt = plt.subplots(figsize=(8, 4))
        self.canvas = None

    def create_canvas(self, parent):
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def plot_gantt(self, plotm1, plotm2, TTm2, idle1, idle2, seq):
        self.gnt.clear()  

        self.gnt.set_ylim(0, 50)
        self.gnt.set_xlim(0, TTm2)
        self.gnt.set_xlabel('seconds since start')
        self.gnt.set_ylabel('Processor')
        self.gnt.set_yticks([15, 25])
        self.gnt.set_yticklabels(['M2', 'M1'])
        self.gnt.grid(False)


        t1 = threading.Thread(target=self.plotbar(plotm1, 20, 9, seq, delay=2000))
        t1.start()
        time.sleep(2)
        t2= threading.Thread(target=self.plotbar(plotm2, 5, 9, seq, delay=2000))
        t2.start()

        self.gnt.text(TTm2, 35, f'IdleTime for M2: {idle2} sec', ha='right', va='center', color='black',
                      fontsize=15)
        self.gnt.text(TTm2, 40, f'IdleTime for M1: {idle1} sec', ha='right', va='center', color='black',
                      fontsize=15)
        self.gnt.text(TTm2, 45, f'Total Time: {TTm2} sec', ha='right', va='center', color='black',
                      fontsize=15)
        self.canvas.draw()

    def plotbar(self, data, y, height, seq, delay):
        def plotjob(i):
            if i < len(data):
                x_start, length = data[i]
                color = plt.cm.viridis((seq[i] - 1) / len(data), alpha=0.3) 
                self.gnt.broken_barh([(x_start, length)], (y, height), facecolors=[color], edgecolor=('tab:grey'))
                self.gnt.text(x_start + length / 2, y + height / 2, f'{seq[i]}', ha='center', va='center',
                              color='black', fontsize=15)
                self.gnt.text(x_start, y - 1, f'{x_start}', ha='center', va='center', color='black')
                self.gnt.text(x_start + length, y - 1, f'{x_start + length}', ha='center', va='center',
                              color='black')
                self.canvas.draw()
                self.master.after(delay, lambda: plotjob(i + 1))  

        plotjob(0)

if __name__ == "__main__":
    root = tk.Tk()
    mpl_app = Matplotlib(root)  
    japp = Job(root, mpl_app)
    root.mainloop()

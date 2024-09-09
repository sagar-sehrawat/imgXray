import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import threading

class imgXray:
    def __init__(self, root):
        self.root = root
        self.root.title("imgXray Tool By Sagar Sehrawat!! V1.0")
        self.root.geometry('1200x800')  

        self.image_path = None
        self.report_history = []
        self.current_report_index = -1
        self.output_dir = "Analysis_Output"

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.image_frame = tk.Frame(root)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.report_frame = tk.Frame(root)
        self.report_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.image_frame, width=600, height=400)
        self.canvas.pack(padx=10, pady=10)

        self.analysis_frame = tk.Frame(self.image_frame)
        self.analysis_frame.pack(pady=10)

        self.analyze_button = tk.Button(self.analysis_frame, text="Analyze", state=tk.DISABLED, command=self.analyze_image)
        self.analyze_button.grid(row=0, column=0, padx=10)

        self.navigation_frame = tk.Frame(self.report_frame)
        self.navigation_frame.pack(pady=10)

        self.prev_button = tk.Button(self.navigation_frame, text="Previous", state=tk.DISABLED, command=self.show_previous_report)
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(self.navigation_frame, text="Next", state=tk.DISABLED, command=self.show_next_report)
        self.next_button.grid(row=0, column=1, padx=10)

        self.output_text = tk.Text(self.report_frame, wrap='word', height=40)  
        self.output_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.output_text.configure(font=("Courier", 12))

        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open Image', command=self.open_image)
        self.file_menu.add_command(label='Exit', command=root.quit)

        self.search_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Search', menu=self.search_menu)
        self.search_menu.add_command(label='Find Text', command=self.find_text)

        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Tools', menu=self.tools_menu)
        self.tools_menu.add_command(label='Stegsolve', command=self.run_stegsolve)

        self.check_and_install_tools()

    def check_and_install_tools(self):
        tools = {
            'binwalk': 'binwalk',
            'strings': 'strings',
            'zsteg': 'zsteg',
            'exiftool': 'exiftool',
        }
        for tool, command in tools.items():
            try:
                subprocess.run([command, '--version'], capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                messagebox.showinfo("Tool Not Found", f"{tool} not found. Downloading...")
                self.install_tool(tool)

    def install_tool(self, tool):
        install_commands = {
            'binwalk': 'pip install binwalk',
            'strings': 'apt-get install -y strings',
            'zsteg': 'gem install zsteg',
            'exiftool': 'apt-get install -y exiftool',
        }
        if tool in install_commands:
            try:
                subprocess.run(install_commands[tool], shell=True, check=True)
                messagebox.showinfo("Tool Installed", f"{tool} has been installed.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Installation Error", f"Failed to install {tool}: {str(e)}")

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((600, 400), Image.Resampling.LANCZOS)
                self.img_tk = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
                self.analyze_button.config(state=tk.NORMAL)
                self.image_path = file_path
                self.output_text.delete(1.0, tk.END)
                self.report_frame.pack_forget()
                self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")

    def run_analysis_in_thread(self, command, report_title):
        def run_command():
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                output_file = os.path.join(self.output_dir, f"{report_title}_report.txt")
                with open(output_file, 'w') as file:
                    file.write(result.stdout)
                report = f"{report_title}\n\n{result.stdout}"
                self.report_history.append(report)
                self.current_report_index += 1
                self.display_report(report)
                self.update_navigation_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run {command[0]}: {str(e)}")
        threading.Thread(target=run_command).start()

    def analyze_image(self):
        if self.image_path:
            self.image_frame.pack_forget()
            self.report_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.run_analysis_in_thread(['binwalk', self.image_path], "Binwalk Report")
            self.run_analysis_in_thread(['strings', self.image_path], "Strings Report")
            self.run_analysis_in_thread(['zsteg', self.image_path], "zsteg Report")
            self.run_analysis_in_thread(['exiftool', self.image_path], "Exiftool Report")

    def display_report(self, report):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, report)

    def update_navigation_buttons(self):
        if self.current_report_index > 0:
            self.prev_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)

        if self.current_report_index < len(self.report_history) - 1:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def show_previous_report(self):
        if self.current_report_index > 0:
            self.current_report_index -= 1
            self.display_report(self.report_history[self.current_report_index])
            self.update_navigation_buttons()

    def show_next_report(self):
        if self.current_report_index < len(self.report_history) - 1:
            self.current_report_index += 1
            self.display_report(self.report_history[self.current_report_index])
            self.update_navigation_buttons()

    def find_text(self):
        search_text = simpledialog.askstring("Find Text", "Enter text to search:")
        if search_text:
            content = self.output_text.get(1.0, tk.END)
            if search_text in content:
                start_index = content.find(search_text)
                end_index = start_index + len(search_text)
                self.output_text.tag_add("highlight", f"1.0 + {start_index} chars", f"1.0 + {end_index} chars")
                self.output_text.tag_config("highlight", background="yellow")
            else:
                messagebox.showinfo("Search Result", "Text not found.")

    def run_stegsolve(self):
        try:
            subprocess.run(['stegsolve'], check=True)
        except FileNotFoundError:
            messagebox.showerror("Tool Not Found", "Stegsolve is not installed.")

def main():
    root = tk.Tk()
    app = imgXray(root)
    root.mainloop()

if __name__ == "__main__":
    main()

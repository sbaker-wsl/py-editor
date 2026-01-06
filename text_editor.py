from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import subprocess
import platform
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator
import tkinter.font as tkfont



current_directory = os.getcwd()
folder_path = current_directory + "/PyProjects"

# for undo and redo functionality
class Action:
    def __init__(self, pos, location):
        self.location = pos
        self.character = location


class Stack:
    def __init__(self):
        self.list = []

    def push(self, c):
        self.list.append(c)

    def peek(self):
        if self.len() > 0:
            return self.list[len(self.list) - 1]

    def pop(self):
        return self.list.pop()

    def len(self):
        return len(self.list)

    def pop_word(self):
        string = ""
        while (self.peek() != "space" and self.len() != 0):
            string += self.pop()
        if self.len() > 0:
            self.pop()
        return string

    def is_empty(self):
        if self.list == []:
            return True
        else:
            return False


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.redo_stack = Stack()
        self.undo_stack = Stack()
        self.delete_stack = Stack()
        self.txt_box = tk.Text(root)
        Percolator(self.txt_box).insertfilter(ColorDelegator())
        font = tkfont.Font(font=self.txt_box['font'])
        tab_width = font.measure(' ' * 4)
        self.txt_box.config(tabs=(tab_width))
        self.txt_box.pack(fill=BOTH, expand=True)
        self.txt_box['state'] = 'normal'
        self.txt_box.bind("<BackSpace>", self.on_backspace)
        self.txt_box.bind("<Delete>", self.on_delete)
        self.txt_box.bind("<KeyPress>", self.on_key_press)
        self.saved_name = ""

    def on_backspace(self, event):
        action = Action(self.txt_box.index("insert-1c"), self.txt_box.get(self.txt_box.index("insert-1c"), self.txt_box.index("insert")))
        self.delete_stack.push(action)
        self.on_key_press(event)

    def on_delete(self, event):
        action = Action(self.txt_box.index("insert"), self.txt_box.get(self.txt_box.index("insert"), self.txt_box.index("insert+1c")))
        self.delete_stack.push(action)
        self.on_key_press(event)

    def on_key_press(self, event):
        char = event.keysym
        if char == "BackSpace" or char == "Delete":
            if not self.delete_stack.is_empty():
                self.undo_stack.push(self.delete_stack.pop())

        elif event.state & 0x0004:
            next_char = event.keysym
            # Redo Operation (CTRL + Y)
            if next_char == "y":
                if not self.redo_stack.is_empty() and self.redo_stack.peek().character == "delete":
                    while not self.redo_stack.is_empty() and self.redo_stack.peek().character == "delete":
                        location = self.redo_stack.peek().location
                        print(self.redo_stack.peek().character)
                        self.undo_stack.push(Action(location, self.txt_box.get(self.txt_box.index(location), self.txt_box.index(location+"+1c"))))
                        self.txt_box.delete(self.redo_stack.peek().location)
                        self.redo_stack.pop()
                else:
                    while not self.redo_stack.is_empty() and self.redo_stack.peek().character != "delete":
                        self.txt_box.insert(self.redo_stack.peek().location, self.redo_stack.peek().character)
                        self.undo_stack.push(Action(self.redo_stack.peek().location, "delete"))
                        self.redo_stack.pop()
            # Undo Operation (CTRL + Z)
            elif next_char == "z":
                if self.undo_stack.is_empty() == False and self.undo_stack.peek().character == "delete":
                    while (self.undo_stack.is_empty() == False) and self.undo_stack.peek().character == "delete":
                        location = self.undo_stack.peek().location
                        self.redo_stack.push(Action(location, self.txt_box.get(self.txt_box.index(location), self.txt_box.index(location+"+1c"))))
                        self.txt_box.delete(self.undo_stack.pop().location)
                else:
                    while (self.undo_stack.is_empty() == False) and self.undo_stack.peek().character != "delete":
                        self.redo_stack.push(Action(self.undo_stack.peek().location, "delete"))
                        self.txt_box.insert(self.undo_stack.peek().location, self.undo_stack.pop().character)

            # Save Operation (CTRL + S)
            elif next_char == "s":
                if self.saved_name:
                    with open(self.saved_name, 'w') as file:
                        file.write(self.txt_box.get("1.0", tk.END))
                        messagebox.showinfo("Successfully Saved", "Your progress has been saved")
                else:
                    on_save_as_click(self)

            elif next_char == "r":
                on_run_click(self)

            elif next_char == "o":
                on_open_click(self)


        else:
            char = self.handle_extraneous(char)
            if (char != ""):
                self.undo_stack.push(Action(self.txt_box.index(tk.INSERT), "delete"))

    def handle_extraneous(self, string):
        match string:
            case "space":
                " "
            case "exclam":
                return "!"
            case "slash":
                return "/"
            case "Shift_L" | "Control_L" | "Control_R" | "Left" | "Down" | "Right" | "Up":
                return ""
            case "backslash":
                return "\\"
            case _:
                return string

# File-related operations
def on_open_click(editor):
    file_path = filedialog.askopenfilename(
        title="Select a file to open",
        initialdir=folder_path,
        filetypes=(("Python files", "*.py"), ("All files", "*.*"))
    )

    editor.saved_name = file_path

    if file_path:
        with open (file_path, 'r') as file:
            editor.undo_stack = Stack()
            editor.redo_stack = Stack()
            editor.delete_stack = Stack()
            content = file.read()
            editor.txt_box.delete("1.0",tk.END)
            editor.txt_box.insert(tk.INSERT,content)
    else:
        messagebox.showinfo("Alert: No Selection", "No file has been selected for opening", parent=editor.root)

def on_save_as_click(editor):
    file_path = filedialog.asksaveasfilename(
        title="Save As:",
        defaultextension=".py",
        initialdir=folder_path,
        filetypes=(("Python file", "*.py"), ("All files", "*.*"))
    )

    editor.saved_name = file_path

    if file_path:
        with open(file_path, 'w') as f:
            f.write(editor.txt_box.get("1.0",tk.END))
            messagebox.showinfo("Saved", f"Progress saved to {file_path}", parent=editor.root)
    else:
        messagebox.showinfo("Alert: Not Saved", "File hasn't been saved", parent=editor.root)

def on_run_click(editor):
    if editor.saved_name == "":
        messagebox.showinfo("Alert: Save before Executing", "You must first save (try CTRL+S) before executing a script!", parent=editor.root)
    else:
        command = "python " + editor.saved_name
        subprocess.Popen(["cmd", "/k", command], creationflags=subprocess.CREATE_NEW_CONSOLE)
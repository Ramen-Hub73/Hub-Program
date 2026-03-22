import tkinter as tk
from tkinter import scrolledtext, Toplevel, messagebox, simpledialog, filedialog
import subprocess
import threading
import os
import sys
import time
import ctypes
import importlib.util
import pkg_resources
import pyperclip
import keyboard
from pathlib import Path
from datetime import datetime
import ast
import webbrowser

if 'win' in sys.platform:
	ctypes.windll.shcore.SetProcessDpiAwareness(2)

try:
	open_file = sys.argv[1]
	print(f"Opening: {open_file}")
except Exception:
	open_file = None

self_file = __file__[len(__file__) - __file__[::-1].find("\\"):]
self_name = f"{self_file.replace('.py', '')}"
platform = sys.platform

root = tk.Tk()
root.title(self_name)
root.resizable(False, False)
root.iconbitmap(default="Hub_Default_Icon.ico")
root.iconbitmap("Hub_Icon.ico")

Length, Height = 70, 30
command_history = []
run = None
absolute_filepath = open_file
self_directory = os.path.dirname(os.path.realpath(__file__))
setting_variables = [tk.StringVar() for i in range(25)]
for var in setting_variables:
	var.set("0")

"""

BACKEND FUNCTIONS

"""

def ConfigWidget(widget=None, arg=None, value=None) -> None:
	Log(f"ConfigWidget(widget={widget}, arg={arg}, value={value})")
	if widget == None or arg == None:
		return
	
	data_type = type(widget)

	if data_type == str:
		exec(f"global {widget}\n{widget}.config({arg}={value})")
	elif data_type == list:
		for w in widget:
			exec(f"global {w}\n{w}.config({arg}={value})")

def Log(entry:str="DefaultLogEntry", type:str="ACCESS", time_log=False) -> None:
	if not bool(setting_variables[6].get()):
		return

	log_file = f"{self_name}Logs.txt"
	if type == "ACCESS":
		log = f"|{type}|{entry}|"
	elif type == "SYSTEM":
		log = f"|{type}|{'=' * 40}\n        {entry}|"
	elif type == "INFO":
		log = f"|{type}|\n{entry}"
	else:
		log = "N: {type}|"

	if time_log:
		log += f"{datetime.now()}"
	log += f"\n"
	cof_out = ContentOfFile(log_file, "List")
	treat_as_new = False
	if cof_out == "Non-existant File" or cof_out == "Empty File":
		treat_as_new = True

	if treat_as_new:
		WriteTo(log_file, log)
	else:
		if len(cof_out) >= 500:
			cof_out.pop(0)
		cof_out.append(log)
		WriteTo(log_file, "".join(cof_out))

def Update(scroll=False):
	if scroll == "down":
		textbox.yview(tk.END)
	elif scroll == "up":
		textbox.yview("1.0")
	elif type(scroll) == int:
		textbox.yview(scroll)
	textbox.update()

def Scan():
	return textbox.get("1.0", tk.END)

def Input(input=""):
	if type(input) == list:
		input = "".join(input)
	textbox.insert(tk.END, input)

def Delete(start=1, lines="All"):
	if not type(start) == int:
		start = 1
	if lines == "All":
		lines = Scan().count(f"\n")
	if start == 1 and lines >= Scan().count(f"\n"):
		textbox.delete("1.0", tk.END)
		return
	#Gets lines
	if start != 1 and lines == Scan().count(f"\n"):
		lines = 1
	kept = []
	text = Scan()
	for i in range(text.count(f"\n")):
		index = text.find(f"\n")
		kept.append(text[:-len(text) + index])
		text = text[index + 1:]
	#Catches out of range (incase nothing to delete)
	try:
		for i in range(lines):
			kept.pop(start - 1)
	except Exception:
		return
	#Displays final string
	textbox.delete("1.0", tk.END)
	for line in kept:
		if line != kept[len(kept) - 1]:
			Input(line + f"\n")
		else:
			Input(line)

def Show(text) -> None:
	Delete()
	Input(text)

def Slowprint(text, plus=False, chars_to_skip="", delay=.05, preset=None):
	if plus:
		content = Scan()
	else:
		content = ""
		Delete()
	
	i = 0	
	while i < len(text):
		string = ""
		display_char = ""
		skipping = False

		if text[i] in chars_to_skip:
			skipping = True
			display_char = ""
			
			string = text[i]
			j = 1
			while True:
				try:
					if text[i + j] in chars_to_skip:
						string += text[i + j]
						j += 1
					else:
						i += len(string) - 1
						break
				except Exception:
					i += len(string) - 1
					break
		else:
			string = text[i]
					
		if i == len(text) - 1:
			display_char = ""
		
		Input(string + display_char)
		Update(scroll="down")
		skip_counter = 0
		if not skipping:
			time.sleep(delay)
			
		i += 1

def Centered(text, char=" ", end=False, half=False, end_line=0,  newline=0, cuts=1, minus=0, length=Length):
	if type(text) == list:
		ls = []
		for value in text:
			ls.append(Centered(value, char, end, half, end_line, newline, cuts, minus, length))
		return ls
	#Minus and end not integrated together
	if not type(minus) == int:
		ShowError("Centered Function", "Argument 'minus' must be an integer")
	if half:
		cuts = 2
	if len(text) < length:
		if len(text) % 2 == 1:
			back = char * ((int(length / (cuts * 2)) -  int(len(text) / 2) - 1) - minus)
		else:
			back = char * ((int(length / (cuts * 2)) -  int(len(text) / 2)) - minus)
		string = back + text
		if end:
			string += char * (int(Length / (cuts)) - len(string))
			
		string = (f"\n" * newline) + string
		string += f"\n" * end_line
		
		return string
	else:
		return text

def ContentOfFile(filename="", type="String", clarification=True):
	try:
		with open(filename, "r") as file:
			if type == "String":
				content = file.read()
			elif type == "List":
				content = file.readlines()
			if content == "" and clarification:
				return "Empty File"
			else:
				return content
				
	except Exception:
		if os.path.exists(filename):
			return "Unable To Read File"
		if clarification:
			return "Non-existant File"
		else:
			return ""

def WriteTo(filename="", content=""):
	if filename == "":
		ShowError(message="Write To", extra="Argument 'filename' got no input")
		return
	
	with open(filename, "w") as file:
		file.write(content.replace(f'\u2192', ">"))

def Zip(list1, list2, zip_small=False) -> list:
	if type(list1) != list or type(list2) != list:
		raise TypeError("Both arguments 'list1' and 'list2' must be of type list")
	
	biggest = list1 if len(list1) > len(list2) else (list2 if len(list2) > len(list1) else None)
	smallest = list1 if biggest == list2 else (list2 if biggest == list1 else None)
	
	if biggest == None:
		biggest = list1
		smallest = list2
	
	reference = len(smallest) if zip_small else len(biggest)
	
	zipped = []
	for i in range(reference):
		try:
			zipped.append(biggest[i])
			zipped.append(smallest[i])
		except Exception:
			pass
	
	return zipped

def FunctionsOf(file:str=None, indexes=False, class_inclusion=False, ext:str="py", order_preset:list=None, indent_desc:bool=False) -> list[str]:
	#Func, indexes, class, indexes
	try:
		if file != None:
			filename = file
		else:
			return "Argument 'file' got no input"
			
		with open(filename, "r") as file:	
			lines = file.readlines()
	
		func_list = []
		class_list = []
		func_index_list = []
		class_index_list = []
	
		index = 0
		recent_class = None
		recent_func = None

		if ext == "py":
			if order_preset == ["class", "function"]:
				if indent_desc:
					for line in lines:
						if line.startswith("def "):
							name = lines[index][lines[index].find(" ") + 1:-len(lines[index]) + lines[index].find("(")]
							func_list.append(name)
							func_index_list.append(index)
							recent_func = name
							recent_class = None
	
						elif line.lstrip().startswith(f"def "):
							name = line[lines[index].find(" ") + 1:-len(lines[index]) + lines[index].find("(")]
							func_list.append(f"{'    ' * line.count(f'\t')}({recent_class if recent_class != None else recent_func}) {name}")
							func_index_list.append(index)
	
						elif line.startswith("class "):
							name = lines[index][lines[index].find(" ") + 1:-len(lines[index]) + lines[index].find(":")]
							class_list.append(name)
							class_index_list.append(index)
							recent_class = name
							recent_func = None
	
						index += 1
	
		if indexes:
			if class_inclusion:
				return func_list, func_index_list, class_list, class_index_list
			return func_list, index_list
		else:
			if class_inclusion:
				return func_list, class_list
			return func_list
		
	except Exception as e:
		return None

def FormatSize(bytes: int=0):
	for unit in ["B", "KB", "MB", "GB", "TB"]:
		if bytes < 1024:
			return f"{bytes:.2f} {unit}"
		bytes /= 1024
	f_bytes = int(bytes) if int(bytes) == bytes else f"{bytes:.2f}"
	return f"{f_bytes} PB"

"""

HUB FUNCTIONS

"""

def SetSelected(name: str="Select a script") -> None:
	Log(f"SetSelected(name={name})")
	if type(name) != str:
		name = "Select a script"
	else:
		if len(name) > 20:
			name = name[:-len(name) + 20] + "..."
	selected_script.set(name)

def Filepath(filename: str|None=None) -> str|None:
	Log(f"Filepath(filename={filename})")
	if filename == "Select a script":
		return None
	elif filename in scripts.keys():
		return scripts[filename]
	elif filename == None:
		return absolute_filepath
	elif os.path.isfile(os.path.join(self_directory, filename)):
		return filename
	else:
		return absolute_filepath

def Filename(path:str=None) -> None:
	path = path.replace("\\", "/")
	if not "/" in path:
		return path
	return path[len(path) - path[::-1].find("/"):]
	
def SeeCode(filename=None) -> None:
	Log(f"SeeCode(filename={filename})")
	Delete()
	filename = filename if filename != None else selected_script.get()
	filepath = Filepath(filename)
	
	if filepath != None:
		text = ContentOfFile(filepath)
		Input(Centered(f"Content Of {filename}", "=", end=True, end_line=1))
		denied = False
		if text == "Unable To Read File":
			denied = True
		if denied:
			Input(Centered(text, newline=14))
			textbox.config(state="disabled", bg="light gray")
			Update()
			time.sleep(3)
			textbox.config(state="normal", bg="white")
			Delete()	
		else:
			Input(text)
		function_setting = bool(setting_variables[1].get())
		copy_to_clip = False if function_setting == True else messagebox.askyesno("Confirmation", "Copy To Clipboard?")
		if copy_to_clip:
			pyperclip.copy(text)
	else:
		Input(Centered(f"Couldn't find file {filename}.", end=True, newline=1))
		Update()
		time.sleep(2)
		Delete()

def RunScript(filename=None) -> None:
	Log(f"RunScript(filename={filename})")
	filename = filename if filename != None else selected_script.get()
	filepath = Filepath(filename)

	if filepath == None or not os.path.exists(filepath):
		messagebox.showerror("File Not Found", f"The file {filename} was not found.", parent=root)
		return

	CloseScript()

	def ScriptThread() -> None:
		global run

		keyboard.add_hotkey("esc", CloseScript)

		ConfigWidget("close_button", "state", "tk.NORMAL")

		function_setting = bool(setting_variables[8].get())
		if function_setting:
			root.iconify()

		run = subprocess.Popen(filepath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
	
		result, error = run.communicate()
		result, error = result if result != "" else "Nothing...", error if error != "" else "Nothing..."

		keyboard.remove_hotkey("esc")

		Delete()
		Input(Centered(f"Output for {filename}", "=", end=True, end_line=3))
		Input(f"{result}\n\n\n{Centered("Error Output", "=", end=True)}\n\n\n{error}\n\n\n")
		root.attributes('-topmost', True)
		root.update_idletasks()
		root.attributes('-topmost', False)
		
		run = None

		ConfigWidget("close_button", "state", "tk.DISABLED")
		TopWindow(root, hold=True)

	run_thread = threading.Thread(target=ScriptThread)
	run_thread.start()

def CloseScript() -> None:
	Log("CloseScript()")
	global run
	if run != None:
		subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=run.pid))
		ConfigWidget("close_button", "state", "tk.DISABLED")
		run = None

def DriveSelect() -> None:
	Log("DriveSelect()")
	global absolute_filepath
	root.iconify()
	absolute_filepath = filedialog.askopenfilename(title="Select A File From Directory")
	if absolute_filepath in scripts.values():
		formatted = list(scripts.keys())[list(scripts.values()).index(absolute_filepath)]
	else:
		formatted = absolute_filepath[len(absolute_filepath) - absolute_filepath[::-1].find("/"):]
	if formatted != "":
		SetSelected(formatted if formatted != "" else "Select a script")
		OnScriptSelection(None, file=absolute_filepath)
	TopWindow(root, hold=True)

def ListScripts() -> None:
	Log("ListScripts()")
	directory = filedialog.askdirectory()
	function_setting = bool(setting_variables[0].get())
	python_exclusive = function_setting if function_setting == True else messagebox.askyesno("Exclusivity Confirmation", "Only Show Python Files?")
	if python_exclusive:
		files = [file for file in os.listdir(directory) if file.endswith(".py")]
	else:
		files = os.listdir(directory)
	
	string = Centered(f"Files in {directory}", char="=", end=True, newline=1) if len(files) > 0 else Centered(f"No files detected in {directory}", end=True, newline=2)
	i = 0
	for index, file in enumerate(files):
		if files == []:
			break
		if len(file) > 20:
			file = file[:-len(file) + 17] + "..."
		if index % 3 == 0:
			string += Centered(file, cuts=3, end=True, newline=2)
		else:
			string += Centered(file, cuts=3, end=True)
	Delete()
	Input(string)

def EditScript(filename=None) -> None:
	Log(f"EditScript(filename={filename})")
	global func_drop_change
	filename = filename if filename != None else selected_script.get()
	filepath = Filepath(filename)
	
	if not filepath == None and os.path.exists(filepath):
		function_setting = bool(setting_variables[4].get())
		if function_setting:
			root.iconify()
		edit_root = Toplevel(root)
		edit_root.title(f"{filename} Edit Window")
		edit_root.resizable(False, False)
		edit_root.iconbitmap("Hub_File_Icon.ico")
		edit_root.focus()

		editing_self = False
		if filepath == self_file or filepath == self_directory + self_file:
			editing_self = True

		updating = True
		keyboard.remove_hotkey("ctrl+shift+h")
		keyboard.add_hotkey("ctrl+shift+h", lambda: TopWindow(edit_root))

		content_list = ContentOfFile(filepath, "List")
		content_str = "".join(content_list)

		denied = False
		if content_str == "Unable To Read File":
			denied = True

		def Exit() -> None:
			function_setting = bool(setting_variables[7].get())
			exiting_content = ContentOfFile(filepath).strip()
			content = text_widget.get("1.0", tk.END).strip()
			keyboard.remove_hotkey("esc")
			keyboard.remove_hotkey("ctrl+shift+h")
			keyboard.add_hotkey("ctrl+shift+h", lambda: TopWindow(root))

			file_difference = True if (exiting_content != content and not exiting_content == "Non-existant File") else False

			if file_difference:
				confirmation = messagebox.askyesno("Save Prompt", "Save before closing?", parent=edit_root)
				if confirmation:
					SaveScript()

			edit_root.destroy()
			root.deiconify()
			if os.path.exists(filepath):
				OnScriptSelection()			

			if file_difference and function_setting and editing_self:
				Refresh()

		edit_root.protocol("WM_DELETE_WINDOW", lambda: Exit())

		text_widget = scrolledtext.ScrolledText(edit_root, wrap="none")
		if denied:
			text_widget.insert(tk.END, Centered(content_str, newline=11, length=80))
		else:
			text_widget.insert(tk.END, content_str)
		text_widget.grid(row=3, column=0, columnspan=6, padx=5, pady=5)

		text_widget.focus()
		text_widget.mark_set("insert", "1.0")

		if denied:
			text_widget.config(state="disabled", bg="light gray")
			updating = False

		selected_func = tk.StringVar()
		selected_func.set("Function Lookup")

		func_list, func_indexes, class_list, class_indexes = [], [], [], []
		if not denied:
			func_list, func_indexes, class_list, class_indexes = FunctionsOf(filepath, indexes=True, class_inclusion=True, order_preset=["class", "function"], indent_desc=True)

		func_list = [f"FUNC {func_indexes[index] + 1}: {f}" for index, f in enumerate(func_list)]
		class_list = [f"CLASS {class_indexes[index] + 1}: {c}" for index, c in enumerate(class_list)]

		functions = class_list + func_list
		indexes = class_indexes + func_indexes

		if functions == []:
			functions = [""]
			indexes = [None]
			selected_func.set("No Func/Class Detected")

		func_drop_change = False

		def PulseFuncDrop(value):
			global func_drop_change
			if denied:
				selected_func.set("No Func/Class Detected")
			func_drop_change = True

		func_dropdown = tk.OptionMenu(edit_root, selected_func, *functions, command=PulseFuncDrop)
		func_dropdown.grid(row=0, column=4, pady=10)
			
		def FindLine(index:int=None) -> None:
			line_index = index
			if line_index == None:
				line_index = simpledialog.askstring("Line Index Input", "What line would you like to go to?", parent=edit_root)
			if type(line_index) == int or line_index.isdigit():
				line_index = int(line_index)
				if len(content_list) < line_index:
					line_index = len(content_list)
				text_widget.yview(line_index - 12)
				text_widget.update()
				text_widget.mark_set("insert", f"{line_index}.0")
				text_widget.focus()
			else:
				messagebox.showerror("Invalid Type", f"Line index must be an integer.")

		def FindString(string=None, _return=False) -> None|list:
			global string_to_find, find_index
			from_user = True
			if string != None:
				from_user = False
			string = string if string != None else simpledialog.askstring("Find Input", "What would you like to search for?", parent=edit_root).strip()

			indexes = []
			#Optimization needed
			WriteTo(f"{self_name}_tempeditfile", text_widget.get("1.0", tk.END))
			content = ContentOfFile(f"{self_name}_tempeditfile", "List")

			for index, line in enumerate(content):
				if string in line:
					indexes.append(index + 1)
					continue

			if indexes == []:
				messagebox.showerror("String Not Found", f"'{string}' was not found in file.", parent=edit_root)
				return
		
			string_to_find = string
			if not from_user:
				return indexes
			messagebox.showinfo("FindString Info", f"Control + ,/. to go to next/prev occurance. (Count: {len(indexes)})", parent=edit_root)
			find_index = 0
			FindLine(indexes[0])

			def Next(event) -> None:
				global find_index
				indexes = FindString(string_to_find)
				index_count = len(indexes)
				if find_index >= index_count - 1:
					find_index = index_count - 1
					messagebox.showinfo("Last Index", "This is the last occurance.", parent=edit_root)
					return

				find_index += 1
				FindLine(indexes[find_index])

			def Prev(event) -> None:
				global find_index
				indexes = FindString(string_to_find)
				index_count = len(indexes)
				if find_index <= 0:
					find_index = 0
					messagebox.showinfo("First Index", "This is the first occurance.", parent=edit_root)
					return

				find_index -= 1
				FindLine(indexes[find_index])

			edit_root.bind("<Control-,>", Prev)
			edit_root.bind("<Control-.>", Next)

		line_button = tk.Button(edit_root, text="Go To Line", command=FindLine, width=20)
		line_button.grid(row=0, column=2, pady=5)

		settings_button = tk.Button(edit_root, text="Settings", command=lambda: OpenSettings(_from=edit_root), width=20)
		settings_button.grid(row=0, column=3, pady=5)

		yview_label = tk.Label(edit_root, text="YView: 1", width=20)
		yview_label.grid(row=2, column=0, columnspan=3, pady=5)

		index_label = tk.Label(edit_root, text="Line: 0 | Char: 0", width=20)
		index_label.grid(row=2, column=2, columnspan=2, pady=5)

		func_count_label = tk.Label(edit_root, text=f"Func Count: {len(func_list)} | Class Count: {len(class_list)}")
		func_count_label.grid(row=2, column=3, columnspan=2, pady=5)

		def UpdateIndex() -> None:
			global func_drop_change
			while updating:
				if func_drop_change:
					selected = selected_func.get()
					try:
						index = indexes[functions.index(selected)]
					except Exception:
						index = None
					if index != None:
						text_widget.yview(index - 11)
						text_widget.update()
						text_widget.mark_set("insert", f"{index + 1}.0")
						text_widget.focus()
					else:
						selected_func.set("No Func/Class Detected")
					func_drop_change = False
				try:
					position = text_widget.index(tk.INSERT)
					seperator_index = position.index(".")
					line = position[:-len(position) + seperator_index]
					char = position[seperator_index + 1:]
					index_label.config(text=f"Line: {line} | Char: {char}")
					y0, y1 = text_widget.yview() #Credit to Lion Kimbro (2 Lines)
					top_view = text_widget.index('@0,%d' % y0)
					yview_label.config(text=f"YView: {top_view}")
				except Exception:
					pass
				time.sleep(.125)

		def RenameScript() -> None:
			return
			confirmation = messagebox.askyesno("Rename Confirmation", "Rename script?", parent=edit_root)
			if confirmation:
				new_name = simpledialog.askstring("Rename Prompt", "Rename file to? (Extension needed)", parent=edit_root)
				WriteTo(new_name, text_widget.get("1.0", tk.END).rstrip())
				os.remove(filepath)

		def SaveScript() -> None:
			Log("SaveScript()")
			if denied:
				messagebox.showerror("Invalid Permissions", "You do not have authority to edit this file.", parent=edit_root)
				return
			function_setting = bool(setting_variables[3].get())
			confirmation = function_setting if function_setting == True else messagebox.askyesno("Save Confirmation", f"Save Changes To {filename}?")
			if confirmation:
				WriteTo(filepath, text_widget.get("1.0", tk.END).rstrip())
				messagebox.showinfo("Save Success", f"Successfully saved content to {filename}.",parent=edit_root)
			text_widget.focus()

		def DeleteScript() -> None:
			Log("DeleteScript()")
			confirmation = messagebox.askyesno("Deletion Confirmation", f"Delete file '{filename}'?", parent=edit_root)
			if confirmation:
				content = text_widget.get("1.0", tk.END)
				try:
					os.remove(filepath)
					messagebox.showinfo("Deletion Success", f"File '{filename}' was successfully deleted.", parent=edit_root)
					text_widget.delete("1.0", tk.END)
					selected_script.set("Select a script")
					ConfigWidget(["run_button", "edit_button", "see_code_button", "dropdown_button"], "state", "tk.DISABLED")
				except Exception:
					messagebox.showerror("Deletion Failure", f"File '{filename}' couldn't be found.", parent=edit_root)

		def RestoreScript() -> None:
			Log("RestoreScript()")
			confirmation = True
			exists = False
			if os.path.exists(filepath):
				confirmation = messagebox.askyesno("Restore Confirmation", f"Restore file to state when opened by EditScript?", parent=edit_root)
				exists = True
			
			if confirmation:
				WriteTo(filepath, content_str)
				if exists:
					messagebox.showinfo("Restored Successfully", f"Successfully restored '{filename}' to previous state.", parent=edit_root)
					return
				messagebox.showinfo("Restored Successfully", f"Successfully recreated file and readded contents.", parent=edit_root)
				text_widget.delete("1.0", tk.END)
				text_widget.insert("1.0", content_str)
				selected_script.set(filename)
				ConfigWidget(["run_button", "edit_button", "see_code_button", "dropdown_button"], "state", "tk.NORMAL")

		def Info() -> None:
			messagebox.showinfo("EditScript Info State", "EditScript Info() in developement.", parent=edit_root)
	
		save_button = tk.Button(edit_root, text="Save Script", command=SaveScript, width=20)
		save_button.grid(row=4, column=2, columnspan=2, pady=5)

		edit_root.bind("<Control-s>", lambda e: SaveScript())
		edit_root.bind("<Control-f>", lambda e: FindString())
		edit_root.bind("<Control-l>", lambda e: FindLine())
		edit_root.bind("<Control-d>", lambda e: DeleteScript())
		edit_root.bind("<Control-r>", lambda e: RestoreScript())
		edit_root.bind("<Control-Shift-i>", lambda e: Info())

		exit_button = tk.Button(edit_root, text="Exit", command=Exit, width=20)
		exit_button.grid(row=4, column=3, columnspan=2, pady=5)
		
		update_thread = threading.Thread(target=UpdateIndex)
		update_thread.daemon = True
		update_thread.start()

		TopWindow(edit_root, hold=True)

		keyboard.add_hotkey("esc", Exit)

	else:
		messagebox.showerror("File Not Found", f"The file {filename} was not found.", parent=root)

def Refresh() -> None:
	Log("Refresh()")
	CloseHub()
	python = sys.executable
	os.execl(python, python, self_file)

def DropdownManipulation() -> None:
	Log("DropdownManipulation()")
	def Add(filename=None) -> None:
		Log("Add()")
		filepath = Filepath(filename)
		if filepath in scripts.values():
			messagebox.showinfo("Add To Dropdown Value Error", f"Filepath '{filepath}' is already in dropdown. Cover name is '{scripts.keys()[scripts.values().index(filepath)]}'.", parent=root)
			return
		confirmed_name = False
		while not confirmed_name:
			name = simpledialog.askstring("Dropdown Name Input", "What would you like to call it? (Char Limit: 25)", parent=root)
			name_len = len(name)
			if name_len > 20:
				messagebox.showerror("Name Length Error", f"Name length was {name_len}, must be 25 or below.", parent=root)
				continue
			confirmed_name = messagebox.askyesno("Name Confirmation", f"Confirm name '{name}'?", parent=root)

		new_scripts = {}

		new_scripts[name] = filepath
		selected_script.set(name)
		for name, path in scripts.items():
			new_scripts[name] = path

		WriteTo(f"{self_name}Scripts.txt", f"scripts = {new_scripts}")
		UpdateScripts()
		ReloadDropdown()

	def Remove():
		Log("Remove()")
		global scripts, inv_scripts
		selected = selected_script.get()
		if selected != "Select a script":
			scripts.pop(selected)
			inv_scripts = {v: k for k, v in scripts.items()}
			WriteTo(f"{self_name}Scripts.txt", f"scripts = {scripts}")
			UpdateScripts()
			ReloadDropdown()

	selected = selected_script.get()
	exists_in = selected in scripts.keys()

	if exists_in:
		confirmation = messagebox.askyesno("Dropdown Removal Confirmation", f"Remove {selected} from dropdown?", parent=root)
	else:
		confirmation = messagebox.askyesno("Dropdown Addition Confirmation", f"Add {selected} to dropdown?", parent=root)

	if confirmation:
		if exists_in:
			Remove()
		else:
			Add()
	else:
		return

def ModuleManipulation() -> None:
	Log("ModuleManipulation()")
	manip = simpledialog.askstring("Manipulation Input", "Would you like to install or delete a module? (Options: 'install' or 'delete')", parent=root).lower().strip()
	module = simpledialog.askstring("Module Name Input", "What is the name of the module?", parent=root)
	if manip == "install":
		confirmation = messagebox.askokcancel("Module Installing", f"Installing module '{module}'...", parent=root)
	elif manip == "delete":
		confirmation = messagebox.askokcancel("Module Deleting", f"Deleting module '{module}'...", parent=root)
	else:
		messagebox.showerror("Invalid Manip", f"Manipulation '{manip}' is invalid, must be 'install' or 'delete'", parent=root)
		return

	if not confirmation:
		return

	search_state = importlib.util.find_spec(module)
	if search_state != None:
		if manip == "delete":
			subprocess.run(["pip", "uninstall", module])
			messagebox.showinfo("Module Deleted", f"The module '{module}' has been deleted.", parent=root)
			return
		messagebox.showinfo("Module Already Installed", f"The module '{module}' is already installed.", parent=root)
		return
	installation = subprocess.run(["pip", "install", module], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	result, error = installation.communicate()
	if result != 0:
		messagbox.showerror("Module Installation Error", error, parent=root)
		return
	messagbox.showinfo("Module Installation Success", f"Successfully installed module '{module}'!", parent=root)

def Backup() -> None:
	Log("Backup()", type="SYSTEM", time_log=True)
	default = f"{self_name}_Backup.py"
	confirmation = messagebox.askyesno("Backup Confirmation", "Backup the program?", parent=root)
	if not confirmation:
		return
	confirmation = messagebox.askyesno("Backup Destination Prompt", f"Choose destination? (If No, default is {default})", parent=root)
	destination = default if not confirmation else simpledialog.askstring("Backup Filename Prompt", "What would you like to name the file?", parent=root)
	destination = destination if destination.endswith(".py") else destination + ".py"
	function_setting = bool(setting_variables[2].get())
	confirmation = True
	if os.path.exists(destination):
		confirmation = function_setting if function_setting == True else messagebox.askyesno("Backup Confirmation", "Backup Hub? This will overwrite the previous backup.", parent=root)
	if confirmation:
		WriteTo(destination, ContentOfFile(__file__))
		messagebox.showinfo("Backup Complete", "Successfully backed up Hub to Hub_Backup.py.", parent=root)
	TopWindow(root, hold=True)

def ListModules() -> None:
	Log("ListModules()")
	string = ""
	installed = []
	installed_packages = pkg_resources.working_set
	for package in sorted(["%s==%s" % (i.key, i.version) for i in installed_packages]):
	    installed.append(package[:-len(package) + package.find("=")])

	i = 0
	while True:
		if installed == []:
			break
		if i % 3 == 0:
			string += Centered(installed[0], cuts=3, end=True, newline=2)
		else:
			string += Centered(installed[0], cuts=3, end=True)
		installed.pop(0)
		i += 1
	Input(string)

def ApplySettings() -> None:
	Log("ApplySettings()")
	global setting_variables
	setting_variables = [tk.BooleanVar() for i in range(25)]
	setting_file_content = ContentOfFile(f"{self_name}Settings.txt").strip()
	disregard = setting_file_content.endswith("File")
	if disregard:
		settings_string = "0" * 25
	else:
		settings_string = setting_file_content
	for index, value in enumerate(settings_string):
		setting_variables[index].set(value)

def BinaryIn(binary_string="") -> str:
	Log(f"BinaryIn(binary_string={binary_string})")
	num = 0
	for index, value in enumerate(binary_string):
		if index == 0 and int(value) == 0:
			continue
		num += (2 * int(value)) ** index
	return str(num)

def BinaryOut(number:str="0") -> str:
	Log(f"BinaryOut(number={number})")
	bin = ""
	number = int(number)
	processing = int(number)
	while True:
		if processing < 1:
			bin += str(processing)
			break
		if processing % 2 == 1:
			bin += "1"
		else:
			bin += "0"
		processing = int(processing / 2)


	return bin
		
def OpenSettings(page:int=0, update:bool=False, _from=root) -> None:
	Log(f"OpenSettings(page={page}, update={update}, _from={_from})")
	_from.iconify()
	settings_root = Toplevel(_from)
	settings_root.title("Hub Settings")
	settings_root.resizable(False, False)
	settings_root.focus()
	settings_root.iconbitmap("Hub_Settings_Icon.ico")

	def ChangePage(page:int=0) -> None:
		widgets = settings_root.winfo_children()
		for widget in widgets:
			widget.destroy()

		if page == 0:
			ReframeToCheckboxes()
		elif page == 1:
			ReframeToKeybinds()
	
	#PAGE 1
	def ReframeToKeybinds() -> None:
		#In Developement
		def Set() -> None:
			...

		def Exit() -> None:
			settings_root.destroy()
			_from.deiconify()

		settings_root.protocol("WM_DELETE_WINDOW", lambda: Exit())
		settings_root.bind("esc", lambda e: Exit())

		def SaveExit() -> None:
			Set()
			Exit()

		syntax_label = tk.Label(settings_root, text="EXAMPLE: 'Control-Shift-b' (In Developement)")
		syntax_label.grid(row=0, column=0,columnspan=6, padx=10, pady=5)

		list_module_label = tk.Label(settings_root, text="Keybind To List All Modules In The Textbox")
		list_module_label.grid(row=1, column=0,columnspan=6, padx=10, pady=5)

		list_modules_keybind = tk.Entry(settings_root)
		list_modules_keybind.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

		settings_id_button = tk.Button(settings_root, text="<- Checkboxes (Page 0)", command=lambda: ChangePage(0))
		settings_id_button.grid(row=4, column=2, padx=5, pady=5)
		
		save_exit_button = tk.Button(settings_root, text="Save and Exit", command=SaveExit)
		save_exit_button.grid(row=5, column=2, padx=5, pady=5)

		exit_button = tk.Button(settings_root, text="Exit", command=Exit)
		exit_button.grid(row=5, column=3, padx=5, pady=5)	

	#PAGE 0
	def ReframeToCheckboxes() -> None:
		def Set() -> None:
			log_string = "".join([str(int(val.get())) for val in setting_variables])
			WriteTo(f"{self_name}Settings.txt", log_string)
			ApplySettings()
	
		def Exit() -> None:
			global update_id
			update_id = False
			time.sleep(.25)
			settings_root.destroy()
			TopWindow(_from, hold=True)

		settings_root.protocol("WM_DELETE_WINDOW", lambda: Exit())
		settings_root.bind("esc", lambda e: Exit())

		def SaveExit() -> None:
			Set()
			Exit()

		def SignalUpdate() -> None:
			global update_needed
			update_needed = True

		def UpdateId() -> None:
			global update_id_status, update_needed
			update_id = True
			update_needed = False
			while update_id:
				if not update_needed:
					time.sleep(.125)
					continue	
				update_id_status = False
				settings_id_label.config(text=f"Settings ID: {BinaryIn("".join(str(int(val.get())) for val in setting_variables))}")
				update_id_status = True
				time.sleep(.125)

		def InputID() -> None:
			id = simpledialog.askinteger("Settings ID Input", "Input the desired ID.", parent=settings_root)
			binary_str = BinaryOut(id)
			for index, setting_object in enumerate(setting_variables):
				setting_object.set(binary_str[index])

		def Flip(page:int=0) -> None:
			Exit()
			ChangePage(page)

		auto_confirm_list_scripts_checkbox = tk.Checkbutton(settings_root, text="Auto confirm Python Exclusivity for 'List Files' keybind", variable=setting_variables[0], command=SignalUpdate)
		auto_confirm_list_scripts_checkbox.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

		auto_deny_see_code_checkbox = tk.Checkbutton(settings_root, text="Auto Deny Copy to Clipboard for 'See Code'", variable=setting_variables[1], command=SignalUpdate)
		auto_deny_see_code_checkbox.grid(row=1, column=0, columnspan=6, padx=10, pady=10)

		auto_confirm_backup_checkbox = tk.Checkbutton(settings_root, text="Auto Confirm Backup Saving", variable=setting_variables[2], command=SignalUpdate)
		auto_confirm_backup_checkbox.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

		auto_confirm_save_checkbox = tk.Checkbutton(settings_root, text="Auto Confirm Saving In Edit", variable=setting_variables[3], command=SignalUpdate)
		auto_confirm_save_checkbox.grid(row=3, column=0, columnspan=6, padx=10, pady=10)

		edit_iconify_checkbox = tk.Checkbutton(settings_root, text="Iconify Root When Editing Script", variable=setting_variables[4], command=SignalUpdate)
		edit_iconify_checkbox.grid(row=4, column=0, columnspan=6, padx=10, pady=10)

		log_checkbox = tk.Checkbutton(settings_root, text="Hub Logs", variable=setting_variables[5], command=SignalUpdate)
		log_checkbox.grid(row=5, column=0, columnspan=6, padx=10, pady=10)

		file_info_checkbox = tk.Checkbutton(settings_root, text="Show File Info On Select", variable=setting_variables[6], command=SignalUpdate)
		file_info_checkbox.grid(row=6, column=0, columnspan=6, padx=10, pady=10)

		edit_self_checkbox = tk.Checkbutton(settings_root, text="Refresh On Exit If Editing Self", variable=setting_variables[7], command=SignalUpdate)
		edit_self_checkbox.grid(row=7, column=0, columnspan=6, padx=10, pady=10)

		icon_run_checkbox = tk.Checkbutton(settings_root, text="Iconify Root When Running", variable=setting_variables[8], command=SignalUpdate)
		icon_run_checkbox.grid(row=8, column=0, columnspan=6, padx=10, pady=10)

		settings_id_label = tk.Label(settings_root, text=f"Settings ID: {BinaryIn("".join(str(int(val.get())) for val in setting_variables))}")
		settings_id_label.grid(row=9, column=0, columnspan=6, padx=5, pady=5)
	
		settings_id_button = tk.Button(settings_root, text="Input Settings ID", command=InputID)
		settings_id_button.grid(row=10, column=2, columnspan=2, padx=5, pady=5)

		keybinds_button = tk.Button(settings_root, text="-> Keybinds (Page 1)", command=lambda: ChangePage(1))
		keybinds_button.grid(row=11, column=2, columnspan=2, padx=5, pady=5)

		save_exit_button = tk.Button(settings_root, text="Save and Exit", command=SaveExit)
		save_exit_button.grid(row=12, column=2, padx=5, pady=5)

		exit_button = tk.Button(settings_root, text="Exit", command=Exit)
		exit_button.grid(row=12, column=3, padx=5, pady=5)

		update_thread = threading.Thread(target=UpdateId)
		update_thread.daemon = True
		update_thread.start()

	ChangePage(0)
	TopWindow(settings_root, hold=True)

def CreateScript() -> None:
	Log("CreateScript()")
	global absolute_filepath
	filename = simpledialog.askstring("Create Script Filename", "What would you like to name the script? (Extension chosen later)", parent=root)
	if filename == "" or filename == None:
		return

	extension = simpledialog.askstring("Create Script Filename", "Extension of the script? Ex: 'txt' (Default is 'py')", parent=root)
	if extension == None:
		return
	directory = filedialog.askdirectory(title=f"{filename} Directory Selection", parent=root, mustexist=True)
	if directory == None:
		return
	confirmation = messagebox.askyesno("Reference Confirmation", "Start file off with contents of another? (Copy)", parent=root)
	base_content = ""
	if confirmation:
		DriveSelect()
		base_content = ContentOfFile(absolute_filepath)

	filepath = f"{filename}.py" if extension == "" else f"{filename}.{extension}"
	abs_filepath = f"{directory}/{filepath}"

	if not os.path.exists(abs_filepath):
		WriteTo(abs_filepath, base_content)
	absolute_filepath = abs_filepath
	if abs_filepath in scripts.values():
		filepath = list(scripts.keys())[list(scripts.values()).index(abs_filepath)]
	SetSelected(filepath)
	EditScript(absolute_filepath)
	
def TopWindow(window=None, hold=False, cancel=True):
	Log(f"TopWindow(window={window}, hold={hold}, cancel={cancel})")
	window.deiconify()
	window.attributes('-topmost', True)
	window.update_idletasks()
	if hold:
		cancel = False
	if not hold or cancel:
		window.attributes('-topmost', False)
	window.focus()

def OnScriptSelection(event=None, file=None, *args) -> None:
	Log("OnScriptSelection()")
	function_setting = bool(setting_variables[6].get())
	if not function_setting:
		return
	Delete()
	file = selected_script.get() if file == None else file
	filepath = Filepath(file)
	if filepath == None:
		Input("Failed To Retrieve File Info (Control-I for Debug Info)")
		return
	if not os.path.exists(filepath):
		return
	ConfigWidget(["run_button", "edit_button", "see_code_button", "dropdown_button"], "state", "tk.NORMAL")
	Input(Centered(f"File Info", "=", end=True, end_line=2))
	mod_time_timestamp = os.path.getmtime(filepath) #Gemini Help (2 Lines) 
	mod_datetime = f"{datetime.fromtimestamp(mod_time_timestamp)}"
	mod_datetime = mod_datetime[:-len(mod_datetime) + mod_datetime.find('.')]
	Input(f"Path: {filepath}\n\nSize: {FormatSize(os.path.getsize(filepath))}\n\nLast Modified: {mod_datetime if mod_datetime.strip() != '' else 'Not Available'}\n\n")

def ShowBinds() -> None:
	Delete()
	Input("ShowBinds in developement.")

def FilteredFiles(directory=self_directory, filter:str="", _return:str="string", list_by:str="Size", order:str="Normal") -> str|list|None:
	Log("ShowFilteredFiles(directory={directory}, filter={filter}, _return={_return}, list_by={list_by}, order={order})")
	if not type(filter) == str:
		return None
	if directory == None:
		return None

	string = ""
	list = []
	end_string = ""
	r_var = _return.lower().strip()
	filter_is_ls = True if type(filter) == list else False
	for file in os.listdir(directory):
		if filter_is_ls:
			for f in filter:
				if filter in file:
					if "str" in r_var:
						end_string += f"{file}\n"
					else:
						list.append(file)
		else:
			if filter in file:
				if "str" in r_var:
					end_string += f"{file}\n"
				else:
					list.append(file)
	
	if r_var == "list":
		return list
	elif "str" in r_var:
		return end_string
	return None

def ListDropdown() -> None:
	Log("DropdownInfo()")
	Delete()
	UpdateScripts()
	string = ""
	for script_name in scripts.keys():
		string += Centered(script_name, end=True, newline=2)
	Input(string)

#In Developement
def ReorderScripts() -> None:
	...

def Info() -> None:
	Log("Info()")
	Delete()
	if_selected_in_scripts = False
	try:
		if_selected_in_scripts = selected_script.get() in scripts.values()
	except Exception:
		pass
	Input(f"Selected: {selected_script.get()}\nAbsolute Path: {absolute_filepath}\nSelected In Scripts: {if_selected_in_scripts}\nSettings: {[bool(setting.get()) for setting in setting_variables]}\nSelf Dir: {self_directory}\nSelf file: {self_file}")

	GLOBALS = globals()
	for g in GLOBALS.keys():
		if isinstance(GLOBALS[g], (int, float, str, list, dict, tuple)):
			Input(f"\n{g}: {GLOBALS[g]}")

def CloseHub():
	WriteTo(f"{self_name}Condition.txt", f"")
	Log("HUB CLOSE", type="SYSTEM", time_log=True)
	root.destroy()

def ReloadDropdown() -> None:
	global script_dropdown, selected_scripts
	try:
		old_selected = selected_script.get()
		menu = script_dropdown["menu"] # Gemini help (4 Lines)
		menu.delete(0, "end")
		for name, path in scripts.items():
			menu.add_command(label=name, command=lambda *args, v=name: (selected_script.set(v), OnScriptSelection(None, file=scripts[v])))
		if old_selected in scripts.keys():
			selected_script.set(old_selected)
		else:
			selected_script.set("Select a script")
			ConfigWidget(["run_button", "edit_button", "see_code_button", "dropdown_button"], "state", "tk.DISABLED")

		Log("ReloadDropdown()")
		
	except Exception:
		return

def UpdateScripts() -> None:
	Log("UpdateScripts()")
	global script_dropdown
	content = ContentOfFile(f"{self_name}Scripts.txt")

	content_invalid = False
	if content == "Non-existant File" or content == "Empty File":
		content_invalid = True

	command = f"scripts = {{'Self': '{__file__.replace('\\', '/')}'}}" if content_invalid else content
	exec(f"global scripts\n{command}")

def LaunchCommandWindow() -> None:
	Log("LaunchCommandWindow()")
	command_root = Toplevel(root)
	command_root.title(f"{self_name} Command Window")
	command_root.resizable(False, False)
	command_root.iconbitmap("Hub_Command_Icon.ico")
	#command_root.config(bg="gray")
	command_root.focus()

	root.iconify()

	#info_label = tk.Label(command_root, text="Control-Left -> prev/Control-Right -> next in history (In Developement)")
	#info_label.grid(row=0, column=3, padx=10, pady=10)

	text_widget = scrolledtext.ScrolledText(command_root, wrap="none", height=10, width=45)
	text_widget.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

	def Run() -> None:
		global command_history
		command = text_widget.get("1.0", tk.END)[:-1]
		listed_globals = []

		GLOBALS = globals()

		for g in GLOBALS.keys():
			if isinstance(GLOBALS[g], (int, float, str, list, dict, tuple)):
				if g in command:
					listed_globals.append(g)
		
		confirmation = True
		if listed_globals != []:
			confirmation = messagebox.askyesno("Global Interference Confirmation", f"Global variables '{listed_globals}' may be affected by this command, proceed?", parent=command_root)
		
		if confirmation:
			Log("COMMAND BEGINNING", type="SYSTEM")
			try:
				exec(command)
				command_history.append(command)
				Log("COMMAND END", type="SYSTEM")
			except Exception as e:
				Exit()
				Log(f"{command}\n{e}", type="INFO")
				messagebox.showerror("Command Error", str(e), parent=root)
				Log("COMMAND ERROR", type="SYSTEM")
	
	def Exit() -> None:
		command_root.destroy()
		TopWindow(root, hold=True)

	def RunExit() -> None:
		Run()
		Exit()

	#In Developement
	def NextHistory() -> None:
		...

	def PrevHistory() -> None:
		...

	run_button = tk.Button(command_root, text="Run Command", command=Run)
	run_button.grid(row=2, column=0, padx=10, pady=10)

	run_exit_button = tk.Button(command_root, text="Run & Exit", command=RunExit)
	run_exit_button.grid(row=2, column=1, padx=10, pady=10)

	exit_button = tk.Button(command_root, text="Exit Window", command=Exit)
	exit_button.grid(row=2, column=2, padx=10, pady=10)

	command_root.protocol("WM_DELETE_WINDOW", lambda: Exit())

	TopWindow(command_root, hold=True)

def WebSearch() -> None:
	query = simpledialog.askstring("Web Query Prompt", "What would you like to search?", parent=root).strip()
	site_endings = [".com", ".org", ".gov", ".to"]
	end_in = 0
	for end in site_endings:
		if end in query:
			end_in += 1

	if end_in == 0:
		query = f"www.google.com/search?q={query.replace(' ', '+')}&oq={query.replace(' ', '+')}&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOTIHCAEQ6wcYQNIBBzE2M2owajGoAgCwAgE&sourceid=chrome&ie=UTF-8&sei=g_G9abexMabJkPIP-si6oAc"

	webbrowser.open(f"https://{query}")

def SystemRun() -> None:
	Log("SystemRun()", type="SYSTEM")
	command = simpledialog.askstring("System Command Prompt", f"What command would you like to execute?\n(This will take over thread)", parent=root)
	if command != None:
		Log(f"Command: {command}", type="INFO")

		def Execute(command="") -> list[str]:
			root.iconify()
			try:
				process = subprocess.run(command, shell=True, capture_output=True, text=True)

				output = process.stdout
				error = process.stderr
				TopWindow(root, hold=True)
				return [output, error]
			except Exception as e:
				TopWindow(root, hold=True)
				return ["Failed At Execute", str(e)]
		
		output = Execute(command)

		Log(f"Output: {output[0]}", type="INFO")
		Log(f"Error(s): {output[1]}", type="INFO")
		Log("SystemRun() Completed", type="SYSTEM")
		if output[1] != "":
			messagebox.showerror("SystemRun Error Output", str(e), parent=root)
		else:
			if output[0] == "":
				messagebox.showinfo("SystemRun Completion", "Command Successfully executed.", parent=root)
			else:
				messagebox.showinfo("SystemRun Completion", f"Output of execute: {output[0]}", parent=root)
		return

	Log("SystemRun() Cancelled", type="SYSTEM")

Log(f"HUB STARTUP", type="SYSTEM", time_log=True)
ApplySettings()
UpdateScripts()

if open_file != None:
	opened_filename = Filename(open_file) if not open_file in list(scripts.values()) else list(scripts.keys())[list(scripts.values()).index(open_file)]

selected_script = tk.StringVar()
selected_script.set("Select a script" if open_file == None else opened_filename)

script_dropdown = tk.OptionMenu(root, selected_script, *scripts.keys(), command=OnScriptSelection)
script_dropdown.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

script_precise_button = tk.Button(root, text="Select From Drive", command=DriveSelect, width=20)
script_precise_button.grid(row=0, column=0, padx=10, pady=10)

settings_button = tk.Button(root, text="Settings", command=OpenSettings, width=20)
settings_button.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=Length, height=Height)
textbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

create_button = tk.Button(root, text="Create File", command=CreateScript, width=20)
create_button.grid(row=3, column=0, columnspan=2, padx=5)

see_code_button = tk.Button(root, text="See Contents", command=SeeCode, width=20, state=tk.DISABLED)
see_code_button.grid(row=3, column=0, padx=5)

run_button = tk.Button(root, text="Open Selected File", command=RunScript, width=20, state=tk.DISABLED)
run_button.grid(row=3, column=1, padx=5)

command_window_button = tk.Button(root, text="Command Window", command=LaunchCommandWindow, width=20)
command_window_button.grid(row=4, column=0, columnspan=2, padx=5)

dropdown_button = tk.Button(root, text="Manipulate Dropdown", command=DropdownManipulation, width=20, state=tk.DISABLED)
dropdown_button.grid(row=5, column=0, columnspan=2, padx=5)

edit_button = tk.Button(root, text="Edit File", command=EditScript, width=20, state=tk.DISABLED)
edit_button.grid(row=5, column=1, padx=5)

close_button = tk.Button(root, text="Close Running", command=CloseScript, width=20, state=tk.DISABLED)
close_button.grid(row=4, column=1, padx=5)

install_button = tk.Button(root, text="Install Module", command=ModuleManipulation, width=20)
install_button.grid(row=4, column=0, padx=5)

backup_button = tk.Button(root, text="Backup Hub", command=Backup, width=20)
backup_button.grid(row=5, column=0, padx=5)

refresh_button = tk.Button(root, text="Refresh", command=Refresh, width=20)
refresh_button.grid(row=6, column=0, columnspan=2, padx=5)

root.bind("<Control-m>", lambda event: ListModules())
root.bind("<Control-i>", lambda event: Info())
root.bind("<Control-b>", lambda event: ShowBinds())
root.bind("<Control-f>", lambda event: Show(FilteredFiles()))
root.bind("<Control-l>", lambda event: ListScripts())
root.bind("<Control-d>", lambda event: ListDropdown())
root.bind("<Control-w>", lambda event: WebSearch())
root.bind("<Control-e>", lambda event: SystemRun())

root.protocol("WM_DELETE_WINDOW", lambda: CloseHub())

keyboard.add_hotkey("ctrl+shift+h", lambda: TopWindow(root))

if open_file != None:
	OnScriptSelection(opened_filename)

TopWindow(root, hold=True)
root.focus()

root.mainloop()

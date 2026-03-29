# Hub-Program

!!! WARNING !!! Program is operating at the system level on some functions, I added confirmation boxes but still be careful on what you run especially on the "Command Window", it has a very thin layer of precaution. Also, just downloading Hub-Program.py will not work (Look at bottom entry for fix/explanation)

The main dish is a python file with file editing along with some system-based and other miscellaneous functions, I use it personally for coding as the functions are great against inconvenieces (Atleast the ones I face with other file editors like VSCode, though I don't think my program can really compare to theirs in terms of quality).

Made on windows 10, I tried making it ready for multiple systems but probably missed some edge cases. This project was based on one of the first scripts I made so it might have some artifacts of unoptimization but runs alright.

When downloading zip, make sure to unzip it by right-clicking the file then selecting "extract" and save it to a file folder, doesn't run without it. You also need python installed to run it.

There are a decent amount of hidden binds in the program that have many useful functions like recovering files (If EditScript is not closed), to look for these just open EditScript with Self selected and press Control-f and look for "root.bind" (This includes binds in other windows as all program roots end with "root" so don't worry about specifics)

Icons currently have the capability to crash it if not found so just use a text editor and search for 'root.iconbitmap' and delete the line if it causes trouble. You shouldn't run into this problem though if you don't mess with the folder.

Running the Hub-Program on another similar file is not fully compatable, it will run but without proper self initialization and will write to the current directory.

# PythonCompilerC
Compile an entire python project into .so files to protect your code

To launch the compiler, put it into your project's root directory and execute:
  - python3 compile.py --project-dir {your prject directory, Eg: .} --build-lib {compiled project destination}

The result will be a new project containing only .so files with the exception of your entry point file to launch the projcet, which is 'main.py' by default but you can change it.

PS: make sure you rename your entry point to main.py so that it doesn't get converted to .so.
PS: Make sure you have another copy of your project because after the compiler finishes it will delete all .py files from the directory if you choose the same directory for compiling.

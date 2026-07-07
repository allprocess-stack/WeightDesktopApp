import sys
from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": [
        "config",
        "core",
        "ui",
        "utils",
        "data",
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
        "win32api",
        "PyQt6",
    ],
    "excludes": [
        "tkinter",
        "test",
        "unittest",
        "distutils",
        "setuptools",
        "pydoc",
    ],
    "include_files": ["requeriments.txt"],
    "optimize": 2,
}

bdist_msi_options = {
    "upgrade_code": "{B8F4A2D1-3E5C-4A7B-9F0D-1C2E3D4F5A6B}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFiles64Folder]\All Process\DesktopViewWeight",
}

executable = Executable(
    script="main.py",
    target_name="DesktopViewWeight",
    base="gui",
    icon=None,
)

setup(
    name="DesktopViewWeight",
    version="1.0.0",
    description="Visor de peso de báscula por puerto serie",
    author="Anthony Josue Laura Perez",
    author_email="",
    url="https://github.com/anthony2004lp",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[executable],
)

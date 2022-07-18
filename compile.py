# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
@File    :   compile.py
@Time    :   2022/07/17 18:10:38
@Author  :   Dison
@Version :   1.0
@Contact :   coldison@foxmail.com
@License :   (C)Copyright 2019-2022
@Desc    :   None
"""

from distutils.core import setup
import shutil
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import glob
import os
import platform
import argparse

parser = argparse.ArgumentParser(description='Compile project using Cython')
parser.add_argument('--project-dir', default=None, help='input folder path', type=str)
parser.add_argument('--build-lib', default=None, help='output folder path', type=str)
args, unknown = parser.parse_known_args()

CLEAN_FOLDERS = ['__pycache__', '.git', '.pytest_cache', 'plots', 'scripts', ".history"]


def fast_scandir(dirname, clean=False):
    """
    Returns all the folders and subfolders inside a directory
    """

    folders_to_clean = CLEAN_FOLDERS if clean is False else [".git"]
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir() and f.name not in folders_to_clean]

    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname, clean=clean))
    return subfolders


def clean_project(dirname=None):
    """
    After the compile is finished,
    We delete all the .c .py and .o files to only keep .so files,
    which are the compiled code
    """
    subfolders = fast_scandir(dirname, clean=True)
    subfolders.append(dirname)
    py_paths = []
    c_paths = []
    o_paths = []
    so_paths = []
    pyd_paths = []
    ipynb_paths = []
    pyc_paths = []
    for element in subfolders:
        py_paths.extend(glob.glob(os.path.join(element, "*.py")))
        c_paths.extend(glob.glob(os.path.join(element, "*.c")))
        o_paths.extend(glob.glob(os.path.join(element, "*.o")))
        so_paths.extend(glob.glob(os.path.join(element, "*.so")))
        pyd_paths.extend(glob.glob(os.path.join(element, "*.pyd")))
        ipynb_paths.extend(glob.glob(os.path.join(element, "*.ipynb")))
        pyc_paths.extend(glob.glob(os.path.join(element, "*.pyc")))
        

    for element in c_paths:
        os.remove(element)
    for element in o_paths:
        os.remove(element)
    for element in ipynb_paths:
        os.remove(element)
    for element in pyc_paths:
        os.remove(element)

    for rm_folder in CLEAN_FOLDERS:
        subfolders = fast_scandir(dirname, clean=True)
        subfolders.append(dirname)
        for element in subfolders:
            if rm_folder in element:
                shutil.rmtree(element)

    if platform.system() in ['Linux', 'Darwin']:
        for so_path in so_paths:
            so_file = so_path.split('/')[-1]
            directory = '/'.join(so_path.split('/')[:-1])

            py_file = so_file.split('.')[0] + '.py'
            py_directory = os.path.join(directory, py_file)
            if py_directory in py_paths:
                os.remove(py_directory)

    elif platform.system() == 'Windows':
        for pyd_path in pyd_paths:
            pyd_file = pyd_path.split('\\')[-1]
            directory = '\\'.join(pyd_path.split('\\')[:-1])

            py_file = pyd_file.split('.')[0] + '.py'
            py_directory = os.path.join(directory, py_file)
            if py_directory in py_paths:
                os.remove(py_directory)


def main(root_path=None, build_path=None):
    if 'build_ext' in unknown and '--inplace' in unknown:
        build_path = '.'

    elif 'build_ext' in unknown:
        if root_path is not None:
            print(
                'Error! If you used "build_ext" please remove it. Only "--project-dir" and "--build-lib" are allowed!')
            exit(1)

    else:
        if root_path is None:
            print('Error! --project-dir is missing.')
            exit(1)
        if build_path is None:
            print('Error! --build-lib is missing.')
            exit(1)
        if build_path == root_path:
            print('Error! --build-lib cannot be the same as --project-dir')
            exit(1)

        #build_path = os.path.abspath(build_path)
        if platform.system() in ['Linux', 'Darwin']:
            os.makedirs(build_path, exist_ok=True)
            os.system('cp -R %s %s' % (root_path, build_path))
        elif platform.system() == 'Windows':
            os.system('xcopy /E /Y /I %s %s' % (root_path, build_path))

        os.system('cd %s' % build_path)

        compile_py_path = os.path.join(root_path, 'scripts', 'compile.py')
        os.system(f'python {compile_py_path} build_ext --build-lib {build_path}')
        if os.path.exists(os.path.join(build_path, 'build')):
            shutil.rmtree(os.path.join(build_path, 'build'))

        if os.path.exists(os.path.join(build_path, 'scripts', 'build')):
            shutil.rmtree(os.path.join(build_path, 'scripts', 'build'))

        if os.path.exists(os.path.join(root_path, 'build')):
            shutil.rmtree(os.path.join(root_path, 'build'))

        if os.path.exists(os.path.join(root_path, 'scripts', 'build')):
            shutil.rmtree(os.path.join(root_path, 'scripts', 'build'))
        exit(0)

    subfolders = fast_scandir(build_path)
    subfolders.append(build_path)

    final = []

    # 映射.py文件到.so文件
    path_dict = dict()

    for element in subfolders:
        file_elements = glob.glob(os.path.join(element, "*.py"))
        final.extend(file_elements)
        for file in file_elements:
            print("file:",file)
            if platform.system() in ['Linux', 'Darwin']:
                path_dict[file.split('/')[-1].split('.')[0]] = element
            elif platform.system() == 'Windows':
                path_dict[file.split('\\')[-1].split('.')[0]] = element

    # final.remove(os.path.join(build_path, "main.py"))

    setup(
        name='Well Integrity',
        cmdclass={'build_ext': build_ext},
        ext_modules=cythonize(final, compiler_directives={'always_allow_keywords': True})
    )

    if platform.system() in ['Linux', 'Darwin']:
        so_file_list = glob.glob(os.path.join(build_path, "*.so"))

        for so in so_file_list:
            file = so.split('/')[-1].split('.')[0]
            if file in path_dict:
                os.system('mv %s %s' % (so, path_dict[file]))
                print(f" move {so} to {path_dict[file]}")

    elif platform.system() == 'Windows':
        pyd_file_list = glob.glob(os.path.join(build_path, "*.pyd"))
        print(f"path_dict: {path_dict} pyd_file_list: {pyd_file_list}")

        for pyd in pyd_file_list:
            file = pyd.split('\\')[-1].split('.')[0]
            print("file:",file)
            if file in path_dict:
                os.system('move %s %s' % (pyd, path_dict[file]))
                print(f" move {pyd} to {path_dict[file]}")

        

    clean_project(build_path)
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # shutil.rmtree(os.path.join(build_path, 'scripts'))

if __name__ == '__main__':
    project_dir_ = args.project_dir
    build_path_ = args.build_lib
    # clean_project(build_path_)
    main(root_path=project_dir_, build_path=build_path_)


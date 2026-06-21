from setuptools import setup, find_packages

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

version = None
with open('./src/jmcomic_shelf/__init__.py', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('__version__'):
            version = line[line.index("'") + 1: line.rindex("'")]
            break

if version is None:
    print('Set version first!')
    exit(1)

setup(
    name='JMComic-Shelf',
    version=version,
    description='Windows desktop shelf for JMComic downloads',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/Dylanliiiii/JMComic-Shelf',
    author='Dylanliiiii',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        'jmcomic_shelf': ['assets/icon.png'],
    },
    python_requires=">=3.9",
    install_requires=[
        'curl_cffi',
        'commonX',
        'img2pdf',
        'PyYAML',
        'Pillow',
        'PySide6',
        'PySide6-Fluent-Widgets',
        'pycryptodome',
        'zhconv',
    ],
    keywords=['python', 'jmcomic', '18comic', '禁漫天堂', 'NSFW'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [
            'jmcomic = jmcomic.cli:main',
            'jmv = jmcomic.cli:view_main',
            'jmcomic-shelf = jmcomic_shelf.app:main',
        ]
    }
)

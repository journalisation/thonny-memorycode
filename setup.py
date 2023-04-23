from setuptools import find_packages, setup

#with open("doc/help.md", "r") as f:
#    long_description = f.read()

setup(
    name="memorycode",
    version="0.0.3",
    author="Jerome Amiguet",
    packages=["thonnycontrib.memorycode"],
    description="Memorycode",
    long_description="Memorycode",
    long_description_content_type="text/markdown",
    url="https://github.com/journalisation/thonny-memorycode",
    install_requires=[
        "GitPython",
    ],
    package_data={
        "thonnycontrib.memorycode": [
            "res/*",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Education",
    ],
    python_requires=">=3.6",
)
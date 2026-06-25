from setuptools import setup, find_packages

setup(
    name="zerodimension",
    version="3.0.0",
    description=(
        "ZeroDimension Framework V3 — a symbolic mathematical framework "
        "for division by zero using layered Theta-space rules."
    ),
    long_description=open("README.md", encoding="utf-8").read() if __name__ == "__main__" else "",
    long_description_content_type="text/markdown",
    author="ZeroDimension Framework",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "sympy>=1.10",
    ],
    extras_require={
        "test": ["pytest>=7.0", "hypothesis>=6.0"],
    },
    entry_points={
        "console_scripts": [
            "zerodimension=zerodimension.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
)

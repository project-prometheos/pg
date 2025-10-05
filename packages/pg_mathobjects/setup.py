"""
Setup configuration for pg_mathobjects package.
"""

from setuptools import setup, find_packages

setup(
    name="pg_mathobjects",
    version="0.1.0",
    description="MathObjects implementation for PG problems",
    author="WeBWorK Project",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "sympy>=1.12",  # For symbolic math
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)

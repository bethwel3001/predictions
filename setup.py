"""
NASA TEMPO Air Quality Forecasting Platform
Setup configuration for Python package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tempo-air-quality",
    version="0.1.0",
    author="NASA Space Apps Team",
    description="Air quality forecasting platform using TEMPO satellite data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bethwel3001/predictions",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "geoalchemy2>=0.14.0",
        "redis>=5.0.0",
        "celery>=5.3.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "xarray>=2023.10.0",
        "netCDF4>=1.6.0",
        "scikit-learn>=1.3.0",
        "tensorflow>=2.14.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.4.0",
        "alembic>=1.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
            "ipython>=8.16.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tempo-api=src.api.main:main",
            "tempo-worker=src.pipeline.worker:main",
        ],
    },
)

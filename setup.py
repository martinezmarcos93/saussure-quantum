"""
Setup configuration for Saussure-Quantum Fusion package
"""

from setuptools import setup, find_packages

# El archivo se llama "Readme.md": en Linux los nombres distinguen mayúsculas
# y abrir "README.md" hacía fallar `pip install -e .`.
with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dependencias runtime: solo lo que el paquete necesita para funcionar.
# Las herramientas de desarrollo (pytest, black, mypy) van en extras_require["dev"],
# no aquí — de lo contrario se instalan en producción con cada `pip install`.
INSTALL_REQUIRES = [
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "matplotlib>=3.4.0",
    "jupyter>=1.0.0",
    "ipywidgets>=7.6.0",
]

setup(
    name="saussure-quantum-fusion",
    version="0.1.0",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Fusión computacional entre semiótica saussureana y mecánica cuántica",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/saussure-quantum-fusion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require={
        # Instalar con: pip install -e ".[dev]"
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "mypy>=0.910",
        ],
        # Instalar con: pip install -e ".[quantum]"
        "quantum": ["qiskit>=0.39.0"],
    },
    include_package_data=True,
    zip_safe=False,
)
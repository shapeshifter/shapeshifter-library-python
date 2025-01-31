from setuptools import setup

setup(
    name="shapeshifter-uftp",
    version="1.3.0",
    python_requires=">=3.10",
    description="Allows connections between DSO, AGR and CRO using the Shapeshifter (UFTP) protocol.",
    packages=[
        "shapeshifter_uftp",
        "shapeshifter_uftp.uftp",
        "shapeshifter_uftp.client",
        "shapeshifter_uftp.service",
    ],
    install_requires=[
        "xsdata[lxml]>=24.4,<=24.7",
        "pynacl==1.5.0",
        "dnspython==2.6.1",
        "fastapi>=0.110,<=0.113",
        "fastapi-xml>=1.1.1,<2.0.0",
        "requests",
        "uvicorn",
        "termcolor",
    ],
    extras_require={
        "dev": [
            "xmlschema",
            "pytest",
            "pytest-cov",
            "pylint",
            "sphinx",
            "sphinx-rtd-theme",
        ]
    },
    entry_points={
        "console_scripts": [
            "shapeshifter-keypair = shapeshifter_uftp.cli:generate_signing_keypair",
            "shapeshifter-lookup = shapeshifter_uftp.cli:perform_lookup",
        ]
    },
)

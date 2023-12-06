# Building-Energy-Modeling-Configurator
This repository contains the scripts and distribution files of an easy-to-use interface for performing multi-objective optimization on a simplified shoebox-shaped building. The configurator consists of an intuitive interface that allows the user to define geometry, envelope, controls, and operational characteristics of the building to create customized models. The user can decide whether or not to include variables in the optimization process to optimize heating and cooling demand, thermal comfort, and costs, and, once the analysis is complete, the configurator automatically presents the results with the optimal design solutions:
![Configurator-GIF](https://github.com/fbattini/Building-Energy-Modeling-Configurator/assets/71373172/764c4435-da1a-4f52-ba9e-3052162a8fe7)
The distribution file are in the folder named Configurator, which can be downloaded to directly use the tool. All the other files present in the repository are the Python files used to develop the configurator.

To use the configurator it is necessary to:
- Download the Configurator folder present in this repository
- Download the 9.4.0 version of EnergyPlus compatible with the operating system from the [program website](https://github.com/NREL/EnergyPlus/releases/tag/v9.4.0), or directly download the installer for the [32-bit](https://github.com/NREL/EnergyPlus/releases/download/v9.4.0/EnergyPlus-9.4.0-998c4b761e-Windows-i386.exe) or [64-bit](https://github.com/NREL/EnergyPlus/releases/download/v9.4.0/EnergyPlus-9.4.0-998c4b761e-Windows-x86_64.exe) version
- Install EnergyPlus in the folder suggested during the installation process (C:\EnergyPlusV9-4-0)
- Open the executable file named Configurator.exe in the Configurator folder

The configurator was developed in Python programming language and is based on numpy, pandas, eppy, and customtkinter.
[Federico Battini](https://www.linkedin.com/in/federico-battini/)

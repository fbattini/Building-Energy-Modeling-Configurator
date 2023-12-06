# Building-Energy-Modeling-Configurator
This repository contains the scripts and distribution files of an easy-to-use interface for performing multi-objective optimization on a simplified shoebox-shaped building. The configurator consists of an intuitive interface that allows the user to define geometry, envelope, controls, and operational characteristics of the building to create customized models. The user can decide whether or not to include variables in the optimization process to optimize heating and cooling demand, thermal comfort, and costs, and, once the analysis is complete, the configurator automatically presents the results with the optimal design solutions:

![Configurator-GIF](https://github.com/fbattini/Building-Energy-Modeling-Configurator/assets/71373172/764c4435-da1a-4f52-ba9e-3052162a8fe7)

The distribution files are located in the Configurator folder, which can be downloaded to use the tool directly. All other files in the repository are the Python files used to develop the configurator.

To use the configurator it is necessary to:
- Download the Configurator folder from this repository
- Download the operating system-compatible version 9.4.0 of EnergyPlus from the [program's website](https://github.com/NREL/EnergyPlus/releases/tag/v9.4.0), or download the installer for the [32-bit](https://github.com/NREL/EnergyPlus/releases/download/v9.4.0/EnergyPlus-9.4.0-998c4b761e-Windows-i386.exe) or [64-bit](https://github.com/NREL/EnergyPlus/releases/download/v9.4.0/EnergyPlus-9.4.0-998c4b761e-Windows-x86_64.exe) version directly
- Install EnergyPlus to the folder suggested during the installation process (C:\EnergyPlusV9-4-0)
- Open the executable file named Configurator.exe in the Configurator folder

The configurator is written in the Python programming language and is based on numpy, pandas, eppy and customtkinter.

## More details and references
To learn more about this work or to cite it, please see the following publication (conference proceeding in Italian):
- Federico Battini, Giovanni Pernigotto, Andrea Gasparella, "Development of a simplified configurator to promote the use of building performance simulation in the design and retrofit process of existing buildings", 39° Convegno Nazionale AiCARR, 8 September 2023, Napoli, Italy ([https://www.sciencedirect.com/science/article/pii/S2210670722006096](https://www.aicarr.org/Convegni/Convegni_Dettaglio.aspx))

## Current limitations
For now, this version of the configurator has the following limitations:
- There is a limited number of implemented energy efficiency measures and it is not yet possible to easily add new ones
- It is not possible to choose which objectives to include in the optimization process
- It is not possible to use optimization algorithms or run simulations in parallel

## Contact
[Federico Battini](https://www.linkedin.com/in/federico-battini/)

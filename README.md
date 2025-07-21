# ISYE6644  
Project for ISYE 6644: Simulation

## Overview

This project simulates a COVID-19 outbreak on a cruise ship environment using an agent-based SEIRS+ network model (https://github.com/ryansmcgee/seirsplus) by Ryan McGee et al. This project is inspired by the Diamond Princess cruise COVID-19 outbreak on 2020. The simulation incorporates realistic contact networks derived from cruise ship layouts, contact durations, and behavioral assumptions. The primary focus is on analyzing transmission dynamics, intervention scenarios, and the effect of vaccination.

## Key Features

- **Network Model (SEIRS+):**  
  Incorporates Susceptible, Exposed, Infected, Recovered, and Fatal states using individual-based dynamics and realistic contact graphs.

- **Dynamic Contact Graphs:**  
  - Base (G): Weighted based on the accumulation of daily contacts between the nodes. Cabinmates, shared facilities, deck level interactions incorporated.   
  - Quarantine (G_Q): Sparse graph reflecting limited cabinmates and crew-to-crew links after isolation protocol. 

- **Parameter Calibration:**  
  Based on real outbreak data such as the 2020 Diamond Princess case and academic literature. Refer to the parameters description:

  
    | Parameter   | Description                                       |
    |-------------|---------------------------------------------------|
    | `BETA`        | Rate of transmission                              |
    | `SIGMA`     | Rate of progression from exposed to infected      |
    | `GAMMA`     | Rate of recovery                                  |
    | `MU_I`      | Rate of infection-related mortality               |
    | `G_quarantine` | Contact graph used during quarantine           |
    | `BETA_Q`    | Transmission rate for detected (quarantined) cases|
    | `SIGMA_Q`   | Progression rate for detected (quarantined) cases |
    | `GAMMA_Q`   | Recovery rate for detected (quarantined) cases    |
    | `theta_E`   | Testing rate for exposed individuals              |
    | `theta_I`   | Testing rate for infected individuals             |
    | `initI`   | Initial number of infected individuals             |


## Simulation Scenarios

- Basic transmission dynamic with 100 initially infected groups onboard.
- Gradual enforcement of intervention. Mask mandates on day 5 quarantine protocols on day 10. 



## Requirements

- Python 3.8+
- `networkx` (version 2.8)
- `numpy`
- `matplotlib`
- `seirsplus` 
- `random`
- `itertools`
- `jupyterlab` (optional, can use other jupyter environment to run .ipynb file)

## Files

- `cruise_outbreak_simulation.ipynb`: Full model and analysis notebook.
- `SEIRS`: original SEIRS package directory.
- `README.md`: Project overview and usage instructions.

## How to Run

1. **Install Dependencies** 

In terminal, install required packages by running:
```bash
pip3 install seirsplus networkx==2.8 numpy matplotlib random itertools
```
Alternatively, you can install in jupyter notebook with command: `!pip3 install <packages>`

2. **Download or Clone repo**

In terminal navigate to desired location to clone gitHub into.
```bash 
git clone https://github.com/nashaibot/IYSE6644.git
```

3. **Run the Simulation**

Run the provided `cruise_outbreak_simulation.ipynb` to simulate. Use preferred jupyter environment to run the file. 

Optionally, if `jupyterlab` is installed, open the lab using `python3 -m jupyterlab` and run the file. 

Modify the parameters based on the scenarios of interest. Refer to the parameters table above or (https://github.com/ryansmcgee/seirsplus/wiki/SEIRSModel-Class) for more information. 



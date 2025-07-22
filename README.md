# ISYE6644  
Project for ISYE 6644: Simulation

## Overview

This project simulates a COVID-19 outbreak on a cruise ship environment using an agent-based SEIRS+ network model (https://github.com/ryansmcgee/seirsplus) by Ryan McGee et al. This project is inspired by the Diamond Princess cruise COVID-19 outbreak on 2020. The simulation incorporates realistic contact networks derived from cruise ship layouts, contact durations, and behavioral assumptions. The primary focus is on analyzing transmission dynamics, intervention scenarios, and the effect of vaccination.

## Key Features

- **Network Model (SEIRS+):**  
  Incorporates Susceptible, Exposed, Infected, Recovered, and Fatal states using individual-based dynamics and realistic contact graphs.

- **Dynamic Contact Graphs:**  
  - Base (G): Weighted based on the accumulation of daily contacts between the nodes. Cabin connections, social/dining connections, random encounter, service interactions incorporated.   
  - Quarantine (G_Q): Sparse graph reflecting limited cabinmates and crew-to-crew links after isolation protocol. 

- **Network Structure**:
  - 3,700 total individuals (2,590 passengers, 1,110 crew)
  - ~26,000 edges representing high-density contact patterns:
    - **Cabin mates**: 1.0 weight
    - **Dining groups / Work teams**: 0.5 (passengers) / 0.7 (crew)
    - **Service interactions**: 0.3
    - **Random encounters**: 0.1

- **Parameter Calibration:**  
  Based on real outbreak data such as the 2020 Diamond Princess case and academic literature. Refer to the parameters description:

  
    | Parameter   | Description                                       |
    |-------------|---------------------------------------------------|
    | `BETA`        | Rate of transmission                              |
    | `SIGMA`     | Rate of progression from exposed to infected      |
    | `GAMMA`     | Rate of recovery                                  |
    | `MU_I`      | Rate of infection-related mortality               |
    | `G_quarantine` | Contact graph used during quarantine           |
    | `theta_E`   | Testing rate for exposed individuals              |
    | `theta_I`   | Testing rate for infected individuals             |
    | `initI`   | Initial number of infected individuals             |


## Simulation Scenarios

The threee main scenarios to compare the effectiveness of intervention strategies:
1. **Baseline** - Full network with no mitigation. 
2. **Complete Quarantine** - Passengers are isolated in their cabins.
3. **Universal Single-Dose Vaccination** - All individuals receive a single-dose of vaccination. 70% effectiveness via 50% reduction in susceptibility and 40% reduction in transmission rate. 
4. **Two-Dose Vaccination for Half the Population** - 50% of population receives an additional dose of vacciantion. Higher individual protection, lower coverage


## Requirements

- Python 3.9+
- `networkx` (version 2.8)
- `numpy`
- `matplotlib`
- `seirsplus` 
- `scipy`


## Files

- `cruise_outbreak_simulation_simplified.py`: The main simulation script. Output is printed to the console and includes time-stepped simulation logs and summary results.
- `README.md`: Project overview and usage instructions.

## How to Run

1. **Install Dependencies** 

Ensure Python 3.9+ is installed. Then install required packages by running:
```bash
pip3 install seirsplus networkx==2.8 numpy matplotlib scipy
```

2. **Run the Simulation**

Once all the dependencies are downloaded, run the provided `cruise_outbreak_simulation_simplified.py` to simulate. 

```bash
python3 cruise_outbreak_simulation_simplifeid.py
```

Modify the parameters based on the scenarios of interest. Refer to the parameters table above or (https://github.com/ryansmcgee/seirsplus/wiki/SEIRSModel-Class) for more information. 

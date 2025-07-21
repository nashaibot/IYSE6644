
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import SEIRS+ with version compatibility
try:
    from seirsplus.models import SEIRSNetworkModel
    print("✅ SEIRS+ library loaded successfully")
except ImportError:
    print("❌ SEIRS+ library not found. Install with: pip install seirsplus networkx==2.8 numpy<2")
    exit(1)

class CruiseShipSimulation:

    
    def __init__(self, n_passengers: int = 2666, n_crew: int = 1045):
        """        
        Args:
        """
        self.n_passengers = n_passengers
        self.n_crew = n_crew
        self.n_total = n_passengers + n_crew
        
        # Configuration parameters
        self.config = self._setup_configuration()
        
        # Networks (will be built)
        self.G_normal = None
        self.G_quarantine = None
        
        # Simulation results storage
        self.results = {}
        
        print(f"🚢 Cruise Ship Simulation Initialized")
        print(f"   Population: {self.n_total:,} ({n_passengers:,} passengers + {n_crew:,} crew)")
        
    def _setup_configuration(self) -> Dict:
        """Setup comprehensive simulation parameters based on research literature."""
        
        config = {
            # Population Structure
            'passengers_per_cabin': 2,
            'decks': 17,
            'dining_cohorts': 9,
            'passenger_crew_ratio': self.n_passengers / self.n_crew,
            
            # Disease Parameters (based on Lauer et al. and Diamond Princess data)
            'incubation_mean': 1.63,  # log-normal mean
            'incubation_sigma': 0.5,  # log-normal std
            'infectious_period': 7,   # days
            'base_transmission_rate': 1.0,  # per contact per day (increased for cruise ship density)
            'mortality_rate': 0.013,  # 1.3% CFR (Diamond Princess: 9/712)
            'asymptomatic_fraction': 0.465,  # 46.5% asymptomatic on Diamond Princess
            
            # Intervention Parameters
            'mask_effectiveness': 0.65,  # 65% transmission reduction
            'social_distancing_factor': 0.4,  # 40% contact reduction
            'quarantine_compliance': 0.95,  # 95% compliance with cabin isolation
            
            # Vaccination Parameters
            'vaccine_efficacy_1dose': 0.70,  # 70% protection after 1 dose
            'vaccine_efficacy_2dose': 0.95,  # 95% protection after 2 doses
            'vaccine_delay_days': 14,  # Days for immunity to develop
            'daily_vaccine_capacity': 200,  # Doses per day
            
            # Testing Parameters
            'test_sensitivity': 0.85,  # 85% test sensitivity
            'daily_test_capacity': 150,  # Tests per day
            'test_delay': 1,  # Days for results
        }
        
        # Calculate derived parameters
        config['sigma'] = 1 / np.exp(config['incubation_mean'])  # Progression rate
        config['gamma'] = 1 / config['infectious_period']  # Recovery rate
        config['mu_I'] = config['mortality_rate'] * config['gamma']  # Death rate
        
        return config
    
    def build_cruise_network(self) -> nx.Graph:
        """
        Build realistic cruise ship contact network based on Diamond Princess structure.
        
        Returns:
            NetworkX graph representing cruise ship social structure
        """
        print("🔧 Building cruise ship contact network...")
        
        G = nx.Graph()
        
        # Add all individuals as nodes
        passengers = list(range(self.n_passengers))
        crew = list(range(self.n_passengers, self.n_total))
        
        # Add nodes with metadata
        for p in passengers:
            G.add_node(p, type='passenger', cabin=p//2, deck=random.randint(1, 17))
        
        for c in crew:
            G.add_node(c, type='crew', 
                      service_type=random.choice(['passenger_service', 'non_passenger_service']),
                      cabin=(c-self.n_passengers)//2)
        
        # 1. CABIN CONNECTIONS (Highest weight)
        self._add_cabin_connections(G)
        
        # 2. DINING COHORT CONNECTIONS
        self._add_dining_connections(G)
        
        # 3. DECK-LEVEL INTERACTIONS
        self._add_deck_connections(G)
        
        # 4. FACILITY SHARING (pools, lounges, etc.)
        self._add_facility_connections(G)
        
        # 5. CREW WORK INTERACTIONS
        self._add_crew_connections(G)
        
        # 6. PASSENGER-CREW SERVICE INTERACTIONS
        self._add_service_connections(G)
        
        # 7. TRANSIENT RANDOM ENCOUNTERS
        self._add_transient_connections(G)
        
        self.G_normal = G
        
        print(f"✅ Network built: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
        print(f"   Average degree: {2*G.number_of_edges()/G.number_of_nodes():.1f}")
        
        return G
    
    def _add_cabin_connections(self, G: nx.Graph):
        """Add cabin mate connections (highest transmission risk)."""
        # Passengers share cabins (2 per cabin)
        for i in range(0, self.n_passengers, 2):
            if i+1 < self.n_passengers:
                duration = random.uniform(16, 20)  # 16-20 hours together
                weight = self._calculate_contact_weight(duration)
                G.add_edge(i, i+1, weight=weight, contact_type='cabin', duration=duration)
        
        # Crew share cabins (2 per cabin)
        for i in range(self.n_passengers, self.n_total, 2):
            if i+1 < self.n_total:
                duration = random.uniform(12, 16)  # Crew work shifts
                weight = self._calculate_contact_weight(duration)
                G.add_edge(i, i+1, weight=weight, contact_type='cabin', duration=duration)
    
    def _add_dining_connections(self, G: nx.Graph):
        """Add dining cohort connections."""
        # Create 9 dining cohorts (8 people each)
        passengers_list = list(range(self.n_passengers))
        random.shuffle(passengers_list)
        
        cohort_size = 8
        for cohort_id in range(self.config['dining_cohorts']):
            start_idx = cohort_id * cohort_size
            end_idx = min(start_idx + cohort_size, len(passengers_list))
            cohort = passengers_list[start_idx:end_idx]
            
            # Add connections within cohort
            for i in range(len(cohort)):
                for j in range(i+1, len(cohort)):
                    duration = random.uniform(1.5, 3.0)  # 1.5-3 hours dining
                    weight = self._calculate_contact_weight(duration)
                    G.add_edge(cohort[i], cohort[j], weight=weight, 
                             contact_type='dining', duration=duration)
    
    def _add_deck_connections(self, G: nx.Graph):
        """Add deck-level interactions."""
        # Group passengers by deck
        deck_groups = {}
        for node in range(self.n_passengers):
            deck = G.nodes[node]['deck']
            if deck not in deck_groups:
                deck_groups[deck] = []
            deck_groups[deck].append(node)
        
        # Add random connections within each deck
        for deck, passengers in deck_groups.items():
            n_connections = min(len(passengers) * 5, 100)  # Increased from 3, 50
            for _ in range(n_connections):
                if len(passengers) >= 2:
                    p1, p2 = random.sample(passengers, 2)
                    if not G.has_edge(p1, p2):
                        duration = random.uniform(0.5, 2.0)  # Brief deck encounters
                        weight = self._calculate_contact_weight(duration)
                        G.add_edge(p1, p2, weight=weight, 
                                 contact_type='deck', duration=duration)
    
    def _add_facility_connections(self, G: nx.Graph):
        """Add shared facility connections (pools, lounges, etc.)."""
        facilities = ['pool', 'lounge', 'gym', 'spa', 'library', 'theater']
        
        for facility in facilities:
            # More people use each facility for more realistic interactions
            users = random.sample(range(self.n_passengers), 
                                random.randint(200, 500))  # Increased from 50-200
            
            # Add connections between facility users
            for i in range(len(users)):
                for j in range(i+1, min(i+12, len(users))):  # Increased from i+6
                    if not G.has_edge(users[i], users[j]):
                        duration = random.uniform(0.5, 1.5)  # Brief facility contact
                        weight = self._calculate_contact_weight(duration)
                        G.add_edge(users[i], users[j], weight=weight, 
                                 contact_type=facility, duration=duration)
    
    def _add_crew_connections(self, G: nx.Graph):
        """Add crew work interactions."""
        crew_list = list(range(self.n_passengers, self.n_total))
        
        # Create work teams
        team_size = 8
        n_teams = len(crew_list) // team_size
        
        for team_id in range(n_teams):
            start_idx = team_id * team_size
            end_idx = min(start_idx + team_size, len(crew_list))
            team = crew_list[start_idx:end_idx]
            
            # Add connections within team
            for i in range(len(team)):
                for j in range(i+1, len(team)):
                    duration = random.uniform(6, 10)  # Work shift together
                    weight = self._calculate_contact_weight(duration)
                    G.add_edge(team[i], team[j], weight=weight, 
                             contact_type='work', duration=duration)
    
    def _add_service_connections(self, G: nx.Graph):
        """Add passenger-crew service interactions."""
        # Only passenger_service crew interact with passengers
        service_crew = [c for c in range(self.n_passengers, self.n_total)
                       if G.nodes[c].get('service_type') == 'passenger_service']
        
        # Each service crew member serves multiple passengers
        for crew_member in service_crew:
            served_passengers = random.sample(range(self.n_passengers), 
                                           random.randint(10, 25))
            
            for passenger in served_passengers:
                duration = random.uniform(0.1, 0.5)  # Brief service interactions
                weight = self._calculate_contact_weight(duration)
                G.add_edge(crew_member, passenger, weight=weight, 
                         contact_type='service', duration=duration)
    
    def _add_transient_connections(self, G: nx.Graph):
        """Add brief random encounters."""
        # More random transient contacts for realistic cruise ship density
        n_transient = self.n_total * 5  # Increased from 2 to 5 random contacts per person
        
        for _ in range(n_transient):
            p1, p2 = random.sample(range(self.n_total), 2)
            if not G.has_edge(p1, p2):
                duration = random.uniform(0.05, 0.2)  # Very brief encounters
                weight = self._calculate_contact_weight(duration)
                G.add_edge(p1, p2, weight=weight, 
                         contact_type='transient', duration=duration)
    
    def _calculate_contact_weight(self, duration: float) -> float:
        """
        Calculate transmission weight based on contact duration.
        Uses exponential saturation: weight = 1 - exp(-duration / 3.0)
        """
        return 1 - np.exp(-duration / 3.0)  # Saturates at ~3 hours
    
    def build_quarantine_network(self) -> nx.Graph:
        """
        Build quarantine network where only cabin mates and essential crew maintain contact.
        
        Returns:
            NetworkX graph representing quarantine contact structure
        """
        print("🔒 Building quarantine network...")
        
        G_Q = nx.Graph()
        
        # Add all nodes
        for node, data in self.G_normal.nodes(data=True):
            G_Q.add_node(node, **data)
        
        # Only keep cabin connections and essential crew connections
        for u, v, data in self.G_normal.edges(data=True):
            contact_type = data.get('contact_type', '')
            
            # Keep cabin connections (people stuck together)
            if contact_type == 'cabin':
                G_Q.add_edge(u, v, **data)
            
            # Keep essential crew work connections (reduced)
            elif contact_type == 'work':
                # Reduce crew interactions by 80%
                if random.random() < 0.2:
                    new_data = data.copy()
                    new_data['weight'] *= 0.3  # Reduced contact intensity
                    G_Q.add_edge(u, v, **new_data)
        
        self.G_quarantine = G_Q
        
        print(f"✅ Quarantine network: {G_Q.number_of_nodes():,} nodes, {G_Q.number_of_edges():,} edges")
        print(f"   Reduction: {(1 - G_Q.number_of_edges()/self.G_normal.number_of_edges())*100:.1f}% fewer contacts")
        
        return G_Q
    
    def run_baseline_simulation(self, duration: int = 60) -> Dict:
        """Run baseline simulation with no interventions."""
        print("🦠 Running baseline simulation (no interventions)...")
        
        # Setup SEIRS model parameters
        beta = self.config['base_transmission_rate']
        sigma = self.config['sigma']
        gamma = self.config['gamma']
        mu_I = self.config['mu_I']
        
        # Initialize model
        model = SEIRSNetworkModel(
            G=self.G_normal,
            beta=beta,
            sigma=sigma,
            gamma=gamma,
            mu_I=mu_I,
            initI=100,  # Start with 100 infectious individuals
            initE=20  # Start with 20 exposed individuals
        )
        
        # Run simulation
        model.run(T=duration)
        
        # Manual state tracking (workaround for SEIRS+ bugs)
        results = self._calculate_manual_states(model)
        results['scenario'] = 'baseline'
        
        self.results['baseline'] = results
        return results
    
    def run_quarantine_simulation(self, quarantine_start: int = 10, duration: int = 60) -> Dict:
        """Run simulation with quarantine intervention."""
        print(f"🔒 Running quarantine simulation (starts day {quarantine_start})...")
        
        # Setup parameters
        beta = self.config['base_transmission_rate']
        sigma = self.config['sigma']
        gamma = self.config['gamma']
        mu_I = self.config['mu_I']
        
        # Quarantine parameters (reduced transmission in quarantine)
        beta_Q = beta * 0.2  # 80% reduction in transmission during quarantine
        
        # Initialize model with quarantine capability
        model = SEIRSNetworkModel(
            G=self.G_normal,
            beta=beta,
            sigma=sigma,
            gamma=gamma,
            mu_I=mu_I,
            G_Q=self.G_quarantine,
            beta_Q=beta_Q,
            sigma_Q=sigma,
            gamma_Q=gamma,
            initI=100,  # Start with 100 infectious individuals
            initE=20   # Start with 20 exposed individuals
        )
        
        # Set quarantine checkpoint in correct SEIRS+ format
        checkpoints = {
            't': [quarantine_start],
            'G': [self.G_quarantine]
        }
        
        # Run simulation
        model.run(T=duration, checkpoints=checkpoints)
        
        # Manual state tracking
        results = self._calculate_manual_states(model)
        results['scenario'] = 'quarantine'
        results['quarantine_start'] = quarantine_start
        
        self.results['quarantine'] = results
        return results
    
    def run_vaccination_simulation(self, strategy: str = 'one_dose_all', duration: int = 60) -> Dict:
        """
        Run simulation with vaccination strategies.
        
        Args:
            strategy: 'one_dose_all' or 'two_dose_half'
            duration: Simulation duration in days
        """
        print(f"💉 Running vaccination simulation (strategy: {strategy})...")
        
        # Setup base parameters
        sigma = self.config['sigma']
        gamma = self.config['gamma']
        mu_I = self.config['mu_I']
        
        # Vaccination parameters
        vacc_1dose_efficacy = self.config['vaccine_efficacy_1dose']
        vacc_2dose_efficacy = self.config['vaccine_efficacy_2dose']
        
        # Calculate effective transmission rate based on strategy
        if strategy == 'one_dose_all':
            # 70% efficacy for everyone = 30% effective transmission
            effective_beta = self.config['base_transmission_rate'] * (1 - vacc_1dose_efficacy)
            vaccinated_fraction = 1.0
        elif strategy == 'two_dose_half':
            # 95% efficacy for half population = weighted average
            # 50% get 95% protection, 50% get 0% protection
            effective_beta = self.config['base_transmission_rate'] * (0.5 * (1 - vacc_2dose_efficacy) + 0.5 * 1.0)
            vaccinated_fraction = 0.5
        else:
            effective_beta = self.config['base_transmission_rate']
            vaccinated_fraction = 0.0
        
        # Initialize model with reduced transmission rate
        model = SEIRSNetworkModel(
            G=self.G_normal,
            beta=effective_beta,
            sigma=sigma,
            gamma=gamma,
            mu_I=mu_I,
            initI=100,  # Start with 100 infectious individuals
            initE=20   # Start with 20 exposed individuals
        )
        
        # Run simulation (no checkpoints needed)
        model.run(T=duration)
        
        # Manual state tracking
        results = self._calculate_manual_states(model)
        results['scenario'] = f'vaccination_{strategy}'
        results['vaccination_strategy'] = strategy
        results['vaccinated_fraction'] = vaccinated_fraction
        results['effective_transmission_rate'] = effective_beta
        
        self.results[f'vaccination_{strategy}'] = results
        return results
    
    def _calculate_manual_states(self, model) -> Dict:
        """
        Calculate Recovered and Deaths manually (workaround for SEIRS+ bugs).
        
        Args:
            model: SEIRS model with completed simulation
            
        Returns:
            Dictionary with time series and summary statistics
        """
        time = model.tseries
        S = model.numS
        E = model.numE
        I = model.numI
        
        # Manual calculation parameters
        recovery_rate = self.config['gamma']
        mortality_rate = self.config['mu_I']
        
        # Initialize manual states
        R_manual = np.zeros_like(time)
        F_manual = np.zeros_like(time)
        
        # Calculate cumulative recoveries and deaths
        dt = np.diff(time, prepend=time[0])
        
        for i in range(1, len(time)):
            new_recoveries = I[i-1] * recovery_rate * dt[i]
            new_deaths = I[i-1] * mortality_rate * dt[i]
            
            R_manual[i] = R_manual[i-1] + new_recoveries
            F_manual[i] = F_manual[i-1] + new_deaths
        
        # Calculate key metrics
        total_infected = R_manual[-1] + F_manual[-1] + I[-1]
        attack_rate = total_infected / self.n_total * 100
        cfr = F_manual[-1] / total_infected * 100 if total_infected > 0 else 0
        peak_infections = np.max(I)
        peak_day = time[np.argmax(I)]
        
        return {
            'time': time,
            'S': S,
            'E': E,
            'I': I,
            'R_manual': R_manual,
            'F_manual': F_manual,
            'total_infected': total_infected,
            'attack_rate': attack_rate,
            'cfr': cfr,
            'peak_infections': peak_infections,
            'peak_day': peak_day,
            'final_deaths': F_manual[-1],
            'final_recovered': R_manual[-1]
        }
    
    def create_comprehensive_visualization(self):
        """Create comprehensive results visualization comparing all scenarios."""
        print("📊 Creating comprehensive results visualization...")
        
        # Setup the plot
        fig = plt.figure(figsize=(20, 16))
        
        # Define color scheme
        colors = {
            'baseline': '#FF6B6B',
            'quarantine': '#4ECDC4', 
            'vaccination_one_dose_all': '#45B7D1',
            'vaccination_two_dose_half': '#96CEB4'
        }
        
        # 1. INFECTION CURVES COMPARISON
        ax1 = plt.subplot(3, 3, 1)
        for scenario, results in self.results.items():
            plt.plot(results['time'], results['I'], 
                    label=scenario.replace('_', ' ').title(), 
                    color=colors.get(scenario, 'gray'), linewidth=2)
        plt.title('Infectious Population Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Days')
        plt.ylabel('Number of Infectious Individuals')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. CUMULATIVE CASES COMPARISON
        ax2 = plt.subplot(3, 3, 2)
        for scenario, results in self.results.items():
            cumulative = results['R_manual'] + results['F_manual']
            plt.plot(results['time'], cumulative, 
                    label=scenario.replace('_', ' ').title(),
                    color=colors.get(scenario, 'gray'), linewidth=2)
        plt.title('Cumulative Cases Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Days')
        plt.ylabel('Total Cases')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 3. DEATHS COMPARISON
        ax3 = plt.subplot(3, 3, 3)
        for scenario, results in self.results.items():
            plt.plot(results['time'], results['F_manual'], 
                    label=scenario.replace('_', ' ').title(),
                    color=colors.get(scenario, 'gray'), linewidth=2)
        plt.title('Deaths Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Days')
        plt.ylabel('Number of Deaths')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 4. ATTACK RATE BAR CHART
        ax4 = plt.subplot(3, 3, 4)
        scenarios = list(self.results.keys())
        attack_rates = [self.results[s]['attack_rate'] for s in scenarios]
        bars = plt.bar(scenarios, attack_rates, 
                      color=[colors.get(s, 'gray') for s in scenarios])
        plt.title('Attack Rate by Scenario', fontsize=14, fontweight='bold')
        plt.ylabel('Attack Rate (%)')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, rate in zip(bars, attack_rates):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # 5. CASE FATALITY RATE BAR CHART
        ax5 = plt.subplot(3, 3, 5)
        cfrs = [self.results[s]['cfr'] for s in scenarios]
        bars = plt.bar(scenarios, cfrs,
                      color=[colors.get(s, 'gray') for s in scenarios])
        plt.title('Case Fatality Rate by Scenario', fontsize=14, fontweight='bold')
        plt.ylabel('CFR (%)')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, cfr in zip(bars, cfrs):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{cfr:.2f}%', ha='center', va='bottom')
        
        # 6. PEAK INFECTIONS BAR CHART
        ax6 = plt.subplot(3, 3, 6)
        peaks = [self.results[s]['peak_infections'] for s in scenarios]
        bars = plt.bar(scenarios, peaks,
                      color=[colors.get(s, 'gray') for s in scenarios])
        plt.title('Peak Infections by Scenario', fontsize=14, fontweight='bold')
        plt.ylabel('Peak Infectious Count')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, peak in zip(bars, peaks):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{peak:.0f}', ha='center', va='bottom')
        
        # 7. NETWORK STRUCTURE VISUALIZATION
        ax7 = plt.subplot(3, 3, 7)
        plt.sca(ax7)  # Set current axes
        
        # Sample network visualization
        sample_nodes = random.sample(list(self.G_normal.nodes()), 100)
        G_sample = self.G_normal.subgraph(sample_nodes)
        pos = nx.spring_layout(G_sample, k=0.3, iterations=50)
        
        # Color nodes by type
        node_colors = ['lightblue' if n < self.n_passengers else 'lightcoral' 
                      for n in G_sample.nodes()]
        
        nx.draw(G_sample, pos, node_color=node_colors, node_size=30, 
               edge_color='gray', alpha=0.7, with_labels=False, ax=ax7)
        ax7.set_title('Cruise Ship Network Structure\n(Sample of 100 individuals)', 
                     fontsize=12, fontweight='bold')
        
        # 8. RESULTS SUMMARY TABLE
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        # Create summary table data
        table_data = []
        for scenario in scenarios:
            r = self.results[scenario]
            table_data.append([
                scenario.replace('_', ' ').title(),
                f"{r['attack_rate']:.1f}%",
                f"{r['cfr']:.2f}%",
                f"{r['peak_infections']:.0f}",
                f"{r['final_deaths']:.0f}"
            ])
        
        table = ax8.table(cellText=table_data,
                         colLabels=['Scenario', 'Attack Rate', 'CFR', 'Peak Infections', 'Deaths'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        plt.title('Summary Statistics', fontsize=14, fontweight='bold', pad=20)
        
        # 9. VACCINATION STRATEGY COMPARISON (if applicable)
        ax9 = plt.subplot(3, 3, 9)
        
        # Filter vaccination scenarios
        vacc_scenarios = {k: v for k, v in self.results.items() if 'vaccination' in k}
        
        if vacc_scenarios:
            strategies = list(vacc_scenarios.keys())
            protected = []
            
            for strategy in strategies:
                if 'one_dose_all' in strategy:
                    # 70% efficacy for everyone
                    protected.append(self.n_total * 0.7)
                elif 'two_dose_half' in strategy:
                    # 95% efficacy for half
                    protected.append(self.n_total * 0.5 * 0.95)
                else:
                    protected.append(0)
            
            infections_prevented = [self.results['baseline']['total_infected'] - 
                                  vacc_scenarios[s]['total_infected'] 
                                  for s in strategies]
            
            x_pos = np.arange(len(strategies))
            width = 0.35
            
            ax9.bar(x_pos - width/2, protected, width, label='Theoretically Protected',
                   alpha=0.7, color='lightgreen')
            ax9.bar(x_pos + width/2, infections_prevented, width, 
                   label='Actual Infections Prevented', alpha=0.7, color='darkgreen')
            
            ax9.set_xlabel('Vaccination Strategy')
            ax9.set_ylabel('Number of People')
            ax9.set_title('Vaccination Strategy Effectiveness', fontsize=12, fontweight='bold')
            ax9.set_xticks(x_pos)
            ax9.set_xticklabels([s.replace('vaccination_', '').replace('_', ' ').title() 
                                for s in strategies])
            ax9.legend()
        else:
            ax9.text(0.5, 0.5, 'No vaccination\nscenarios run', 
                    ha='center', va='center', transform=ax9.transAxes)
            ax9.set_title('Vaccination Analysis', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.suptitle('🚢 Cruise Ship COVID-19 Outbreak Simulation - Comprehensive Results', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        return fig
    
    def generate_results_report(self) -> str:
        """Generate comprehensive text report of simulation results."""
        
        report = """
🚢 CRUISE SHIP COVID-19 OUTBREAK SIMULATION - RESULTS REPORT
============================================================

SIMULATION OVERVIEW:
"""
        
        report += f"""
Population: {self.n_total:,} individuals ({self.n_passengers:,} passengers + {self.n_crew:,} crew)
Network Structure: {self.G_normal.number_of_edges():,} contact relationships
Simulation Duration: {list(self.results.values())[0]['time'][-1]:.0f} days

"""
        
        report += "\nSCENARIO COMPARISON:\n"
        report += "=" * 50 + "\n"
        
        for scenario, results in self.results.items():
            report += f"\n{scenario.upper().replace('_', ' ')}:\n"
            report += f"  • Attack Rate: {results['attack_rate']:.1f}% ({results['total_infected']:.0f} infected)\n"
            report += f"  • Case Fatality Rate: {results['cfr']:.2f}% ({results['final_deaths']:.0f} deaths)\n"
            report += f"  • Peak Infections: {results['peak_infections']:.0f} on day {results['peak_day']:.1f}\n"
            report += f"  • Final Recovered: {results['final_recovered']:.0f}\n"
        
        # Calculate intervention effectiveness
        if 'baseline' in self.results:
            baseline = self.results['baseline']
            
            report += "\nINTERVENTION EFFECTIVENESS:\n"
            report += "=" * 40 + "\n"
            
            for scenario, results in self.results.items():
                if scenario == 'baseline':
                    continue
                
                infections_prevented = baseline['total_infected'] - results['total_infected']
                deaths_prevented = baseline['final_deaths'] - results['final_deaths']
                peak_reduction = baseline['peak_infections'] - results['peak_infections']
                
                report += f"\n{scenario.upper().replace('_', ' ')} vs BASELINE:\n"
                report += f"  • Infections prevented: {infections_prevented:.0f} ({infections_prevented/baseline['total_infected']*100:.1f}%)\n"
                report += f"  • Deaths prevented: {deaths_prevented:.0f} ({deaths_prevented/baseline['final_deaths']*100:.1f}% if baseline>0)\n"
                report += f"  • Peak reduction: {peak_reduction:.0f} ({peak_reduction/baseline['peak_infections']*100:.1f}%)\n"
        
        # Vaccination strategy analysis
        vacc_scenarios = {k: v for k, v in self.results.items() if 'vaccination' in k}
        if len(vacc_scenarios) >= 2:
            report += "\nVACCINATION STRATEGY COMPARISON:\n"
            report += "=" * 35 + "\n"
            
            one_dose = vacc_scenarios.get('vaccination_one_dose_all')
            two_dose = vacc_scenarios.get('vaccination_two_dose_half')
            
            if one_dose and two_dose:
                report += f"\nONE DOSE FOR ALL vs TWO DOSES FOR HALF:\n"
                report += f"  • One-dose attack rate: {one_dose['attack_rate']:.1f}%\n"
                report += f"  • Two-dose attack rate: {two_dose['attack_rate']:.1f}%\n"
                report += f"  • Deaths difference: {two_dose['final_deaths'] - one_dose['final_deaths']:.0f}\n"
                
                if one_dose['attack_rate'] < two_dose['attack_rate']:
                    report += "  • CONCLUSION: One dose for all is more effective for population protection\n"
                else:
                    report += "  • CONCLUSION: Two doses for half provides better overall protection\n"
        
        report += "\nKEY FINDINGS:\n"
        report += "=" * 15 + "\n"
        
        # Generate key findings
        if 'quarantine' in self.results and 'baseline' in self.results:
            quar_reduction = (self.results['baseline']['peak_infections'] - 
                            self.results['quarantine']['peak_infections']) / self.results['baseline']['peak_infections'] * 100
            report += f"• Quarantine reduces peak infections by {quar_reduction:.1f}%\n"
        
        report += f"• Cruise ship environment enables rapid transmission (attack rates: "
        attack_rates = [r['attack_rate'] for r in self.results.values()]
        report += f"{min(attack_rates):.1f}%-{max(attack_rates):.1f}%)\n"
        
        report += f"• Network structure critical: {self.G_normal.number_of_edges():,} contacts among {self.n_total:,} people\n"
        
        # Add methodology note
        report += "\nMETHODOLOGY NOTE:\n"
        report += "=" * 18 + "\n"
        report += "• Used SEIRS+ network-based epidemiological modeling\n"
        report += "• Manual state tracking implemented due to library limitations\n"
        report += "• Network structure based on Diamond Princess cruise ship layout\n"
        report += "• Disease parameters calibrated to COVID-19 literature\n"
        
        return report

    def create_detailed_network_visualizations(self):
        """Create detailed network visualizations for academic report."""
        print("🖼️ Creating detailed network visualizations...")
        
        # 1. NORMAL CRUISE SHIP NETWORK VISUALIZATION
        fig1, ax1 = plt.subplots(1, 1, figsize=(12, 10))
        
        # Sample 500 nodes for visualization
        sample_nodes = random.sample(list(self.G_normal.nodes()), 500)
        G_sample = self.G_normal.subgraph(sample_nodes)
        
        # Create layout
        pos = nx.spring_layout(G_sample, k=0.5, iterations=100)
        
        # Color and size nodes by type and service
        node_colors = []
        node_sizes = []
        for node in G_sample.nodes():
            if node < self.n_passengers:
                node_colors.append('lightblue')  # Passengers
                node_sizes.append(50)
            else:
                # Crew - different colors for service types
                service_type = self.G_normal.nodes[node].get('service_type', 'passenger_service')
                if service_type == 'non_passenger_service':
                    node_colors.append('darkred')  # Non-passenger service (isolated)
                    node_sizes.append(60)
                else:
                    node_colors.append('lightcoral')  # Passenger service
                    node_sizes.append(55)
        
        # Draw edges with weights
        edge_weights = [G_sample[u][v].get('weight', 0.1) for u, v in G_sample.edges()]
        edge_colors = ['gray' if w < 0.5 else 'darkgray' for w in edge_weights]
        edge_widths = [w * 2 for w in edge_weights]  # Scale weights for visibility
        
        nx.draw_networkx_edges(G_sample, pos, edge_color=edge_colors, width=edge_widths, alpha=0.6, ax=ax1)
        nx.draw_networkx_nodes(G_sample, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8, ax=ax1)
        
        ax1.set_title('🚢 Normal Cruise Ship Network Structure\n(500 Random Individuals)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Non-passenger service crew (red) isolated in clusters\nDarker edges show stronger contact weights')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightblue', label='Passengers'),
            Patch(facecolor='lightcoral', label='Passenger Service Crew'),
            Patch(facecolor='darkred', label='Non-Passenger Service Crew (Isolated)')
        ]
        ax1.legend(handles=legend_elements, loc='upper right')
        ax1.axis('off')
        
        plt.tight_layout()
        plt.savefig('cruise_network_normal.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. QUARANTINE NETWORK VISUALIZATION
        fig2, ax2 = plt.subplots(1, 1, figsize=(12, 10))
        
        # Same 500 nodes but quarantine network
        G_quarantine_sample = self.G_quarantine.subgraph(sample_nodes)
        
        # Use same positions for comparison
        pos_q = pos.copy()
        
        # Color nodes same way
        node_colors_q = []
        node_sizes_q = []
        for node in G_quarantine_sample.nodes():
            if node < self.n_passengers:
                node_colors_q.append('lightblue')  # Passengers
                node_sizes_q.append(50)
            else:
                service_type = self.G_quarantine.nodes[node].get('service_type', 'passenger_service')
                if service_type == 'non_passenger_service':
                    node_colors_q.append('darkred')
                    node_sizes_q.append(60)
                else:
                    node_colors_q.append('lightcoral')
                    node_sizes_q.append(55)
        
        # Draw quarantine network (much fewer edges)
        if G_quarantine_sample.edges():
            edge_weights_q = [G_quarantine_sample[u][v].get('weight', 0.1) for u, v in G_quarantine_sample.edges()]
            edge_colors_q = ['red' if w > 0.5 else 'orange' for w in edge_weights_q]
            edge_widths_q = [w * 3 for w in edge_weights_q]  # Thicker for visibility
            
            nx.draw_networkx_edges(G_quarantine_sample, pos_q, edge_color=edge_colors_q, 
                                 width=edge_widths_q, alpha=0.8, ax=ax2)
        
        nx.draw_networkx_nodes(G_quarantine_sample, pos_q, node_color=node_colors_q, 
                             node_size=node_sizes_q, alpha=0.8, ax=ax2)
        
        ax2.set_title('🔒 Quarantine Network Structure\n(Same 500 Individuals - Cabin Isolation)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel(f'Connections reduced from {G_sample.number_of_edges()} to {G_quarantine_sample.number_of_edges()} edges\n'
                      f'({(1-G_quarantine_sample.number_of_edges()/G_sample.number_of_edges())*100:.1f}% reduction)')
        
        # Add legend
        ax2.legend(handles=legend_elements, loc='upper right')
        ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig('cruise_network_quarantine.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Network visualizations saved:")
        print("  • cruise_network_normal.png - Normal cruise ship network")
        print("  • cruise_network_quarantine.png - Quarantine network comparison")
        
        return fig1, fig2


def main():
    """Main function to run comprehensive cruise ship simulation."""
    
    print("🚢 CRUISE SHIP COVID-19 OUTBREAK SIMULATION")
    print("=" * 50)
    print("Advanced pandemic flu spread simulation for Project 14")
    print("Based on Diamond Princess outbreak data\n")
    
    # Initialize simulation
    sim = CruiseShipSimulation()
    
    # Build networks
    print("\n📡 BUILDING CRUISE SHIP NETWORKS")
    print("-" * 35)
    sim.build_cruise_network()
    sim.build_quarantine_network()
    
    # Create detailed network visualizations first
    print("\n🖼️ CREATING DETAILED NETWORK VISUALIZATIONS")
    print("-" * 45)
    sim.create_detailed_network_visualizations()
    
    # Run scenarios
    print("\n🧪 RUNNING SIMULATION SCENARIOS")
    print("-" * 35)
    
    # 1. Baseline (no interventions)
    sim.run_baseline_simulation(duration=60)
    
    # 2. Quarantine intervention
    sim.run_quarantine_simulation(quarantine_start=10, duration=60)
    
    # 3. Vaccination strategies
    sim.run_vaccination_simulation(strategy='one_dose_all', duration=60)
    sim.run_vaccination_simulation(strategy='two_dose_half', duration=60)
    
    # Generate results
    print("\n📊 GENERATING RESULTS")
    print("-" * 25)
    
    # Create visualizations
    fig = sim.create_comprehensive_visualization()
    plt.savefig('cruise_outbreak_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Generate report
    report = sim.generate_results_report()
    print(report)
    
    # Save report to file
    with open('cruise_outbreak_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ SIMULATION COMPLETE!")
    print("Files generated:")
    print("  • cruise_network_normal.png (normal network structure)")
    print("  • cruise_network_quarantine.png (quarantine network comparison)")
    print("  • cruise_outbreak_results.png (comprehensive visualization)")
    print("  • cruise_outbreak_report.txt (detailed results report)")
    
    return sim


if __name__ == "__main__":
    # Run the simulation
    simulation = main()

#!/usr/bin/env python3
"""
🚢 SIMPLIFIED CRUISE SHIP INTERVENTION COMPARISON SIMULATION
============================================================

10X Engineering: Focus on the core research question:
"What interventions work best for cruise ship outbreak control?"

Compare: Baseline vs Quarantine vs Vaccination Strategies
Simplified network but comprehensive intervention analysis.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from seirsplus.models import SEIRSNetworkModel
import random

class SimpleCruiseSimulation:
    """Simplified cruise ship simulation for intervention comparison."""
    
    def __init__(self, n_people: int = 3700):
        # Calculate passengers and crew (roughly 70% passengers, 30% crew)
        self.n_passengers = int(n_people * 0.7)
        self.n_crew = n_people - self.n_passengers
        self.n_people = n_people  # Keep for compatibility
        self.n_total = n_people
        self.results = {}
        
        # SIMPLIFIED CONFIG - Core parameters only
        self.config = {
            'transmission_rate': 0.8,
            'infectious_days': 7,
            'incubation_days': 5,
            'mortality_rate': 0.013,  # 1.3% - constant across all scenarios
            'vaccine_1dose_efficacy': 0.70,
            'vaccine_2dose_efficacy': 0.95,
            'quarantine_effectiveness': 0.8,  # 80% transmission reduction
        }
        
        # Networks (will be built)
        self.G_normal = None
        self.G_quarantine = None
        
        print(f"🚢 Cruise Intervention Simulation: {n_people:,} people")
        print(f"   {self.n_passengers:,} passengers, {self.n_crew:,} crew")
    
    def build_simple_network(self) -> nx.Graph:
        """Build simple but realistic cruise ship network - 3 contact types with crew/passenger distinction."""
        G = nx.Graph()
        
        # Add nodes with crew/passenger distinction
        passengers = list(range(self.n_passengers))
        crew = list(range(self.n_passengers, self.n_total))
        
        # Add passenger nodes
        for p in passengers:
            G.add_node(p, type='passenger', cabin=p//2)
        
        # Add crew nodes
        for c in crew:
            G.add_node(c, type='crew', cabin=(c-self.n_passengers)//2)
        
        # 1. HIGH RISK: Cabin pairs (closest contacts)
        # Passenger cabins (2 per cabin)
        for i in range(0, self.n_passengers, 2):
            if i+1 < self.n_passengers:
                G.add_edge(i, i+1, weight=1.0, contact_type='cabin')
        
        # Crew cabins (2 per cabin)  
        for i in range(self.n_passengers, self.n_total, 2):
            if i+1 < self.n_total:
                G.add_edge(i, i+1, weight=1.0, contact_type='cabin')
        
        # 2. MEDIUM RISK: Dining/social groups (8 people each)
        # Passenger dining groups
        passengers_list = list(range(self.n_passengers))
        random.shuffle(passengers_list)
        for group in range(self.n_passengers // 8):
            start = group * 8
            members = passengers_list[start:start+8]
            for i in range(len(members)):
                for j in range(i+1, len(members)):
                    G.add_edge(members[i], members[j], weight=0.5, contact_type='social')
        
        # Crew work groups (higher contact weight since they work together)
        crew_list = list(range(self.n_passengers, self.n_total))
        random.shuffle(crew_list)
        for group in range(len(crew_list) // 8):
            start = group * 8
            members = crew_list[start:start+8]
            for i in range(len(members)):
                for j in range(i+1, len(members)):
                    G.add_edge(members[i], members[j], weight=0.7, contact_type='work')  # Higher weight for work
        
        # Passenger-crew service interactions (medium risk)
        for crew_member in crew[:len(crew)//3]:  # 1/3 of crew serve passengers
            served_passengers = random.sample(passengers, random.randint(8, 15))
            for passenger in served_passengers:
                G.add_edge(crew_member, passenger, weight=0.3, contact_type='service')
        
        # 3. LOW RISK: Random encounters (2 per person)
        for person in range(self.n_total):
            possible_contacts = [p for p in range(self.n_total) if p != person]
            contacts = random.sample(possible_contacts, 2)
            for contact in contacts:
                if not G.has_edge(person, contact):
                    G.add_edge(person, contact, weight=0.1, contact_type='random')
        
        print(f"✅ Normal network: {G.number_of_edges():,} connections")
        print(f"   Passengers: {self.n_passengers:,}, Crew: {self.n_crew:,}")
        return G
    
    def build_quarantine_network(self) -> nx.Graph:
        """Build quarantine network - cabin isolation only."""
        G_Q = nx.Graph()
        
        # Add all nodes with same attributes
        for node, data in self.G_normal.nodes(data=True):
            G_Q.add_node(node, **data)
        
        # Only keep cabin connections during quarantine (complete isolation to cabins)
        for i in range(0, self.n_total, 2):
            if i+1 < self.n_total:
                G_Q.add_edge(i, i+1, weight=1.0, contact_type='cabin')
        
        print(f"✅ Quarantine network: {G_Q.number_of_edges():,} connections "
              f"({(1-G_Q.number_of_edges()/self.G_normal.number_of_edges())*100:.1f}% reduction)")
        return G_Q
    
    def run_scenario(self, scenario_name: str, network: nx.Graph, effective_transmission: float) -> dict:
        """Run a single simulation scenario."""
        print(f"🧪 Running {scenario_name}...")
        
        # SEIRS parameters
        gamma = 1 / self.config['infectious_days']
        sigma = 1 / self.config['incubation_days']
        
        # Initialize model
        model = SEIRSNetworkModel(
            G=network,
            beta=effective_transmission,
            sigma=sigma,
            gamma=gamma,
            mu_I=self.config['mortality_rate'] * gamma,
            initI=100,  # Start with outbreak in progress
            initE=20
        )
        
        # Run simulation
        model.run(T=60)
        
        # Extract results (use working S, E, I from SEIRS+)
        time = model.tseries
        S, E, I = model.numS, model.numE, model.numI
        
        # Manual R, F calculation (only because SEIRS+ is buggy)
        R, F = self._calculate_outcomes(time, I)
        
        total_infected = R[-1] + F[-1] + I[-1]
        attack_rate = total_infected / self.n_people * 100
        
        return {
            'time': time, 'S': S, 'E': E, 'I': I, 'R': R, 'F': F,
            'attack_rate': attack_rate,
            'peak_infections': np.max(I),
            'total_infected': total_infected,
            'deaths': F[-1]
        }
    
    def _calculate_outcomes(self, time, I):
        """Simple R/F calculation - just the math, no complexity."""
        dt = np.diff(time, prepend=time[0])
        R, F = np.zeros_like(time), np.zeros_like(time)
        
        recovery_rate = 1 / self.config['infectious_days']
        death_rate = self.config['mortality_rate'] * recovery_rate
        
        for i in range(1, len(time)):
            R[i] = R[i-1] + I[i-1] * recovery_rate * dt[i]
            F[i] = F[i-1] + I[i-1] * death_rate * dt[i]
        
        return R, F
    
    def run_all_scenarios(self):
        """Run all intervention scenarios - the complete comparison."""
        # Build networks
        self.G_normal = self.build_simple_network()
        self.G_quarantine = self.build_quarantine_network()
        
        base_transmission = self.config['transmission_rate']
        
        # 1. Baseline (no interventions)
        self.results['baseline'] = self.run_scenario(
            'Baseline', self.G_normal, base_transmission)
        
        # 2. Quarantine intervention (reduced transmission + limited network)
        quarantine_transmission = base_transmission * (1 - self.config['quarantine_effectiveness'])
        self.results['quarantine'] = self.run_scenario(
            'Quarantine', self.G_quarantine, quarantine_transmission)
        
        # 3. One dose for all (70% efficacy for everyone)
        eff_trans_1dose = base_transmission * (1 - self.config['vaccine_1dose_efficacy'])
        self.results['vaccination_1dose'] = self.run_scenario(
            'One Dose All', self.G_normal, eff_trans_1dose)
        
        # 4. Two doses for half (95% efficacy for 50%, 0% for other 50%)
        eff_trans_2dose = base_transmission * (0.5 * (1 - self.config['vaccine_2dose_efficacy']) + 0.5 * 1.0)
        self.results['vaccination_2dose'] = self.run_scenario(
            'Two Dose Half', self.G_normal, eff_trans_2dose)
    
    def create_results_visualization(self):
        """Focused visualization - intervention comparison without CFR."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        colors = {
            'baseline': '#FF6B6B', 
            'quarantine': '#4ECDC4',
            'vaccination_1dose': '#45B7D1', 
            'vaccination_2dose': '#96CEB4'
        }
        
        # 1. Infection Curves Comparison
        for scenario, results in self.results.items():
            ax1.plot(results['time'], results['I'], 
                    label=scenario.replace('_', ' ').title(), 
                    color=colors[scenario], linewidth=3)
        ax1.set_title('Infectious Population Over Time', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Number of Infectious')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Attack Rates (KEY METRIC)
        scenarios = list(self.results.keys())
        attack_rates = [self.results[s]['attack_rate'] for s in scenarios]
        bars = ax2.bar([s.replace('_', ' ').title() for s in scenarios], attack_rates,
                      color=[colors[s] for s in scenarios])
        ax2.set_title('Attack Rate by Intervention\n(KEY METRIC)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Attack Rate (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, rate in zip(bars, attack_rates):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 3. Peak Infections Comparison
        peaks = [self.results[s]['peak_infections'] for s in scenarios]
        bars3 = ax3.bar([s.replace('_', ' ').title() for s in scenarios], peaks,
                       color=[colors[s] for s in scenarios])
        ax3.set_title('Peak Infections by Intervention', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Peak Infectious Count')
        ax3.tick_params(axis='x', rotation=45)
        
        for bar, peak in zip(bars3, peaks):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{peak:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Intervention Effectiveness
        baseline_infections = self.results['baseline']['total_infected']
        interventions = [s for s in scenarios if s != 'baseline']
        infections_prevented = [baseline_infections - self.results[s]['total_infected'] 
                              for s in interventions]
        
        bars4 = ax4.bar([s.replace('_', ' ').title() for s in interventions], 
                       infections_prevented,
                       color=[colors[s] for s in interventions])
        ax4.set_title('Infections Prevented\n(vs Baseline)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Infections Prevented')
        ax4.tick_params(axis='x', rotation=45)
        
        for bar, prevented in zip(bars4, infections_prevented):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                    f'{prevented:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.suptitle('Cruise Ship Outbreak Intervention Comparison', 
                     fontsize=16, fontweight='bold', y=0.98)
        plt.savefig('cruise_intervention_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def create_network_visualizations(self):
        """Create network structure comparison visualizations."""
        print("🖼️ Creating network structure visualizations...")
        
        # Sample 500 nodes for visualization (manageable size)
        # Ensure we get both passengers and crew in sample
        passenger_sample = random.sample(range(self.n_passengers), min(350, self.n_passengers))
        crew_sample = random.sample(range(self.n_passengers, self.n_total), min(150, self.n_crew))
        sample_nodes = passenger_sample + crew_sample
        
        # 1. NORMAL CRUISE SHIP NETWORK
        fig1, ax1 = plt.subplots(1, 1, figsize=(12, 10))
        
        G_sample = self.G_normal.subgraph(sample_nodes)
        pos = nx.spring_layout(G_sample, k=0.3, iterations=50)
        
        # Color nodes by type: passengers (blue) vs crew (orange)
        node_colors = []
        node_sizes = []
        for node in G_sample.nodes():
            if self.G_normal.nodes[node]['type'] == 'passenger':
                node_colors.append('lightblue')
                node_sizes.append(40)
            else:  # crew
                node_colors.append('orange')
                node_sizes.append(60)
        
        # Draw edges with weights and contact types
        edge_weights = [G_sample[u][v].get('weight', 0.1) for u, v in G_sample.edges()]
        edge_colors = []
        for u, v in G_sample.edges():
            contact_type = G_sample[u][v].get('contact_type', 'random')
            if contact_type == 'cabin':
                edge_colors.append('red')
            elif contact_type == 'work':
                edge_colors.append('darkgreen')
            elif contact_type == 'service':
                edge_colors.append('purple')
            elif contact_type == 'social':
                edge_colors.append('blue')
            else:
                edge_colors.append('gray')
        
        edge_widths = [w * 2.5 for w in edge_weights]
        
        nx.draw_networkx_edges(G_sample, pos, edge_color=edge_colors, width=edge_widths, alpha=0.6, ax=ax1)
        nx.draw_networkx_nodes(G_sample, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8, ax=ax1)
        
        ax1.set_title('Normal Cruise Ship Network\n(350 Passengers + 150 Crew)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel(f'Network connections: {G_sample.number_of_edges():,} edges\n'
                      f'Blue=Passengers, Orange=Crew\n'
                      f'Red=Cabin, Green=Work, Purple=Service, Blue=Social, Gray=Random')
        ax1.axis('off')
        
        plt.tight_layout()
        plt.savefig('cruise_network_normal.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. QUARANTINE NETWORK (SAME NODES)
        fig2, ax2 = plt.subplots(1, 1, figsize=(12, 10))
        
        G_quarantine_sample = self.G_quarantine.subgraph(sample_nodes)
        
        # Use same positions for direct comparison
        pos_q = pos.copy()
        
        # Color quarantine nodes - simple crew vs passenger distinction
        node_colors_q = []
        node_sizes_q = []
        
        for node in G_quarantine_sample.nodes():
            node_type = self.G_quarantine.nodes[node]['type']
            
            if node_type == 'passenger':
                node_colors_q.append('lightcoral')  # Passengers in quarantine
                node_sizes_q.append(40)
            else:  # crew in quarantine
                node_colors_q.append('orange')
                node_sizes_q.append(60)
        
        # Draw quarantine network (only cabin connections)
        if G_quarantine_sample.edges():
            # All edges in quarantine are cabin connections
            edge_colors_q = ['red' for _ in G_quarantine_sample.edges()]
            edge_widths_q = [3 for _ in G_quarantine_sample.edges()]
            
            nx.draw_networkx_edges(G_quarantine_sample, pos_q, edge_color=edge_colors_q, 
                                 width=edge_widths_q, alpha=0.8, ax=ax2)
        
        nx.draw_networkx_nodes(G_quarantine_sample, pos_q, node_color=node_colors_q, 
                             node_size=node_sizes_q, alpha=0.8, ax=ax2)
        
        ax2.set_title('Quarantine Network Structure\n(Complete Cabin Isolation)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel(f'Connections: {G_quarantine_sample.number_of_edges():,} edges '
                      f'({(1-G_quarantine_sample.number_of_edges()/G_sample.number_of_edges())*100:.1f}% reduction)\n'
                      f'Orange=Crew, Light Red=Passengers (all isolated to cabins)\n'
                      f'Red edges=Cabin connections only')
        ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig('cruise_network_quarantine.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Network visualizations saved:")
        print("  • cruise_network_normal.png - Normal cruise ship network (crew vs passengers)")
        print("  • cruise_network_quarantine.png - Quarantine network (cabin isolation only)")
        print(f"  • Shows {(1-self.G_quarantine.number_of_edges()/self.G_normal.number_of_edges())*100:.1f}% contact reduction during quarantine")
        
        return fig1, fig2
    
    def create_epidemic_dynamics_visualization(self):
        """Create detailed epidemic dynamics visualizations."""
        print("📈 Creating epidemic dynamics visualizations...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        colors = {
            'baseline': '#FF6B6B', 
            'quarantine': '#4ECDC4',
            'vaccination_1dose': '#45B7D1', 
            'vaccination_2dose': '#96CEB4'
        }
        
        # 1. SEIR COMPARTMENT DYNAMICS (for baseline)
        baseline = self.results['baseline']
        ax1.plot(baseline['time'], baseline['S'], label='Susceptible', color='blue', linewidth=2)
        ax1.plot(baseline['time'], baseline['E'], label='Exposed', color='orange', linewidth=2)
        ax1.plot(baseline['time'], baseline['I'], label='Infectious', color='red', linewidth=2)
        ax1.plot(baseline['time'], baseline['R'], label='Recovered', color='green', linewidth=2)
        ax1.plot(baseline['time'], baseline['F'], label='Deaths', color='black', linewidth=2)
        
        ax1.set_title('SEIR Compartment Dynamics\n(Baseline Scenario)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Number of People')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. DAILY NEW INFECTIONS (calculated from cumulative)
        for scenario, results in self.results.items():
            # Calculate daily new infections from cumulative
            cumulative_infected = results['R'] + results['F']
            daily_new = np.diff(cumulative_infected, prepend=0)
            # Smooth with 3-day rolling average
            if len(daily_new) >= 3:
                daily_smooth = np.convolve(daily_new, np.ones(3)/3, mode='same')
            else:
                daily_smooth = daily_new
            
            ax2.plot(results['time'], daily_smooth, 
                    label=scenario.replace('_', ' ').title(), 
                    color=colors[scenario], linewidth=2)
        
        ax2.set_title('Daily New Infections\n(3-day rolling average)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('New Infections per Day')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. CUMULATIVE OUTCOMES OVER TIME
        for scenario, results in self.results.items():
            total_cases = results['R'] + results['F'] + results['I']
            ax3.plot(results['time'], total_cases, 
                    label=scenario.replace('_', ' ').title(), 
                    color=colors[scenario], linewidth=3)
        
        ax3.set_title('Cumulative Total Cases Over Time', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Total Cases (Ever Infected)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. EPIDEMIC TIMELINE COMPARISON
        timeline_data = []
        for scenario, results in self.results.items():
            # Find epidemic start (>50 infectious)
            epidemic_start = next((i for i, val in enumerate(results['I']) if val > 50), 0)
            
            # Find peak day
            peak_day = np.argmax(results['I'])
            peak_infections = results['I'][peak_day]
            
            # Find end (when infectious drops below 5% of peak)
            epidemic_end = next((i for i, val in enumerate(results['I'][peak_day:], peak_day) 
                               if val < peak_infections * 0.05), len(results['I'])-1)
            
            timeline_data.append({
                'scenario': scenario.replace('_', ' ').title(),
                'start': epidemic_start,
                'peak': peak_day,
                'end': epidemic_end,
                'duration': epidemic_end - epidemic_start,
                'peak_infections': peak_infections
            })
        
        # Create timeline visualization
        scenarios = [d['scenario'] for d in timeline_data]
        starts = [d['start'] for d in timeline_data]
        peaks = [d['peak'] for d in timeline_data]
        ends = [d['end'] for d in timeline_data]
        
        y_pos = range(len(scenarios))
        
        # Plot timeline bars
        for i, (scenario, start, peak, end) in enumerate(zip(scenarios, starts, peaks, ends)):
            color = colors[list(self.results.keys())[i]]
            # Full epidemic duration
            ax4.barh(i, end - start, left=start, height=0.3, color=color, alpha=0.3, 
                    label=f'{scenario} (Duration)')
            # Peak marker
            ax4.scatter(peak, i, color=color, s=100, marker='o', zorder=3)
        
        ax4.set_title('Epidemic Timeline Comparison', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Intervention Scenario')
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(scenarios)
        ax4.grid(True, alpha=0.3)
        
        # Add peak markers legend
        ax4.scatter([], [], color='black', s=100, marker='o', label='Peak Infections')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.suptitle('Cruise Ship Epidemic Dynamics Analysis', 
                     fontsize=16, fontweight='bold', y=0.98)
        plt.savefig('cruise_epidemic_dynamics.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print timeline summary
        print("\n📅 EPIDEMIC TIMELINE SUMMARY:")
        print("-" * 50)
        for data in timeline_data:
            print(f"{data['scenario']:20s}: Start day {data['start']:2d}, "
                  f"Peak day {data['peak']:2d} ({data['peak_infections']:3.0f} infectious), "
                  f"Duration {data['duration']:2d} days")
        
        return fig
    
    def create_transmission_analysis_visualization(self):
        """Create transmission and contact analysis visualizations."""
        print("🔬 Creating transmission analysis visualizations...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        colors = {
            'baseline': '#FF6B6B', 
            'quarantine': '#4ECDC4',
            'vaccination_1dose': '#45B7D1', 
            'vaccination_2dose': '#96CEB4'
        }
        
        # 1. ATTACK RATE BY POPULATION SIZE
        population_sizes = [500, 1000, 2000, 3700, 5000]  # Hypothetical sizes
        baseline_rate = self.results['baseline']['attack_rate']
        
        # Estimate attack rates for different population sizes (simplified model)
        attack_rates_baseline = []
        attack_rates_quarantine = []
        attack_rates_vacc = []
        
        for pop in population_sizes:
            # Simple scaling based on network density (more people = higher density = higher attack rate)
            density_factor = min(1.5, pop / 3700)  # Cap at 1.5x
            attack_rates_baseline.append(min(baseline_rate * density_factor, 100))
            attack_rates_quarantine.append(min(self.results['quarantine']['attack_rate'] * density_factor, 100))
            attack_rates_vacc.append(min(self.results['vaccination_1dose']['attack_rate'] * density_factor, 100))
        
        ax1.plot(population_sizes, attack_rates_baseline, 'o-', color=colors['baseline'], 
                linewidth=2, markersize=8, label='Baseline')
        ax1.plot(population_sizes, attack_rates_quarantine, 'o-', color=colors['quarantine'], 
                linewidth=2, markersize=8, label='Quarantine')
        ax1.plot(population_sizes, attack_rates_vacc, 'o-', color=colors['vaccination_1dose'], 
                linewidth=2, markersize=8, label='Vaccination (1-dose)')
        
        # Highlight our actual population size
        ax1.axvline(x=3700, color='red', linestyle='--', alpha=0.7, label='Our Study (3,700)')
        
        ax1.set_title('Attack Rate vs Population Size\n(Theoretical Scaling)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Population Size')
        ax1.set_ylabel('Attack Rate (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. INTERVENTION EFFECTIVENESS OVER TIME
        baseline_cumulative = self.results['baseline']['R'] + self.results['baseline']['F']
        baseline_time = self.results['baseline']['time']
        
        for scenario, results in self.results.items():
            if scenario == 'baseline':
                continue
            scenario_cumulative = results['R'] + results['F']
            scenario_time = results['time']
            
            # Find common time range (minimum of the two)
            min_length = min(len(baseline_time), len(scenario_time))
            common_time = baseline_time[:min_length]
            baseline_common = baseline_cumulative[:min_length]
            scenario_common = scenario_cumulative[:min_length]
            
            # Calculate effectiveness
            effectiveness = np.where(baseline_common > 0, 
                                   (1 - scenario_common / baseline_common) * 100, 
                                   0)
            
            ax2.plot(common_time, effectiveness, 
                    label=scenario.replace('_', ' ').title(), 
                    color=colors[scenario], linewidth=2)
        
        ax2.set_title('Intervention Effectiveness Over Time\n(% Reduction vs Baseline)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Effectiveness (% Reduction)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        # 3. CONTACT NETWORK ANALYSIS
        # Analyze network properties
        network_stats = {
            'Normal Network': {
                'Nodes': self.G_normal.number_of_nodes(),
                'Edges': self.G_normal.number_of_edges(),
                'Avg Degree': 2 * self.G_normal.number_of_edges() / self.G_normal.number_of_nodes(),
                'Density': nx.density(self.G_normal),
                'Clustering': nx.average_clustering(self.G_normal)
            },
            'Quarantine Network': {
                'Nodes': self.G_quarantine.number_of_nodes(),
                'Edges': self.G_quarantine.number_of_edges(),
                'Avg Degree': 2 * self.G_quarantine.number_of_edges() / self.G_quarantine.number_of_nodes(),
                'Density': nx.density(self.G_quarantine),
                'Clustering': nx.average_clustering(self.G_quarantine)
            }
        }
        
        metrics = ['Edges', 'Avg Degree', 'Density', 'Clustering']
        normal_values = [network_stats['Normal Network'][metric] for metric in metrics]
        quarantine_values = [network_stats['Quarantine Network'][metric] for metric in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, normal_values, width, label='Normal Network', 
                       color=colors['baseline'], alpha=0.7)
        bars2 = ax3.bar(x + width/2, quarantine_values, width, label='Quarantine Network', 
                       color=colors['quarantine'], alpha=0.7)
        
        ax3.set_title('Network Structure Comparison', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Network Metrics')
        ax3.set_ylabel('Metric Value')
        ax3.set_xticks(x)
        ax3.set_xticklabels(metrics, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 4. RECOVERY VS DEATH OUTCOMES
        scenarios_list = list(self.results.keys())
        final_recovered = [self.results[s]['R'][-1] for s in scenarios_list]
        final_deaths = [self.results[s]['F'][-1] for s in scenarios_list]
        
        x = np.arange(len(scenarios_list))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, final_recovered, width, label='Recovered', 
                       color='green', alpha=0.7)
        bars2 = ax4.bar(x + width/2, final_deaths, width, label='Deaths', 
                       color='darkred', alpha=0.7)
        
        ax4.set_title('Final Outcomes: Recovery vs Death', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Intervention Scenario')
        ax4.set_ylabel('Number of People')
        ax4.set_xticks(x)
        ax4.set_xticklabels([s.replace('_', ' ').title() for s in scenarios_list], rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.suptitle('Cruise Ship Transmission Analysis', 
                     fontsize=16, fontweight='bold', y=0.98)
        plt.savefig('cruise_transmission_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print network analysis
        print("\n🔗 NETWORK ANALYSIS SUMMARY:")
        print("-" * 50)
        for network_type, stats in network_stats.items():
            print(f"\n{network_type}:")
            for metric, value in stats.items():
                print(f"  {metric:15s}: {value:.3f}")
        
        return fig
    
    def print_summary(self):
        """Print comprehensive intervention comparison results."""
        print("\n" + "="*70)
        print("🎯 CRUISE SHIP INTERVENTION COMPARISON RESULTS")
        print("="*70)
        
        baseline = self.results['baseline']['total_infected']
        
        print(f"\n📊 ATTACK RATE OUTCOMES:")
        for scenario, results in self.results.items():
            print(f"   {scenario.replace('_', ' ').title():20s}: {results['attack_rate']:6.1f}% attack rate")
        
        print(f"\n💪 INTERVENTION EFFECTIVENESS:")
        for scenario, results in self.results.items():
            if scenario == 'baseline':
                continue
            prevented = baseline - results['total_infected']
            effectiveness = prevented / baseline * 100
            print(f"   {scenario.replace('_', ' ').title():20s}: {prevented:6.0f} infections prevented ({effectiveness:.1f}%)")
        
        # Find best intervention
        best_scenario = min([s for s in self.results.keys() if s != 'baseline'], 
                           key=lambda s: self.results[s]['attack_rate'])
        best_prevented = baseline - self.results[best_scenario]['total_infected']
        
        print(f"\n🏆 BEST INTERVENTION:")
        print(f"   {best_scenario.replace('_', ' ').title()}")
        print(f"   Prevents {best_prevented:.0f} infections ({best_prevented/baseline*100:.1f}% reduction)")
        
        # Quarantine vs Vaccination comparison
        quarantine_prevented = baseline - self.results['quarantine']['total_infected']
        vacc1_prevented = baseline - self.results['vaccination_1dose']['total_infected']
        vacc2_prevented = baseline - self.results['vaccination_2dose']['total_infected']
        
        print(f"\n🔄 INTERVENTION COMPARISON:")
        print(f"   Quarantine:        {quarantine_prevented:6.0f} infections prevented")
        print(f"   One dose for all:  {vacc1_prevented:6.0f} infections prevented")
        print(f"   Two dose for half: {vacc2_prevented:6.0f} infections prevented")
        
        if vacc1_prevented > vacc2_prevented:
            print(f"   📋 Vaccination: One dose strategy is {vacc1_prevented-vacc2_prevented:.0f} infections better")
        else:
            print(f"   📋 Vaccination: Two dose strategy is {vacc2_prevented-vacc1_prevented:.0f} infections better")
        
        print(f"\n📋 SIMULATION DETAILS:")
        print(f"   Population: {self.n_people:,} people")
        print(f"   Network: {self.G_normal.number_of_edges():,} normal connections")
        print(f"   Quarantine: {self.G_quarantine.number_of_edges():,} connections (cabin only)")
        print(f"   CFR: {self.config['mortality_rate']*100:.1f}% (constant across all scenarios)")
        print("="*70)


def main():
    """Run the complete intervention comparison simulation."""
    print("🚢 CRUISE SHIP INTERVENTION COMPARISON SIMULATION")
    print("="*55)
    print("Comparing: Baseline vs Quarantine vs Vaccination Strategies")
    print("Simplified network, comprehensive intervention analysis")
    print("")
    
    # Run simulation
    sim = SimpleCruiseSimulation()
    sim.run_all_scenarios()
    
    # Create network visualizations
    print("\n🖼️ GENERATING NETWORK VISUALIZATIONS")
    print("-" * 40)
    sim.create_network_visualizations()
    
    # Create detailed epidemic dynamics visualizations
    print("\n📈 GENERATING EPIDEMIC DYNAMICS ANALYSIS")
    print("-" * 45)
    sim.create_epidemic_dynamics_visualization()
    
    # Create transmission analysis visualizations
    print("\n🔬 GENERATING TRANSMISSION ANALYSIS")
    print("-" * 38)
    sim.create_transmission_analysis_visualization()
    
    # Results summary and main intervention comparison
    print("\n📊 RESULTS ANALYSIS")
    print("-" * 25)
    sim.print_summary()
    sim.create_results_visualization()
    
    print(f"\n✅ SIMULATION COMPLETE!")
    print(f"Files generated:")
    print(f"  • cruise_network_normal.png (normal network structure)")
    print(f"  • cruise_network_quarantine.png (quarantine network comparison)")
    print(f"  • cruise_intervention_results.png (4-panel intervention analysis)")
    print(f"  • cruise_epidemic_dynamics.png (detailed epidemic dynamics)")
    print(f"  • cruise_transmission_analysis.png (transmission and contact analysis)")
    print(f"  • Code: {__file__}")
    
    return sim


if __name__ == "__main__":
    simulation = main() 

“Project 14:

(2–4 members) “Advanced” Pandemic Flu Spread. Project 3 considered a (trivial) discrete-event simulation of pandemic flu spread in a classroom. (Project 4 concerned a continuous-time, deterministic simulation that doesn’t apply here.) If you feel a little more adventuresome, I’d like you to think about a bigger-and-better simulation involving a larger population. 

Here’s a potential scenario (there are many other interesting ones — feel free to be imaginative):
• Some infectious people enter a population of susceptibles, and some of the
susceptibles become infected.
• There is a short period of a couple of days before a newly-infected person in
turn becomes infectious.
• When a person recovers (or dies), the person is not again susceptible.
• Infectiousness or death can be mitigated by masking, social distancing, etc.
• Infectiousness or death can be mitigated by vaccination. Vaccines can be
delivered in one or two doses. But there could be supply chain issues.
• Even if a vaccine requires two doses, the vaccine nevertheless provides partial
immunization after even only one dose. Might you immediately give everyone
only one dose instead of two, and hope that the supply chain catches up so
that you can “eventually” give everyone two doses?

To determine whether a particular strategy is any good, you probably ought to consider the number of people who eventually get infected (or die), the length of the epidemic, etc.”


Task Points Description, Title & Group, Member Names 5 
Include a descriptive title, the group number, and all group member names at the beginning of your project.

Abstract 5 
A short synopsis (at most 200 words) of what problem you’re working on, including major findings

Background & Description of the Problem 5  
Some details of the problem under investigation (e.g., a literature review along with a description of the organization of what’s coming up in the remainder of the write-up).

Tech Overview 
Everyone (rewrite your paragraphs to make it clear that we didn’t end up choosing it but it was interesting because of X reason anyway)

Cruise ship outbreak simulation provides a unique setting for high-risk disease transmission, due to factors such as limited intervention, confined spaces, and scheduled gatherings. The COVID-19 pandemic on the Diamond Princess Cruise ship serves as a background reference for our model as it experienced high infection concentration among 2666 passengers and 1045 crew members. Among 3711 Diamond Princess passengers, 712 tested positive. Out of the infected patients, 46.5% were asymptomatic and 9 out of 381 symptomatic people died. (Moriarty)  A study on U.S passengers aboard showed that shared cabins for 2-4 people have a notable transmission rate among other layouts. In particular, the attack rate in cabins shared with symptomatic individuals was 81 percent while only 16 percent attack rate in single cabins or those without infected cabin mates. (Plucinski, Mateusz M et al.). This suggests that the specific layout of a cruise ship is more susceptible to disease transmission and such dynamics compelled us to develop this simulation of a cruise ship outbreak.
Beyond the Diamond Princess Cruise ship, there are other confirmed COVID-19 outbreak cases on cruise ships. On Mar. 8, 2020 the Ruby Princess cruise departed Sydney for a 13-day voyage around New Zealand.The cruise was carrying 2,671 passengers and 1,146 crew members. At the time of the departure, COVID-19 had major outbreaks globally. Despite several passengers falling ill onboard, no quarantine took place, and the ship’s nearly 2,700 passengers disembarked the Ruby Princess to return home. After two weeks, authorities found 622 confirmed cases of COVID-19 and 10 deaths among the passengers and crew of the Ruby Princess. (CGTN) Clearly, the confined, high-density nature of cruise ships with shared dining spaces, entertainment venues, and limited ventilation poses a high risk environment for the transmission of gastrointestinal and respiratory illnesses. 
Given the complex environment and situational constraints, we reviewed multiple open-source simulation codes and academic studies to better understand epidemic parameters, transmission patterns, and general epidemic dynamics. To better understand the general epidemic dynamics, our team explored numerous open-source frameworks and analyzed their use cases. In 2020, the Maple Rain Research Company used Python’s Mesa framework to create an agent-based simulation of how COVID-19 can spread. The model defines a dictionary of parameters, including grid size, infection probability, and recovery time, and then runs the simulation for a fixed number of ticks, or units of time. 

JULIO (WRITE A PARAGRAPH HERE INTRODUCING ALL THE APPROACHES WE TRIED) 
In an effort to evaluate which simulation framework might be best for modeling pandemic flu on a cruise ship, we assessed several open-source approaches. Each approach had its own capabilities and limitations, and through the evaluation process we developed a better understanding of the trade-offs between spatial realism, complexity of transmission, and flexibility of interventions.
We first examined agents-based simulations based on Mesa,	 such as the MapleRain COVID-19 model. It is built on Python’s Mesa agent-based modeling library and has fundamental epidemic dynamics such as a representation of movement, time of exposure, and recovery in a confined grid. This model offered us a chance to get familiarized with the temporal progression and transitions of infection states. However, the model’s grid-based environment, more representative of an urban layout, proved too simplistic for the structured nature of cruise ship interactions, which are shaped by predefined cabin groups, dining halls, and scheduled entertainment.
Next, we visited the Infectious-Disease-Agent-Based-Modeling project. This model used several helpful features:  disease severity, hospital capacity limitations, vaccines and social distancing interventions. This model employed a uniform network where each edge was equal and made no distinction between weak and high-risk exposures, e.g., sharing a cabin with a fellow passenger. This made it challenging to model spatial heterogeneity, while forming context-specific transmission events.
Another valuable source was the Cruise Network dataset and model, which provided actual proximity data collected via wearable sensors on cruise ships. It allowed us to consider real-world contact graphs and empirically informed parameters (e.g., lognormal incubation period, mask effectiveness at 50–80%). While this approach offered important insights, it lacked extensibility for tracking different disease states or simulating vaccine-induced partial immunity, making it difficult to conduct strategy testing beyond descriptive modeling.
Through these investigations, we eventually settled on SEIRS+ since it had the greatest compatibility with our objectives. SEIRS+ differs from the models above since it can allow for complex epidemic dynamics while allowing for individuals and offering built-in and customizable probabilities for transmission and interventions layered over the individual. It also allowed us to model the structured, close population of a cruise ship, while assessing interventions such as quarantining, staggered vaccinations, and behavior-based changes (masking, distancing). Finally, it could model tradeoffs, such as vaccination at aggregate scale and full vs. partial vaccination.
By exploring multiple modeling strategies before committing to a final platform, we were able to identify both the conceptual and technical requirements necessary for our cruise ship scenario and confidently adopt SEIRS+ to implement a high-fidelity simulation environment.



(https://github.com/maplerainresearch/covid19-sim-mesa). Though this Mesa-based simulation provides a useful starting point to understand the COVID-19 spread, we identified several limitations in depicting the cruise-specific scenarios. First, the environment is modeled as an undifferentiable grid resembling a generic urban space that underrepresents the varying exposure risks of distinct cruise ship areas such as dining rooms, outdoor areas, and cabins. 
We also evaluated the Infectious-Disease-Agent-Based-Modeling repository (https://github.com/kaionwong/infectious-disease-agent-based-modeling) that provides  Mesa-based agent-based model supporting multiple features like infection states (susceptible, four symptom severities, recovered with complications, dead), time-varying transmission/recovery/death probabilities, and a number of interventions (testing, vaccination, social distancing, finite hospital/ICU/ventilator capacity). However, this framework again had some limitations in reflecting the cruise ship scenarios. The contact structure is an unlabeled graph with uniform, distance-1 infection and this would treat all social connections equally, assuming there is the same chance of infecting regardless of context. For this reason, while this framework provides basic implementation ideas, we found the SEIRS+ framework line up more closely to serve our purposes. 
Lastly, we reviewed the Cruise Network study (https://github.com/rachaelpung/cruise_networks/tree/main?tab=readme-ov-file) which was developed using the real-world proximity data from cruise outbreaks. This study provided a more systematic insight into modeling parameters that we could integrate into our studies. In particular, modeling the incubation period with a lognormal distribution, infectivity with a Weibull function, exponential weight saturation function, and mask effectivity of 50-80 percent reduction well reflected real-world scenarios. However, the code is primarily focused on contact network structure and is less focused on disease state modeling, making it difficult to customize patient states such as asymptomatic and symptomatic patients.  
After reviewing multiple frameworks, we selected the SEIRS+ package. (https://github.com/ryansmcgee/seirsplus) In contrast with the models above, SEIRS+ offers an individual-level modeling using both network and compartment structures. The node-level metadata like categories for crew classification, cohort membership, and age demographics can be represented precisely for the simulated population which we can customize relative to our scenarios. The system allows for stochastic SEIR dynamics, asymptomatic transmission, variation in infectivity, testing regimes, quarantine policies, as well as other interventions. This feature makes it useful for simulating a wide range of policy settings, from a baseline setting to no-intervention settings and those with stringent preventive measures. The modular design and flexibility in defining transmission rates, disease progression, and interventions make SEIRS+ a more powerful and adaptable engine for simulating outbreak dynamics in complex, closed environments like cruise ships.

Describe the problem at hand thoroughly and past efforts by others to solve it.

Our project addresses the advanced pandemic flu spread challenge outlined in Project 14, implementing a large-scale agent-based simulation in a cruise ship environment. The core problem requires modeling disease transmission through a population of thousands of individuals while evaluating complex intervention strategies including vaccination, quarantine measures, and behavioral modifications.
The cruise ship scenario presents unique epidemiological challenges that make it ideal for this advanced simulation. Unlike the classroom model from Project 3, cruise ships feature confined spaces that accelerate transmission, limited medical resources that force difficult triage decisions, etc. These constraints create a natural laboratory for testing intervention strategies under resource scarcity. 
The resource allocation problem is particularly acute. Project 14 specifically asks, given limited vaccine supply, should we fully vaccinate half the population (providing ~95% to 50%) or give everyone a single dose (providing ~70% protection to 100%)? This isn’t just a mathematical optimization. The cruise ship setting amplifies these challenges. 

FIRST JULIO DESCRIBE SEIRS AND WHY WE CHOSE IT 


After investigating a variety of epidemic simulation frameworks, our team chose SEIRS+, a comprehensive and flexible Python package for simulating infectious disease spread in structured populations. SEIRS+ extends the classical SEIR compartmental model (Susceptible, Exposed, Infectious, Recovered) through individual-level customization, stochastic behavior, and interactions on networks. These features were helpful for our cruise ship scenario where several aspects, such as population structure, contact patterns, and intervention timing can have a substantial impact on disease transmission dynamics.
One of SEIRS+’s key advantages is its flexibility in representing networked populations. In a cruise ship setting, individuals do not interact randomly. Instead, passengers and crew have structured and repeated contacts: cabinmates, work cohorts, dining groups, and shared activities. SEIRS+ supports infection spread through a contact network, allowing us to encode these relationships explicitly. We can assign varying edge weights to model higher transmission likelihood in shared cabins versus brief hallway interactions.
The framework also supports stochastic simulation, meaning that each simulation run may differ due to the probabilistic nature of infection, recovery, and death events. This allowed us to test the range of outcomes under various intervention strategies. Additionally, SEIRS+ allows for specifying distributions for disease parameters like:
1.      Incubation and infection duration (e.g., lognormal, gamma)
2.      Symptomatic vs. asymptomatic infection ratios
3.      Variable infectivity and mortality rates
4.      Delayed onset of infectiousness (important for quarantine timing)
Importantly, intervention mechanisms can be flexibly defined. We implemented mask mandates (reducing transmission probability), quarantine policies (removing individuals from the contact network temporarily), and vaccination strategies. SEIRS+ even allows modeling partial vaccination by defining a new susceptible group with reduced transmission risk, which let us simulate tradeoffs between one-dose-for-all versus two-dose-for-some strategies.
Finally, SEIRS+ enables individual-level metadata tagging. We categorized nodes by role (passenger vs. crew), cabin assignment, age cohort, and vaccination status. This granularity allowed us to implement and test policies like vaccinating high-risk crew first or isolating specific sub-cohorts during an outbreak.
In summary, SEIRS+ was the ideal framework for simulating our cruise ship. Its realism in terms of networks, stochastic nature, extensibility, and ability to model the complexities of how policy interventions and disease dynamics interact provides insights into how best to allocate limited resources in a resource constrained and high-risk context.




• Develop and document your code. 


CLAIRE:  WRITEUP EVERYTHING DONE ALREADY WITH CODE (RE: VINCE, QUARANTINE + GRAPH NETWORKS) 

• Some infectious people enter a population of susceptibles, and some of the
susceptibles become infected.
• There is a short period of a couple of days before a newly-infected person in
turn becomes infectious.
• When a person recovers (or dies), the person is not again susceptible.
• Infectiousness or death can be mitigated by masking, social distancing, etc.

We developed a detailed SEIRS+ based network model to simulate a COVID-19 outbreak on a cruise ship. The parameters and environment settings reflect the real Diamond Princess cruise outbreak in 2020. The contact network consists of approximately 3000 nodes, representing people separated into passengers and crews with a ratio of about 2.5:1. The crews are further classified into passenger service and non-passenger service groups. Importantly, we strictly restricted non-passenger service groups from having contact with the passengers, simulating operational segregation aboard the ship. The edges in the network graph represent the contact weight between the nodes based on the cumulative contact duration. As mentioned in the background description section, we applied an exponential saturation function to allow longer contacts to increase transmission risk but asymptotically approach a maximum value of 1. The function we used is: weight = 1 - exp(-duration / total_duration)
We set  total_duration value to 180, so that any contact above 3 hours results in a maximum transmission weight of nearly 1. We accumulate the duration time for each node pairs and apply the weight function to compute final edge weights.

The above network graph shows the connection between 500 randomly selected individuals on the cruise. As described, the non-passenger-service is visibly isolated in the lower left corner of the graph, maintaining only internal interactions. Darker edges in the graph show the moderate to strong weights between the nodes. 


To accurately reflect the actual cruise environment, we referenced Diamond Princess deck plans to simulate dining cohorts, cabin arrangements, deck levels, and shared facilities. (“Diamond Princess deck plan”)
There are 9 dining areas on the ship, and we arbitrarily assigned 8-person dining groups. Each dining group spends a random uniform duration between 35 and 90 minutes. This time has been applied based on the national average dining spend of 67 minutes. (Hamrick)
Each pair of passengers is assigned a cabin. The cabinmates have the longest contact duration and therefore the highest edge weight. Crew members also have close contact with their own bunkmates, and cohorts. The passenger-service group may have some interaction with passengers.
The ship has 17 decks with random shuffles of passengers applied to each level of the decks. We added moderate interaction among the passengers on the same deck, a random uniform time between 10 and 240 minutes. 
Based on the deck plan, Diamond Princess Cruise includes multiple shared facilities such as a lounge, swimming pool, jacuzzi, and elevators. We simulate random passengers and crews sharing these facilities multiple times in a day.
To capture incidental contact between the people on the ship, we included brief transient contacts reflecting brief encounters as people walked past each other aboard the ship..

With the base network graph created, we developed a quarantine version of the network in our simulation. In the quarantine graph, edges are removed except for the cabinmates for both passengers and crews. This is to simulate how people are confined in their cabins during the quarantine. We kept some connection between the crew members as they would keep the ship running. 

Above is the quarantine network graph with random 500 nodes. We can see that there aren't any connections between the nodes. The outer circle will reflect passengers and crews confined in their cabins. Some people are in the center of the circle because their cabin mates are not included in the 500 nodes. Overall, the structure validates the logic of the quarantine model. 
	After creating the network graph, we applied SEIRS+ package to simulate different scenarios. The key parameters for constructing SEIRS model are (https://github.com/ryansmcgee/seirsplus/wiki/SEIRSModel-Class) : 
BETA - rate of transmission
SIGMA - rate of progression 
GAMMA - rate of recovery
MU_I - rate of infection related mortality    
G_quarantine - graph during quarantine
BETA_Q - rate of transmission for detected cases  
SIGMA_Q - rate of progression for detected cases  
GAMMA_Q - rate of recovery for detected cases            
theta_E - rate of testing for exposed individual
theta_I - rate of testing for infected individuals
We applied parameters based on actual statistical references. For example, we used a random lognormal function to represent incubation period of the disease, based on the study (Lauer, Stephen A. et al), with a mean of 1.63 and a standard deviation of 0.5. The inverse of the mean of the log-normal distribution corresponds to an average incubation period of approximately 5.2 days, which is used for our initial SIGMA value.
Through the structured approach, we have successfully constructed a cruise scenario graph that represents the complexity of COVID-19 transmission on a cruise ship. The SEIRS+ model enables us to test different interventions, vaccination actions which helps build insight into the effective protocols in a confined, high-contact environment. 
WILL CODING: DYING PPL, PARTIAL VACCINATION, FULL VACCINATION

• Show how to run your program(s).


Give illustrations of what you can learn from your code (e.g., whether a PRN generator is any good, or whether a certain strategy will work better than others in blackjack)

RESULTS: (VINCENT REVIEW CODE, DO WRITEUP OF WHAT STRATEGIES WORK BEST)



Conclusions 5 
What did you find/learn from the project? Provide ideas for future work that could be built
using your project as a starting point.



Works Cited
CGTN. “622 People Infected with COVID-19 on Ruby Princess Cruise Ship.” CGTN, 5 Apr. 2020, https://news.cgtn.com/news/2020-04-05/622-people-infected-with-COVID-19-on-Ruby-Princess-cruise-ship-Prq1OwbXXy/index.html. Accessed 15 July 2025.
“Diamond Princess Deck Plan.” CruiseMapper, https://www.cruisemapper.com/deckplans/Diamond-Princess-534#google_vignette. Accessed 21 July 2025.
Hamrick, Karen. “How Much Time Do Americans Spend Eating?” USDA, 22 Nov. 2011, https://www.usda.gov/about-usda/news/blog/how-much-time-do-americans-spend-eating. Accessed 21 July 2025.
Lauer, Stephen A., Kyra H. Grantz, Qifang Bi, et al. “The Incubation Period of Coronavirus Disease 2019 (COVID-19) from Publicly Reported Confirmed Cases: Estimation and Application.” Annals of Internal Medicine, vol. 172, no. 9, 2020, pp. 577–582, https://doi.org/10.7326/M20-0504.
Moriarty, Leah F., et al. “Public Health Responses to COVID-19 Outbreaks on Cruise Ships — Worldwide, February–March 2020.” Centers for Disease Control and Prevention, Morbidity and Mortality Weekly Report, vol. 69, no. 12, 27 Mar. 2020, https://www.cdc.gov/mmwr/volumes/69/wr/mm6912e3.htm. Accessed 21 July 2025.
Plucinski, Mateusz M., et al. “Coronavirus Disease 2019 (COVID-19) in Americans Aboard the Diamond Princess Cruise Ship.” Clinical Infectious Diseases, vol. 72, no. 10, 2021, pp. e448–e457, https://doi.org/10.1093/cid/ciaa1180.



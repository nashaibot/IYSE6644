
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

Cruise ship outbreak simulation provides a unique setting for high-risk disease transmission, due to factors such as limited intervention, confined spaces, and scheduled gatherings. The COVID-19 pandemic on the Diamond Princess Cruise ship serves as a background reference for our model as it experienced high infection concentration among 2666 passengers and 1045 crew members. Among 3711 Diamond Princess passengers, 712 tested positive. Out of the infected patients, 46.5% were asymptomatic and 9 out of 381 symptomatic people died.(https://www.cdc.gov/mmwr/volumes/69/wr/mm6912e3.htm)  A study on U.S passengers aboard showed that shared cabins for 2-4 people have a notable transmission rate among other layouts. In particular, the attack rate in cabins shared with symptomatic individuals was 81 percent while only 16 percent attack rate in single cabins or those without infected cabin mates. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7454359/). This suggests that the specific layout of a cruise ship is more susceptible to disease transmission and such dynamics compelled us to develop this simulation of a cruise ship outbreak.
Beyond the Diamond Princess Cruise ship, there are other confirmed COVID-19 outbreak cases on cruise ships. On Mar. 8, 2020 the Ruby Princess cruise departed Sydney for a 13-day voyage around New Zealand.The cruise was carrying 2,671 passengers and 1,146 crew members. At the time of the departure, COVID-19 had major outbreaks globally. Despite several passengers falling ill onboard, no quarantine took place, and the ship’s nearly 2,700 passengers disembarked the Ruby Princess to return home. After two weeks, authorities found 622 confirmed cases of COVID-19 and 10 deaths among the passengers and crew of the Ruby Princess. (https://news.cgtn.com/news/2020-04-05/622-people-infected-with-COVID-19-on-Ruby-Princess-cruise-ship-Prq1OwbXXy/index.html) Clearly, the confined, high-density nature of cruise ships with shared dining spaces, entertainment venues, and limited ventilation poses a high risk environment for the transmission of gastrointestinal and respiratory illnesses. 
Given the complex environment and situational constraints, we reviewed multiple open-source simulation codes and academic studies to better understand epidemic parameters, transmission patterns, and general epidemic dynamics. To better understand the general epidemic dynamics, our team explored numerous open-source frameworks and analyzed their use cases. In 2020, the Maple Rain Research Company used Python’s Mesa framework to create an agent-based simulation of how COVID-19 can spread. The model defines a dictionary of parameters, including grid size, infection probability, and recovery time, and then runs the simulation for a fixed number of ticks, or units of time. 

JULIO (WRITE A PARAGRAPH HERE INTRODUCING ALL THE APPROACHES WE TRIED) 
(https://github.com/maplerainresearch/covid19-sim-mesa). Though this Mesa-based simulation provides a useful starting point to understand the COVID-19 spread, we identified several limitations in depicting the cruise-specific scenarios. First, the environment is modeled as an undifferentiable grid resembling a generic urban space that underrepresents the varying exposure risks of distinct cruise ship areas such as dining rooms, outdoor areas, and cabins. 
We also evaluated the Infectious-Disease-Agent-Based-Modeling repository (https://github.com/kaionwong/infectious-disease-agent-based-modeling) that provides  Mesa-based agent-based model supporting multiple features like infection states (susceptible, four symptom severities, recovered with complications, dead), time-varying transmission/recovery/death probabilities, and a number of interventions (testing, vaccination, social distancing, finite hospital/ICU/ventilator capacity). However, this framework again had some limitations in reflecting the cruise ship scenarios. The contact structure is an unlabeled graph with uniform, distance-1 infection and this would treat all social connections equally, assuming there is the same chance of infecting regardless of context. For this reason, while this framework provides basic implementation ideas, we found the SEIRS+ framework line up more closely to serve our purposes. 
Lastly, we reviewed the Cruise Network study (https://github.com/rachaelpung/cruise_networks/tree/main?tab=readme-ov-file) which was developed using the real-world proximity data from cruise outbreaks. This study provided a more systematic insight into modeling parameters that we could integrate into our studies. In particular, modeling the incubation period with a lognormal distribution, infectivity with a Weibull function, exponential weight saturation function, and mask effectivity of 50-80 percent reduction well reflected real-world scenarios. However, the code is primarily focused on contact network structure and is less focused on disease state modeling, making it difficult to customize patient states such as asymptomatic and symptomatic patients.  
After reviewing multiple frameworks, we selected the SEIRS+ package. (https://github.com/ryansmcgee/seirsplus) In contrast with the models above, SEIRS+ offers an individual-level modeling using both network and compartment structures. The node-level metadata like categories for crew classification, cohort membership, and age demographics can be represented precisely for the simulated population which we can customize relative to our scenarios. The system allows for stochastic SEIR dynamics, asymptomatic transmission, variation in infectivity, testing regimes, quarantine policies, as well as other interventions. This feature makes it useful for simulating a wide range of policy settings, from a baseline setting to no-intervention settings and those with stringent preventive measures. The modular design and flexibility in defining transmission rates, disease progression, and interventions make SEIRS+ a more powerful and adaptable engine for simulating outbreak dynamics in complex, closed environments like cruise ships.

Describe the problem at hand thoroughly and past efforts by others to solve it.

Our project addresses the advanced pandemic flu spread challenge outlined in Project 14, implementing a large-scale agent-based simulation in a cruise ship environment. The core problem requires modeling disease transmission through a population of thousands of individuals while evaluating complex intervention strategies including vaccination, quarantine measures, and behavioral modifications.
The cruise ship scenario presents unique epidemiological challenges that make it ideal for this advanced simulation. Unlike the classroom model from Project 3, cruise ships feature confined spaces that accelerate transmission, limited medical resources that force difficult triage decisions, etc. These constraints create a natural laboratory for testing intervention strategies under resource scarcity. 
The resource allocation problem is particularly acute. Project 14 specifically asks, given limited vaccine supply, should we fully vaccinate half the population (providing ~95% to 50%) or give everyone a single dose (providing ~70% protection to 100%)? This isn’t just a mathematical optimization. The cruise ship setting amplifies these challenges. 

FIRST JULIO DESCRIBE SEIRS AND WHY WE CHOSE IT 

• Develop and document your code. 


CLAIRE:  WRITEUP EVERYTHING DONE ALREADY WITH CODE (RE: VINCE, QUARANTINE + GRAPH NETWORKS) 

• Some infectious people enter a population of susceptibles, and some of the
susceptibles become infected.
• There is a short period of a couple of days before a newly-infected person in
turn becomes infectious.
• When a person recovers (or dies), the person is not again susceptible.
• Infectiousness or death can be mitigated by masking, social distancing, etc.

WILL CODING: DYING PPL, PARTIAL VACCINATION, FULL VACCINATION

• Show how to run your program(s).


Give illustrations of what you can learn from your code (e.g., whether a PRN generator is any good, or whether a certain strategy will work better than others in blackjack)

RESULTS: (VINCENT REVIEW CODE, DO WRITEUP OF WHAT STRATEGIES WORK BEST)



Conclusions 5 
What did you find/learn from the project? Provide ideas for future work that could be built
using your project as a starting point.



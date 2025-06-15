# AI-Enhanced Epidemic Simulator

This is an interactive, browser-based agent simulation that models the spread of an epidemic through a population. It features customizable disease profiles, vaccination strategies, and a dynamic commentary system powered by a simulated Google AI to provide real-time and post-simulation analysis.

## Features

* **Customizable Scenarios:** Choose from a wide range of pre-configured virus profiles, including COVID-19, Measles, Ebola, and even a fictional super-virus, or create your own custom scenario.
* **Detailed Parameters:** Fine-tune the simulation by adjusting key epidemiological and vaccination variables:
    * **Disease:** R0, incubation period, infectious period, fatality rate, and long-term effect rate.
    * **Vaccine:** Efficacy, initial vaccination rate, daily vaccination rate, and rare adverse effects (mortality and long-term effects).
* **Agent-Based Simulation:** A visual canvas displays hundreds of individual agents, each with their own state (Susceptible, Infected, Recovered, Vaccinated, Deceased), providing a clear graphical representation of the outbreak.
* **Live Data Visualization:** A real-time dashboard tracks key metrics, including:
    * Effective Reproduction Number (R(t))
    * Total Sick Days
    * Counts and percentages for each population state.
    * A stacked line chart showing the historical progression of the epidemic.
* **Live AI Commentary:** A running log provides daily, AI-powered commentary on the state of the epidemic, noting key milestones like the outbreak's peak, the effectiveness of interventions, and the current growth rate.
* **In-Depth Final Analysis:** Once the simulation concludes, generate a detailed final report from the perspective of different AI-powered specialists:
    * **Epidemiologist:** Focuses on disease dynamics, R(t), and the impact of interventions.
    * **Economist:** Analyzes the financial impact, including lost productivity and vaccination costs.
    * **Public Health Official:** Provides a balanced view on the human cost and the effectiveness of public health measures.

## How to Use

1.  **Setup:**
    * Open the `index.html` file in your browser.
    * On the setup screen, use the dropdown to select a pre-configured virus profile.
    * Alternatively, adjust the parameters manually. Any change will automatically switch the profile to "Custom".
    * Click "Start Simulation" to begin.
2.  **Simulation:**
    * Observe the agents on the main canvas as the disease spreads.
    * Monitor the real-time statistics and the historical chart on the right-hand panel.
    * Follow the live AI commentary log to understand key events as they happen.
    * Click the "Return to Setup" button at any time to end the current simulation and start a new one.
3.  **Analysis:**
    * When the epidemic ends, the "Final Report" section will appear.
    * Select a specialist from the dropdown menu.
    * Click "Generate Report" to receive a detailed analysis based on the complete simulation data and the chosen specialist's perspective.

## Running the Simulator

This is a self-contained, single-file web application. No server or build process is required.

* Simply download the `index.html` file.
* Open it in a modern web browser like Chrome, Firefox, or Edge.
* Or access website https://ambiguouserror.github.io/epidemic/ and https://ambiguouserror.github.io/epidemic/ai_dashboard.html

## Technologies Used

* **HTML5**
* **CSS3** (with CSS Variables for easy theming)
* **Vanilla JavaScript (ES6+)**
* [**Chart.js**](https://www.chartjs.org/) for data visualization.

## Code Structure

The entire application logic is embedded within the `<script>` tag in the `index.html` file.

* **`App` Object:** A single global object that encapsulates the entire state and logic of the application to avoid polluting the global namespace.
    * `init()`: Caches DOM elements and sets up initial event listeners.
    * `startSimulation()`: Gathers parameters from the form and kicks off the simulation.
    * `gameLoop()`, `update()`, `render()`: The core functions that drive the simulation's state changes and visual updates every frame.
    * `getAIAssistedCommentary()`: Simulates a call to an AI to generate the live commentary.
    * `generateFinalReport()`: Simulates a call to an AI specialist to generate the end-of-simulation analysis.
* **`Agent` Class:** Defines the properties (state, position, etc.) and methods (movement, state updates) for each individual agent in the simulation.

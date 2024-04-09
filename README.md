## **Energy Transition Scenario Explorer**

### Overview:

The Energy Transition Scenario Explorer is a web-based tool designed to facilitate the selection and customization of energy transition scenarios. Users can choose from predefined scenarios or create custom scenarios by adjusting various levers that represent different aspects of the energy transition. The application provides visualizations and charts based on the selected scenarios, allowing users to analyze and compare different transition pathways.

### Key Features:

1. **Scenario Selection:**

   - Users can choose from a list of predefined energy transition scenarios or create custom scenarios.
   - Predefined scenarios offer a quick way to explore common transition pathways, while custom scenarios allow for more tailored analysis.

2. **Lever Settings:**

   - The application provides sliders for adjusting key levers that represent various aspects of the energy transition, such as transition year and technology adoption rates.
   - Users can customize these levers to create scenarios that reflect different policy interventions or technological advancements.

3. **Visualization:**

   - Based on the selected scenarios and lever settings, the application generates visualizations and charts to illustrate the projected outcomes of each scenario.
   - Visualizations help understand the implications of different transition pathways on energy consumption, emissions, and other relevant metrics.

4. **User Interaction:**
   - The application features an intuitive user interface with dropdowns, sliders, and input fields for easy scenario selection and customization.
   - Tooltips provide additional information and guidance to users, helping them make informed decisions when adjusting lever settings.

### Use Cases:

1. **Policy Planning:**

   - Policymakers can use the application to explore the potential impacts of different policy interventions on energy transition pathways.
   - By comparing various scenarios, policymakers can identify strategies that align with their goals for emissions reduction, renewable energy adoption, and economic growth.

2. **Research and Analysis:**

   - Researchers and analysts can leverage the application to study the effects of technological advancements and market trends on energy transition trajectories.
   - By creating custom scenarios and adjusting lever settings, researchers can simulate different future scenarios and evaluate their feasibility and implications.

3. **Education and Outreach:**
   - Educators and outreach professionals can use the application as a teaching tool to illustrate complex concepts related to energy transition and sustainability.
   - Interactive visualizations and scenario simulations engage learners and facilitate discussions on topics such as renewable energy integration, carbon pricing, and energy efficiency measures.

## **User Guide**

## Using the Sidebar for Energy Transition Scenario Selection

The sidebar allows users to set an energy transition scenario and generate charts based on their selections. Here's a step-by-step guide on how to use the sidebar:

1. **Scenario Selection:**

   - **Predefined Scenarios Dropdown:** This dropdown allows users to select predefined energy transition scenarios. Users can choose one or more scenarios from the list.
   - After selecting the scenario(s), the selected scenario(s) will be displayed below the dropdown.

2. **Custom Scenario Creation:**

   - **Scenario Name Field:** Users can enter a custom name for their scenario in this text field.
   - **Create & Display Button:** Clicking this button will create and display the custom scenario based on the selected lever values and scenario name.

3. **Lever Settings:**

   - The sidebar provides sliders for adjusting different levers that represent various aspects of the energy transition scenario. These levers include:
     - **Net-zero Slider:** Adjusting the transition year to Net Zero (NZ), which represents the target year for achieving zero emissions.
     - **Heat Pump Slider:** Adjusting the lever related to the rollout of domestic heat pumps.
     - **District Heating Slider:** Adjusting the rollout of district heating networks.
     - **Hydrogen Slider:** Adjusting the potential use of hydrogen for heating.
     - **Local Pledges Slider:** Adjusting what extent local authorities net-zero pledges are achieved.
   - Users can adjust these sliders to customize their scenario according to their preferences.

4. **Popovers for Levers:**

   - Users can hover over the question mark icon next to each lever to view tooltips that provide additional information about the lever settings.

5. **Scenario Display:**
   - After selecting or creating a scenario and adjusting the lever settings, users can generate charts or visualizations based on their scenario selections.

## **Developer Guide**

### The following classes are reusable components

### `Chart` Class

The `Chart` class serves as a utility for creating different types of charts commonly used in data visualization tasks. It contains several static methods, each tailored for specific chart types and data formats.

### Static Methods

`LongFormBarchart`

This method generates a bar chart using long-form data, which is typically stored in a CSV file. It allows for easy comparison of data across different categories.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `path`: Path to the CSV file containing the data.
  - `x`: Column name for the x-axis.
  - `y`: Column name for the y-axis.
  - `category`: Column name for the category (used for color differentiation).
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `scenario` (optional): Filter for specific scenarios in the data.
  - `sex` (optional): Sex label for the legend.
  - `title` (optional): Title of the chart.

`ScenCompInvBarchart`

This method generates a bar chart for comparing scenarios, focusing on investment-related data. It aggregates and visualizes investment data across different scenarios.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `df_inv`: DataFrame containing investment data.
  - `naming`: Dictionary for renaming data categories.
  - `title` (optional): Title of the chart.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `z_label` (optional): Label for the z-axis.
  - `scenarios` (optional): List of scenarios to include in the comparison.
  - `lads` (optional): List of local areas or regions.

`ScenCompCostBarchart`

This method generates a bar chart for comparing scenarios based on costs. It visualizes cost-related data across different scenarios and years.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `df_cost`: DataFrame containing cost data.
  - `year`: Year of interest for cost comparison.
  - `scenarios`: List of scenarios to include in the comparison.
  - `naming`: Dictionary for renaming data categories.
  - `title` (optional): Title of the chart.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `z_label` (optional): Label for the z-axis.

`ScenCompGenBarchart`

This method generates a bar chart for comparing scenarios based on energy generation. It visualizes energy generation data across different scenarios.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `df_gen`: DataFrame containing energy generation data.
  - `df_cost`: DataFrame containing cost data.
  - `year`: Year of interest for cost comparison.
  - `naming`: Dictionary for renaming data categories.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `scenarios` (optional): List of scenarios to include in the comparison.
  - `colormap` (optional): Color map for distinguishing different technologies.
  - `title` (optional): Title of the chart.

`ScenLocalCompGenBarchart`

This method generates a bar chart for comparing energy generation within local areas or regions. It allows for comparison of energy generation data specific to certain regions.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `df_gen`: DataFrame containing energy generation data.
  - `lads`: List of local areas or regions.
  - `year`: Year of interest for cost comparison.
  - `naming`: Dictionary for renaming data categories.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `scenarios` (optional): List of scenarios to include in the comparison.
  - `colormap` (optional): Color map for distinguishing different technologies.
  - `title` (optional): Title of the chart.

`GenericLinechart`

This method generates a generic line chart, which can be customized to plot various types of data over time or other continuous variables.

- **Parameters:**
  - `id`: ID of the HTML element where the chart will be rendered.
  - `df`: DataFrame containing the data.
  - `x`: Column name for the x-axis.
  - `y`: Column name for the y-axis.
  - `category`: Column name for the category (used for color differentiation).
  - `naming` (optional): Dictionary for renaming data categories.
  - `title` (optional): Title of the chart.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.
  - `l_label` (optional): Label for the legend.
  - `y_range` (optional): Range for the y-axis.
  - `scenarios` (optional): List of scenarios to include in the comparison.
  - `lads` (optional): List of local areas or regions.

### `Map` Class

The `Map` class serves as a utility for creating different types of maps commonly used in geographic data visualization tasks. It contains several static methods, each tailored for specific map types and data formats.

### Static Methods

`GenericHexmap`

This method generates a hexagonal map visualization using data from a DataFrame. It allows for comparison of values across different scenarios and technologies.

- **Parameters:**
  - `id`: ID of the HTML element where the map will be rendered.
  - `df`: DataFrame containing the data.
  - `scenarios`: List of scenarios to include in the comparison.
  - `techs` (optional): List of technologies to include in the comparison.
  - `year` (optional): Year of interest for the comparison.
  - `title` (optional): Title of the map.
  - `zlabel` (optional): Label for the z-axis.
  - `naming` (optional): Dictionary for renaming data categories.
  - `range_color` (optional): Range for the color scale.
  - `figonly` (optional): Flag to return only the Plotly figure.
  - `textangle` (optional): Angle for the text displayed on the map.

`LongFormHexmap`

This method generates a hexagonal map visualization using long-form data from a CSV file. It allows for easy visualization of data across different regions.

- **Parameters:**
  - `id`: ID of the HTML element where the map will be rendered.
  - `path`: Path to the CSV file containing the data.
  - `zlabel`: Label for the z-axis.
  - `title` (optional): Title of the map.
  - `scenario` (optional): Scenario to visualize.
  - `sex` (optional): Sex label for the legend.
  - `x_label` (optional): Label for the x-axis.
  - `y_label` (optional): Label for the y-axis.

### `FigureGrid` Class

The `FigureGrid` class facilitates the creation of a grid layout containing multiple figures. It offers a static method `create` for generating the grid layout based on the specified figures and layout configuration.

### Static Method

`create`

This method generates a grid layout of figures based on the provided list of figures and the desired number of columns per row.

- **Parameters:**
  - `figures`: A list of dictionaries, each containing information about a figure to be included in the grid layout. Each dictionary should have the following keys:
    - `title`: Title of the figure.
    - `popover`: Dictionary containing information about the popover tooltip associated with the figure. It should have the following keys:
      - `id`: ID of the popover.
      - `tooltip`: Text for the tooltip.
      - `className`: CSS class for styling the popover.
    - `facet`: Facet for the figure, if applicable.
    - `graph`: Graph component (e.g., `dcc.Graph`) representing the figure.
  - `columns_per_row`: A string specifying the number of columns per row in the grid layout.

### `Filter` Class

The `Filter` class provides static methods for generating various filter components such as dropdowns and sliders.

### Static Methods

`Dropdown`

This method creates a dropdown filter component with customizable options.

- **Parameters:**
  - `options`: A list of dictionaries, where each dictionary contains the label and value for a dropdown option.
  - `id`: ID of the dropdown component.
  - `default_option`: Default selected option for the dropdown (optional).
  - `clearable`: Boolean indicating whether the dropdown allows clearing the selection (default is `False`).
  - `className`: CSS class for styling the dropdown component (optional).
  - `multiple`: Boolean indicating whether the dropdown allows multiple selections (default is `False`).
  - `placeholder`: Placeholder text displayed when no option is selected (optional).
  - `option_style`: CSS styles applied to the dropdown options (default styles provided).

`YearSlider`

This method creates a slider filter component specifically for selecting years.

- **Parameters:**
  - `min`: Minimum value of the slider (start year).
  - `max`: Maximum value of the slider (end year).
  - `step`: Interval between slider values.
  - `id`: ID of the slider component.
  - `default_value`: Default selected value for the slider (optional).
  - `tooltip`: Tooltip text displayed when hovering over the slider (optional).
  - `className`: CSS class for styling the slider component (optional).

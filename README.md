# **INTRODUCTION**

# Chart Class and Static Methods

This markdown file provides a detailed overview of the `Chart` class and its static methods, which are used for generating various types of charts using Plotly and Dash components.

## `Chart` Class

The `Chart` class serves as a utility for creating different types of charts commonly used in data visualization tasks. It contains several static methods, each tailored for specific chart types and data formats.

## Static Methods

### `LongFormBarchart`

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

### `ScenCompInvBarchart`

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

### `ScenCompCostBarchart`

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

### `ScenCompGenBarchart`

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

### `ScenLocalCompGenBarchart`

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

### `GenericLinechart`

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

# Map Class and Static Methods

This markdown file provides a detailed overview of the `Map` class and its static methods, which are used for generating various types of maps using Plotly and Dash components.

## `Map` Class

The `Map` class serves as a utility for creating different types of maps commonly used in geographic data visualization tasks. It contains several static methods, each tailored for specific map types and data formats.

## Static Methods

### `GenericHexmap`

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

### `LongFormHexmap`

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

# FigureGrid Class and Static Method

This markdown file provides a detailed overview of the `FigureGrid` class and its static method, which is used for creating a grid layout of figures using Dash Bootstrap Components.

## `FigureGrid` Class

The `FigureGrid` class facilitates the creation of a grid layout containing multiple figures. It offers a static method `create` for generating the grid layout based on the specified figures and layout configuration.

## Static Method

### `create`

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

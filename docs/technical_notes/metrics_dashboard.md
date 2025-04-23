# Metrics Dashboard for InfoFlow Social Media Simulation

## Overview

The InfoFlow Metrics Dashboard provides a comprehensive set of visualizations and analytics to help users understand the dynamics of information flow in social media networks. It extends the basic simulation capabilities with advanced metrics, distributions, correlations, and interactive visualizations.

## Features

The dashboard offers several key features:

### 1. Summary Statistics

- At-a-glance metrics for the current simulation state
- Average truth assessment across the network
- Trust levels for different social media account types
- Polarization index to measure opinion division

### 2. Truth Assessment Analytics

- **Distribution Visualization**: Shows how truth assessments are distributed across users
- **Evolution Tracking**: Charts the change in average truth assessment over time
- **Polarization Metrics**: Measures how opinions diverge into separate clusters
- **Opinion Cluster Tracking**: Identifies distinct belief groups that form during simulation

### 3. Trust Dynamics Analysis

- **Trust Level Trends**: Shows how trust in different sources evolves over time
- **Trust Distributions**: Visualizes the spread of trust levels across the user population
- **Comparative Analysis**: Allows comparison of trust in corporate, influencer, and government accounts

### 4. User Parameter Distributions

- Visualization of cognitive parameter distributions:
  - Confirmation bias
  - Critical thinking
  - Social conformity
  - Truth seeking

### 5. Correlation Analysis

- **Parameter Impact Charts**: Shows relationships between parameters and truth assessment
- **Statistical Correlations**: Measures how strongly different parameters affect outcomes
- **Regression Analysis**: Identifies predictive relationships between variables

### 6. Network Visualization

- **Network Structure Visualization**: Displays the social network topology
- **Truth Assessment Mapping**: Colors nodes (users) by their truth assessment values
- **Content Flow Visualization**: Shows how information propagates through the network

## Implementation Details

The dashboard is implemented using:

1. **Backend Components**:
   - Enhanced data collectors that track additional metrics
   - Comprehensive visualization module with specialized chart types
   - Metric calculation functions for advanced analytics

2. **Frontend Components**:
   - Interactive web dashboard with tabbed navigation
   - Bootstrap-based responsive interface
   - Chart.js for interactive visualization
   - Dashboard organization by metric category

## Educational Value

The metrics dashboard significantly enhances the educational value of the InfoFlow simulation by:

1. Making abstract information flow dynamics visually concrete
2. Enabling users to see how parameters affect outcomes
3. Providing insights into network effects on belief formation
4. Visualizing polarization and opinion clustering that emerges from interactions
5. Allowing comparison between different social media account types and their influence

## How to Access

The dashboard can be accessed in two ways:

1. **Live Dashboard**: Available at `/metrics-dashboard` or `/metrics-dashboard/<run_id>` for specific simulation runs
2. **Exported Dashboard**: Included in interactive HTML exports for offline viewing and sharing

## Future Enhancements

Planned enhancements for the dashboard include:

1. **Real-time Updates**: Live updating of metrics during simulation runs
2. **Custom Chart Builder**: Allow users to create custom visualization combinations
3. **Comparative View**: Side-by-side comparison of multiple simulation runs
4. **Advanced Filtering**: Filter users by parameter values for targeted analysis
5. **Parameter Sensitivity Analysis**: Show how changes in parameters affect outcomes

This dashboard is a powerful tool for educational purposes, providing deep insights into how information flows through social media networks and how people form beliefs based on social media content.
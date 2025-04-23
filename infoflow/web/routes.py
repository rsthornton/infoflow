"""Routes for the InfoFlow web interface."""

import json
import math
import time
from flask import Blueprint, jsonify, render_template, request, make_response

from infoflow.core.model import create_model
from infoflow.utils.simple_stats import StatsCollector
from infoflow.utils.scenarios import list_scenarios, get_scenario

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@bp.route("/simulation")
def simulation():
    """Render the simulation page."""
    return render_template("simulation.html")


@bp.route("/simulations")
def simulations():
    """Render the simulation history page."""
    return render_template("simulations.html")


@bp.route("/guided-scenarios")
def guided_scenarios():
    """Render the guided scenarios page."""
    # Temporarily disabled
    return render_template("error.html", message="Guided scenarios are temporarily unavailable.")
    # Uncomment to re-enable:
    # scenarios = list_scenarios()
    # return render_template("guided_scenarios.html", scenarios=scenarios)


@bp.route("/guided-scenarios/<scenario_id>")
def view_scenario(scenario_id):
    """Render a specific guided scenario page."""
    # Temporarily disabled
    return render_template("error.html", message="Guided scenarios are temporarily unavailable.")
    # Uncomment to re-enable:
    # scenario = get_scenario(scenario_id)
    # if not scenario:
    #     return render_template("error.html", message=f"Scenario '{scenario_id}' not found")
    # 
    # return render_template("scenario_detail.html", scenario=scenario)


@bp.route("/research-scenarios")
def research_scenarios():
    """Render the research scenarios page."""
    # Get the three research-focused scenarios
    research_scenario_ids = ["trust_study", "network_connectivity", "belief_resistance"]
    scenarios = []
    
    for scenario_id in research_scenario_ids:
        scenario = get_scenario(scenario_id)
        if scenario:
            scenarios.append(scenario)
    
    return render_template("research_scenarios.html", scenarios=scenarios)


@bp.route("/research-scenarios/<scenario_id>/variation")
def research_variation(scenario_id):
    """Render the research parameter variation page for a specific scenario."""
    # Only allow specific research scenarios
    if scenario_id not in ["trust_study", "network_connectivity", "belief_resistance"]:
        return render_template("error.html", message="Invalid research scenario")
        
    # Get the scenario
    scenario = get_scenario(scenario_id)
    if not scenario:
        return render_template("error.html", message="Scenario not found")
    
    # Add the research question to the scenario data
    if scenario_id == "trust_study":
        scenario["research_question"] = "What is the relationship between institutional trust and a healthy social media information ecosystem?"
    elif scenario_id == "network_connectivity":
        scenario["research_question"] = "How does the amount, and the types of connectivity in social media networks influence how information spreads?"
    elif scenario_id == "belief_resistance":
        scenario["research_question"] = "How does resistance to update one's beliefs affect information trust evaluation?"
    
    return render_template("research_variation.html", scenario=scenario)


@bp.route("/metrics-dashboard")
@bp.route("/metrics-dashboard/<run_id>")
def metrics_dashboard(run_id=None):
    """Render the metrics dashboard page."""
    # Use simple results page for research scenarios
    data = {}
    params = {}
    
    if run_id:
        # Get data for the specified run
        data = StatsCollector.get_run_data(run_id)
        
        if not data:
            # Return error if run not found
            return render_template("error.html", message="Simulation run not found")
            
        # Extract parameters if available
        if "parameters" in data:
            params = data["parameters"]
            
            # Add run_id as scenario_id for template use
            params["scenario_id"] = run_id
    
    # Get metrics for the final step if available
    final_metrics = {}
    if "metrics" in data and data["metrics"]:
        # Find the highest step number (final step)
        steps = [int(step) for step in data["metrics"].keys()]
        if steps:
            final_step = str(max(steps))
            final_metrics = data["metrics"].get(final_step, {})
    
    # Render the basic results template with simplified data
    return render_template("basic_results.html", 
                          run_id=run_id,
                          avg_truth_assessment=final_metrics.get("avg_truth_assessment", 0.58),
                          trust_corp=final_metrics.get("avg_trust_corporate", 6.2),
                          trust_inf=final_metrics.get("avg_trust_influencer", 5.8),
                          trust_gov=final_metrics.get("avg_trust_government", 4.7),
                          polarization=final_metrics.get("polarization_index", 0.12),
                          params=params)
    
    # Full dashboard is disabled for now:
    """
    try:
        import os
        import numpy as np
        # Force matplotlib to use a non-interactive backend
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend to prevent window creation
        import matplotlib.pyplot as plt
        from infoflow.data.visualization import (
            plot_truth_assessment_distribution,
            plot_trust_levels,
            plot_truth_assessment_evolution,
            plot_trust_distribution,
            plot_cognitive_parameter_distribution,
            plot_polarization_over_time,
            plot_opinion_clusters_over_time,
            plot_parameter_vs_truth_assessment
        )
    except Exception as e:
        print(f"Error importing required modules: {e}")
        return render_template("error.html", message=f"Failed to initialize visualization system: {str(e)}")
    """
    
    data = {}
    charts_generated = False
    has_simulations = False
    recent_simulations = []
    
    # Check if there are any available simulations
    try:
        # Get up to 10 recent simulations to show in the dropdown
        recent_simulations = StatsCollector.get_recent_runs(limit=10)
        has_simulations = len(recent_simulations) > 0
        
        # If we're viewing a specific run, make sure it's included in the list
        # even if it's not one of the most recent runs
        if run_id and has_simulations:
            # Check if the run_id is already in recent_simulations
            run_in_list = any(sim['id'] == run_id for sim in recent_simulations)
            
            # If not, try to get this specific run's data and add it to the list
            if not run_in_list:
                run_data = StatsCollector.get_run_metadata(run_id)
                if run_data:
                    recent_simulations.append(run_data)
    except Exception as e:
        print(f"Error checking for simulations: {e}")
    
    if run_id:
        # Get data for the specified run
        data = StatsCollector.get_run_data(run_id)
        
        if not data:
            # Return error if run not found
            return render_template("error.html", message="Simulation run not found")
    
    # Define the directory to save charts
    try:
        # Get the absolute path to the web module directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define static/charts directory path from the web module
        static_dir = os.path.join(current_dir, "static", "charts")
        
        # Ensure the directory exists
        os.makedirs(static_dir, exist_ok=True)
        print(f"Using charts directory: {static_dir}")
    except Exception as e:
        print(f"Error creating charts directory: {e}")
        # Fallback to a directory we know should be writable
        static_dir = os.path.join(os.getcwd(), "charts")
        try:
            os.makedirs(static_dir, exist_ok=True)
            print(f"Using fallback charts directory: {static_dir}")
        except Exception as e2:
            print(f"Error creating fallback charts directory: {e2}")
            # Last resort - use a temp directory
            import tempfile
            static_dir = tempfile.mkdtemp(prefix="infoflow_charts_")
            print(f"Using temporary charts directory: {static_dir}")
    
    # If we don't have data, generate placeholder charts
    try:
        if not run_id or not data:
            # Generate sample data for placeholder charts
            np.random.seed(42)  # For reproducibility
            
            # Sample truth assessments (0-1 scale)
            truth_assessments = np.random.beta(5, 3, 100)
            
            # Sample trust levels (0-10 scale)
            trust_corp = np.random.normal(6.2, 1.5, 100).clip(0, 10)
            trust_inf = np.random.normal(5.8, 1.8, 100).clip(0, 10)
            trust_gov = np.random.normal(4.7, 2.0, 100).clip(0, 10)
            
            # Sample cognitive parameters
            confirmation_bias = np.random.normal(5.5, 1.5, 100).clip(0, 10)
            critical_thinking = np.random.normal(4.8, 1.7, 100).clip(0, 10)
            social_conformity = np.random.normal(6.2, 1.6, 100).clip(0, 10)
            truth_seeking = np.random.normal(0.5, 2.5, 100).clip(-5, 5)
            
            # Sample time series data (50 steps)
            steps = 50
            time_steps = np.arange(steps)
            mean_truth_assessment = 0.5 + 0.25 * (1 - np.exp(-time_steps/20))
            truth_variance = 0.2 * np.exp(-time_steps/30)
            
            trust_corp_time = 5.0 + np.cumsum(0.1 * np.random.normal(0, 1, steps))
            trust_inf_time = 5.0 + np.cumsum(0.15 * np.random.normal(0, 1, steps))
            trust_gov_time = 5.0 + np.cumsum(-0.05 * np.random.normal(0, 1, steps))
            
            # Clamp values to valid ranges
            trust_corp_time = np.clip(trust_corp_time, 0, 10)
            trust_inf_time = np.clip(trust_inf_time, 0, 10)
            trust_gov_time = np.clip(trust_gov_time, 0, 10)
            
            # Generate polarization and opinion clusters
            polarization = 0.05 + 0.15 * (1 - np.exp(-time_steps/15))
            opinion_clusters = np.round(1 + time_steps/10).clip(1, 5)
            
            # Prepare complete sample data for the dashboard
            sample_data = {
                "current_truth_assessments": truth_assessments,
                "mean_truth_assessment": mean_truth_assessment.tolist(),
                "truth_assessment_variance": truth_variance.tolist(),
                "trust_in_CorporateMediaAgent": trust_corp_time.tolist(),
                "trust_in_InfluencerAgent": trust_inf_time.tolist(),
                "trust_in_GovernmentMediaAgent": trust_gov_time.tolist(),
                "current_trust_in_CorporateMediaAgent": trust_corp,
                "current_trust_in_InfluencerAgent": trust_inf,
                "current_trust_in_GovernmentMediaAgent": trust_gov,
                "current_confirmation_bias": confirmation_bias,
                "current_critical_thinking": critical_thinking,
                "current_social_conformity": social_conformity,
                "current_truth_seeking": truth_seeking,
                "polarization_over_time": polarization.tolist(),
                "opinion_clusters_over_time": opinion_clusters.tolist(),
                "polarization_index": polarization[-1],
            }
            
            # Generate all charts using the comprehensive dashboard function
            from infoflow.data.visualization import create_complete_metrics_dashboard
            charts = create_complete_metrics_dashboard(sample_data)
            
            # Save all charts to the static directory
            for chart_name, fig in charts.items():
                try:
                    chart_path = os.path.join(static_dir, f"{chart_name}.png")
                    fig.savefig(chart_path, dpi=100, bbox_inches="tight")
                    plt.close(fig)
                except Exception as e:
                    print(f"Error saving chart {chart_name}: {e}")
            
            # Set data for the template
            data = {
                "mean_truth_assessment": mean_truth_assessment[-1],
                "trust_in_CorporateMediaAgent": trust_corp_time[-1],
                "trust_in_InfluencerAgent": trust_inf_time[-1],
                "trust_in_GovernmentMediaAgent": trust_gov_time[-1],
                "polarization_index": polarization[-1]
            }
            
            charts_generated = True
        elif not os.path.exists(os.path.join(static_dir, "truth_distribution.png")):
            # Generate charts from actual data if they don't exist
            from infoflow.data.visualization import create_complete_metrics_dashboard
            
            # Generate charts using the enhanced visualization module
            charts = create_complete_metrics_dashboard(data)
            
            # Save all charts to the static directory
            for chart_name, fig in charts.items():
                try:
                    chart_path = os.path.join(static_dir, f"{chart_name}.png")
                    fig.savefig(chart_path, dpi=100, bbox_inches="tight")
                    plt.close(fig)
                except Exception as e:
                    print(f"Error saving chart {chart_name}: {e}")
                
            charts_generated = True
    except Exception as e:
        print(f"Error generating charts: {e}")
        # Create a simple error chart
        fig = plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, f"Error generating charts: {str(e)}", 
                horizontalalignment='center',
                verticalalignment='center',
                transform=plt.gca().transAxes)
        plt.title("Dashboard Error")
        error_path = os.path.join(static_dir, "error.png")
        fig.savefig(error_path, dpi=100, bbox_inches="tight")
        plt.close(fig)
        
        # Set minimal data
        data = {
            "mean_truth_assessment": 0.58,
            "trust_in_CorporateMediaAgent": 6.2,
            "trust_in_InfluencerAgent": 5.8, 
            "trust_in_GovernmentMediaAgent": 4.7,
            "polarization_index": 0.12
        }
        charts_generated = True
    
    # Create a list of all chart files that should exist
    expected_charts = [
        "truth_distribution.png", "truth_evolution.png", "polarization.png", "opinion_clusters.png",
        "trust_evolution.png", "trust_dist_CorporateMediaAgent.png", "trust_dist_InfluencerAgent.png", 
        "trust_dist_GovernmentMediaAgent.png", "confirmation_bias_dist.png", "critical_thinking_dist.png",
        "social_conformity_dist.png", "truth_seeking_dist.png", "network_truth.png",
        "confirmation_bias_vs_truth.png", "critical_thinking_vs_truth.png",
        "social_conformity_vs_truth.png", "truth_seeking_vs_truth.png",
        "content_sources.png", "content_spread.png"
    ]
    
    # Verify which charts actually exist
    existing_charts = {}
    for chart in expected_charts:
        chart_path = os.path.join(static_dir, chart)
        existing_charts[chart] = os.path.exists(chart_path)
    
    # Generate a placeholder image for any missing charts
    for chart in expected_charts:
        if not existing_charts[chart]:
            try:
                print(f"Creating placeholder for missing chart: {chart}")
                chart_path = os.path.join(static_dir, chart)
                
                # Create a simple placeholder image
                fig = plt.figure(figsize=(10, 5))
                plt.text(0.5, 0.5, "Chart data not available", 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=plt.gca().transAxes,
                        fontsize=14)
                
                # Add a hint based on chart type
                if "trust" in chart.lower():
                    plt.text(0.5, 0.4, "Trust data may not have been collected in this simulation run",
                            horizontalalignment='center', verticalalignment='center',
                            transform=plt.gca().transAxes, fontsize=10)
                elif "truth" in chart.lower():
                    plt.text(0.5, 0.4, "Truth assessment data may not have been collected",
                            horizontalalignment='center', verticalalignment='center',
                            transform=plt.gca().transAxes, fontsize=10)
                
                plt.title(chart.replace(".png", "").replace("_", " ").title())
                plt.axis('off')
                fig.savefig(chart_path, dpi=100, bbox_inches="tight")
                plt.close(fig)
            except Exception as e:
                print(f"Error creating placeholder for {chart}: {e}")
    
    # Pass simulation data to the template
    return render_template("metrics_dashboard.html", 
                          run_id=run_id,
                          charts_generated=charts_generated,
                          avg_truth_assessment=data.get("mean_truth_assessment", 0.58),
                          trust_corp=data.get("trust_in_CorporateMediaAgent", 6.2),
                          trust_inf=data.get("trust_in_InfluencerAgent", 5.8),
                          trust_gov=data.get("trust_in_GovernmentMediaAgent", 4.7),
                          polarization=data.get("polarization_index", 0.12),
                          has_simulations=has_simulations,
                          recent_simulations=recent_simulations)


@bp.route("/api/run-simulation", methods=["POST"])
def run_simulation():
    """Run a simulation with the provided parameters."""
    params = request.json

    # Generate a run ID
    current_time = int(time.time())
    run_id = f"run_{current_time}"
    
    # Create a new stats collector with our specific run_id
    # This prevents duplicate simulations by avoiding the automatic UUID generation
    collector = StatsCollector(run_id=run_id)
    
    # Record the start of the run with parameters, forcing our specific run_id
    collector.start_run(params, force_id=True)

    # Get simulation name if provided and set it
    simulation_name = params.get("simulationName")
    if simulation_name:
        collector.name_run(simulation_name)
    else:
        # If no name is provided, use a timestamped default name
        # This helps prevent the appearance of "unnamed" simulations
        default_name = f"Simulation_{current_time}"
        collector.name_run(default_name)
    
    # Create and run model with all parameters
    model = create_model(
        # Basic parameters
        num_citizens=params.get("num_citizens", 100),
        num_corporate_media=params.get("num_corporate_media", 3),
        num_influencers=params.get("num_influencers", 5),
        num_government=params.get("num_government", 1),
        network_type=params.get("network_type", "small_world"),
        # Citizen parameters
        truth_seeking_mean=params.get("truth_seeking_mean", 1.0),
        truth_seeking_std=params.get("truth_seeking_std", 2.0),
        confirmation_bias_min=params.get("confirmation_bias_min", 4),
        confirmation_bias_max=params.get("confirmation_bias_max", 7),
        critical_thinking_min=params.get("critical_thinking_min", 4),
        critical_thinking_max=params.get("critical_thinking_max", 7),
        social_conformity_min=params.get("social_conformity_min", 4),
        social_conformity_max=params.get("social_conformity_max", 7),
        initial_trust_in_corporate=params.get("initial_trust_in_corporate", 5.0),
        initial_trust_in_influencers=params.get("initial_trust_in_influencers", 5.0),
        initial_trust_in_government=params.get("initial_trust_in_government", 5.0),
        # Media parameters
        corporate_bias_min=params.get("corporate_bias_min", -3),
        corporate_bias_max=params.get("corporate_bias_max", 3),
        influencer_bias_min=params.get("influencer_bias_min", -4),
        influencer_bias_max=params.get("influencer_bias_max", 4),
        government_bias=params.get("government_bias", 1.0),
        truth_commitment_corporate=params.get("truth_commitment_corporate", 6.0),
        truth_commitment_influencer=params.get("truth_commitment_influencer", 4.0),
        truth_commitment_government=params.get("truth_commitment_government", 5.0),
        # Media Reach Parameters - publication rates are fixed at 1.0 in the model
        corporate_influence_reach=params.get("corporate_influence_reach", 0.7),
        influencer_influence_reach=params.get("influencer_influence_reach", 0.6),
        government_influence_reach=params.get("government_influence_reach", 0.7),
        # Network parameters
        small_world_k=params.get("small_world_k", 4),
        small_world_p=params.get("small_world_p", 0.1),
        scale_free_m=params.get("scale_free_m", 3),
        random_p=params.get("random_p", 0.1),
    )

    # Run for specified steps
    steps = params.get("steps", 10)
    for step in range(steps):
        model.step()
        
        # Collect metrics at each step
        metrics = {
            "avg_trust_government": model.datacollector.model_vars["Trust in Government"][-1],
            "avg_trust_corporate": model.datacollector.model_vars["Trust in Corporate Media"][-1],
            "avg_trust_influencer": model.datacollector.model_vars["Trust in Influencers"][-1],
            "avg_truth_assessment": model.datacollector.model_vars["Average Truth Assessment"][-1],
        }
        
        # Add variance metrics if available
        if "Trust Variance - Government" in model.datacollector.model_vars:
            metrics["trust_var_government"] = model.datacollector.model_vars["Trust Variance - Government"][-1]
            metrics["trust_var_corporate"] = model.datacollector.model_vars["Trust Variance - Corporate"][-1]
            metrics["trust_var_influencer"] = model.datacollector.model_vars["Trust Variance - Influencers"][-1]
            
        collector.record_step(step, metrics)

    # Get data from model
    data = model.datacollector.get_model_vars_dataframe().to_dict("records")

    # Transform data to use truth_assessment terminology
    for record in data:
        if "Average Belief" in record:
            record["Average Truth Assessment"] = record.pop("Average Belief")
        if "Belief Variance" in record:
            record["Truth Assessment Variance"] = record.pop("Belief Variance")
    
    # Get agent tracking data if available
    agent_data = {}
    if hasattr(model, 'agent_snapshots'):
        agent_data = model.agent_snapshots
        
    # Get network structure for visualization
    network_data = get_network_data(model)
    
    # Get content flow data if available
    content_flow_data = []
    if hasattr(model, "content_tracker"):
        print(f"Found content_tracker with {len(model.content_tracker)} items")
        for content_id, content in model.content_tracker.items():
            # Only include content that has spread beyond the origin
            spread_path = content.get("spread_path", [])
            if len(spread_path) > 1:
                # Extract key information for visualization
                flow_data = {
                    "content_id": content_id,
                    "accuracy": content.get("accuracy", 0.5),
                    "created_step": content.get("created_step", 0),
                    "origin_id": content.get("origin_id", "unknown"),
                    "source_type": content.get("source_type", "Unknown"),
                    "spread_path": spread_path,
                    "last_shared_step": content.get("last_shared_step", 0)
                }
                
                # Add seed nodes information if available
                try:
                    if hasattr(model, "content_seed_nodes") and content_id in model.content_seed_nodes:
                        # Convert all node IDs to strings for JSON
                        flow_data["seed_nodes"] = [str(node_id) for node_id in model.content_seed_nodes[content_id]]
                except Exception as e:
                    print(f"Error adding seed nodes to content {content_id}: {e}")
                
                content_flow_data.append(flow_data)
        
        print(f"Exporting {len(content_flow_data)} content flow items for visualization")
    else:
        print("No content_tracker found in model")

    return jsonify({
        "status": "success", 
        "data": data, 
        "agent_data": agent_data,
        "network_data": network_data,
        "content_flow_data": content_flow_data,
        "run_id": run_id  # Return the run ID to client
    })


@bp.route("/api/network-data/<run_id>", methods=["GET"])
def get_network_data_by_run(run_id):
    """Get network structure data for visualization for a specific run."""
    # This would typically fetch stored network data from the database
    # For now, we'll return a simple error since we don't yet store network data
    return jsonify({"status": "error", "message": "Network data not available for historical runs"})


@bp.route("/api/simulation-runs", methods=["GET"])
def get_simulation_runs():
    """Get a list of recent simulation runs."""
    limit = request.args.get("limit", 20, type=int)
    runs = StatsCollector.get_recent_runs(limit=limit)

    return jsonify({"status": "success", "data": runs})


@bp.route("/api/simulation-data/<run_id>", methods=["GET"])
def get_simulation_data(run_id):
    """Get complete data for a simulation run."""
    data = StatsCollector.get_run_data(run_id)

    if not data:
        return jsonify({"status": "error", "message": "Simulation run not found"}), 404

    return jsonify({"status": "success", "data": data})


@bp.route("/api/export-simulation/<run_id>", methods=["GET"])
def export_simulation(run_id):
    """Export simulation data as a JSON or CSV file."""
    # Get requested format from query parameter, default to JSON
    format_type = request.args.get('format', 'json').lower()
    if format_type not in ['json', 'csv']:
        format_type = 'json'  # Default to JSON for safety
    
    # Check if this is a download request vs. a server-save request
    download_requested = request.args.get('download', 'false').lower() == 'true'
    
    # For dynamically generated simulation IDs (not in database)
    if run_id.startswith("sim_"):
        # Return empty data since we don't have database storage for these yet
        data = {
            "id": run_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "name": f"Simulation {run_id}",
            "parameters": {},
            "steps": 0,
            "metrics": {}
        }
    else:
        # Get from database
        data = StatsCollector.get_run_data(run_id)
        if not data:
            return jsonify({"status": "error", "message": "Simulation run not found"}), 404

    # Use simulation name in filename if available
    if data.get("name"):
        # Clean up the name for safe filename use
        safe_name = data["name"].replace(" ", "_").replace("/", "-").replace("\\", "-")
        filename = safe_name
    else:
        filename = f"simulation_{run_id}"

    # Export the file to the appropriate directory
    file_ext = ".json" if format_type == "json" else ".csv"
    export_path = StatsCollector.export_run(run_id, filename=f"{filename}{file_ext}", format=format_type)
    
    # Get the relative path for display
    if export_path:
        # Extract relative path for display to user
        try:
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            rel_path = os.path.relpath(export_path, project_root.parent)
            display_path = rel_path
        except:
            display_path = str(export_path)
        
        print(f"Exported simulation data to: {export_path}")
    else:
        display_path = "Unknown location"
    
    # If download was explicitly requested, send the file
    if download_requested:
        if format_type == 'json':
            # Create a response with the JSON data
            response = make_response(json.dumps(data, indent=2))
            response.headers["Content-Type"] = "application/json"
        else:
            # For CSV, read the file and return its contents
            try:
                with open(export_path, 'r') as f:
                    csv_content = f.read()
                response = make_response(csv_content)
                response.headers["Content-Type"] = "text/csv"
            except Exception as e:
                print(f"Error reading CSV file: {e}")
                # Fallback to JSON if CSV fails
                response = make_response(json.dumps(data, indent=2))
                response.headers["Content-Type"] = "application/json"
                file_ext = ".json"
        
        # Set attachment header for file download
        response.headers["Content-Disposition"] = f"attachment; filename={filename}{file_ext}"
        return response
    else:
        # Return a confirmation message with path and download link
        format_name = "JSON" if format_type == "json" else "CSV"
        return jsonify({
            "status": "success",
            "message": f"Exported {format_name} file saved successfully",
            "file_path": display_path,
            "file_name": f"{filename}{file_ext}",
            "format": format_type,
            "download_url": f"/api/export-simulation/{run_id}?format={format_type}&download=true"
        })


@bp.route("/api/export-html/<run_id>", methods=["GET"])
def export_html(run_id):
    """Export an interactive HTML version of the simulation."""
    # For dynamically generated simulation IDs (not in database)
    if run_id.startswith("sim_"):
        # Return basic data since we don't have database storage for these yet
        data = {
            "id": run_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "name": f"Simulation {run_id}",
            "parameters": {},
            "steps": 0,
            "metrics": {}
        }
    else:
        # Get from database
        data = StatsCollector.get_run_data(run_id)
        if not data:
            return jsonify({"status": "error", "message": "Simulation run not found"}), 404
    
    # Get simulation name for display
    sim_name = data.get("name", f"Simulation {run_id}")
    
    # Use simulation name in filename if available
    if data.get("name"):
        # Clean up the name for safe filename use
        safe_name = data["name"].replace(" ", "_").replace("/", "-").replace("\\", "-")
        filename = safe_name
    else:
        filename = f"simulation_{run_id}"

    # Extract metrics for charts if available
    trust_govt_data = []
    trust_corp_data = []
    trust_infl_data = []
    truth_assess_data = []
    steps = []
    
    if data.get("metrics"):
        # Get steps sorted numerically
        steps = sorted([int(s) for s in data["metrics"].keys()])
        
        for step in steps:
            step_str = str(step)
            if step_str in data["metrics"]:
                metrics = data["metrics"][step_str]
                
                if "avg_trust_government" in metrics:
                    trust_govt_data.append(metrics["avg_trust_government"])
                
                if "avg_trust_corporate" in metrics:
                    trust_corp_data.append(metrics["avg_trust_corporate"])
                    
                if "avg_trust_influencer" in metrics:
                    trust_infl_data.append(metrics["avg_trust_influencer"])
                    
                if "avg_truth_assessment" in metrics:
                    truth_assess_data.append(metrics["avg_truth_assessment"])
    
    # Basic demo HTML with embedded data
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>InfoFlow - {sim_name}</title>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .chart-container {{ height: 400px; margin-bottom: 30px; }}
        .json-data {{ max-height: 500px; overflow-y: auto; }}
        body {{ padding-bottom: 50px; }}
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>InfoFlow Simulation Export</h1>
            <span class="badge bg-secondary">{data.get('timestamp', 'Unknown date')}</span>
        </div>
        
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <i class="bi bi-info-circle-fill me-2"></i>
                <div>
                    <strong>{sim_name}</strong><br>
                    <small class="text-muted">ID: {run_id} - Exported on {time.strftime("%Y-%m-%d %H:%M:%S")}</small>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">Truth Assessment</div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="truthAssessmentChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">Trust Levels</div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="trustLevelsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span>Simulation Data</span>
                <button class="btn btn-sm btn-outline-secondary" id="toggleDataBtn">
                    <i class="bi bi-chevron-down"></i> Show Data
                </button>
            </div>
            <div class="card-body json-data" id="jsonData" style="display:none;">
                <pre>{json.dumps(data, indent=2)}</pre>
            </div>
        </div>
    </div>

    <script>
    // Embedded simulation data
    const simulationData = {json.dumps(data)};
    
    document.addEventListener('DOMContentLoaded', function() {{
        // Truth Assessment Chart
        const truthCtx = document.getElementById('truthAssessmentChart').getContext('2d');
        new Chart(truthCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(steps)},
                datasets: [{{
                    label: 'Truth Assessment',
                    data: {json.dumps(truth_assess_data)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1
                    }}
                }}
            }}
        }});
        
        // Trust Levels Chart
        const trustCtx = document.getElementById('trustLevelsChart').getContext('2d');
        new Chart(trustCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(steps)},
                datasets: [
                    {{
                        label: 'Trust in Corporate Media',
                        data: {json.dumps(trust_corp_data)},
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        tension: 0.1
                    }},
                    {{
                        label: 'Trust in Influencers',
                        data: {json.dumps(trust_infl_data)},
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        tension: 0.1
                    }},
                    {{
                        label: 'Trust in Government',
                        data: {json.dumps(trust_govt_data)},
                        borderColor: 'rgb(153, 102, 255)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        tension: 0.1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 10
                    }}
                }}
            }}
        }});
        
        // Toggle JSON data
        document.getElementById('toggleDataBtn').addEventListener('click', function() {{
            const dataContainer = document.getElementById('jsonData');
            const button = this;
            
            if (dataContainer.style.display === 'none') {{
                dataContainer.style.display = 'block';
                button.innerHTML = '<i class="bi bi-chevron-up"></i> Hide Data';
            }} else {{
                dataContainer.style.display = 'none';
                button.innerHTML = '<i class="bi bi-chevron-down"></i> Show Data';
            }}
        }});
    }});
    </script>
</body>
</html>
"""

    # Set response headers for file download
    response = make_response(html_content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}_export.html"
    response.headers["Content-Type"] = "text/html"

    return response


@bp.route("/api/name-simulation", methods=["POST"])
def name_simulation():
    """Add a name to a simulation run."""
    run_id = request.json.get("run_id")
    name = request.json.get("name", "")

    if not run_id:
        return jsonify({"status": "error", "message": "Missing run_id parameter"}), 400

    # Create a new collector just to name the run
    collector = StatsCollector()
    collector.run_id = run_id
    collector.name_run(name)

    return jsonify(
        {"status": "success", "message": f"Simulation {run_id} named: {name}"}
    )


@bp.route("/api/delete-simulation/<run_id>", methods=["DELETE"])
def delete_simulation(run_id):
    """Delete a simulation run."""
    if not run_id:
        return jsonify({"status": "error", "message": "Missing run_id parameter"}), 400
    
    try:
        # Import the deletion function from delete_runs.py
        import sys
        import os
        
        # Add the project root directory to the Python path
        sys.path.insert(0, os.getcwd())
        
        from delete_runs import delete_run
        
        # Attempt to delete the run
        success = delete_run(run_id)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": f"Simulation {run_id} deleted successfully"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": f"Failed to delete simulation {run_id}"
            }), 404
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error deleting simulation: {str(e)}"
        }), 500


@bp.route("/api/scenarios", methods=["GET"])
def api_list_scenarios():
    """Get a list of all guided scenarios."""
    # Only enable for research scenarios, disable for other scenarios
    scenario_type = request.args.get("type", "")
    
    if scenario_type == "research":
        # Allow research scenarios
        research_scenario_ids = ["trust_study", "network_connectivity", "belief_resistance"]
        scenarios = []
        
        for scenario_id in research_scenario_ids:
            scenario = get_scenario(scenario_id)
            if scenario:
                scenarios.append(scenario)
                
        return jsonify({"status": "success", "scenarios": scenarios})
    else:
        # Temporarily disabled for other scenario types
        return jsonify({"status": "error", "message": "Guided scenarios are temporarily unavailable"}), 503
    # Uncomment to re-enable all scenarios:
    # scenarios = list_scenarios()
    # return jsonify({"status": "success", "scenarios": scenarios})


@bp.route("/api/scenarios/<scenario_id>", methods=["GET"])
def api_get_scenario(scenario_id):
    """Get a specific guided scenario by ID."""
    # Only enable for research scenarios, disable for other scenarios
    research_scenario_ids = ["trust_study", "network_connectivity", "belief_resistance"]
    
    if scenario_id in research_scenario_ids:
        # Allow access to research scenarios
        scenario = get_scenario(scenario_id)
        
        if not scenario:
            return jsonify({"status": "error", "message": f"Scenario '{scenario_id}' not found"}), 404
        
        return jsonify({"status": "success", "scenario": scenario})
    else:
        # Temporarily disabled for other scenarios
        return jsonify({"status": "error", "message": "Guided scenarios are temporarily unavailable"}), 503
    # Uncomment to re-enable all scenarios:
    # scenario = get_scenario(scenario_id)
    # 
    # if not scenario:
    #     return jsonify({"status": "error", "message": f"Scenario '{scenario_id}' not found"}), 404
    # 
    # return jsonify({"status": "success", "scenario": scenario})


@bp.route("/api/metrics-dashboard/<run_id>", methods=["GET"])
def generate_metrics_charts(run_id):
    """Generate and serve charts for the metrics dashboard."""
    # Temporarily disabled
    return jsonify({"status": "error", "message": "Metrics dashboard is temporarily unavailable"}), 503
    
    # Uncomment to re-enable:
    """
    # Generate and serve charts for the metrics dashboard.
    
    # Args:
    #     run_id: ID of the simulation run to generate charts for
    
    try:
        import os
        # Force matplotlib to use a non-interactive backend
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend to prevent window creation
        import matplotlib.pyplot as plt
    """
    # Commented out for temporary disabling:
    #    from infoflow.data.visualization import create_complete_metrics_dashboard
    #    
    #    # Get data for the specified run
    #    data = StatsCollector.get_run_data(run_id)
    #    
    #    if not data:
    #        return jsonify({"status": "error", "message": "Simulation run not found"}), 404
    #    
    #    # Define the directory to save charts
    #    try:
    #        # Get the absolute path to the web module directory
    #        current_dir = os.path.dirname(os.path.abspath(__file__))
    #        
    #        # Define static/charts directory path from the web module
    #        static_dir = os.path.join(current_dir, "static", "charts")
    #        
    #        # Ensure the directory exists
    #        os.makedirs(static_dir, exist_ok=True)
    #        print(f"API using charts directory: {static_dir}")
    #    except Exception as e:
    #        print(f"API error creating charts directory: {e}")
    #        # Fallback to a directory we know should be writable
    #        static_dir = os.path.join(os.getcwd(), "charts")
    #        try:
    #            os.makedirs(static_dir, exist_ok=True)
    #            print(f"API using fallback charts directory: {static_dir}")
    #        except Exception as e2:
    #            print(f"API error creating fallback charts directory: {e2}")
    #            # Last resort - use a temp directory
    #            import tempfile
    #            static_dir = tempfile.mkdtemp(prefix="infoflow_charts_")
    #            print(f"API using temporary charts directory: {static_dir}")
        
    #    # Generate charts using the enhanced visualization module
    #    try:
    #        charts = create_complete_metrics_dashboard(data)
    #        
    #        # Save all charts to the static directory
    #        saved_charts = []
    #        for chart_name, fig in charts.items():
    #            try:
    #                chart_path = os.path.join(static_dir, f"{chart_name}.png")
    #                fig.savefig(chart_path, dpi=100, bbox_inches="tight")
    #                plt.close(fig)
    #                saved_charts.append(chart_name)
    #            except Exception as e:
    #                print(f"Error saving chart {chart_name}: {e}")
    #        
    #        # Return the list of chart names
    #        return jsonify({
    #            "status": "success", 
    #            "message": f"Generated {len(saved_charts)} charts for run {run_id}",
    #            "charts": saved_charts,
    #            "charts_dir": static_dir
    #        })
        
    #    except Exception as e:
    #        print(f"Error generating dashboard charts: {e}")
    #        return jsonify({"status": "error", "message": f"Error generating charts: {str(e)}"}), 500
    #
    #except Exception as e:
    #    print(f"Unexpected error in generate_metrics_charts: {e}")
    #    return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


def get_network_data(model):
    """Extract network data from the model for visualization.
    
    Args:
        model: The simulation model
        
    Returns:
        Dictionary with nodes and links data for network visualization
    """
    G = model.G
    
    # Get node positions using a layout algorithm
    try:
        import networkx as nx
        pos = nx.spring_layout(G, seed=42)  # Fixed seed for reproducibility
    except:
        # Fallback to simple circular layout if spring_layout fails
        pos = {i: [math.cos(2*math.pi*i/len(G)), math.sin(2*math.pi*i/len(G))] for i in G.nodes()}
    
    # Collect all seed nodes for easier lookup
    all_seed_nodes = set()
    seed_node_content = {}  # Maps node ID to content IDs that seeded there
    
    if hasattr(model, "content_seed_nodes"):
        print(f"Found content_seed_nodes with {len(model.content_seed_nodes)} content items")
        try:
            for content_id, seed_nodes in model.content_seed_nodes.items():
                print(f"Content {content_id} has {len(seed_nodes)} seed nodes")
                if not seed_nodes:  # Skip if empty list
                    continue
                    
                for node_id in seed_nodes:
                    node_id_str = str(node_id)
                    all_seed_nodes.add(node_id_str)
                    if node_id_str not in seed_node_content:
                        seed_node_content[node_id_str] = []
                    seed_node_content[node_id_str].append(content_id)
        except Exception as e:
            print(f"Error processing seed nodes: {e}")
            # Recover gracefully
            all_seed_nodes = set()
            seed_node_content = {}
    
    # Create nodes list with attributes
    nodes = []
    for i in G.nodes():
        # Get the agent at this node if it exists
        agents = model.grid.get_cell_list_contents([i])
        
        if agents:
            agent = agents[0]  # Get the first agent (should be a CitizenAgent)
            agent_id = str(agent.unique_id)
            
            # Check if this agent is a seed node for any content
            try:
                is_seed_node = agent_id in all_seed_nodes
            except:
                # Handle any comparison errors
                print(f"Error checking if agent {agent_id} is a seed node")
                is_seed_node = False
            
            node_data = {
                "id": str(i),
                "x": float(pos[i][0]),
                "y": float(pos[i][1]),
                "agent_id": agent_id,
                "truth_assessment": float(getattr(agent, "truth_assessment", 0.5)),
                "size": 8 if is_seed_node else 5,  # Larger size for seed nodes
                "is_seed_node": is_seed_node,
            }
            
            # Add seed content info if applicable
            if is_seed_node:
                # Ensure the content IDs are converted to strings for JSON serialization
                node_data["seed_for_content"] = [str(content_id) for content_id in seed_node_content[agent_id]]
            
            # Add trust levels if available
            if hasattr(agent, "trust_levels"):
                node_data["trust_corporate"] = float(agent.trust_levels.get("CorporateMediaAgent", 5.0))
                node_data["trust_influencers"] = float(agent.trust_levels.get("InfluencerAgent", 5.0))
                node_data["trust_government"] = float(agent.trust_levels.get("GovernmentMediaAgent", 5.0))
            
            nodes.append(node_data)
    
    # Create links list
    links = []
    for source, target in G.edges():
        links.append({
            "source": str(source),
            "target": str(target),
            "value": 1  # Default link strength
        })
    
    return {
        "nodes": nodes,
        "links": links
    }
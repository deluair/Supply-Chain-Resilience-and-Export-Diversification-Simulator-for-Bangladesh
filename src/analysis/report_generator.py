# src/analysis/report_generator.py
import os
import datetime
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, config=None):
        self.config = config if config else {}
        self.report_data = {}

    def add_data(self, key, value):
        """Adds a piece of data to the report."""
        self.report_data[key] = value

    def generate_html_report(self, simulation_summary_data, output_dir="reports", filename="simulation_report.html"):
        """
        Generates an HTML report from the simulation summary data.

        Args:
            simulation_summary_data (dict): A dictionary containing summary data from the simulation.
            output_dir (str): The directory where the report will be saved.
            filename (str): The name of the HTML report file.
        """
        logger.info(f"ReportGenerator.generate_html_report called.")
        logger.info(f"Received output_dir: '{output_dir}', filename: '{filename}'")

        # Ensure output_dir is relative to the project root if it's a relative path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # src/analysis -> src -> project_root
        
        calculated_output_dir = output_dir
        if not os.path.isabs(calculated_output_dir):
            calculated_output_dir = os.path.join(project_root, calculated_output_dir)
        logger.info(f"Calculated absolute output_dir: '{calculated_output_dir}'")

        # Use calculated_output_dir for os.makedirs and os.path.join
        if not os.path.exists(calculated_output_dir):
            try:
                os.makedirs(calculated_output_dir)
                logger.info(f"Created report directory: {calculated_output_dir}")
            except OSError as e:
                logger.error(f"Error creating report directory {calculated_output_dir}: {e}")
                return None

        output_path = os.path.join(calculated_output_dir, filename)
        # Ensure output_dir is relative to the project root if it's a relative path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # src/analysis -> src -> project_root


        html_content = """
        <!DOCTYPE html>
        <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>Simulation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
                .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
                h2 { color: #555; margin-top: 30px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .footer { margin-top: 30px; text-align: center; font-size: 0.9em; color: #777; }
            </style>
        </head>
        <body>
            <div class=\"container\">
                <h1>Simulation Report</h1>
                <p><strong>Report Generated:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <h2>Simulation Summary</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
        """

        # Process summary data robustly for HTML display
        processed_data_for_html = {}
        for key, value in simulation_summary_data.items():
            try:
                processed_key_str = str(key).replace('_', ' ').title()
                processed_value_str = str(value)
                processed_data_for_html[processed_key_str] = processed_value_str
            except Exception as e_data_proc:
                logger.warning(f"Could not process data for report key '{key}' (value: '{value}'): {e_data_proc}. Using placeholder.")
                # Ensure a placeholder is still added to maintain table structure if desired
                processed_data_for_html[str(key).replace('_', ' ').title()] = "[Data Processing Error]"
        
        for key_str, value_str in processed_data_for_html.items():
            html_content += f"<tr><td>{key_str}</td><td>{value_str}</td></tr>\n"
        
        html_content += """
                </table>
                
                <!-- Add more sections here as needed -->

                <div class=\"footer\">
                    <p>&copy; {datetime.datetime.now().year} Bangladesh Supply Chain Simulator</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            with open(output_path, 'w') as f:
                f.write(html_content)
            logger.info(f"HTML report generated successfully: {output_path}")
            return output_path
        except IOError as e:
            logger.error(f"Error writing HTML report to {output_path}: {e}")
            return None

if __name__ == '__main__':
    print("Executing ReportGenerator as standalone script...")
    # Configure basic logging to see output from the ReportGenerator's logger
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()] # Ensure logs go to console
    )
    logger.info("Standalone script execution started (logging has been configured).")

    report_gen = ReportGenerator()
    sample_data = {
        "simulation_run_time_seconds": 120.5,
        "total_simulation_steps": 1000,
        "number_of_factories": 10,
        "number_of_ports": 2,
        "average_product_throughput": 578.3,
        "disruptions_triggered": 5,
        "test_run_indicator": "This is a standalone test run v3"
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_for_standalone = os.path.abspath(os.path.join(script_dir, '..', '..'))
    
    test_output_dir_name = "reports_standalone_test_v3"
    test_output_dir_abs_path = os.path.join(project_root_for_standalone, test_output_dir_name)
    
    print(f"Attempting to generate report in absolute path: {test_output_dir_abs_path}")
    logger.info(f"Target output directory for standalone test (absolute): {test_output_dir_abs_path}")

    report_file = report_gen.generate_html_report(
        simulation_summary_data=sample_data, 
        output_dir=test_output_dir_abs_path, 
        filename="standalone_test_report_v3.html"
    )
    
    if report_file:
        print(f"--- STANDALONE TEST SUCCESS ---")
        print(f"Sample report generated: {os.path.abspath(report_file)}")
    else:
        print(f"--- STANDALONE TEST FAILED ---")
        logger.error("Failed to generate sample report during standalone test.")
    print("Standalone script execution finished.")


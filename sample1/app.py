import psycopg2
import logging
from flask import Flask, request, jsonify
from utility import (
    get_db_connection,
    address_to_coordinates,
    wgs84_to_lambert93,
)

app = Flask(__name__)


def create_app(config_class="app_config.Config"):
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        app = Flask(__name__)
        app.config.from_object(config_class)
        logging.info(f"Loaded configuration: {config_class}")
    except ImportError as e:
        logging.error(f"Error importing configuration '{config_class}': {e}")
        raise

    # Register routes
    register_routes(app)

    return app


def register_routes(app):
    """
    Register all routes with the Flask app.
    """

    @app.route("/api/", methods=["GET"])
    def get_network_coverage():
        address = request.args.get("q")
        if not address:
            return jsonify({"message": "No address provided."}), 400

        coordinates = address_to_coordinates(address)
        if not coordinates:
            return jsonify({"message": "Unable to fetch coordinates."}), 404

        addr_x_l93, addr_y_l93 = wgs84_to_lambert93(
            coordinates["lon"], coordinates["lat"]
        )

        # Determine partition range for x
        if addr_x_l93 < 400000:
            partition = "network_data_p1"
        elif addr_x_l93 < 800000:
            partition = "network_data_p2"
        else:
            partition = "network_data_p3"

        # Query database
        try:
            MAX_DISTANCE = 3000  # radius to search aroud coordinate in meters
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"""
                SELECT Operateur, x, y, g2, g3, g4
                FROM {partition}
                WHERE x BETWEEN %s AND %s AND
                      SQRT(POW(x - %s, 2) + POW(y - %s, 2)) <= {MAX_DISTANCE};
            """
            cursor.execute(
                query,
                (
                    addr_x_l93 - MAX_DISTANCE,
                    addr_x_l93 + MAX_DISTANCE,
                    addr_x_l93,
                    addr_y_l93,
                ),
            )
            rows = cursor.fetchall()
            conn.close()
        except psycopg2.Error as e:
            logging.error(f"Database query failed: {e}")
            return jsonify({"message": "Internal server error"}), 500

        # Map the results directly without additional distance checks
        available_networks = {}
        operator_mapping = {
            "20801": "Orange",
            "20810": "SFR",
            "20820": "Bouygues",
            "20815": "Free",
        }

        for row in rows:
            operator_code, row_x_l93, row_y_l93, g2, g3, g4 = row
            operator_name = operator_mapping.get(
                operator_code, f"Unknown (Code={operator_code})"
            )
            if operator_name not in available_networks:
                available_networks[operator_name] = {"2G": g2, "3G": g3, "4G": g4}

        if not available_networks:
            return jsonify({"message": "No network coverage found."}), 200
        return jsonify(available_networks)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

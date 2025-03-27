from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Set OpenAI API key from env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to PostgreSQL (update this with actual Render/Railway credentials if needed)
DB_CONFIG = {
    "dbname": "nz_standards",
    "user": "postgres",
    "password": "your_password",
    "host": "your_db_host",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Missing keyword"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT clause_id, clause_text
            FROM nzs3604_index
            WHERE searchable @@ plainto_tsquery(%s)
            ORDER BY ts_rank(searchable, plainto_tsquery(%s)) DESC
            LIMIT 10;
        """
        cur.execute(query, (keyword, keyword))
        results = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([
            {"clause_id": row[0], "clause_text": row[1]} for row in results
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app on Render's expected host and port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# Flask backend logic
# (Your full script logic here)
